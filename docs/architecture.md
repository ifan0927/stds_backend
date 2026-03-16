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
| Health Check | `GET /healthz` | 待實作 |
| Graceful Shutdown | SIGTERM → drain → exit | 待實作 |
| DB 連線 | Cloud SQL unix socket / Auth Proxy | 待實作 |
| Secrets | Secret Manager | 待實作 |
| Logging | slog JSON → Cloud Logging | 待實作 |
| Container | non-root、distroless/alpine | 待實作 |

---

## 已建立的實作慣例

> 隨模組開發推進填入。每個模組完成後更新。

### Error Handling

_待 Phase 2 / 第一個模組完成後補充。_

### DTO / Model Mapping

_待第一個模組完成後補充。_

### GORM Query 風格

_待第一個模組完成後補充。_

### Response 格式

_待 Phase 2 Bootstrap 確認後補充。_

---

## 模組開發進度

| 模組 | 狀態 |
|------|------|
| Phase 1 Code Gen | ✅ 完成 |
| Phase 2 Bootstrap | 進行中 |
| Estate | 待開始 |
| Estate Rent | 待開始 |
| Estate Electric | 待開始 |
| Estate Schedule | 待開始 |
| Accounting | 待開始 |
| Users | 待開始 |
| 群組/權限 | 待開始 |
| 檔案管理 | 待開始 |
| Email 通知 | 待開始 |
