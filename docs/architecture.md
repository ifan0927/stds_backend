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

> 隨 Phase 2 Bootstrap 完成後持續補充

| 項目 | 實作方式 | 狀態 |
|------|---------|------|
| Health Check | `GET /healthz` | 已實作 |
| Graceful Shutdown | SIGTERM → drain → exit | 已實作 |
| DB 連線 | Cloud SQL unix socket / Auth Proxy | 已實作 |
| Secrets | Secret Manager | 待實作 |
| Logging | Gin middleware + `slog` JSON + `X-Cloud-Trace-Context` | 已建立基礎 middleware |
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

### DTO / Model Mapping

_待第一個模組完成後補充。_

### GORM Query 風格

- 預設關閉 GORM 內建 logger，避免 SQL 與參數直接輸出到 stdout；需要慢查詢或額外觀測時再透過專案 logging 策略補上

### Config / Bootstrap

- application config 集中於 `internal/config`，由 `caarlos0/env` 自環境變數載入
- DB 連線優先讀 `STDS_DB_URL`，否則以 `DB_*` 欄位組 DSN；Cloud SQL 使用 unix socket 組法
- server entrypoint 統一由 `cmd/server/main.go` 負責 logger、DB、router、graceful shutdown wiring
- OpenAPI generated routes 在模組尚未實作前，可先接 placeholder strict server，不直接在 `main.go` 留未接線 TODO
- `config.Config` 實作 `slog.LogValuer`，避免 DSN / DB password 等敏感設定直接寫入 structured log

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
| Phase 2 Bootstrap | 進行中（logging / error middleware / config / db / main 基礎完成） |
| Estate | 待開始 |
| Estate Rent | 待開始 |
| Estate Electric | 待開始 |
| Estate Schedule | 待開始 |
| Accounting | 待開始 |
| Users | 待開始 |
| 群組/權限 | 待開始 |
| 檔案管理 | 待開始 |
| Email 通知 | 待開始 |
