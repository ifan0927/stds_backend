# API 業務邏輯說明

## 模組：物業管理（Estate）

---

## POST /v1/estates

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色（`role=admin`）
2. 驗證必填欄位（title、shortTitle、ownerName、ownerEmail、electricityRate、electricityBillingCycle）
3. 驗證 ownerEmail 格式合法
4. 查詢資料庫是否已有相同 email 的使用者帳號
   - 若有：取得現有使用者的 userId
   - 若無：自動建立新使用者帳號，帳號名稱取 email `@` 前段，初始密碼由系統產生並以 email 發送，並將新使用者加入「業主」群組
5. 若使用者已存在但尚未在「業主」群組，將其加入
6. 寫入 estates 資料表，關聯 ownerUserId
7. 回傳 201 + Location header + 完整物業詳情

### Side Effects
- Email 通知：若自動建立業主帳號，寄送帳號開通通知 Email 給 ownerEmail
- 其他副作用：自動建立系統使用者帳號（若同 email 帳號不存在）；自動將業主帳號加入「業主」群組

### PHP 參考
- `estate/index.php:insert_estate`（L121-214）
- `estate/class/user_group.php:add_user_to_xoops`
- `estate/class/user_group.php:mk_group`

---

## PUT /v1/estates/{estateId}

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證 estateId 存在
3. 驗證 JWT 中 estateId 授權範圍（middleware）
4. 驗證必填欄位
5. 更新 estates 資料表
6. 回傳 200 + 完整更新後的物業詳情

### Side Effects
- Email 通知：無
- 其他副作用：若 ownerEmail 異動，不自動重建帳號（僅更新 ownerEmail 欄位）

### PHP 參考
- `estate/index.php:update_estate`（L217-280）

---

## DELETE /v1/estates/{estateId}

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證 estateId 存在
3. 刪除 estate_member_links（成員關聯）
4. 刪除 estate 主檔記錄
5. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：cascade 刪除 estate_member_links。注意：房間、租約、帳務等資料需在 cascade 策略中明確定義（建議 DB 層以外鍵約束控制，或由服務層先驗證無子資源）

### PHP 參考
- `estate/index.php` switch case `delete_estate_list`

---

## PUT /v1/estates/{estateId}/facilities

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限（memberLevel=admin）或系統管理員
2. 驗證 estateId 存在
3. 驗證 facilityName 存在於 estate.facilities 清單中；若不存在回傳 `VALIDATION_ERROR`（details.field = facilityName）
4. 更新對應設施的備忘錄記錄（upsert：存在則更新，不存在則建立）
5. 回傳 200 + 完整設施清單（含所有設施的備忘錄）

### Side Effects
- Email 通知：無
- 其他副作用：舊系統以 EAV（xx_estate_data_center）儲存備忘錄；新系統改為獨立的 facility_memos 資料表，schema 由 agent-schema-designer 定義

### PHP 參考
- `estate/index.php:save_estate_facility`（L381-389）
- `TadDataCenter:saveData`（第三方 lib，新系統不沿用）

---

## PUT /v1/estates/{estateId}/members

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限（memberLevel=admin）或系統管理員
2. 驗證 estateId 存在
3. 驗證每個 userId 存在於使用者資料表
4. 取得現有成員清單，比對差異：
   - 新增：在 estate_member_links 建立記錄，memberLevel 預設為 `readonly`
   - 移除：從 estate_member_links 刪除記錄（保留 estate_mems 個人設定不刪除，避免重新加入時需重設）
   - 無變化：保留
5. 回傳 200 + 完整成員清單

### Side Effects
- Email 通知：無
- 其他副作用：移除成員時不刪除 estate_mems 個人設定（職稱、顏色），方便日後重新加入時恢復設定

### PHP 參考
- `estate/index.php:save_estate_mem`（L497-525）
- `estate/index.php:estate_mem_setup`（L564-620）

---

## PATCH /v1/estates/{estateId}/members/{userId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限（memberLevel=admin）或系統管理員
2. 驗證 estateId 存在，estateId 在 JWT 授權範圍內
3. 驗證 userId 存在於此物業的成員清單（estate_member_links）
4. 若提供 calendarTextColor 或 calendarBgColor，驗證格式為合法 hex 色碼（`#RRGGBB`）
5. 更新 estate_member_links 的 memberLevel（若提供）
6. Upsert estate_mems 的個人設定（unit、title、calendarTextColor、calendarBgColor）
7. 回傳 200 + 更新後的成員資料

### Side Effects
- Email 通知：無
- 其他副作用：estate_mems 為跨物業的個人設定（一個使用者只有一筆）；更新時會影響該使用者在所有物業的個人顯示資訊（職稱、顏色）

### PHP 參考
- `estate/index.php:save_estate_mem_setup`（L527-562）

---

## POST /v1/estates/{estateId}/rooms

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 estateId 存在
3. 驗證 roomNumber 不為空
4. 若提供 zone，驗證 zone 值存在於 estate.zones 清單中
5. 若未提供 sortOrder，自動取現有最大排序 + 1
6. 寫入 rooms 資料表
7. 回傳 201 + Location header + 完整房間詳情

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `estate/room.php:insert_estate_room`（L122-178）

---

## PUT /v1/estates/{estateId}/rooms/{roomId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 estateId 和 roomId 存在，且 room 屬於該 estate
3. 若提供 zone，驗證 zone 值存在於 estate.zones 清單
4. 更新 rooms 資料表
5. 回傳 200 + 完整更新後的房間詳情

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `estate/room.php:update_estate_room`（L182-222）

---

## DELETE /v1/estates/{estateId}/rooms/{roomId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 roomId 存在且屬於 estateId
3. 查詢該房間是否有現役租約（rentEnable=true）；若有則回傳 409 `ROOM_ALREADY_RENTED`
4. 刪除房間附件（Cloud Storage 物件 + 資料庫記錄）（待檔案模組確認介面）
5. 刪除 rooms 資料表記錄
6. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：連帶刪除房間所有附件（Cloud Storage 物件及資料庫記錄）

### PHP 參考
- `estate/room.php:delete_estate_room`（L226-240）

---

## POST /v1/estates/{estateId}/rooms/{roomId}/actions/copy

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 roomId 存在且屬於 estateId
3. 讀取原房間所有欄位
4. 計算新房號：取原房號首字元 + (原末尾數字 + 1)，例如 A101 → A102
5. 新 sortOrder = 原 sortOrder + 1
6. 複製欄位：facilities、prices、note、zone、storey、roomType、sizeSquareMeter
7. 寫入新房間記錄
8. 附件不複製（舊系統有複製附件邏輯，新系統實作時由檔案模組確認後決定）
9. 回傳 201 + Location header + 完整新房間詳情

### Side Effects
- Email 通知：無
- 其他副作用：無（附件不複製）

### PHP 參考
- `estate/room.php:estate_room_copy`（L419-478）

---

## PUT /v1/estates/{estateId}/rooms/sort

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 estateId 存在
3. 驗證提交清單中的所有 roomId 均屬於 estateId；若有不屬於的 roomId 回傳 `VALIDATION_ERROR`
4. 批次更新 rooms 的 sortOrder
5. 回傳 200 + 更新後的排序清單

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `estate/room.php` switch case `update_estate_room_sort`

---

## 模組：房客管理（Tenant）

---

## POST /v1/tenants

### 業務邏輯步驟
1. 驗證請求者已認證（任何已登入使用者均可建立房客主檔）
2. 驗證必填欄位（name）
3. 寫入 tenants 資料表
4. 回傳 201 + Location header（/v1/tenants/{tenantId}）+ 完整房客資料

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `estate/rent.php:insert_estate_rent_user`（L302-340，舊系統建立房客邏輯，新系統獨立為全域 CRUD）

---

## PUT /v1/tenants/{tenantId}

### 業務邏輯步驟
1. 驗證請求者已認證
2. 驗證 tenantId 存在
3. 驗證必填欄位（name）
4. 更新 tenants 資料表
5. 回傳 200 + 完整更新後的房客資料

### Side Effects
- Email 通知：無
- 其他副作用：此房客關聯的所有租約讀取房客資料時，將反映更新後的內容（共享同一主檔）

### PHP 參考
- `estate/rent.php:update_estate_rent`（含房客資料更新邏輯）

---

## DELETE /v1/tenants/{tenantId}

### 業務邏輯步驟
1. 驗證請求者已認證
2. 驗證 tenantId 存在
3. 查詢 rent_tenant_links，若該房客有任何關聯租約則回傳 409 `TENANT_HAS_ACTIVE_RENTS`
4. 刪除 tenants 資料表記錄
5. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：無（刪除前需確保無任何 rent_tenant_link 關聯）

### PHP 參考
- `estate/rent.php:delete_estate_rent`（含房客刪除邏輯，舊系統隨租約一起刪除，新系統需先解除所有關聯）

---

## 模組：租賃管理（Estate Rent）

---

## POST /v1/estates/{estateId}/rents

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限（memberLevel=admin）或系統管理員
2. 驗證 estateId 存在，且在 JWT 授權範圍內
3. 驗證必填欄位（roomId、startDate、endDate、paymentMethod、deposit、initialElectricReading）
4. 驗證 endDate > startDate
5. 若提供 earlyMoveInDate，驗證 earlyMoveInDate <= startDate
6. 驗證 roomId 存在且屬於 estateId
7. 查詢 roomId 是否已有 status=active 的現役租約；若有則回傳 409 `ROOM_ALREADY_RENTED`
8. 若提供 tenants 陣列，驗證每個 tenantId 存在於 tenants 資料表；若有不存在的 tenantId 回傳 400 `VALIDATION_ERROR`
9. 寫入 rents 資料表（status=active）
10. 若提供 tenants 陣列，批次寫入 rent_tenant_links（rentId + 每個 tenantId）
11. 回傳 201 + Location header + 完整租期詳情（含關聯房客清單）

### Side Effects
- Email 通知：無（feature-list 未標注新增租約時發送通知）
- 其他副作用：若提供 tenants，自動建立 rent_tenant_links 關聯記錄

### PHP 參考
- `estate/rent.php:insert_estate_rent`（L55-120）

---

## PUT /v1/estates/{estateId}/rents/{rentId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 estateId 存在，rentId 存在且屬於 estateId
3. 查詢租約 status；若 status=archived 則回傳 409 `RENT_ALREADY_TERMINATED`
4. 驗證必填欄位
5. 驗證 endDate > startDate
6. 若提供 earlyMoveInDate，驗證 earlyMoveInDate <= startDate
7. 更新 rents 資料表
8. 回傳 200 + 完整更新後的租期詳情

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `estate/rent.php:update_estate_rent`（L124-180）

---

## DELETE /v1/estates/{estateId}/rents/{rentId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 rentId 存在且屬於 estateId
3. 查詢是否有關聯帳務記錄（accounting 表中 accounting_col_name='estate_rent_id' AND accounting_col_sn=rentId）；若有則回傳 409 `CANNOT_DELETE_HAS_ACCOUNTING`
4. 刪除所有 rent_tenant_links（租期與房客的關聯記錄）
5. 刪除 rent 主檔記錄
6. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：cascade 刪除 rent_tenant_links 關聯記錄。Tenant 主檔不會被刪除（保留以供歷史查閱或重新關聯）。帳務記錄存在時刪除被擋（需先手動處理帳務）

### PHP 參考
- `estate/rent.php:delete_estate_rent`（L247-254；舊系統刪除租約時同時刪除房客主檔，新系統僅刪除關聯）

---

## POST /v1/estates/{estateId}/rents/{rentId}/tenants

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 rentId 存在且屬於 estateId
3. 驗證必填欄位（tenantId）
4. 驗證 tenantId 存在於 tenants 資料表；若不存在回傳 404 `TENANT_NOT_FOUND`
5. 查詢 rent_tenant_links，確認此 tenantId 尚未關聯至此 rentId；若已關聯回傳 409 `TENANT_ALREADY_LINKED`
6. 建立 rent_tenant_link 關聯（rentId + tenantId）
7. 回傳 201 + Location header（/v1/estates/{estateId}/rents/{rentId}/tenants/{tenantId}）+ 完整房客資料

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `estate/rent.php:insert_estate_rent_user`（L302-340，舊系統為建立+關聯，新系統僅關聯）

---

## PUT /v1/estates/{estateId}/rents/{rentId}/tenants/{tenantId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 tenantId 存在且已關聯至此 rentId（查詢 rent_tenant_links）
3. 驗證必填欄位（name）
4. 更新 tenants 主檔記錄（與 PUT /v1/tenants/{tenantId} 相同效果）
5. 回傳 200 + 完整更新後的房客資料

### Side Effects
- Email 通知：無
- 其他副作用：由於更新的是全域 tenant 主檔，此房客關聯的所有租約資料均反映更新後的內容

### PHP 參考
- `estate/rent.php:update_estate_rent`（含房客資料更新邏輯）

---

## DELETE /v1/estates/{estateId}/rents/{rentId}/tenants/{tenantId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 tenantId 存在且已關聯至此 rentId（查詢 rent_tenant_links）；若無關聯記錄回傳 404 `TENANT_NOT_FOUND`
3. 刪除 rent_tenant_link 關聯記錄（僅解除關聯，不刪除 tenant 主檔）
4. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：僅刪除關聯記錄，tenant 主檔保留。如需刪除主檔，需另外呼叫 DELETE /v1/tenants/{tenantId}

### PHP 參考
- `estate/rent.php:delete_estate_rent`（含房客刪除邏輯，L247-254；舊系統刪除關聯同時刪除主檔，新系統分離）

---

## POST /v1/estates/{estateId}/rents/{rentId}/actions/terminate-preview

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 rentId 存在且屬於 estateId
3. 查詢租約 status；若 status=archived 則回傳 409 `RENT_ALREADY_TERMINATED`
4. 驗證必填欄位（terminationDate、finalElectricReading、reason）
5. 驗證 finalElectricReading >= rent.initialElectricReading（退租度數不可小於入住度數）
6. 取得物業電費單價（estate.electricityRate）
7. 計算電費：electricityUsage = finalElectricReading - initialElectricReading；electricityCost = round(electricityUsage * electricityRate)
8. 計算退押金：depositRefund = -deposit（負數表示退款）
9. 彙整 additionalCharges（damageFee、cleaningFee、otherFee、rentBack）
10. 計算 totalRefund = depositRefund + rentBack - damageFee - cleaningFee - otherFee
11. 回傳 200 + 結算預覽（不寫入 DB）

### Side Effects
- Email 通知：無
- 其他副作用：無（純計算，不寫入任何資料）

### PHP 參考
- `estate/rent.php:estate_rent_stop`（L839-932，step 1 計算邏輯）

---

## POST /v1/estates/{estateId}/rents/{rentId}/actions/terminate

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 rentId 存在且屬於 estateId
3. 查詢租約 status；若 status=archived 則回傳 409 `RENT_ALREADY_TERMINATED`
4. 驗證必填欄位（terminationDate、finalElectricReading、reason）
5. 驗證 finalElectricReading >= rent.initialElectricReading
6. Server 端重新計算各費用（同 terminate-preview 步驟 6-10，不信任 client 傳入的計算結果）
7. 寫入帳務記錄（accounting 表）：
   a. 電費（accounting_tag='電費'，income）
   b. 退押金（accounting_tag='押金'，income 負數）
   c. 毀損費（accounting_tag='退租其他費用'，income，若 > 0）
   d. 清潔費（accounting_tag='退租其他費用'，income，若 > 0）
   e. 其他費用（accounting_tag='退租其他費用'，income，若 > 0）
   f. 未到期租金退還（accounting_tag='租金'，income 負數，若 > 0）
8. 將退租結算資訊序列化寫入 rent.terminationInfo（JSON）
9. 更新租約 status 為 archived（estate_rent_enable='0'）
10. 回傳 200 + 完整更新後的租期詳情

### Side Effects
- Email 通知：無（feature-list 未標注退租時發送通知）
- 其他副作用：建立多筆帳務記錄（電費、退押金、額外費用），並將租約封存

### PHP 參考
- `estate/rent.php:estate_rent_checkout`（L856-932）

---

## POST /v1/estates/{estateId}/rents/{rentId}/actions/reactivate

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 rentId 存在且屬於 estateId
3. 查詢租約 status；若 status=active 則已是現役（不需重新啟用，回傳 409 `RENT_ALREADY_ACTIVE`）
4. 查詢同一 roomId 是否已有其他 status=active 的租約；若有則回傳 409 `ROOM_ALREADY_RENTED`
5. 清除 rent.terminationInfo（設為 null）
6. 更新租約 status 為 active（estate_rent_enable='1'）
7. 回傳 200 + 完整更新後的租期詳情

### Side Effects
- Email 通知：無
- 其他副作用：terminationInfo 被清除；先前因退租建立的帳務記錄不會自動刪除（需人工處理）

### PHP 參考
- `estate/rent.php`（模板 op_show_unable_rent.tpl enable_rent op，PHP 邏輯從模板推斷）

### 待確認
- 🟡 取消封存時，先前的退租帳務記錄是否需要一併刪除？假設：不自動刪除，由使用者手動處理。

---

## 模組：電費管理（Estate Electric）

---

## PATCH /v1/estates/{estateId}/electric-readings

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限（memberLevel=admin）或系統管理員
2. 驗證 estateId 存在且在 JWT 授權範圍內
3. 驗證 items 陣列不為空
4. 對每個 item 驗證：
   a. roomId 存在且屬於此 estateId；若不屬於回傳 400 `VALIDATION_ERROR`（details.field = items[n].roomId）
   b. year 範圍合法（2000–9999）
   c. month 範圍合法（1–12）
   d. degrees >= 0
5. 批次執行 upsert（以 [roomId, year, month] 為唯一鍵）：
   - 若該 [roomId, year, month] 已有記錄：更新 degrees、recordedBy（取 JWT userId）、updatedAt
   - 若無記錄：新增
6. 回傳 200 + 本次 upsert 的所有記錄（items 陣列）

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `estate/electric.php:save_estate_electric`（L100-140；使用 REPLACE INTO 執行 upsert）

---

## GET /v1/estates/{estateId}/electric-report

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內
2. 驗證 estateId 存在
3. 驗證 year、month query 參數必填且範圍合法
4. 查詢此物業所有房間及各房間當月（year/month）與前一個月（year/month-1）的電錶度數
   - 前期度數邏輯：若該房間有現役租約且「入住月 > 前一個月」，則前期度數取 initialElectricReading（入住起始電錶度數）
5. 計算各房間用電量：currentDegrees - prevDegrees
6. 計算各房間電費：round(usedDegrees * estate.electricityRate)
7. 產生 Word 報表並存入 Cloud Storage（或即時產生 signed URL）
8. 回傳 302 redirect 至 Cloud Storage 簽署 URL

### Side Effects
- Email 通知：無
- 其他副作用：產生 Word 檔案存入 Cloud Storage（或即時 signed URL，由實作決定是否持久化）

### PHP 參考
- `estate/word_estate_electric.php`（L1-181；完整 Word 產生邏輯）

---

## GET /v1/estates/{estateId}/electric-receipt

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內
2. 驗證 estateId 存在
3. 驗證 year、month query 參數必填且範圍合法
4. 查詢此物業所有有現役租約的房間，以及各房間當月與前一個月的電錶度數
   - 前期度數邏輯同 electric-report（若為新入住月，前期取 initialElectricReading）
5. 計算各房間電費金額
6. 產生 PDF（每個房間一張收據，含存根聯與顧客留存聯）並存入 Cloud Storage
7. 回傳 302 redirect 至 Cloud Storage 簽署 URL

### Side Effects
- Email 通知：無
- 其他副作用：產生 PDF 存入 Cloud Storage（或即時 signed URL，由實作決定是否持久化）

### PHP 參考
- `estate/pdf_electric.php`（L1-214；完整 PDF 產生邏輯，含 pdf_block 和 pdf_blank 函式）

---

## 模組：日誌/排程管理（Estate Schedule）

---

## POST /v1/estates/{estateId}/schedules

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內（estateId 在 JWT 授權範圍）
2. 驗證必填欄位（scheduledAt、kind、status、content）
3. 若 roomId 有值，驗證該 roomId 屬於此 estateId（否則回傳 ROOM_NOT_FOUND）
4. 若 reporterUserId 有值，驗證該 userId 存在；不帶時取 JWT 當前使用者
5. 若 assistUserId > 0，驗證該 userId 存在（0 = 全體人員，null = 無協辦，不需驗證）
6. 寫入 schedules 資料表
7. 自動建立一筆帳務記錄：
   - tag = '日誌'
   - accountingCode = scheduleId
   - accountingDate = scheduledAt
   - accountingTitle = content 去除 HTML 後前 36 個字元
   - income = 0，expenditure = 0（預設無金額）
   - 關聯欄位：table='estate_schedule'、colName='estate_schedule_id'、colSn=scheduleId
   - 頂層關聯：mainCol='estate_id'、mainSn=estateId
8. 回傳 201 + Location header + 完整 Schedule 物件
9. 非同步發送 Email 通知給物業全體成員（fire-and-forget）

### Side Effects
- Email 通知：觸發條件為新增日誌成功；收件對象為物業全體成員（estate_mem_link 中此 estateId 的所有成員）；Email 標題格式「「{estate.shortTitle}」新進度」；內容含辦理日期、辦理狀況、填報人、協辦人員、日誌內容
- 其他副作用：自動建立關聯帳務記錄（金額 0，tag='日誌'）

### PHP 參考
- `estate/function_log.php:insert_estate_schedule`
- `estate/function_log.php:send_to_mems`

---

## PUT /v1/estates/{estateId}/schedules/{scheduleId}

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於此 estateId（否則回傳 SCHEDULE_NOT_FOUND）
3. 驗證必填欄位（scheduledAt、kind、status、content）
4. 若 roomId 有值，驗證該 roomId 屬於此 estateId
5. 若 assistUserId > 0，驗證該 userId 存在
6. 更新 schedules 資料表（reporterUserId 不可修改，忽略 request body 中的此欄位）
7. 同步更新關聯帳務記錄：
   - 查詢 tag='日誌' 且 accountingCode=scheduleId 的帳務記錄
   - 若存在：更新 accountingTitle（content 去除 HTML 前 36 字元）和 accountingDate（scheduledAt）
   - 若不存在：補建一筆帳務記錄（同 POST 步驟 7）
8. 回傳 200 + 完整更新後的 Schedule 物件
9. 非同步發送 Email 通知給物業全體成員（fire-and-forget）

### Side Effects
- Email 通知：觸發條件為更新日誌成功；收件對象及格式與 POST 相同
- 其他副作用：同步更新關聯帳務記錄的 title 與 date

### PHP 參考
- `estate/function_log.php:update_estate_schedule`

---

## DELETE /v1/estates/{estateId}/schedules/{scheduleId}

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於此 estateId（否則回傳 SCHEDULE_NOT_FOUND）
3. 嘗試刪除關聯帳務記錄（依 table='estate_schedule'、colName='estate_schedule_id'、colSn=scheduleId 批次刪除）
   - 若帳務刪除失敗：回傳 409 CANNOT_DELETE_HAS_ACCOUNTING，日誌保留，流程終止
4. 帳務刪除成功後，刪除日誌本體（schedules 資料表）
5. 附件清理：由檔案模組連帶刪除所有 resource_type='schedule'、resource_id=scheduleId 的附件
6. 回應清理：級聯刪除所有 scheduleId 對應的 replies（含各 reply 的附件）
7. 回傳 204 No Content

### Side Effects
- Email 通知：無
- 其他副作用：級聯刪除所有關聯 replies；附件由檔案模組連帶刪除

### PHP 參考
- `estate/function_log.php:delete_estate_schedule`

---

## POST /v1/estates/{estateId}/schedules/{scheduleId}/replies

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於此 estateId（否則回傳 SCHEDULE_NOT_FOUND）
3. 驗證必填欄位（content）
4. 若 authorUserId 有值，驗證該 userId 存在；不帶時取 JWT 當前使用者
5. repliedAt 由系統寫入當下時間（client 不可傳入）
6. 寫入 replies 資料表
7. 回傳 201 + Location header + 完整 Reply 物件
8. 非同步發送 Email 通知給物業全體成員（fire-and-forget）

### Side Effects
- Email 通知：觸發條件為新增回應成功；收件對象為物業全體成員；Email 標題格式「「{estate.shortTitle}」回應通知」；內容含原始日誌內容與回應內容
- 其他副作用：無

### PHP 參考
- `estate/function_log.php:insert_estate_reply`
- `estate/function_log.php:send_to_mems`

---

## PUT /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於此 estateId（否則回傳 SCHEDULE_NOT_FOUND）
3. 驗證 replyId 存在且屬於此 scheduleId（若不存在回傳 SCHEDULE_NOT_FOUND）
4. 驗證必填欄位（content）
5. repliedAt 由系統更新為當下時間（與舊系統 update_estate_reply 一致，client 不可傳入）
6. 更新 replies 資料表（authorUserId 不可修改）
7. 回傳 200 + 完整更新後的 Reply 物件

### Side Effects
- Email 通知：無（更新回應不觸發通知，與舊系統一致）
- 其他副作用：無

### PHP 參考
- `estate/function_log.php:update_estate_reply`

---

## DELETE /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}

### 業務邏輯步驟
1. 驗證請求者已認證且在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於此 estateId（否則回傳 SCHEDULE_NOT_FOUND）
3. 驗證 replyId 存在且屬於此 scheduleId（若不存在回傳 SCHEDULE_NOT_FOUND）
4. 刪除 replies 資料表對應記錄
5. 附件清理：由檔案模組連帶刪除所有 resource_type='reply'、resource_id=replyId 的附件
6. 回傳 204 No Content

### Side Effects
- Email 通知：無
- 其他副作用：附件由檔案模組連帶刪除

### PHP 參考
- `estate/function_log.php:delete_estate_reply`

---

## 模組：帳務管理（Accounting）

---

## POST /v1/estates/{estateId}/accountings

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限（memberLevel=admin）或系統管理員
2. 驗證 estateId 存在且在 JWT 授權範圍內
3. 驗證必填欄位（accountingDate、income、expenditure）
4. 驗證 income >= 0 且 expenditure >= 0
5. 驗證 income 與 expenditure 不可同時為非零值（一筆帳務只能是收入或支出）
6. 若提供 titleId，驗證該 titleId 存在於系統科目表且類別為物業適用（46xx/66xx）
7. 若提供 linkedResourceType + linkedResourceId，驗證對應資源存在且屬於此 estateId：
   - linkedResourceType='rent'：查詢 rents 表確認 rentId 存在且 estateId 相符
   - linkedResourceType='schedule'：查詢 schedules 表確認 scheduleId 存在且 estateId 相符
8. 若 linkedResourceType 或 linkedResourceId 只提供其一，回傳 `VALIDATION_ERROR`
9. 寫入 accountings 資料表，createdBy 取 JWT 當前 userId
10. 回傳 201 + Location header + 完整帳務記錄

### Side Effects
- Email 通知：無
- 其他副作用：cashAccountId（零用金帳戶）欄位預留，目前即使 paymentMethod='現金' 也不自動觸發零用金入帳（income 模組排除，待後續補入）

### PHP 參考
- `accounting/api.php:insert_accounting`（L300-413）

---

## PUT /v1/estates/{estateId}/accountings/{accountingId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 accountingId 存在且屬於此 estateId；若不存在回傳 404 `ACCOUNTING_NOT_FOUND`
3. 驗證必填欄位（accountingDate、income、expenditure）
4. 驗證 income >= 0 且 expenditure >= 0
5. 驗證 income 與 expenditure 不可同時為非零值
6. 若提供 titleId，驗證該 titleId 存在且為物業適用科目
7. 若提供 linkedResourceType + linkedResourceId，驗證對應資源存在且屬於此 estateId
8. 若 linkedResourceType 或 linkedResourceId 只提供其一，回傳 `VALIDATION_ERROR`
9. 更新 accountings 資料表（createdBy 不可修改，ignoring request body 中的此欄位）
10. 回傳 200 + 完整更新後的帳務記錄

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `accounting/api.php:update_accounting`

---

## DELETE /v1/estates/{estateId}/accountings/{accountingId}

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 accountingId 存在且屬於此 estateId；若不存在回傳 404 `ACCOUNTING_NOT_FOUND`
3. 刪除 accountings 資料表對應記錄
4. 回傳 204 No Content

### Side Effects
- Email 通知：無
- 其他副作用：無（帳務記錄無子資源，直接刪除）。注意：若此帳務記錄為日誌或退租流程自動建立，刪除前應由呼叫端業務邏輯確認，避免資料不一致

### PHP 參考
- `accounting/api.php:delete_accounting`（支援依 accounting_id 或 table+col_name+col_sn 批次刪除；新系統 API 層只提供單筆，批次刪除由服務層在業務流程中呼叫）

---

## GET /v1/estates/{estateId}/accountings/overview

### 業務邏輯步驟（複雜查詢，需列出）
1. 驗證請求者具備此物業的管理員權限或系統管理員
2. 驗證 estateId 存在且在 JWT 授權範圍內
3. 若提供 periodFrom，驗證日期格式合法（YYYY-MM-DD）；不提供時預設當月 1 日
4. 若提供 periodTo，驗證日期格式合法（YYYY-MM-DD）；不提供時預設今日
5. 驗證 periodFrom <= periodTo；若不合法回傳 `VALIDATION_ERROR`
6. 計算上月結餘（previousBalance）：
   - 查詢 accountings 表，條件：estateId 相符 + accountingDate < periodFrom
   - previousBalance = SUM(income) - SUM(expenditure)
7. 計算本期收入（periodIncome）：查詢 accountingDate 在 [periodFrom, periodTo] 內的 SUM(income)
8. 計算本期支出（periodExpenditure）：查詢 accountingDate 在 [periodFrom, periodTo] 內的 SUM(expenditure)
9. 計算本期結餘（periodBalance）= periodIncome - periodExpenditure
10. 計算累計結餘（totalBalance）= previousBalance + periodBalance
11. 若未指定 titleId，計算各科目本期加總明細（titleBreakdown）：
    - 依 titleId 分組，計算每個科目的 SUM(income)、SUM(expenditure)
    - 包含 titleId = null 的未分類帳務（以 null 科目歸類）
12. 若指定 titleId，回傳該科目本期加總（仍含 previousBalance 等匯總欄位，titleBreakdown 只含此科目一筆）
13. 回傳 200 + AccountingOverview

### Side Effects
- Email 通知：無
- 其他副作用：無（純查詢）

### PHP 參考
- `estate/accounting.php:estate_accounting_list`（L43-48，accounting_main_col='estate_id' 查詢邏輯）
- `accounting/api.php:accounting_date_sum`（計算截至某日結餘）
- `accounting/api.php:accounting_tid_sum`（計算特定科目加總）

---

## 模組：會員管理（Users）

---

## POST /v1/auth/login

### 業務邏輯步驟
1. 驗證必填欄位（username、password）
2. 查詢 users 資料表，依 username 查找使用者；若不存在回傳 401 `INVALID_CREDENTIALS`
3. 驗證使用者帳號為啟用狀態（isEnabled=true）；若停用回傳 401 `INVALID_CREDENTIALS`（不揭示帳號停用資訊）
4. 以 bcrypt 驗證 password 是否與資料庫中的 hash 相符；若不符回傳 401 `INVALID_CREDENTIALS`
5. 查詢使用者被授權的物業 ID 清單（透過 estate_member_links WHERE user_id = ?，用於 JWT payload estateIds）
6. 產生 JWT，payload 包含：sub（userId）、username、role（系統層角色 admin/user）、estateIds（授權的物業 ID 清單）、exp（到期時間，18h 後）、iat（簽發時間）
7. 更新 users 資料表的 lastLoginAt 為當下時間
8. 回傳 200 + `access_token`（JWT）+ `expiresAt`（過期時間）+ `user`（使用者詳情）

### Side Effects
- Email 通知：無
- 其他副作用：更新使用者 lastLoginAt 時間戳記

### PHP 參考
- `tad_users/index.php`（L3，重導向至 XOOPS user.php；新系統不沿用此設計）
- `tad_users/function.php:add_user`（L65，舊系統密碼 MD5 邏輯；新系統改為 bcrypt）

---

## POST /v1/auth/logout

### 業務邏輯步驟
1. 驗證 JWT 有效（middleware 處理）
2. 若系統實作了 token blacklist：將此 JWT 的 jti（JWT ID）加入黑名單，直到 exp 到期
3. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：若有 token blacklist，jti 加入 blacklist 直到 exp

### PHP 參考
- 無對應 PHP 實作（舊系統使用 XOOPS session，不需顯式登出 API）

---

## POST /v1/users

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證必填欄位（username、name、email、password）
3. 驗證 username 長度在 1–25 字元之間，且只含合法字元（字母、數字、底線）
4. 驗證 email 格式合法
5. 驗證 password 長度 >= 6 字元
6. 查詢 users 資料表，確認 username 尚未存在；若已存在回傳 409 `USERNAME_ALREADY_EXISTS`
7. 以 bcrypt 對 password 進行 hash
8. 寫入 users 資料表（isEnabled=true）
9. 若提供 groupIds，驗證每個 groupId 存在；若有不存在的 groupId 回傳 400 `VALIDATION_ERROR`
10. 批次寫入 user_group_links（userId + 每個 groupId）
11. 回傳 201 + Location header + 完整使用者詳情（不含密碼）

### Side Effects
- Email 通知：無（feature-list 未標注新增使用者時發送通知；若業主帳號由 POST /v1/estates 自動建立時才有通知，詳見 estate 模組）
- 其他副作用：若提供 groupIds，自動建立 user_group_links 關聯記錄

### PHP 參考
- `tad_users/admin/add.php`（新增使用者頁面入口）
- `tad_users/function.php:add_user`（L45-85，建立使用者邏輯；新系統不沿用 MD5 密碼）

---

## PUT /v1/users/{userId}

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證 userId 存在；若不存在回傳 404 `USER_NOT_FOUND`
3. 驗證必填欄位（name、email）
4. 驗證 email 格式合法
5. 若提供 password：驗證長度 >= 6 字元；以 bcrypt 重新 hash
6. 若提供 groupIds：驗證每個 groupId 存在；若有不存在的 groupId 回傳 400 `VALIDATION_ERROR`
7. 更新 users 資料表（name、email、occupation、bio、isEnabled；若提供 password 則同時更新密碼 hash）
8. 若提供 groupIds：取得現有 user_group_links，計算差異，新增/刪除對應記錄（完整取代）
9. 回傳 200 + 完整更新後的使用者詳情（不含密碼）

### Side Effects
- Email 通知：無
- 其他副作用：若 groupIds 有異動，user_group_links 記錄被新增或刪除

### PHP 參考
- `tad_users/admin/main.php:update_user`（L85-120；新系統不沿用 MD5 密碼，L105 的 md5 呼叫改為 bcrypt）

---

## POST /v1/users/batch

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證 users 陣列不為空
3. 對每個使用者項目驗證（與 POST /v1/users 步驟 3–5 相同）
4. 批次查詢所有提交的 username 是否已存在（含批次內自身重複）；若任何一筆衝突回傳 409 `USERNAME_ALREADY_EXISTS`，整批取消
5. 以 bcrypt 對每個 password 進行 hash
6. 批次寫入 users 資料表（all-or-nothing，使用 DB transaction）
7. 批次建立 user_group_links（若各 user 有提供 groupIds）
8. 回傳 201 + 所有新建使用者的清單（不含密碼）

### Side Effects
- Email 通知：無
- 其他副作用：若提供 groupIds，批次建立 user_group_links 關聯記錄

### PHP 參考
- `tad_users/admin/add.php`（頁面支援多筆輸入，batch 語意）
- `tad_users/function.php:add_user`（單筆建立邏輯；批次為多次呼叫）

---

## POST /v1/users/import

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證上傳的檔案存在且 Content-Type 為 text/csv 或 application/vnd.ms-excel
3. 驗證檔案大小 <= 5MB
4. 解析 CSV（UTF-8 編碼），讀取標題列驗證必填欄位存在（username、name、email、password）
5. 對每列資料：
   a. 驗證必填欄位不為空
   b. 驗證 email 格式合法
   c. 驗證 password 長度 >= 6
   d. 查詢 username 是否已存在（含 CSV 內自身重複）；若重複標記為失敗，跳過此列
   e. 驗證通過者：以 bcrypt hash password，寫入 users 資料表（partial success：逐列處理，失敗不影響其他列）
6. 回傳 200 + UserImportResult（totalRows、successCount、failureCount、failures 明細）

### Side Effects
- Email 通知：無
- 其他副作用：成功列自動建立 users 記錄；失敗列不寫入

### PHP 參考
- `tad_users/admin/import.php`（CSV 匯入頁面）
- `tad_users/csv.php`（CSV 處理邏輯）

---

## POST /v1/users/actions/batch-add-group

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證必填欄位（userIds、groupId）
3. 驗證 groupId 存在；若不存在回傳 404 `GROUP_NOT_FOUND`
4. 驗證 userIds 陣列不為空
5. 查詢 user_group_links，過濾出尚未在此群組的 userId 清單
6. 批次寫入 user_group_links（userId + groupId），已在群組者略過
7. 回傳 200 + affectedCount（實際新增的關聯數量）

### Side Effects
- Email 通知：無
- 其他副作用：user_group_links 建立新的關聯記錄

### PHP 參考
- `tad_users/admin/main.php:add_group`（批次加入群組邏輯）

---

## POST /v1/users/actions/batch-remove-group

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證必填欄位（userIds、groupId）
3. 驗證 groupId 存在；若不存在回傳 404 `GROUP_NOT_FOUND`
4. 驗證 userIds 陣列不為空
5. 批次刪除 user_group_links 中符合（userId IN userIds AND groupId = groupId）的記錄；不在群組者自動略過
6. 回傳 200 + affectedCount（實際刪除的關聯數量）

### Side Effects
- Email 通知：無
- 其他副作用：user_group_links 刪除關聯記錄；不影響 users 主檔

### PHP 參考
- `tad_users/admin/main.php:del_group`（批次移除群組邏輯）

---

## PATCH /v1/users/actions/batch-update-field

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證必填欄位（userIds、field、value）
3. 驗證 field 為支援的欄位（isEnabled、occupation、bio）；密碼欄位不支援批次更新
4. 驗證 value 型別與 field 相符：
   - isEnabled：boolean
   - occupation：string，最長 100 字元
   - bio：string
5. 驗證 userIds 陣列不為空
6. 批次更新 users 資料表中指定 userId 的指定欄位值
7. 回傳 200 + updatedCount（實際更新的使用者數量）

### Side Effects
- Email 通知：無
- 其他副作用：若 field=isEnabled 且設為 false，被停用的使用者下次登入將被拒絕（JWT 仍可能暫時有效，直到過期）

### PHP 參考
- `tad_users/admin/main.php:update_users_value`（批次更新單一欄位邏輯）

---

## 模組：群組/權限管理（Groups）

---

## POST /v1/groups

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證必填欄位（name）
3. 驗證 name 最長 50 字元
4. 查詢是否已存在相同 name 的群組；若重複回傳 409 `GROUP_NAME_ALREADY_EXISTS`
5. 建立群組記錄（groupType 固定為 Global）
6. 回傳 201 + Location header + 完整群組詳情（成員清單為空）

### Side Effects
- Email 通知：無
- 其他副作用：無。注意：新增物業時系統會自動呼叫此邏輯（POST /v1/estates 會自動建立「業主」群組），群組建立也可由管理員手動觸發

### PHP 參考
- `estate/class/user_group.php:mk_group`（新增物業時自動建立業主群組的邏輯）

---

## PUT /v1/groups/{groupId}

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證 groupId 存在；若不存在回傳 404 `GROUP_NOT_FOUND`
3. 驗證必填欄位（name）
4. 驗證 name 最長 50 字元
5. 若 name 異動，查詢是否已有其他群組使用相同 name；若重複回傳 409 `GROUP_NAME_ALREADY_EXISTS`
6. 更新群組記錄（name、description；groupType 不可更改）
7. 回傳 200 + 完整更新後的群組詳情（含成員清單，分頁預設第 1 頁）

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- 舊系統無對應的群組更新功能；群組名稱在建立後未見修改流程（依 schema 推斷）

---

## DELETE /v1/groups/{groupId}

### 業務邏輯步驟
1. 驗證請求者具備系統管理員角色
2. 驗證 groupId 存在；若不存在回傳 404 `GROUP_NOT_FOUND`
3. 查詢 user_group_links 是否有此群組的成員關聯；若有則回傳 409 `GROUP_HAS_MEMBERS`
4. 刪除群組記錄
5. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：無 cascade 刪除（成員關聯需先清空才能刪除群組，確保不意外移除使用者的群組關聯）

### PHP 參考
- 舊系統無對應的群組刪除功能（依 schema 推斷）

---

## 模組：檔案管理（Attachments）

> 附件操作以「父資源確認」為第一步，確保呼叫者有權存取父資源後，才允許對附件進行操作。
> 以下以房間附件為代表說明完整業務邏輯；租期附件、日誌附件、回應附件、設施附件的邏輯結構相同，僅父資源類型不同。

---

## POST /v1/estates/{estateId}/rooms/{roomId}/attachments

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內（middleware 處理）
2. 驗證 estateId 存在；若不存在回傳 404 `ESTATE_NOT_FOUND`
3. 驗證 roomId 存在且屬於 estateId；若不存在回傳 404 `ROOM_NOT_FOUND`
4. 驗證上傳檔案存在（multipart file 欄位不可為空）；若無檔案回傳 400 `VALIDATION_ERROR`
5. 驗證檔案大小 <= 50MB；若超出回傳 400 `VALIDATION_ERROR`（details.field = file）
6. 讀取檔案 MIME type（由伺服器端偵測，不信任 client 傳入的 Content-Type）
7. 產生 Cloud Storage object path：`attachments/{resourceType}/{resourceId}/{uuid}.{ext}`（例：`attachments/rooms/42/a1b2c3d4.jpg`）
8. 上傳檔案至 Cloud Storage
9. 取得現有該房間最大 sortOrder，新附件 sortOrder = max + 1（若無附件則從 1 開始）
10. 寫入 attachments 資料表（fileName、mimeType、fileSize、storageObjectPath、description、tag、sortOrder、uploadedBy = JWT userId、uploadedAt = 當下時間）
11. 回傳 201 + Location header（`/v1/estates/{estateId}/rooms/{roomId}/attachments/{attachmentId}`）+ 完整 AttachmentItem

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案寫入 Cloud Storage；資料庫寫入附件 metadata

### PHP 參考
- `estate/room.php`（TadUpFiles 呼叫 up_estate_room_id；新系統不沿用本地檔案儲存）

---

## DELETE /v1/estates/{estateId}/rooms/{roomId}/attachments/{attachmentId}

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 roomId 存在且屬於 estateId；若不存在回傳 404 `ROOM_NOT_FOUND`
3. 驗證 attachmentId 存在且屬於此 roomId；若不存在回傳 404 `ATTACHMENT_NOT_FOUND`
4. 從資料庫取得 storageObjectPath
5. 刪除 Cloud Storage 物件（若 Cloud Storage 回傳物件不存在，視為已刪除，繼續流程）
6. 刪除 attachments 資料表記錄
7. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案從 Cloud Storage 永久刪除；資料庫記錄同步刪除

### PHP 參考
- `estate/room.php:delete_estate_room`（舊系統刪除房間時連帶清除附件）

---

## GET /v1/estates/{estateId}/rooms/{roomId}/attachments/{attachmentId}/download

### 業務邏輯步驟（複雜查詢，列出）
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 roomId 存在且屬於 estateId
3. 驗證 attachmentId 存在且屬於此 roomId；若不存在回傳 404 `ATTACHMENT_NOT_FOUND`
4. 從資料庫取得 storageObjectPath
5. 向 Cloud Storage 產生簽署 URL（Signed URL，有效期 15 分鐘，HTTP method = GET）
6. 將資料庫中此附件的 downloadCount + 1
7. 回傳 302 redirect，Location header 設為簽署 URL

### Side Effects
- Email 通知：無
- 其他副作用：downloadCount 累加 1

### PHP 參考
- `xx_estate_files_center.counter`（舊系統追蹤下載次數；新系統同樣維護此計數）
- 舊系統以 `hash_filename` 防止直接存取；新系統改用 Cloud Storage 簽署 URL

---

## PATCH /v1/estates/{estateId}/rooms/{roomId}/attachments/{attachmentId}

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 roomId 存在且屬於 estateId
3. 驗證 attachmentId 存在且屬於此 roomId；若不存在回傳 404 `ATTACHMENT_NOT_FOUND`
4. 更新 attachments 資料表的 description 欄位（null 時清空說明）
5. 回傳 200 + 完整更新後的 AttachmentItem

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `xx_estate_files_center.description`（舊系統 description 欄位）

---

## PUT /v1/estates/{estateId}/rooms/{roomId}/attachments/sort

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 roomId 存在且屬於 estateId
3. 驗證 attachmentIds 陣列不為空
4. 驗證 attachmentIds 中的每個 ID 均屬於此 roomId（比對資料庫）；若有不屬於的 ID 回傳 400 `VALIDATION_ERROR`
5. 驗證 attachmentIds 數量與此 roomId 現有附件數量相符（需包含所有附件）；若不符回傳 400 `VALIDATION_ERROR`
6. 依 attachmentIds 陣列順序批次更新 sortOrder（index 0 = sortOrder 1，以此類推）
7. 回傳 200 + 排序後的完整附件清單

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- `xx_estate_files_center.sort`（舊系統排序欄位）

---

## POST /v1/estates/{estateId}/rents/{rentId}/attachments

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 rentId 存在且屬於 estateId；若不存在回傳 404 `RENT_NOT_FOUND`
3. 驗證上傳檔案存在，檔案大小 <= 50MB
4. 讀取檔案 MIME type（伺服器端偵測）
5. 產生 Cloud Storage object path：`attachments/rents/{rentId}/{uuid}.{ext}`
6. 上傳至 Cloud Storage
7. 取現有最大 sortOrder + 1 作為新附件排序
8. 寫入 attachments 資料表
9. 回傳 201 + Location header + 完整 AttachmentItem

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案寫入 Cloud Storage；資料庫寫入附件 metadata

### PHP 參考
- `estate/rent.php`（TadUpFiles 呼叫 up_estate_rent_form）

---

## DELETE /v1/estates/{estateId}/rents/{rentId}/attachments/{attachmentId}

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 rentId 存在且屬於 estateId；若不存在回傳 404 `RENT_NOT_FOUND`
3. 驗證 attachmentId 存在且屬於此 rentId；若不存在回傳 404 `ATTACHMENT_NOT_FOUND`
4. 從資料庫取得 storageObjectPath，刪除 Cloud Storage 物件
5. 刪除 attachments 資料表記錄
6. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案從 Cloud Storage 永久刪除

### PHP 參考
- `estate/rent.php`（TadUpFiles 相關刪除邏輯）

---

## POST /v1/estates/{estateId}/schedules/{scheduleId}/attachments

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於 estateId；若不存在回傳 404 `SCHEDULE_NOT_FOUND`
3. 驗證上傳檔案存在，檔案大小 <= 50MB
4. 讀取檔案 MIME type（伺服器端偵測）
5. 產生 Cloud Storage object path：`attachments/schedules/{scheduleId}/{uuid}.{ext}`
6. 上傳至 Cloud Storage
7. 取現有最大 sortOrder + 1 作為新附件排序
8. 寫入 attachments 資料表
9. 回傳 201 + Location header + 完整 AttachmentItem

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案寫入 Cloud Storage；資料庫寫入附件 metadata

### PHP 參考
- `estate/function_log.php`（TadUpFiles 呼叫 up_estate_schedule_id）

---

## DELETE /v1/estates/{estateId}/schedules/{scheduleId}/attachments/{attachmentId}

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於 estateId；若不存在回傳 404 `SCHEDULE_NOT_FOUND`
3. 驗證 attachmentId 存在且屬於此 scheduleId；若不存在回傳 404 `ATTACHMENT_NOT_FOUND`
4. 從資料庫取得 storageObjectPath，刪除 Cloud Storage 物件
5. 刪除 attachments 資料表記錄
6. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案從 Cloud Storage 永久刪除

### PHP 參考
- `estate/function_log.php:delete_estate_schedule`（刪除日誌時連帶刪除附件）

---

## POST /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於 estateId；若不存在回傳 404 `SCHEDULE_NOT_FOUND`
3. 驗證 replyId 存在且屬於此 scheduleId；若不存在回傳 404 `SCHEDULE_NOT_FOUND`（reply 沿用相同 error code）
4. 驗證上傳檔案存在，檔案大小 <= 50MB
5. 讀取檔案 MIME type（伺服器端偵測）
6. 產生 Cloud Storage object path：`attachments/replies/{replyId}/{uuid}.{ext}`
7. 上傳至 Cloud Storage
8. 取現有最大 sortOrder + 1 作為新附件排序
9. 寫入 attachments 資料表
10. 回傳 201 + Location header + 完整 AttachmentItem

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案寫入 Cloud Storage；資料庫寫入附件 metadata

### PHP 參考
- `estate/function_log.php`（TadUpFiles 呼叫 up_estate_reply_id）

---

## DELETE /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments/{attachmentId}

### 業務邏輯步驟
1. 驗證請求者已認證且 estateId 在 JWT 授權範圍內
2. 驗證 scheduleId 存在且屬於 estateId；若不存在回傳 404 `SCHEDULE_NOT_FOUND`
3. 驗證 replyId 存在且屬於此 scheduleId
4. 驗證 attachmentId 存在且屬於此 replyId；若不存在回傳 404 `ATTACHMENT_NOT_FOUND`
5. 從資料庫取得 storageObjectPath，刪除 Cloud Storage 物件
6. 刪除 attachments 資料表記錄
7. 回傳 204

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案從 Cloud Storage 永久刪除

### PHP 參考
- `estate/function_log.php:delete_estate_reply`（刪除回應時連帶刪除附件）

---

## POST /v1/estates/{estateId}/facilities/{facilityName}/attachments

### 業務邏輯步驟
1. 驗證請求者具備此物業的管理員權限（memberLevel=admin）或系統管理員
2. 驗證 estateId 存在；若不存在回傳 404 `ESTATE_NOT_FOUND`
3. 驗證 facilityName（URL decoded 後）存在於 estate.facilities 清單；若不存在回傳 400 `VALIDATION_ERROR`（details.field = facilityName）
4. 驗證上傳檔案存在，檔案大小 <= 50MB
5. 讀取檔案 MIME type（伺服器端偵測）；建議僅允許圖片類型（image/*），非圖片時回傳 400 `VALIDATION_ERROR`
6. 產生 Cloud Storage object path：`attachments/facilities/{estateId}/{facilityNameSlug}/{uuid}.{ext}`
7. 上傳至 Cloud Storage
8. 取現有最大 sortOrder + 1 作為新附件排序
9. 寫入 attachments 資料表
10. 回傳 201 + Location header + 完整 AttachmentItem

### Side Effects
- Email 通知：無
- 其他副作用：實體檔案寫入 Cloud Storage；資料庫寫入附件 metadata

### PHP 參考
- `estate/index.php:estate_show_one`（L361-388，公共設施圖片上傳邏輯，TadUpFiles 呼叫 facility_file）

---

## 模組：Email 通知（Notification）

> 本模組無獨立 API endpoint。所有 Email 通知均為各業務操作的 side effect，實作層面由後端服務在業務邏輯完成後以非同步方式（background job 或 Cloud Tasks）觸發，不阻塞 API 回應。

---

## Email 通知觸發規則彙整

### 設計原則

- **Fire-and-forget**：Email 發送為非同步操作，發送失敗不影響主業務操作的 HTTP 回應（不回傳 5xx）
- **收件對象「物業全體成員」定義**：`estate_member_links` 表中 `estateId` 對應的所有成員（不限 memberLevel）
- **Email 標題前綴**：使用物業簡稱（`estate.shortTitle`）作為標題前綴，格式為「{estate.shortTitle}」xxx，與舊系統 `send_to_mems` 一致
- **發送時機**：業務資料寫入資料庫成功後，再派發非同步通知任務

### 觸發點清單

#### 1. 業主帳號開通通知

| 項目 | 內容 |
|------|------|
| 觸發操作 | POST /v1/estates（新增物業，且業主 email 尚無帳號，自動建立業主帳號） |
| 收件對象 | 業主本人（ownerEmail） |
| 觸發條件 | 新增物業時自動建立業主帳號（非已存在帳號） |
| Email 內容 | 含登入帳號（username）及初始密碼，提示業主登入後修改密碼 |
| 發送失敗處理 | 不影響物業建立成功；但應在後台記錄發送失敗，供管理員手動補發 |

**PHP 參考**：`estate/function_log.php:send_to_mems`、`estate/index.php:insert_estate`（L121-214）

---

#### 2. 新增日誌通知

| 項目 | 內容 |
|------|------|
| 觸發操作 | POST /v1/estates/{estateId}/schedules（新增日誌成功後） |
| 收件對象 | 物業全體成員（estate_member_links 中此 estateId 的所有成員） |
| 觸發條件 | 日誌資料寫入成功（HTTP 201 回傳後異步觸發） |
| Email 標題 | 「{estate.shortTitle}」新進度 |
| Email 內容 | 辦理日期（scheduledAt）、辦理狀況（status）、填報人（reporterUser.name）、協辦人員（assistUser.name 或「全體人員」或「無」）、日誌內容（content，去除 HTML 標籤後的純文字） |
| 發送失敗處理 | 不影響日誌建立成功 |

**PHP 參考**：`estate/function_log.php:insert_estate_schedule`、`estate/function_log.php:send_to_mems`

---

#### 3. 更新日誌通知

| 項目 | 內容 |
|------|------|
| 觸發操作 | PUT /v1/estates/{estateId}/schedules/{scheduleId}（更新日誌成功後） |
| 收件對象 | 物業全體成員 |
| 觸發條件 | 日誌資料更新成功（HTTP 200 回傳後異步觸發） |
| Email 標題 | 「{estate.shortTitle}」新進度 |
| Email 內容 | 同新增日誌通知（含更新後的最新內容） |
| 發送失敗處理 | 不影響日誌更新成功 |

**PHP 參考**：`estate/function_log.php:update_estate_schedule`、`estate/function_log.php:send_to_mems`

---

#### 4. 新增日誌回應通知

| 項目 | 內容 |
|------|------|
| 觸發操作 | POST /v1/estates/{estateId}/schedules/{scheduleId}/replies（新增回應成功後） |
| 收件對象 | 物業全體成員 |
| 觸發條件 | 回應資料寫入成功（HTTP 201 回傳後異步觸發） |
| Email 標題 | 「{estate.shortTitle}」回應通知 |
| Email 內容 | 原始日誌的辦理日期與內容摘要（content 去除 HTML 前 36 字元）、回應者（authorUser.name）、回應時間（repliedAt）、回應內容（content，去除 HTML 標籤後的純文字） |
| 發送失敗處理 | 不影響回應建立成功 |

**PHP 參考**：`estate/function_log.php:insert_estate_reply`、`estate/function_log.php:send_to_mems`

---

### 明確不觸發通知的操作

以下操作依據 feature-list.md 功能項目描述或 PHP 程式碼分析，確認不發送 Email 通知：

| 操作 | 不觸發原因 |
|------|------------|
| POST /v1/estates/{estateId}/rents（新增租約） | feature-list 功能清單提及通知但 PHP 實作（estate/rent.php:insert_estate_rent）無 send_to_mems 呼叫；確認不觸發 |
| POST /v1/estates/{estateId}/accountings（新增帳務） | feature-list 功能清單提及通知但 PHP 實作（accounting/api.php:insert_accounting）無通知邏輯；確認不觸發 |
| PUT、DELETE 操作（租約、帳務、附件等） | feature-list 及 PHP 均無對應通知邏輯 |
| PUT /v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}（更新回應） | PHP 實作（update_estate_reply）無通知邏輯；更新回應不觸發通知 |

### PHP 參考
- `estate/function_log.php:send_to_mems`（統一發送函式，接收物業 estateId 查詢全體成員後逐一發送）

---

## 附錄：Transaction 保護範圍 與 併發說明

---

### 系統背景

本系統為小型工作室使用的物業管理系統，**同時在線使用者數極少（通常 1–3 人）**，資料量與請求頻率均不高。因此：

- **不需要實作樂觀鎖（Optimistic Locking）或版本號（ETag）機制**
- **不需要 Redis 分散式鎖**
- **不需要 SELECT FOR UPDATE**
- Race condition 發生機率極低，即使發生影響範圍也小，以標準 DB transaction 保護資料一致性即已足夠

---

### 必須使用 DB Transaction 的操作

以下操作涉及多張資料表的寫入，需包在同一個 DB transaction 中，任一步驟失敗則整體 rollback：

| 操作 | 涉及的多表寫入 | 失敗處理 |
|------|-------------|---------|
| `POST /v1/estates` | users（建立業主帳號）+ user_group_links（加入業主群組）+ estates | 任一失敗整體 rollback，業主帳號不殘留 |
| `POST /v1/estates/{estateId}/rents` | rents + rent_tenant_links（若有 tenants） | 任一失敗整體 rollback，rent 不殘留 |
| `DELETE /v1/estates/{estateId}/rents/{rentId}` | 刪 rent_tenant_links + 刪 rents | 確保關聯記錄與主檔同步刪除 |
| `POST /v1/estates/{estateId}/rents/{rentId}/actions/terminate` | 寫入多筆 accountings（電費、押金、額外費用）+ 更新 rents.status + 寫入 rents.terminationInfo | 任一 accounting 寫入失敗則整體 rollback，租約狀態不變 |
| `POST /v1/estates/{estateId}/schedules` | 寫入 schedules + 自動建立關聯 accountings（tag='日誌'） | 帳務建立失敗則 schedule 也不建立（原子性） |
| `PUT /v1/estates/{estateId}/schedules/{scheduleId}` | 更新 schedules + 更新/補建 accountings | 帳務更新失敗則 schedule 更新也 rollback |
| `DELETE /v1/estates/{estateId}/schedules/{scheduleId}` | 刪 accountings + 刪 replies + 刪 schedules（DB 部分） | Cloud Storage 附件清理在 DB transaction 之外（見下節） |
| `POST /v1/users/batch` | 批次寫入 users + user_group_links | all-or-nothing，任一使用者寫入失敗整批 rollback |
| `PUT /v1/users/{userId}` | 更新 users + 差異計算後更新 user_group_links | group 關聯更新失敗則使用者更新也 rollback |
| `PUT /v1/estates/{estateId}/members` | 差異計算後批次新增/刪除 estate_member_links | 部分失敗則整批 rollback，成員清單維持原狀 |

---

### 跨外部系統操作（Cloud Storage + DB）

涉及 Cloud Storage 的附件操作**無法包在同一個 DB transaction 中**，依以下原則處理：

#### 上傳附件（POST .../attachments）

**順序：先上傳 Cloud Storage，成功後再寫 DB**

- Cloud Storage 上傳成功 → 寫 DB metadata → 成功回傳 201
- Cloud Storage 上傳失敗 → 直接回傳 500，DB 無殘留
- Cloud Storage 成功但 DB 寫入失敗 → Cloud Storage 有孤兒檔案，但 client 看到的是失敗（後台可定期清理無 DB 記錄的 Cloud Storage 物件）

#### 刪除附件（DELETE .../attachments/{attachmentId}）

**順序：先嘗試刪 Cloud Storage，再刪 DB**

- Cloud Storage 刪除成功（或物件已不存在）→ 刪 DB → 成功回傳 204
- Cloud Storage 刪除失敗 → 回傳 500，DB 記錄保留

#### 刪除父資源時的附件清理（如 DELETE room、DELETE schedule）

- DB transaction 內處理資料表關聯刪除
- DB commit 成功後，再異步觸發 Cloud Storage 清理
- 若 Cloud Storage 清理失敗，DB 資料已刪除（Cloud Storage 有孤兒檔案），可由後台排程清理

---

### 不需特別保護的操作

以下操作僅涉及單一資料表的單筆寫入，不需 transaction：

- 所有單純的 PUT/PATCH 更新（單表）
- GET（純查詢）
- `POST /v1/tenants`、`PUT /v1/tenants/{tenantId}`
- `PATCH /v1/estates/{estateId}/electric-readings`（雖為批次，但 upsert 語意明確，失敗重試安全）
- `POST /v1/groups`、`PUT /v1/groups/{groupId}`
- `POST /v1/auth/login`（更新 lastLoginAt 失敗不影響登入回應）

---

## 模組：會員管理（Users）── 自服務端點補充

---

## PATCH /v1/users/me/password

### 業務邏輯步驟
1. 從 JWT payload 取得目前登入的 userId（任何已登入使用者均可呼叫，不需 admin 角色）
2. 驗證 `currentPassword` 與 `newPassword` 均已提供且不為空；`newPassword` 至少 6 個字元
3. 查詢 DB 取得使用者的 `password_hash`
4. 以 `bcrypt.CompareHashAndPassword` 驗證 `currentPassword` 是否與 `password_hash` 相符
   - 不相符：回傳 409 `CURRENT_PASSWORD_INCORRECT`
5. 以 `bcrypt.GenerateFromPassword` 將 `newPassword` 產生新的 bcrypt hash
6. 更新 `users.password_hash` 為新 hash
7. 回傳 204（無 body）

### Side Effects
- Email 通知：無
- 其他副作用：無

### PHP 參考
- 舊系統無對應端點（XOOPS 密碼修改入口為 user.php，新系統此端點為全新設計）

### 設計說明
- 此端點與 `PUT /v1/users/{userId}` 的差異：
  - `PUT /v1/users/{userId}` 為 admin 後台功能，可直接設定密碼（不需提供現有密碼）
  - `PATCH /v1/users/me/password` 為使用者自服務功能，必須提供現有密碼驗證身份，且只能修改自己的密碼
- 新增此端點的背景：遷移時所有使用者的 `password_hash` 將統一填入預設密碼（bcrypt hash of "ChangeMeNow123!"），遷移後通知使用者透過此端點自行修改密碼
