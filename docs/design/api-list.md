# API 清單

## 模組：物業管理（Estate）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates | 列出物業清單（依 JWT 授權範圍過濾） | 列出物業清單（依業主 session 過濾可見範圍） |
| POST | /v1/estates | 新增物業 | 新增物業（自動建立業主 XOOPS 帳號並加入「業主」群組） |
| GET | /v1/estates/{estateId} | 取得物業詳情 | 檢視物業詳情 |
| PUT | /v1/estates/{estateId} | 更新物業基本資料 | 編輯物業基本資料 |
| DELETE | /v1/estates/{estateId} | 刪除物業 | 刪除物業 |
| GET | /v1/estates/{estateId}/facilities | 列出公共設施清單（含備忘錄） | 管理公共設施：每個設施可上傳圖片、編輯備忘錄 |
| PUT | /v1/estates/{estateId}/facilities | 更新公共設施備忘錄 | 管理公共設施：每個設施可上傳圖片、編輯備忘錄（EAV 儲存） |
| GET | /v1/estates/{estateId}/members | 列出物業成員 | 管理物業成員：設定成員職稱、管理權限（0/1）、行事曆顏色 |
| PUT | /v1/estates/{estateId}/members | 更新物業成員清單（分配/移出） | 物業成員分配：從系統指定群組挑選成員加入/移出物業 |
| PATCH | /v1/estates/{estateId}/members/{userId} | 更新單一成員設定（職稱、權限、顏色） | 管理物業成員：設定成員職稱、管理權限（0/1）、行事曆顏色 |
| GET | /v1/estates/{estateId}/rooms | 列出房間清單（可依區域過濾） | 列出房間清單（支援按區域分頁顯示） |
| POST | /v1/estates/{estateId}/rooms | 新增房間 | 新增房間 |
| GET | /v1/estates/{estateId}/rooms/{roomId} | 取得房間詳情 | 編輯房間（含詳情顯示） |
| PUT | /v1/estates/{estateId}/rooms/{roomId} | 更新房間 | 編輯房間 |
| DELETE | /v1/estates/{estateId}/rooms/{roomId} | 刪除房間 | 刪除房間（連帶刪除附件） |
| POST | /v1/estates/{estateId}/rooms/{roomId}/actions/copy | 複製房間 | 複製房間（房號自動遞增、設備/價格/設施複製） |
| PUT | /v1/estates/{estateId}/rooms/sort | 更新房間排序 | 更新房間排序（拖曳式） |
| GET | /v1/users/available-members | 列出可加入物業的成員候選清單 | 物業成員分配：從系統指定群組挑選成員加入/移出物業 |

> 💡 改善說明：`isBoss` 和 `isMine` 在舊系統為 PHP 函式，新系統由 JWT middleware 統一處理，不設計為獨立 endpoint。
> 💡 改善說明：`send_to_mems`（發送 Email 給物業全體成員）為 side effect，依 feature-list 模組九設計，不設計為獨立 endpoint。
> 💡 改善說明：`JSON API: 取得物業清單及各物業房間清單`（estate/api.php:get_estaties）與 GET /v1/estates 合併，由 client 依需求組合查詢，不需重複設計專屬 JSON API endpoint。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 列出物業清單（依業主 session 過濾可見範圍） | ✅ | GET /v1/estates |
| 2 | 新增物業（自動建立業主 XOOPS 帳號並加入「業主」群組） | ✅ | POST /v1/estates（新系統：自動建立系統使用者並加入「業主」群組） |
| 3 | 編輯物業基本資料 | ✅ | PUT /v1/estates/{estateId} |
| 4 | 刪除物業 | ✅ | DELETE /v1/estates/{estateId} |
| 5 | 檢視物業詳情 | ✅ | GET /v1/estates/{estateId} |
| 6 | 管理公共設施：每個設施可上傳圖片、編輯備忘錄（EAV 儲存） | ✅ | GET + PUT /v1/estates/{estateId}/facilities（備忘錄部分）；設施圖片由模組八 POST /v1/estates/{estateId}/facilities/{facilityName}/attachments 補入 |
| 7 | 管理物業成員：設定成員職稱、管理權限（0/1）、行事曆顏色 | ✅ | PATCH /v1/estates/{estateId}/members/{userId} |
| 8 | 物業成員分配：從系統指定群組挑選成員加入/移出物業 | ✅ | PUT /v1/estates/{estateId}/members + GET /v1/users/available-members |
| 9 | 列出房間清單（支援按區域分頁顯示） | ✅ | GET /v1/estates/{estateId}/rooms?zone=xxx |
| 10 | 新增房間 | ✅ | POST /v1/estates/{estateId}/rooms |
| 11 | 編輯房間 | ✅ | PUT /v1/estates/{estateId}/rooms/{roomId} |
| 12 | 刪除房間（連帶刪除附件） | ✅ | DELETE /v1/estates/{estateId}/rooms/{roomId} |
| 13 | 複製房間（房號自動遞增、設備/價格/設施複製） | ✅ | POST /v1/estates/{estateId}/rooms/{roomId}/actions/copy |
| 14 | 更新房間排序（拖曳式） | ✅ | PUT /v1/estates/{estateId}/rooms/sort |
| 15 | 上傳/管理房間附件 | ✅ | POST /v1/estates/{estateId}/rooms/{roomId}/attachments（模組八補入） |
| 16 | 判斷業主身份（isBoss） | ⏸ | 新系統由 JWT middleware 處理，不需獨立 endpoint |
| 17 | 判斷成員身份及管理權限（isMine） | ⏸ | 新系統由 JWT + estate_member role 處理，不需獨立 endpoint |
| 18 | 發送 Email 給物業全體成員（send_to_mems） | ⏸ | 屬 Email 通知模組 side effect，不設計獨立 endpoint |
| 19 | JSON API：取得物業清單及各物業房間清單 | ✅ | 由 GET /v1/estates 覆蓋，不需重複設計 |

---

## 模組：房客管理（Tenant）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/tenants | 列出房客清單（全域，可依姓名/身份證號搜尋） | 新增房客並關聯到租期（需先能查詢既有房客） |
| POST | /v1/tenants | 新增房客主檔 | 新增房客並關聯到租期 |
| GET | /v1/tenants/{tenantId} | 取得房客詳情 | 顯示租期詳情（房客資料為詳情的一部分） |
| PUT | /v1/tenants/{tenantId} | 更新房客資料 | 編輯租期（含房客資料） |
| DELETE | /v1/tenants/{tenantId} | 刪除房客主檔 | 刪除租期（含房客關聯） |

> 💡 改善說明：舊系統 `xx_estate_user` 為獨立資料表，不隸屬於特定物業，因此新系統將 Tenant 設計為全域實體（`/v1/tenants`）而非嵌套在 estate 路徑下。房客主檔與租約的對應關係由 `rent_tenant_links` 關聯表管理。
> 💡 改善說明：舊系統建立租約時直接在同一表單嵌入房客資料。新系統分離為「先建立/查找房客主檔 → 再關聯至租約」兩步驟，避免房客資料重複，支援同一房客關聯多筆租約歷史。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 新增房客並關聯到租期 | ✅ | POST /v1/tenants（建立主檔）+ POST /v1/estates/{estateId}/rents/{rentId}/tenants（關聯） |
| 2 | 編輯房客資料 | ✅ | PUT /v1/tenants/{tenantId} |
| 3 | 刪除房客 | ✅ | DELETE /v1/tenants/{tenantId}（主檔）；解除關聯由 DELETE /v1/estates/{estateId}/rents/{rentId}/tenants/{tenantId} 處理 |
| 4 | 顯示房客詳情 | ✅ | GET /v1/tenants/{tenantId} |

---

## 模組：租賃管理（Estate Rent）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/rents | 列出物業租期清單（可依狀態、房間過濾） | 列出物業所有租期（含入住/空屋狀態、剩餘天數） |
| POST | /v1/estates/{estateId}/rents | 新增租期（可同時關聯現有房客） | 新增租期（含起始電錶度數、繳費方式、押金、提前入住日） |
| GET | /v1/estates/{estateId}/rents/payment-reminders | 取得物業繳費到期提醒清單 | 顯示全物業繳費到期提醒（比對最後繳費日與下次應繳日） |
| GET | /v1/estates/{estateId}/rents/{rentId} | 取得租期詳情 | 顯示租期詳情 |
| PUT | /v1/estates/{estateId}/rents/{rentId} | 更新租期 | 編輯租期 |
| DELETE | /v1/estates/{estateId}/rents/{rentId} | 刪除租期 | 刪除租期（連帶刪除 estate_rent_user、estate_user 及關聯帳務） |
| GET | /v1/estates/{estateId}/rents/{rentId}/payment-schedule | 計算租金應繳時程 | 計算租金應繳時程（依繳費方式產生繳費日陣列） |
| GET | /v1/estates/{estateId}/rents/{rentId}/payment-notice | 下載租金繳費通知單（PDF） | 列印租金繳費通知單（PDF，每筆未繳費期次一張） |
| GET | /v1/estates/{estateId}/rents/{rentId}/checkout-summary | 下載退租結算書（Word） | 列印退租結算書（Word docx） |
| POST | /v1/estates/{estateId}/rents/{rentId}/actions/terminate-preview | 退租預覽（step 1）：計算電費差值、退款及額外費用 | 執行退租流程 step 1（計算電費差值、退款及額外費用，顯示預覽） |
| POST | /v1/estates/{estateId}/rents/{rentId}/actions/terminate | 確認退租（step 2）：寫入帳務並封存租約 | 執行退租流程 step 2（確認後寫入帳務並封存租約） |
| POST | /v1/estates/{estateId}/rents/{rentId}/actions/reactivate | 取消封存（重新啟用租約） | 取消封存（重新啟用租約） |
| GET | /v1/estates/{estateId}/rents/{rentId}/tenants | 列出租期關聯的房客清單 | 新增房客並關聯到租期（需先能查詢） |
| POST | /v1/estates/{estateId}/rents/{rentId}/tenants | 將現有房客（by tenantId）關聯至租期 | 新增房客並關聯到租期 |
| GET | /v1/estates/{estateId}/rents/{rentId}/tenants/{tenantId} | 取得此租期下特定房客詳情 | 顯示租期詳情（房客資料為詳情的一部分） |
| PUT | /v1/estates/{estateId}/rents/{rentId}/tenants/{tenantId} | 更新房客資料（等同 PUT /v1/tenants/{tenantId}） | 編輯租期（含房客資料） |
| DELETE | /v1/estates/{estateId}/rents/{rentId}/tenants/{tenantId} | 從租期解除房客關聯（不刪除主檔） | 刪除租期（含房客關聯） |

> 💡 改善說明：「列出物業所有租期」與「列出已封存租約」在舊系統為兩個分開的頁面，新系統統一為 GET /v1/estates/{estateId}/rents，以 `status` query 參數（active/archived）區分，減少重複端點。
> 💡 改善說明：退租流程分兩步（step1 預覽 + step2 確認），使用 `/actions/terminate-preview` 和 `/actions/terminate` 明確區分兩個動作，避免用 PATCH 表達複雜狀態轉移。
> 💡 改善說明：計算租金應繳時程（payment-schedule）為純查詢動作，設計為 GET 而非舊系統 PHP function 呼叫，便於 client 在建立租約前預覽時程。
> 💡 改善說明：PDF/Word 下載端點回傳 redirect 至 Cloud Storage 簽署 URL（302），而非直接串流檔案，符合 Cloud Run stateless 設計。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 列出物業所有租期（含入住/空屋狀態、剩餘天數） | ✅ | GET /v1/estates/{estateId}/rents |
| 2 | 顯示全物業繳費到期提醒（比對最後繳費日與下次應繳日） | ✅ | GET /v1/estates/{estateId}/rents/payment-reminders |
| 3 | 新增租期（含起始電錶度數、繳費方式、押金、提前入住日） | ✅ | POST /v1/estates/{estateId}/rents |
| 4 | 編輯租期 | ✅ | PUT /v1/estates/{estateId}/rents/{rentId} |
| 5 | 刪除租期（連帶刪除 estate_rent_user、estate_user 及關聯帳務） | ✅ | DELETE /v1/estates/{estateId}/rents/{rentId} |
| 6 | 顯示租期詳情 | ✅ | GET /v1/estates/{estateId}/rents/{rentId} |
| 7 | 新增房客並關聯到租期 | ✅ | POST /v1/estates/{estateId}/rents/{rentId}/tenants |
| 8 | 計算租金應繳時程（依繳費方式產生繳費日陣列） | ✅ | GET /v1/estates/{estateId}/rents/{rentId}/payment-schedule |
| 9 | 執行退租流程 step 1（計算電費差值、退款及額外費用，顯示預覽） | ✅ | POST /v1/estates/{estateId}/rents/{rentId}/actions/terminate-preview |
| 10 | 執行退租流程 step 2（確認後寫入帳務並封存租約） | ✅ | POST /v1/estates/{estateId}/rents/{rentId}/actions/terminate |
| 11 | 列出已封存租約 | ✅ | GET /v1/estates/{estateId}/rents?status=archived（與現役租約統一端點） |
| 12 | 取消封存（重新啟用租約） | ✅ | POST /v1/estates/{estateId}/rents/{rentId}/actions/reactivate |
| 13 | 列印租金繳費通知單（PDF，每筆未繳費期次一張） | ✅ | GET /v1/estates/{estateId}/rents/{rentId}/payment-notice（302 redirect to signed URL） |
| 14 | 列印退租結算書（Word docx） | ✅ | GET /v1/estates/{estateId}/rents/{rentId}/checkout-summary（302 redirect to signed URL） |
| 15 | 上傳/管理租期附件 | ✅ | POST /v1/estates/{estateId}/rents/{rentId}/attachments（模組八補入） |

---

## 模組：電費管理（Estate Electric）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/electric-readings | 查詢物業電錶度數（支援年月篩選與近 7 個月預設範圍） | 顯示電費管理介面（以物業為單位，顯示近 7 個月的電錶度數格）；查詢特定年月的電錶度數 |
| PATCH | /v1/estates/{estateId}/electric-readings | 批次 upsert 電錶度數（多房間 × 多月份） | 批次輸入電錶度數（房間×月份表格，一次儲存多筆） |
| GET | /v1/estates/{estateId}/electric-report | 下載電費計算報表（Word，302 redirect to signed URL） | 輸出電費計算報表（Word 格式） |
| GET | /v1/estates/{estateId}/electric-receipt | 下載電費收據（PDF，302 redirect to signed URL） | 輸出電費 PDF |

> 💡 改善說明：「顯示電費管理介面」與「查詢特定年月的電錶度數」在舊系統是同一 PHP function（estate_electric_list），新系統統一為 GET /v1/estates/{estateId}/electric-readings，以 query params（year、month、rangeMonths）控制查詢範圍，避免重複端點。
> 💡 改善說明：批次輸入電錶度數使用 PATCH 而非 POST，因為舊系統用 REPLACE INTO（upsert 語意），對已存在的 [roomId, year, month] 組合為更新、對不存在的為新增，PATCH 最能表達此部分更新/upsert 語意。
> 💡 改善說明：Word/PDF 報表端點回傳 302 redirect 至 Cloud Storage 簽署 URL，與租約模組的 payment-notice 及 checkout-summary 設計一致，符合 Cloud Run stateless 設計。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 顯示電費管理介面（以物業為單位，顯示近 7 個月的電錶度數格） | ✅ | GET /v1/estates/{estateId}/electric-readings（預設回傳近 7 個月） |
| 2 | 批次輸入電錶度數（房間×月份表格，一次儲存多筆） | ✅ | PATCH /v1/estates/{estateId}/electric-readings |
| 3 | 查詢特定年月的電錶度數 | ✅ | GET /v1/estates/{estateId}/electric-readings?year=2026&month=3 |
| 4 | 輸出電費計算報表（Word 格式） | ✅ | GET /v1/estates/{estateId}/electric-report?year=2026&month=3（302 redirect） |
| 5 | 輸出電費 PDF | ✅ | GET /v1/estates/{estateId}/electric-receipt?year=2026&month=3（302 redirect） |

---

## 模組：日誌/排程管理（Estate Schedule）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/schedules | 列出物業日誌清單（可依年月、房間、分類、關鍵字過濾，分頁） | 列出物業日誌清單（可依年月、房間、設施、分類、關鍵字過濾，分頁顯示） |
| POST | /v1/estates/{estateId}/schedules | 新增日誌 | 新增日誌（含辦理日期、分類、填報人、協辦人、狀態、內容、帳務） |
| GET | /v1/estates/{estateId}/schedules/{scheduleId} | 取得日誌詳情（含回應清單） | 列出物業日誌清單（詳情為清單的延伸） |
| PUT | /v1/estates/{estateId}/schedules/{scheduleId} | 更新日誌 | 編輯日誌 |
| DELETE | /v1/estates/{estateId}/schedules/{scheduleId} | 刪除日誌（先刪帳務，失敗則整體取消） | 刪除日誌（連帶刪除關聯帳務；帳務刪除失敗則日誌不刪） |
| POST | /v1/estates/{estateId}/schedules/{scheduleId}/replies | 新增日誌回應 | 新增日誌回應 |
| PUT | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId} | 更新日誌回應 | 編輯回應 |
| DELETE | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId} | 刪除日誌回應（連帶刪除附件） | 刪除回應（連帶刪除附件） |

> 💡 改善說明：舊系統 `estate_schedule_assist` 使用 -1/0/>0 三種特殊語意值（無協辦/全體/指定人員），新系統改為 `assistUserId`（null=無協辦、0=全體人員、>0=指定 userId），語意相同但更清晰。
> 💡 改善說明：`estate_schedule_facility`（公共設施關聯）依據待確認清單 #8 答覆，暫時無此需求，不納入本批次設計。
> 💡 改善說明：「依月份分組顯示日誌導覽」（ym_arr）整合在 GET /schedules 的回應結構 `monthGroups` 欄位中，不需獨立 endpoint，避免 client 兩次請求。
> 💡 改善說明：新增/更新日誌及新增回應的 Email 通知設計為 side effect（非同步），不設計獨立 endpoint，詳見 api-info.md。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 列出物業日誌清單（可依年月、房間、設施、分類、關鍵字過濾，分頁顯示） | ✅ | GET /v1/estates/{estateId}/schedules |
| 2 | 新增日誌（含辦理日期、分類、填報人、協辦人、狀態、內容、附件、帳務） | ✅ | POST /v1/estates/{estateId}/schedules（附件待檔案模組） |
| 3 | 編輯日誌 | ✅ | PUT /v1/estates/{estateId}/schedules/{scheduleId} |
| 4 | 刪除日誌（連帶刪除關聯帳務；帳務刪除失敗則日誌不刪） | ✅ | DELETE /v1/estates/{estateId}/schedules/{scheduleId} |
| 5 | 新增日誌回應 | ✅ | POST /v1/estates/{estateId}/schedules/{scheduleId}/replies |
| 6 | 編輯回應 | ✅ | PUT /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId} |
| 7 | 刪除回應（連帶刪除附件） | ✅ | DELETE /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId} |
| 8 | 上傳/管理日誌附件 | ✅ | POST /v1/estates/{estateId}/schedules/{scheduleId}/attachments（模組八補入） |
| 9 | 上傳/管理回應附件 | ✅ | POST /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments（模組八補入） |
| 10 | 新增/更新日誌時自動 Email 通知物業全體成員 | ⏸ | Side effect，不設計獨立 endpoint，於 api-info.md 的 Side Effects 標注 |
| 11 | 新增回應時自動 Email 通知物業全體成員 | ⏸ | Side effect，不設計獨立 endpoint，於 api-info.md 的 Side Effects 標注 |
| 12 | 依月份分組顯示日誌導覽 | ✅ | 整合於 GET /v1/estates/{estateId}/schedules 回應的 monthGroups 欄位 |

---

## 模組：帳務管理（Accounting）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/accountings | 查詢物業帳務記錄清單（支援多維條件過濾，含分頁） | 查詢帳務記錄（支援多維條件過濾：table/col/tag/code/日期區間/頂層對象） |
| POST | /v1/estates/{estateId}/accountings | 新增帳務記錄（收入或支出） | 新增帳務記錄（收入或支出，關聯至各業務物件） |
| GET | /v1/estates/{estateId}/accountings/{accountingId} | 取得單筆帳務詳情 | 查詢帳務記錄 |
| PUT | /v1/estates/{estateId}/accountings/{accountingId} | 更新帳務記錄 | 更新帳務記錄 |
| DELETE | /v1/estates/{estateId}/accountings/{accountingId} | 刪除單筆帳務記錄 | 刪除帳務記錄（可依 accounting_id 或 table+col_name+col_sn 批次刪除） |
| GET | /v1/estates/{estateId}/accountings/overview | 取得物業帳務總覽（上月結餘、本期收支、累計結餘） | 顯示物業帳務總覽（含上月結餘、本期收支、累計結餘） |
| GET | /v1/estates/{estateId}/accounting-titles | 取得適用的收支科目清單 | 取得收支科目清單（依使用的模組過濾適用科目） |

> 💡 改善說明：舊系統的 Polymorphic 設計（accounting_table + accounting_col_name + accounting_col_sn）在新 API 中改為明確的 `linkedResourceType`（如 `rent`、`schedule`）+ `linkedResourceId`，語意清晰且不依賴資料表名稱字串。`accounting_main_col` / `accounting_main_sn` 固定以 `estateId` 取代，因新系統帳務已透過路徑 `/v1/estates/{estateId}/accountings` 限定物業範圍。
> 💡 改善說明：「計算特定對象某日前的結餘」（accounting_date_sum）與「計算特定科目在指定日期區間的加總」（accounting_tid_sum）整合進 GET /v1/estates/{estateId}/accountings/overview 的 query 參數中，避免設計純計算用的特殊 endpoint。
> 💡 改善說明：「現金入款自動同步寫入零用金帳戶」依賴 income 模組（已確認排除），改為在 POST/PUT 帳務的 Side Effect 說明中標注此功能暫不實作，保留 `cashAccountId` 欄位預留。
> 💡 改善說明：科目清單（accounting-titles）為全系統設定資料，新系統固定只回傳物業模組適用科目（46xx 費用類、66xx 收益類），不需傳入模組前綴參數過濾。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 新增帳務記錄（收入或支出，關聯至各業務物件） | ✅ | POST /v1/estates/{estateId}/accountings |
| 2 | 更新帳務記錄 | ✅ | PUT /v1/estates/{estateId}/accountings/{accountingId} |
| 3 | 刪除帳務記錄（可依 accounting_id 或 table+col_name+col_sn 批次刪除） | ✅ | DELETE /v1/estates/{estateId}/accountings/{accountingId}（單筆）；批次刪除由呼叫方（如退租流程）在服務層處理 |
| 4 | 查詢帳務記錄（支援多維條件過濾：table/col/tag/code/日期區間/頂層對象） | ✅ | GET /v1/estates/{estateId}/accountings（query params 支援 linkedResourceType、linkedResourceId、tag、code、dateFrom、dateTo） |
| 5 | 計算特定對象某日前的結餘 | ✅ | GET /v1/estates/{estateId}/accountings/overview?dateTo=xxx 可計算截至特定日的結餘 |
| 6 | 計算特定科目在指定日期區間的加總 | ✅ | GET /v1/estates/{estateId}/accountings/overview?titleId=xxx&dateFrom=xxx&dateTo=xxx |
| 7 | 顯示物業帳務總覽（含上月結餘、本期收支、累計結餘） | ✅ | GET /v1/estates/{estateId}/accountings/overview |
| 8 | 取得收支科目清單（依使用的模組過濾適用科目） | ✅ | GET /v1/estates/{estateId}/accounting-titles |
| 9 | 現金入款自動同步寫入零用金帳戶 | ⏸ | 依賴 income 模組（已確認排除），暫不實作；POST/PUT 帳務保留 cashAccountId 欄位，功能待 income 模組加入後補入 |
| 10 | 取得可選零用金帳戶清單 | ⏸ | 依賴 income 模組（已確認排除），暫不設計 endpoint |

---

## 模組：會員管理（Users）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| POST | /v1/auth/login | 使用者登入，取得 JWT | 登入（重導向至 XOOPS 標準 user.php） |
| POST | /v1/auth/logout | 登出（JWT blacklist / Client 端清除） | 登入功能的對稱操作，JWT stateless 架構標準設計 |
| GET | /v1/users | 列出使用者清單（可依群組過濾，支援多條件搜尋，分頁） | 列出所有使用者（可依群組過濾，支援 name/uname/email/user_occ/bio 搜尋） |
| POST | /v1/users | 新增單一使用者 | 批次新增使用者（單次新增為批次的子集） |
| GET | /v1/users/{userId} | 取得使用者詳情 | 列出所有使用者（詳情為清單的延伸） |
| PUT | /v1/users/{userId} | 更新使用者資料（職業、簡介、密碼、所屬群組） | 編輯使用者（職業、簡介、密碼、所屬群組） |
| POST | /v1/users/batch | 批次新增使用者 | 批次新增使用者 |
| POST | /v1/users/import | 匯入使用者（CSV 上傳） | 匯入使用者（Excel/CSV） |
| POST | /v1/users/actions/batch-add-group | 批次將使用者加入群組 | 批次加入群組 |
| POST | /v1/users/actions/batch-remove-group | 批次將使用者從群組移除 | 批次移除群組 |
| PATCH | /v1/users/actions/batch-update-field | 批次更新使用者單一欄位值 | 批次更新單一欄位值 |
| GET | /v1/users/check-username | 查詢帳號是否已存在 | 查詢帳號是否已存在 |
| PATCH | /v1/users/me/password | 使用者自行修改密碼（需驗證現有密碼） | 編輯使用者（職業、簡介、密碼、所屬群組）── 自服務密碼修改場景 |

> 💡 改善說明：舊系統「登入」重導向至 XOOPS 標準 user.php，新系統採用 JWT stateless 認證，改為 POST /v1/auth/login 回傳 JWT token，由 client 保存於 Authorization header，不需 session/cookie。
> 💡 改善說明：舊系統密碼使用 MD5（無 salt），新系統改為 bcrypt（Go 標準 golang.org/x/crypto/bcrypt），密碼欄位永不在 response body 出現。
> 💡 改善說明：「批次新增使用者」與「新增單一使用者」在舊系統為同一入口（add.php），新系統分離為 POST /v1/users（單筆）和 POST /v1/users/batch（多筆陣列），語意更明確。
> 💡 改善說明：「查詢帳號是否已存在」（id_existed）設計為 GET /v1/users/check-username?username=xxx，以 query param 傳入帳號，回傳 200（包含 exists: true/false），符合 RESTful GET 語意且避免 POST 查詢。
> 💡 改善說明：批次操作（batch-add-group、batch-remove-group、batch-update-field）在舊系統為 PHP function call，新系統設計為 `/v1/users/actions/xxx` 動作端點，符合「無法用純 CRUD 表達的動作」的 actions 慣例。
> 💡 改善說明：舊系統 user_intrest 欄位（借用儲存 estate_id）和 actkey 欄位（借用儲存 estate_id 清單）在新系統均廢棄，改由 estate_member_links 和業主 User 的明確關聯管理，不在 Users API 設計任何借用欄位。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 列出所有使用者（可依群組過濾，支援 name/uname/email/user_occ/bio/user_intrest 搜尋） | ✅ | GET /v1/users（搜尋欄位：name、username、email、occupation、bio；user_intrest 欄位廢棄，不納入搜尋） |
| 2 | 編輯使用者（職業、簡介、密碼、所屬群組） | ✅ | PUT /v1/users/{userId}（admin 後台）；使用者自行改密碼由 PATCH /v1/users/me/password 處理 |
| 3 | 批次新增使用者 | ✅ | POST /v1/users/batch（多筆）、POST /v1/users（單筆） |
| 4 | 匯入使用者（Excel/CSV） | ✅ | POST /v1/users/import（multipart/form-data，CSV 格式） |
| 5 | 批次加入群組 | ✅ | POST /v1/users/actions/batch-add-group |
| 6 | 批次移除群組 | ✅ | POST /v1/users/actions/batch-remove-group |
| 7 | 批次更新單一欄位值 | ✅ | PATCH /v1/users/actions/batch-update-field |
| 8 | 登入（重導向至 XOOPS 標準 user.php） | ✅ | POST /v1/auth/login（新系統改為 JWT，不需重導向） |
| 9 | 查詢帳號是否已存在 | ✅ | GET /v1/users/check-username?username=xxx |

---

## 模組：群組/權限管理（Groups）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/groups | 列出群組清單（可依 groupType 過濾，支援分頁） | 建立群組（需先能列出群組）；依群組篩選可選成員 |
| POST | /v1/groups | 建立新群組 | 建立群組（estate/index.php:insert_estate 中 user_group::mk_group 呼叫） |
| GET | /v1/groups/{groupId} | 取得群組詳情（含成員清單） | 建立群組；依群組篩選可選成員 |
| PUT | /v1/groups/{groupId} | 更新群組資料（名稱、說明） | 建立群組（群組維護的對稱操作） |
| DELETE | /v1/groups/{groupId} | 刪除群組 | 建立群組（群組維護的對稱操作） |

> 💡 改善說明：舊系統 `xx_group_permission`（XOOPS 框架的模組功能權限機制）依賴 `gperm_modid`（xx_modules.mid）與 XOOPS 框架整合，新系統不使用 XOOPS 框架，此機制整體廢棄。新系統存取控制改為 JWT role（系統管理員 vs 一般使用者）+ estate_member level（物業層級的 admin/readonly 區分）統一處理，不需要 XOOPS 式的 group_permission 端點。
> 💡 改善說明：新增/移除使用者至群組（feature-list 第 2、3 項）已在模組六設計為 `POST /v1/users/actions/batch-add-group` 與 `POST /v1/users/actions/batch-remove-group`，模組七不重複設計，語意一致。
> 💡 改善說明：依群組篩選可選成員（feature-list 第 4 項）已在物業管理模組設計為 `GET /v1/users/available-members?groupId=xxx`，模組七不重複設計。
> 💡 改善說明：判斷使用者是否屬於業主群組（`isBoss`）與屬於專案群組（`send_to_group`）在舊系統為 PHP 函式，新系統由 JWT payload 中的 `roles` / `groupIds` 欄位提供，middleware 統一判斷，不設計為獨立 endpoint。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 建立群組（estate/index.php:insert_estate 中 user_group::mk_group 呼叫） | ✅ | POST /v1/groups |
| 2 | 新增使用者至群組（tad_users/admin/main.php:add_group） | ⏸ | 已在模組六 POST /v1/users/actions/batch-add-group 完成，語意一致，不重複設計 |
| 3 | 從群組移除使用者（tad_users/admin/main.php:del_group） | ⏸ | 已在模組六 POST /v1/users/actions/batch-remove-group 完成，語意一致，不重複設計 |
| 4 | 依群組篩選可選成員（estate/index.php:estate_mem_setup L574） | ⏸ | 已在模組一 GET /v1/users/available-members?groupId=xxx 完成，不重複設計 |
| 5 | 判斷使用者是否屬於「業主」群組（estate/function.php:isBoss） | ⏸ | 新系統由 JWT payload 中群組資訊提供，middleware 統一判斷，不需獨立 endpoint |
| 6 | 判斷使用者是否屬於「專案群組」（estate/function.php:send_to_group） | ⏸ | 同上，JWT middleware 處理 |
| 7 | 模組功能存取權限管理（xx_group_permission，XOOPS 框架機制） | ⏸ | XOOPS 框架特有機制，新系統以 JWT role + estate_member level 取代，不設計對應 endpoint |

---

## 模組：檔案管理（Attachments）

> 採用「附件掛在父資源下」的子資源設計模式，讓各模組共用同一套附件機制，取代舊系統的 polymorphic col_name/col_sn 設計。
> 所有附件路徑均具備完整的父資源路徑，以確保存取控制由 estate_id middleware 統一驗證。

### 房間附件

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/rooms/{roomId}/attachments | 列出房間附件清單 | 上傳/管理房間附件（取得清單） |
| POST | /v1/estates/{estateId}/rooms/{roomId}/attachments | 上傳房間附件 | 上傳/管理房間附件 |
| GET | /v1/estates/{estateId}/rooms/{roomId}/attachments/{attachmentId}/download | 取得附件下載連結（302 redirect to signed URL） | 取得檔案下載/預覽連結 |
| PATCH | /v1/estates/{estateId}/rooms/{roomId}/attachments/{attachmentId} | 更新附件說明 | 更新檔案說明 |
| DELETE | /v1/estates/{estateId}/rooms/{roomId}/attachments/{attachmentId} | 刪除附件 | 刪除檔案（同步刪除 Cloud Storage 物件與資料庫記錄） |
| PUT | /v1/estates/{estateId}/rooms/{roomId}/attachments/sort | 更新房間附件排序 | 更新檔案排序 |

### 設施附件（公共設施圖片）

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/facilities/{facilityName}/attachments | 列出設施附件清單 | 管理公共設施：每個設施可上傳圖片 |
| POST | /v1/estates/{estateId}/facilities/{facilityName}/attachments | 上傳設施圖片 | 管理公共設施：每個設施可上傳圖片 |
| GET | /v1/estates/{estateId}/facilities/{facilityName}/attachments/{attachmentId}/download | 取得設施圖片下載連結 | 取得檔案下載/預覽連結 |
| PATCH | /v1/estates/{estateId}/facilities/{facilityName}/attachments/{attachmentId} | 更新設施附件說明 | 更新檔案說明 |
| DELETE | /v1/estates/{estateId}/facilities/{facilityName}/attachments/{attachmentId} | 刪除設施附件 | 刪除檔案 |
| PUT | /v1/estates/{estateId}/facilities/{facilityName}/attachments/sort | 更新設施附件排序 | 更新檔案排序 |

### 租期附件

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/rents/{rentId}/attachments | 列出租期附件清單 | 上傳/管理租期附件（取得清單） |
| POST | /v1/estates/{estateId}/rents/{rentId}/attachments | 上傳租期附件 | 上傳/管理租期附件 |
| GET | /v1/estates/{estateId}/rents/{rentId}/attachments/{attachmentId}/download | 取得附件下載連結（302 redirect to signed URL） | 取得檔案下載/預覽連結 |
| PATCH | /v1/estates/{estateId}/rents/{rentId}/attachments/{attachmentId} | 更新附件說明 | 更新檔案說明 |
| DELETE | /v1/estates/{estateId}/rents/{rentId}/attachments/{attachmentId} | 刪除附件 | 刪除檔案 |
| PUT | /v1/estates/{estateId}/rents/{rentId}/attachments/sort | 更新租期附件排序 | 更新檔案排序 |

### 日誌附件

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/schedules/{scheduleId}/attachments | 列出日誌附件清單 | 上傳/管理日誌附件（取得清單） |
| POST | /v1/estates/{estateId}/schedules/{scheduleId}/attachments | 上傳日誌附件 | 上傳/管理日誌附件 |
| GET | /v1/estates/{estateId}/schedules/{scheduleId}/attachments/{attachmentId}/download | 取得附件下載連結（302 redirect to signed URL） | 取得檔案下載/預覽連結 |
| PATCH | /v1/estates/{estateId}/schedules/{scheduleId}/attachments/{attachmentId} | 更新附件說明 | 更新檔案說明 |
| DELETE | /v1/estates/{estateId}/schedules/{scheduleId}/attachments/{attachmentId} | 刪除附件 | 刪除檔案 |
| PUT | /v1/estates/{estateId}/schedules/{scheduleId}/attachments/sort | 更新日誌附件排序 | 更新檔案排序 |

### 日誌回應附件

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments | 列出回應附件清單 | 上傳/管理回應附件（取得清單） |
| POST | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments | 上傳回應附件 | 上傳/管理回應附件 |
| GET | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments/{attachmentId}/download | 取得附件下載連結（302 redirect to signed URL） | 取得檔案下載/預覽連結 |
| PATCH | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments/{attachmentId} | 更新附件說明 | 更新檔案說明 |
| DELETE | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments/{attachmentId} | 刪除附件 | 刪除檔案 |
| PUT | /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments/sort | 更新回應附件排序 | 更新檔案排序 |

### 物業整體附件

> 對應 `attachments.resource_type = 'estate'`，用於掛載在物業整體層級的通用文件（如管委會章程、物業平面圖、管理規約等），不屬於特定房間、租約、日誌或設施。

| Method | Path | 說明 | feature-list 依據 |
|--------|------|------|-----------------|
| GET | /v1/estates/{estateId}/attachments | 列出物業整體附件清單 | Q11 決策：新增 resource_type='estate' 支援物業層級附件 |
| POST | /v1/estates/{estateId}/attachments | 上傳物業整體附件 | Q11 決策：新增 resource_type='estate' 支援物業層級附件 |
| GET | /v1/estates/{estateId}/attachments/{attachmentId}/download | 取得附件下載連結（302 redirect to signed URL） | 取得檔案下載/預覽連結 |
| PATCH | /v1/estates/{estateId}/attachments/{attachmentId} | 更新附件說明 | 更新檔案說明 |
| DELETE | /v1/estates/{estateId}/attachments/{attachmentId} | 刪除附件 | 刪除檔案（同步刪除 Cloud Storage 物件與資料庫記錄） |
| PUT | /v1/estates/{estateId}/attachments/sort | 更新物業整體附件排序 | 更新檔案排序 |

> 💡 改善說明：舊系統 `xx_estate_files_center` 以 `col_name`（如 "estate_room_id"）+ `col_sn` 的 polymorphic 設計定位附件所屬對象。新系統改為各資源的 API 路徑下掛載 `attachments` 子資源，語意明確且與 REST 路由一致，也方便 middleware 統一驗證 estate 存取範圍。
> 💡 改善說明：附件下載連結設計為獨立的 `/download` 子路徑（回傳 302 redirect 至 Cloud Storage 簽署 URL），而非在 GET attachments 清單中直接暴露 storage 路徑。這與舊系統 `hash_filename` 防止直接存取的設計意圖一致，且符合 Cloud Run stateless 設計。
> 💡 改善說明：舊系統 `kind` 欄位（enum 'img'/'file'）在新系統改由 MIME type 自動判斷，不需 client 傳入，減少人為分類錯誤。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 上傳檔案（支援圖片與一般檔案，存入 Cloud Storage） | ✅ | POST /v1/estates/{estateId}/{resourceType}/{resourceId}/attachments（各資源子路徑） |
| 2 | 取得資源附件清單（依 resource_type + resource_id 查詢） | ✅ | GET /v1/estates/{estateId}/{resourceType}/{resourceId}/attachments |
| 3 | 刪除檔案（同步刪除 Cloud Storage 物件與資料庫記錄） | ✅ | DELETE /v1/estates/{estateId}/{resourceType}/{resourceId}/attachments/{attachmentId} |
| 4 | 取得檔案下載/預覽連結（回傳 Cloud Storage 簽署 URL） | ✅ | GET /v1/estates/{estateId}/{resourceType}/{resourceId}/attachments/{attachmentId}/download（302 redirect） |
| 5 | 更新檔案排序 | ✅ | PUT /v1/estates/{estateId}/{resourceType}/{resourceId}/attachments/sort |
| 6 | 更新檔案說明 | ✅ | PATCH /v1/estates/{estateId}/{resourceType}/{resourceId}/attachments/{attachmentId} |

---

## 模組：Email 通知（Notification）

> 本模組不產出獨立 API endpoint。Email 通知為各業務操作的 side effect，觸發規則與收件對象已在各模組的 api-info.md Side Effects 說明中定義。
> 本節僅作覆蓋率驗證與觸發點彙整，不新增任何 openapi.yaml path 或 schema。

### 觸發點彙整

| 觸發操作 | Endpoint | 收件對象 | Email 標題格式 |
|----------|----------|----------|----------------|
| 新增物業且自動建立業主帳號 | POST /v1/estates | 業主本人（ownerEmail） | 帳號開通通知 |
| 新增日誌 | POST /v1/estates/{estateId}/schedules | 物業全體成員 | 「{estate.shortTitle}」新進度 |
| 更新日誌 | PUT /v1/estates/{estateId}/schedules/{scheduleId} | 物業全體成員 | 「{estate.shortTitle}」新進度 |
| 新增日誌回應 | POST /v1/estates/{estateId}/schedules/{scheduleId}/replies | 物業全體成員 | 「{estate.shortTitle}」回應通知 |

> 所有 Email 通知均為非同步 fire-and-forget 發送，發送失敗不影響主業務操作的成功回應。

### 覆蓋率驗證

| # | feature-list 功能項目 | 狀態 | 備注 |
|---|----------------------|------|------|
| 1 | 發送通知 Email 給物業全體成員（send_to_mems） | ⏸ | Side effect，不設計獨立 endpoint；觸發規則由各模組 api-info.md Side Effects 定義 |
| 2 | 新增租約時通知相關成員 | ⏸ | feature-list 依據標注「各模組 insert 操作後的 send_to_mems 呼叫」，但實際 PHP 程式碼（estate/rent.php:insert_estate_rent）無 send_to_mems 呼叫，且業務分析確認不觸發通知；api-info.md 已標注「Email 通知：無」 |
| 3 | 新增日誌/排程時通知相關成員 | ⏸ | Side effect，已在 POST /schedules、PUT /schedules/{scheduleId} 的 api-info.md 完整定義 |
| 4 | 新增帳務記錄時通知相關成員 | ⏸ | feature-list 依據標注「accounting 模組 insert 操作後的通知邏輯」，但 PHP 程式碼（accounting/api.php:insert_accounting）無通知邏輯；api-info.md 已標注「Email 通知：無」 |
