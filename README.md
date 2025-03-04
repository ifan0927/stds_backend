# 物業管理系統 API

## 概述

此 API 作為一個正在開發中的物業管理內部系統的後端，專為代書和物業管理服務設計。系統旨在簡化物業管理操作、租戶管理、會計和行政任務。

⚠️ **注意：此專案目前正在積極開發中。**

## 功能特色

物業管理系統提供以下核心功能：

- **物業管理**：追蹤和管理物業、建築和設施
- **房間管理**：管理個別房間、其詳細信息和可用性
- **租賃管理**：處理租戶協議、押金和租賃期間
- **用戶管理**：通過基於角色的權限控制系統訪問
- **會計**：追蹤收入、支出並生成財務報告
- **電費記錄**：監控和計費公共事業使用情況
- **排程管理**：安排維護和檢查時間
- **文件管理**：存儲和檢索重要文件
- **加班追蹤**：管理員工加班和審批
- **電子郵件通知**：各種事件的自動通信

## 認證

API 使用 OAuth2 進行認證。用戶需要通過 `/auth/token` 端點進行認證以接收訪問令牌，該令牌應包含在後續請求中。

``` 
POST /auth/token 
```

還可以通過 `/auth/refresh` 端點獲取刷新令牌。

## API 結構

API 按以下邏輯模塊組織：

- `/estates` - 物業管理
- `/rooms` - 房間管理
- `/rentals` - 租戶和租賃協議管理
- `/users` - 租戶信息管理
- `/auth` - 認證和員工用戶管理
- `/electric_records` - 公用事業使用追蹤
- `/files` - 文件管理
- `/schedules` - 事件排程
- `/accounting` - 財務記錄
- `/overtime_payments` - 員工加班管理
- `/emails` - 通知服務

## 技術細節

- API 遵循 RESTful 原則
- 數據以 JSON 格式交換
- 驗證錯誤以標準化格式返回詳細信息
- 大多數端點需要認證
- 支持通過 `skip` 和 `limit` 參數進行分頁

## 入門指南

1. `git clone` 此專案
2. 配置環境變量
   - 本專案使用兩個 `.env` 分別設定 `docker-compose` 和 `fastapi` 的環境變數
3. 透過 `docker-compose` 建置
4. 在 `/docs` 或 `/redoc` 訪問 API 文檔

## Jenkins 自動化部署學習紀錄

此專案透過 Jenkins 進行自動化部署，以下是學習與實作的紀錄：

### 1. Jenkins Master-Slave 架構
- 一般情況下，Master-Slave 架構應該分佈在不同主機，但由於此專案規模較小，Master 與 Slave 現在同在一台 VM。
- 儘管如此，仍然維持 Slave Node 的概念，以確保未來可擴展性。

### 2. 憑證與敏感資料管理
- 使用 Jenkins `credentials()` 管理敏感資訊，例如 `docker-compose-env`、`fastapi-env`、`gcp-service-account`、`gcp-bucket-name`。
- `.env` 檔案用於環境變數，而大型檔案則存放於 GCP Cloud Storage Bucket。

### 3. Jenkins 工作區與權限處理
- 最初 Jenkins 共享同一個工作區，導致權限問題。
- 由於專案使用 Docker Compose，發現工作區影響較小，因此改用 Jenkins 預設工作區，避免權限錯誤。

### 4. Jenkins Pipeline 設定
- **Checkout**：從 GitHub 下載程式碼。
- **Setup Environment**：設置環境變數，確保敏感資料安全。
- **Build and Deploy**：使用 `docker-compose` 建立並啟動服務。
- **Health Check**：確保 API 服務正常運行。
- **Post 部署步驟**：成功或失敗後，清理敏感資料。

---
此 Jenkins 自動化流程幫助專案順利部署，並展示了 CI/CD 的基本實踐，對於未來的開發與維運具有實際價值。