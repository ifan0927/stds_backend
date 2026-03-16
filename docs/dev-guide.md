# STDS Backend — 開發指南

## 目錄

- [環境設定](#環境設定)
- [本地開發啟動](#本地開發啟動)
- [新增 API 流程](#新增-api-流程)
- [Code Gen（oapi-codegen）](#code-genoapi-codegen)
- [Database Migration](#database-migration)
- [Agent 使用指南](#agent-使用指南)

---

## 環境設定

設定檔位置：`.env`（本地開發，不進 git）

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=stds
DB_PASSWORD=stds
DB_NAME=stds_dev
DB_SSLMODE=disable

# golang-migrate 用
DATABASE_URL=postgres://stds:stds@localhost:5432/stds_dev?sslmode=disable
```

> Production 設定從環境變數注入（Cloud Run），不使用 .env 檔案。

---

## 本地開發啟動

### 啟動 PostgreSQL

```bash
# 啟動
docker compose up -d

# 確認狀態
docker compose ps

# 停止
docker compose down
```

`docker-compose.yml` 設定：
- image：`postgres:16`
- port：`5432`
- volume：`pgdata`（持久化）
- healthcheck：`pg_isready`

### 啟動 API Server

```bash
go run ./cmd/server
```

---

## 新增 API 流程

### 步驟概覽

```
1. /agent-designer  設計 API + Schema
       ↓
2. 更新 docs/design/openapi.yaml（agent 輸出）
       ↓
3. 執行 oapi-codegen 重新 generate
       ↓
4. 撰寫 migration SQL
       ↓
5. 執行 migration
       ↓
6. 實作 handler / service / repository（使用者手寫）
```

### 詳細說明

#### 1. 設計階段

使用 `/agent-designer` 描述新功能需求。

agent 會：
- 資訊不足時提出問題（討論模式）
- 資訊充足時依序輸出設計文件（設計模式）：
  1. `docs/design/api-list.md`（追加）
  2. `docs/design/openapi.yaml`（追加）
  3. `docs/design/api-info.md`（追加）
  4. `docs/design/schema.md`（追加）
  5. `docs/design/erd.mermaid`（更新）

> 注意：`docs/design/` 下的文件為唯讀設計文件，不手動修改。

#### 2. Code Gen

設計文件更新後，重新執行 code gen（見下方 [Code Gen](#code-genoapi-codegen) 章節）。

#### 3. Migration

依 schema.md 撰寫 migration SQL（見下方 [Database Migration](#database-migration) 章節）。

#### 4. 實作

依 `docs/spec/` 下的 spec 進行實作，層次順序：
```
repository → service → handler
```

---

## Code Gen（oapi-codegen）

### 設定檔

`oapi-codegen.yaml`（專案根目錄）：

```yaml
package: api
generate:
  gin-server: true
  strict-server: true
  models: true
output: internal/api/api.gen.go
```

### 執行指令

```bash
# 從 openapi.yaml 重新生成
oapi-codegen -config oapi-codegen.yaml docs/design/openapi.yaml
```

> 若未安裝 oapi-codegen：
> ```bash
> go install github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@latest
> ```

### 注意事項

- 輸出檔案 `internal/api/api.gen.go` 為**唯讀，不手動修改**
- 每次 `openapi.yaml` 有變動後都需要重新執行
- strict-server 模式：handler 需實作 typed request/response interface

---

## Database Migration

### 工具

[golang-migrate](https://github.com/golang-migrate/migrate)

> 若未安裝：
> ```bash
> brew install golang-migrate
> # 或
> go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest
> ```

### 設定

- Migration 檔案路徑：`migration/`
- 命名格式：`{version}_{description}.up.sql` / `{version}_{description}.down.sql`
- 版本編號：6 位數字，如 `000018_create_foo.up.sql`

### 常用指令

```bash
# 執行所有 pending migration（up）
migrate -path ./migration -database "$STDS_DB_URL" up

# 回滾最後一個 migration（down 1 步）
migrate -path ./migration -database "$STDS_DB_URL" down 1

# 回滾所有 migration
migrate -path ./migration -database "$STDS_DB_URL" down

# 查看目前 migration 版本
migrate -path ./migration -database "$STDS_DB_URL" version

# 強制設定版本（修復 dirty state 用）
migrate -path ./migration -database "$STDS_DB_URL" force {version}
```

> `$DATABASE_URL` 取自 `.env`,開發環境已設定環境變數：
> ```
> DATABASE_URL=postgres://stds:stds@localhost:5432/stds_dev?sslmode=disable
> ```

### 新增 Migration 檔案

```bash
# 建立新的 migration 檔案對
migrate create -ext sql -dir migration -seq {description}
# 例：
migrate create -ext sql -dir migration -seq create_notifications
# 產出：
#   migration/000018_create_notifications.up.sql
#   migration/000018_create_notifications.down.sql
```

### 匯入資料

> /migration_input為原系統資料
> /migration/data中放的是匯入腳本使用說明如下
```bash
# 匯入全部
go run ./migration/data/... --module=all --input=./migration_input
# 測試輸入
go run ./migration/data/... --module=all --input=./migration_input --dry-run

```

---

## Agent 使用指南

所有 agent 由使用者主動呼叫，不主動介入。

| Agent | 指令 | 用途 |
|-------|------|------|
| **agent-designer** | `/agent-designer` | 設計新功能的 API + DB Schema |
| **tutor** | `/tutor` | 解釋 Go / Gin / GORM 概念，給方向與 pseudocode |
| **codereview** | `/codereview` | PR 級別 code review，輸出建議（不 auto-fix） |

### agent-designer 使用方式

```
/agent-designer 我需要一個通知功能，使用者可以收到系統通知，支援已讀/未讀狀態管理。
```

agent 若資訊不足，會先列出問題清單請你確認；確認後再輸出設計文件。

### 設計文件結構

```
docs/
├── design/          ← agent-designer 輸出，唯讀
│   ├── api-list.md
│   ├── openapi.yaml
│   ├── api-info.md
│   ├── schema.md
│   └── erd.mermaid
├── spec/            ← dev agent 任務 spec
│   ├── dev-spec-template.md
│   ├── phase2-bootstrap/
│   ├── estate/
│   └── ...（各模組）
└── architecture.md  ← 全 agent 共用，活文件
```
