# STDS Backend — Project Architecture

這是活文件，隨模組開發推進持續更新。
所有 agent 應以此文件作為架構一致性的基準。

---

## 目錄結構

```
internal/
├── api/          ← oapi-codegen 生成，唯讀，不手動修改
├── handler/      ← HTTP handler 實作，精簡，只做 request parsing + 呼叫 service + 回傳 response
├── middleware/   ← auth、logging、error handling
├── repository/   ← GORM query，資料存取層
└── service/      ← 業務邏輯編排，transaction 邊界在此層管理

docs/
├── design/       ← API / schema 設計文件，唯讀
└── spec/         ← dev agent 的任務 spec（Markdown）

migration/        ← golang-migrate SQL 檔案
```

---

## 各層職責

| 層 | 職責 | 不做 |
|----|------|------|
| **handler** | request parsing、basic validation、呼叫 service、HTTP response 組裝 | 不含業務規則、不直接呼叫 repository |
| **service** | 業務流程編排、商業規則、transaction 邊界協調 | 不含 HTTP 細節、不直接組 SQL |
| **repository** | GORM query、資料讀寫、not found / constraint error 處理 | 不含業務規則、不知道 HTTP |

---

## Tech Stack 關鍵決策

| 項目 | 決策 |
|------|------|
| Code Gen | oapi-codegen v2.6.0，strict-server 模式 |
| 生成檔案 | `internal/api/api.gen.go`（單一檔案，唯讀） |
| Server 模式 | strict-server（typed request/response） |
| ORM | GORM |
| Config | caarlos0/env，所有設定從環境變數注入 |
| 日誌 | slog，JSON 格式，structured logging |

---

## Cloud Ready 關鍵決策

| 項目 | 實作方式 | 狀態 |
|------|---------|------|
| Health Check | `GET /healthz`，含 DB ping | ✅ 已實作 |
| Graceful Shutdown | `signal.NotifyContext` + `http.Server.Shutdown(ctx)` | ✅ 已實作 |
| DB 連線 | `DATABASE_DSN` 環境變數注入；Cloud SQL unix socket 組法 | ✅ 已實作 |
| Secrets | Secret Manager | 待實作 |
| Logging | Gin middleware + `slog` JSON + `X-Cloud-Trace-Context` | ✅ 已實作 |
| Secret 保護 | `config.Config` / `DBconfig` 實作 `slog.LogValuer`，DSN/JWTSecret 不寫入 log | ✅ 已實作 |
| Container | non-root、distroless/alpine | 待實作 |

---

## 已建立的實作慣例

> 隨模組開發推進填入。每個模組完成後更新。

### Error Handling

- 共用錯誤型別集中於 `internal/apperr`
- 錯誤代碼常數集中於 `internal/apperr/code.go`，常數值需直接對齊 OpenAPI `ErrorResponse.code`
- `AppError` 區分 `HTTPStatus`、對外 `Code`/`Message`、對內原始 `Err`
- validation 錯誤以 `[]ErrorDetail` 承載欄位明細，供 middleware 映射 API response
- Gin error handler middleware 讀取 `c.Errors`，統一轉為 OpenAPI `ErrorResponse`
- OpenAPI wrapper 的 request parse/bind error 對外只回固定訊息，不直接暴露 codegen/govalidator 內部錯誤細節
- **Internal error 兩種用法：**
  - 有原始 `error` cause（如 DB error、外部呼叫失敗）：用 `apperr.WrapInternal(err)`，保留 cause 供 Cloud Logging 追查
  - 純邏輯狀態異常（如 context 缺少預期值）、無 cause：用 `apperr.NewInternalError()`

### DTO / Model Mapping

_待第一個模組完成後補充。_

### 跨模組 Transaction 慣例

**適用場景：** 單一 service 操作需要寫入多個 repository（如 Estate 建立時同步建立業主 User）。

**兩種 service 結構，依是否需要 transaction 選擇：**

| 情境 | Service struct 設計 |
|---|---|
| 單模組，不需要 tx | 持有 `repo XxxRepository`（interface instance） |
| 跨模組，需要 tx | 持有 `db *gorm.DB` + `xxxRepo func(*gorm.DB) XxxRepository`（factory function） |

**跨模組 tx 的 service 結構方向：**

```go
// service/estate.go
type estateService struct {
    db         *gorm.DB
    estateRepo func(*gorm.DB) EstateRepository
    userRepo   func(*gorm.DB) UserRepository  // 跨模組，interface 定義在此
    groupRepo  func(*gorm.DB) GroupRepository // 跨模組，module 7 實作；interface 定義在此
}

func (s *estateService) Create(ctx context.Context, input CreateEstateInput) (*EstateRow, error) {
    var result *EstateRow
    err := s.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
        estateRepo := s.estateRepo(tx)
        userRepo   := s.userRepo(tx)
        groupRepo  := s.groupRepo(tx)
        // ... return nil = commit, return err = rollback
    })
    return result, err
}
```

**Wiring（`cmd/server/setup.go`）：**

```go
estateService := service.NewEstateService(
    db,
    repository.NewEstateRepo,   // func(*gorm.DB) service.EstateRepository
    repository.NewUserRepo,     // func(*gorm.DB) service.UserRepository
    repository.NewGroupRepo,    // func(*gorm.DB) service.GroupRepository
)
```

**重點：**
- Repository struct 設計不變（持有 `DB *gorm.DB`），在 tx closure 內用 tx 建立 instance，`r.DB` 自動是 tx
- 跨模組的 `UserRepository` interface 定義在 **使用方**（`service/estate.go`），只宣告 estate 需要的方法，不是 user 模組的全部
- 不需要 tx 的 service（如 auth）完全不受影響，繼續用 instance 注入

### Estate 業主帳號建立慣例

`POST /v1/estates` 觸發的業主帳號建立流程，**在同一個 transaction 內完成**：

1. 以 `ownerEmail` 查找 `users` 表，已存在則直接使用該 user ID
2. 不存在：建立新 user（`ownerUsername` / `ownerName` / `ownerEmail` 來自 request，`role = 'user'`，隨機初始密碼 bcrypt hash 儲存）
3. 若業主 user 尚未在「業主」user_group 中，將其加入（`GroupRepository.AddUserToOwnerGroup`，module 7 實作）
4. 建立 estate，`owner_user_id` 指向上述 user
5. 將業主加入 `estate_member_links`，`member_level = readonly`
6. commit 後，由 Email 模組（模組九）非同步寄送初始密碼通知給業主（僅新建帳號時觸發）

`PUT /v1/estates/:id` 更新時：
- `ownerName` / `ownerEmail` 同步寫入對應 `users` 記錄（同一 transaction，使用 `UserRepository.UpdateOwnerInfo`）
- 若 `ownerEmail` 異動且新 email 對應到**不同**的現有使用者，回傳 400（不允許透過 PUT 切換業主）
- `user_group` 與 `estate_member_links` 不受 PUT 影響

### GORM Query 風格

- 預設關閉 GORM 內建 logger，避免 SQL 與參數直接輸出到 stdout；需要慢查詢或額外觀測時再透過專案 logging 策略補上
- 單筆查詢一律使用 `First`（自動加 `LIMIT 1`，找不到時回傳 `gorm.ErrRecordNotFound`）；`Scan` 用於多筆查詢或明確不需要 not-found 語意的場景
- Repository 的 `gorm.ErrRecordNotFound` 統一在 repository 層轉為 domain error（如 `service.ErrNotFound`、`auth.ErrUserNotFound`），不往上暴露 GORM 內部型別
- Repository struct 欄位命名：`DB *gorm.DB`（全大寫縮寫，符合 Go convention）

### Seed Data

- Seed 腳本放在 `migration/data/seed/`，對應 `--module=seed`，與 module01、module02 平行
- **每個模組開發前**需補齊：該模組 Request schema 的 `openapi.yaml example` 值 + 對應 DB seed 資料，兩者保持同步
- 密碼以 `bcrypt.DefaultCost` hash 儲存；seed 帳號密碼與 openapi.yaml example 值綁定
- 標準 seed 帳號：

  | username | password | role |
  |----------|----------|------|
  | alice | secret123 | admin |
  | bob | secret123 | member |

- Seed 資料僅供開發環境，不進 production migration

### Auth / Context

- JWT claims 與 context helpers 集中於 `internal/auth`
- Auth middleware 驗證 token 後，將 `*auth.Claims` 與 `*auth.UserState` 存入 request context
- Context 存取 helpers 命名規則：`XxxFromContext(ctx)`（如 `ClaimsFromContext`、`UserStateFromContext`），不使用 `GetXxx` 前綴
- Middleware 傳遞 context 給下層時使用 `c.Request.Context()`，不直接傳 `*gin.Context`
- JWT Claims 僅包含 `sub`（userID）、`username`、`role`（系統層角色 admin/user）、`exp`、`iat`；**物業存取清單不放入 JWT**
- 物業層授權（member_level）由 `StateLoader` 在每次 request 動態從 DB 載入，結果存入 `*auth.UserState`；handler 從 `UserState` 取 estate 存取資訊

### ListEstates 授權 Filter 慣例

`ListEstates` 由 handler 萃取 claims 後傳入 filter，service 不直接存取 auth package：

```go
type EstateListFilter struct {
    AllowedIDs []int64 // nil = 不過濾（system admin）；非 nil = 只回傳清單內的物業
}

func (s *estateService) ListEstates(ctx context.Context, page, pagesize int, filter EstateListFilter) (PageInfo, []EstateSummary, error)
```

Handler 責任：
- `role=admin`：傳入 `EstateListFilter{AllowedIDs: nil}`
- `role=user`：從 `claims.Estates` 萃取 ID 清單，傳入 `EstateListFilter{AllowedIDs: ids}`

### Config / Bootstrap

- application config 集中於 `internal/config`，由 `caarlos0/env` 自環境變數載入
- DB 連線由 `DATABASE_DSN` 環境變數注入；Cloud SQL 使用 unix socket 組法
- server entrypoint 為 `cmd/server/main.go`，純 wiring（解析 config → init logger → init DB → init router → 啟動 server → graceful shutdown）
- bootstrap 輔助函式（`initLogger`、`initRouter`）集中於 `cmd/server/setup.go`，不放在 `main.go`
- OpenAPI generated routes 在模組尚未實作前，接 placeholder strict server（`panic("not implemented")`），搭配 `gin.Recovery()` 確保不 crash
- `config.Config` 與 `config.DBconfig` 均實作 `slog.LogValuer`，避免 DSN / JWTSecret 等敏感設定寫入 structured log
- `apperr.AppError` 實作 `Unwrap() error`，確保 `errors.Is` / `errors.As` 可穿透 error chain

### Response 格式

- 錯誤回應統一使用 OpenAPI `ErrorResponse`
- `details` 僅在 validation error 且有欄位明細時回傳

### Logging

- request logging 由最外層 Gin middleware 負責，確保 401/404 等請求也會留下 log
- request ID 優先沿用 `X-Request-Id`，否則生成 UUID，並同步寫回 response header 與 gin context
- request log 使用 `slog.Info` 輸出 structured JSON，欄位固定包含 request metadata 與 `X-Cloud-Trace-Context`

### Documentation

- 補充 godoc 時，預設以英文撰寫標準 declaration comment，內容應以目前實作責任為準，不延伸承諾尚未存在的行為
- 檔案範圍明確的註解任務可使用 `docs/spec/godoc-file-scope-template.md` 作為通用 spec 起點

---

## 模組開發進度

| 模組 | 狀態 |
|------|------|
| Phase 1 Code Gen | ✅ 完成 |
| Phase 2 Bootstrap | ✅ 完成 |
| Auth | ✅ 完成 |
| Estate | 待開始 |
| Estate Rent | 待開始 |
| Estate Electric | 待開始 |
| Estate Schedule | 待開始 |
| Accounting | 待開始 |
| Users | 待開始 |
| 群組/權限 | 待開始 |
| 檔案管理 | 待開始 |
| Email 通知 | 待開始 |
