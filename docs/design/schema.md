# STDS 物業管理系統 - PostgreSQL Schema 設計

> 設計日期：2026-03-15
> 技術決策：PostgreSQL（Cloud SQL）、單一 DB、estate_id row-level 隔離、TIMESTAMPTZ、BIGSERIAL 主鍵

---

## 模組一：物業管理（Estate）

> 對應 API 資源：`/v1/estates`、`/v1/estates/{estateId}/rooms`、`/v1/estates/{estateId}/members`、`/v1/estates/{estateId}/facilities`

---

### estates

> 說明：物業（案件）主檔。每筆記錄代表一個獨立管理的物業社區/大樓。對應 API 資源：`/v1/estates`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| title | VARCHAR(255) | NOT NULL | — | 物業全名（案名）。對應 API: `title` |
| short_title | VARCHAR(255) | NOT NULL | — | 物業簡稱，用於 Email 標題等。對應 API: `shortTitle` |
| owner_user_id | BIGINT | NULL | — | FK → users(id)。業主系統使用者 ID。對應 API: `ownerUserId` |
| owner_name | VARCHAR(255) | NOT NULL | — | 業主姓名。對應 API: `ownerName` |
| owner_email | VARCHAR(255) | NULL | — | 業主 Email。可為空，業主 email 為選填聯絡資訊。對應 API: `ownerEmail` |
| address | VARCHAR(255) | NULL | — | 物業門牌地址。對應 API: `address` |
| phone | VARCHAR(255) | NULL | — | 物業聯絡電話。對應 API: `phone` |
| website | VARCHAR(255) | NULL | — | 物業官網網址。對應 API: `website` |
| facebook | VARCHAR(255) | NULL | — | 物業 Facebook 連結。對應 API: `facebook` |
| note | TEXT | NULL | — | 物業備註（HTML rich text）。對應 API: `note` |
| facilities | JSONB | NOT NULL | '[]' | 公共設施名稱清單。舊欄位：`estate_facility`（TEXT，JSON 字串陣列）→ 新設計：JSONB。結構：`["電梯", "停車場", "游泳池"]`。對應 API: `facilities` |
| electricity_rate | NUMERIC(6,2) | NOT NULL | 4.50 | 每度電費單價（元/度）。對應 API: `electricityRate` |
| electricity_billing_cycle | VARCHAR(20) | NOT NULL | 'bimonthly' | 電費收費週期。CHECK 約束值：`monthly`（單月）、`bimonthly`（雙月）。舊欄位：`electric_month` ENUM('單月','雙月')。對應 API: `electricityBillingCycle` |
| zones | JSONB | NOT NULL | '[]' | 區域/棟別清單。舊欄位：`estate_zone`（VARCHAR，分號分隔字串）→ 新設計：JSONB。結構：`["A棟", "B棟"]`。對應 API: `zones` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除） |

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_estates_owner_user (owner_user_id)`
- `INDEX idx_estates_deleted_at (deleted_at)` -- 查詢有效物業時常用

**外鍵：**
- `owner_user_id` → `users(id)` ON DELETE SET NULL

**CHECK 約束：**
- `CHECK (electricity_billing_cycle IN ('monthly', 'bimonthly'))`

**舊系統對應：**
- 對應舊表：`xx_estate`
- JSONB 轉換：舊欄位 `estate_facility`（TEXT，JSON 字串陣列）→ 新欄位 `facilities`（JSONB）
- JSONB 轉換：舊欄位 `estate_zone`（VARCHAR，分號分隔字串 "A棟;B棟"）→ 新欄位 `zones`（JSONB 陣列）
- 欄位廢棄：`electric_money` FLOAT → 新欄位 `electricity_rate` NUMERIC(6,2)（精度保障）
- 欄位廢棄：舊系統 `estate_uid` 借用 `xx_users.actkey` 儲存 estate_id 清單，新系統改由 `owner_user_id` FK 明確關聯，不再借用欄位

---

### rooms

> 說明：房間/單位主檔，隸屬於特定物業。對應 API 資源：`/v1/estates/{estateId}/rooms`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。所屬物業 |
| room_number | VARCHAR(255) | NOT NULL | — | 房號（如 A101）。對應 API: `roomNumber` |
| storey | VARCHAR(255) | NULL | — | 所在樓層。對應 API: `storey` |
| room_type | VARCHAR(255) | NULL | — | 房型（如 2房1廳）。對應 API: `roomType` |
| size_sqm | NUMERIC(7,2) | NULL | — | 坪數。舊欄位：`estate_room_size` DECIMAL(5,2)。對應 API: `sizeSquareMeter` |
| facilities | JSONB | NOT NULL | '{}' | 房間設備清單。舊欄位：`estate_room_facility`（TEXT，JSON object 字串）→ 新設計：JSONB object。結構：`{"床組": 1, "書桌": 2, "冷氣": 1, "電視": 0}`。key 為設備名稱，value 為整數數量，0 表示不含此設備。舊系統 value 為數字字串（如 "1"），遷移時轉為整數。對應 API: `facilities` |
| prices | JSONB | NOT NULL | '{}' | 各繳費週期的租金定價。舊欄位：`estate_room_price`（TEXT，JSON）→ 新設計：JSONB。結構：`{"yearly": 48000, "halfYearly": null, "quarterly": null, "monthly": 4500}`。各週期金額可為 null（未設定時為 null，舊系統以空字串表示）。對應 API: `prices` |
| note | TEXT | NULL | — | 備註（HTML rich text）。對應 API: `note` |
| sort_order | INTEGER | NOT NULL | 0 | 顯示排序（支援拖曳排序）。對應 API: `sortOrder` |
| zone | VARCHAR(255) | NULL | — | 所屬棟別/區域，對應 estates.zones 其中一個值。對應 API: `zone` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除） |

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_rooms_estate (estate_id)`
- `INDEX idx_rooms_estate_zone (estate_id, zone)` -- 依棟別過濾的查詢
- `INDEX idx_rooms_estate_sort (estate_id, sort_order)` -- 排序清單查詢
- `UNIQUE (estate_id, room_number)` WHERE deleted_at IS NULL -- 同一物業內房號唯一

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE RESTRICT

**舊系統對應：**
- 對應舊表：`xx_estate_room`
- JSONB 轉換：舊欄位 `estate_room_facility`（TEXT，JSON 字串陣列）→ 新欄位 `facilities`（JSONB）
- JSONB 轉換：舊欄位 `estate_room_price`（TEXT，JSON，key 為 year/half/season/month）→ 新欄位 `prices`（JSONB，key 改為 yearly/halfYearly/quarterly/monthly 對應 API 命名）

---

### estate_member_profiles

> 說明：成員個人設定檔（職稱、所屬單位、行事曆顏色），與使用者綁定但跨物業共用同一設定。對應 API 資源：`/v1/estates/{estateId}/members/{userId}`（PATCH 的設定部分）

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| user_id | BIGINT | NOT NULL | — | PK，FK → users(id)。成員使用者 ID |
| unit | VARCHAR(255) | NULL | — | 所屬單位名稱。對應 API: `unit` |
| title | VARCHAR(255) | NULL | — | 職稱（如「主承辦人」）。對應 API: `title` |
| calendar_text_color | VARCHAR(7) | NOT NULL | '#FFFFFF' | 行事曆文字顏色（hex，7 碼含 #）。對應 API: `calendarTextColor` |
| calendar_bg_color | VARCHAR(7) | NOT NULL | '#6EB3E5' | 行事曆背景顏色（hex，7 碼含 #）。對應 API: `calendarBgColor` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |

**索引：**
- `PRIMARY KEY (user_id)`

**外鍵：**
- `user_id` → `users(id)` ON DELETE CASCADE

**舊系統對應：**
- 對應舊表：`xx_estate_mems`（PK 為 `estate_mem_uid`，對應 users.uid）
- 注意：舊設計以 uid 為 PK，設定跨物業共用，新設計保持相同語意

---

### estate_member_links

> 說明：成員與物業的關聯表，記錄哪些使用者隸屬於哪個物業，及其管理權限層級。對應 API 資源：`/v1/estates/{estateId}/members`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵（替代複合主鍵，便於關聯操作） |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。所屬物業 |
| user_id | BIGINT | NOT NULL | — | FK → users(id)。成員使用者 ID |
| member_level | VARCHAR(20) | NOT NULL | 'readonly' | 管理權限。CHECK 約束值：`admin`（管理員）、`readonly`（唯讀/通知成員）。舊欄位：`estate_mem_level` ENUM('0','1') → '1'=admin, '0'=readonly。對應 API: `memberLevel` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE (estate_id, user_id)` -- 同一物業同一成員只能有一筆
- `INDEX idx_estate_member_links_estate (estate_id)` -- 查詢物業成員清單
- `INDEX idx_estate_member_links_user (user_id)` -- 查詢使用者加入的物業

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE CASCADE
- `user_id` → `users(id)` ON DELETE CASCADE

**CHECK 約束：**
- `CHECK (member_level IN ('admin', 'readonly'))`

**舊系統對應：**
- 對應舊表：`xx_estate_mem_link`（複合主鍵 estate_mem_uid + estate_id）
- 舊系統 `estate_mem_level` ENUM('0','1') → 新系統 `member_level` VARCHAR CHECK('admin','readonly')

---

### estate_facility_memos

> 說明：公共設施備忘錄。舊系統使用 EAV 設計（xx_estate_data_center），新系統改為正規化的備忘錄表格，以 (estate_id, facility_name) 定位唯一記錄。對應 API 資源：`/v1/estates/{estateId}/facilities`（PUT 備忘錄更新部分）

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。所屬物業 |
| facility_name | VARCHAR(255) | NOT NULL | — | 設施名稱，需與 estates.facilities 陣列中的值一致。對應 API: `facilityName` / `name` |
| memo | TEXT | NULL | — | 設施備忘錄（HTML rich text）。對應 API: `memo` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE (estate_id, facility_name)` -- 每個物業每個設施只有一筆備忘錄
- `INDEX idx_facility_memos_estate (estate_id)` -- 查詢物業所有設施備忘錄

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE CASCADE

**舊系統對應：**
- 對應舊表：`xx_estate_data_center`（EAV 設計，以 col_name=設施名稱、col_id=estate_id 定位，data_name/data_value 儲存備忘錄動態欄位）
- 設計改善：EAV 正規化為具名欄位，`memo` 對應舊系統中同一 (estate_id, col_name) 下所有 data_name/data_value 的純文字串接（格式：`{data_name}：{data_value}`，以換行分隔，依 data_sort 排序）。舊系統實際不存在 data_name='content' 記錄。

---

## 覆蓋率驗證（模組一）

### estates 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | estateId | estates.id | ✅ |
| 2 | title | estates.title | ✅ |
| 3 | shortTitle | estates.short_title | ✅ |
| 4 | ownerUserId | estates.owner_user_id | ✅ |
| 5 | address | estates.address | ✅ |
| 6 | phone | estates.phone | ✅ |
| 7 | ownerName | estates.owner_name | ✅ |
| 8 | ownerEmail | estates.owner_email | ✅ |
| 9 | website | estates.website | ✅ |
| 10 | facebook | estates.facebook | ✅ |
| 11 | note | estates.note | ✅ |
| 12 | facilities | estates.facilities (JSONB) | ✅ |
| 13 | electricityRate | estates.electricity_rate | ✅ |
| 14 | electricityBillingCycle | estates.electricity_billing_cycle | ✅ |
| 15 | zones | estates.zones (JSONB) | ✅ |

### rooms 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | roomId | rooms.id | ✅ |
| 2 | estateId | rooms.estate_id | ✅ |
| 3 | roomNumber | rooms.room_number | ✅ |
| 4 | storey | rooms.storey | ✅ |
| 5 | roomType | rooms.room_type | ✅ |
| 6 | sizeSquareMeter | rooms.size_sqm | ✅ |
| 7 | facilities | rooms.facilities (JSONB) | ✅ |
| 8 | prices (yearly/halfYearly/quarterly/monthly) | rooms.prices (JSONB) | ✅ |
| 9 | note | rooms.note | ✅ |
| 10 | sortOrder | rooms.sort_order | ✅ |
| 11 | zone | rooms.zone | ✅ |
| 12 | activeRentId | ⏸ 由 rents 模組查詢計算，非儲存欄位 | ⏸ |

### estate_member_profiles 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | unit | estate_member_profiles.unit | ✅ |
| 2 | title | estate_member_profiles.title | ✅ |
| 3 | calendarTextColor | estate_member_profiles.calendar_text_color | ✅ |
| 4 | calendarBgColor | estate_member_profiles.calendar_bg_color | ✅ |

### estate_member_links 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | userId | estate_member_links.user_id | ✅ |
| 2 | memberLevel | estate_member_links.member_level | ✅ |
| 3 | name | ⏸ 由 users 表 JOIN 提供，非 estate_member_links 欄位 | ⏸ |
| 4 | username | ⏸ 由 users 表 JOIN 提供 | ⏸ |

### estate_facility_memos 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | name (FacilityItem) | estate_facility_memos.facility_name | ✅ |
| 2 | memo (FacilityItem) | estate_facility_memos.memo | ✅ |
| 3 | updatedAt (FacilityItem) | estate_facility_memos.updated_at | ✅ |
| 4 | facilityName (FacilityMemoUpdateRequest) | estate_facility_memos.facility_name | ✅ |

---

> 注意：`users` 表（對應模組六）將在後續批次設計，本批次僅定義 FK 引用關係。
> 注意：附件相關欄位（`attachments`）由模組八（檔案管理）統一設計，本批次不納入。

---

## 模組二：租賃管理（Estate Rent）

> 對應 API 資源：`/v1/estates/{estateId}/rents`、`/v1/estates/{estateId}/rents/{rentId}/tenants`、`/v1/tenants`

---

### tenants

> 說明：房客（承租人）主檔。Tenant 為跨 estate 的全域資源，不綁定特定物業，同一 Tenant 可關聯至不同物業的多筆租期。對應 API 資源：`/v1/tenants`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| name | VARCHAR(255) | NOT NULL | — | 房客姓名。對應 API: `name` |
| birthday | DATE | NULL | — | 生日（YYYY-MM-DD）。舊欄位：`estate_user_birthday` DATE DEFAULT '0000-00-00'（NULL 取代 '0000-00-00' 表示未填寫）。對應 API: `birthday` |
| national_id | VARCHAR(255) | NULL | — | 身份證號。舊欄位：`estate_user_pid`。對應 API: `nationalId` |
| registered_address | VARCHAR(255) | NULL | — | 戶籍地址。舊欄位：`estate_user_addr`。對應 API: `registeredAddress` |
| phone | VARCHAR(255) | NULL | — | 聯絡電話。舊欄位：`estate_user_tel`。對應 API: `phone` |
| occupation | VARCHAR(255) | NULL | — | 職業。舊欄位：`estate_user_job`。對應 API: `occupation` |
| emergency_contact | VARCHAR(255) | NULL | — | 緊急聯絡人姓名或聯絡方式。舊欄位：`estate_user_contact`。對應 API: `emergencyContact` |
| email | VARCHAR(255) | NULL | — | Email。舊欄位：`estate_user_email`。對應 API: `email` |
| note | TEXT | NULL | — | 備註。舊欄位：`estate_user_note`。對應 API: `note` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除） |

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_tenants_name (name)` -- 全域搜尋房客姓名
- `INDEX idx_tenants_deleted_at (deleted_at)`

**外鍵：**
- 無（全域資源，不關聯 estate）

**CHECK 約束：**
- 無

**舊系統對應：**
- 對應舊表：`xx_estate_user`
- 欄位改善：舊欄位 `estate_user_birthday` DEFAULT '0000-00-00' 代表未填寫 → 新設計改為 NULL
- 注意：舊系統 `delete_estate_rent` 會連帶刪除 `estate_user`；新系統 Tenant 為獨立資源，刪除租期僅解除關聯，不刪除 Tenant 本體

---

### rents

> 說明：租約/租期主檔。每筆記錄代表一段房間租賃期間，隸屬於特定物業但透過 room_id 定位房間。對應 API 資源：`/v1/estates/{estateId}/rents`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。所屬物業（多租戶隔離欄位）。對應 API 路徑參數: `estateId` |
| room_id | BIGINT | NOT NULL | — | FK → rooms(id)。所屬房間。舊欄位：`estate_room_id`。對應 API: `roomId` |
| start_date | DATE | NOT NULL | — | 租約起始日。舊欄位：`estate_rent_start`。對應 API: `startDate` |
| end_date | DATE | NOT NULL | — | 租約到期日。舊欄位：`estate_rent_end`。對應 API: `endDate` |
| early_move_in_date | DATE | NULL | — | 提前入住日（NULL 表示無提前入住）。舊欄位：`estate_rent_early` date NULL。對應 API: `earlyMoveInDate` |
| deposit | NUMERIC(10,0) | NOT NULL | 0 | 押金金額（元）。舊欄位：`estate_rent_deposit` smallint(6)（精度提升）。對應 API: `deposit` |
| payment_method | VARCHAR(20) | NOT NULL | — | 繳費方式。CHECK 約束值：`yearly`（年繳）、`halfYearly`（半年）、`quarterly`（季繳）、`monthly`（月繳）。舊欄位：`estate_rent_money` VARCHAR（中文字串）→ 新設計改為英文 enum 值。對應 API: `paymentMethod` |
| initial_electric_reading | NUMERIC(10,1) | NOT NULL | 0.0 | 入住時起始電錶累積度數。舊欄位：`estate_rent_electric` decimal(10,1)。對應 API: `initialElectricReading` |
| renewal_status | VARCHAR(20) | NOT NULL | 'unset' | 到期續租意向。CHECK 約束值：`unset`（未設定）、`renew`（續租）、`no_renew`（不續租）。舊欄位：`estate_rent_continue` ENUM('','0','1') → 新設計語意更清晰。對應 API: `renewalStatus` |
| note | TEXT | NULL | — | 備註（HTML rich text）。舊欄位：`estate_rent_note`。對應 API: `note` |
| pet_info | VARCHAR(255) | NULL | — | 寵物資訊。舊欄位：`estate_rent_pet`。對應 API: `petInfo` |
| status | VARCHAR(20) | NOT NULL | 'active' | 租約狀態。CHECK 約束值：`active`（現役）、`archived`（已封存/退租）。舊欄位：`estate_rent_enable` ENUM('0','1') → '1'=active, '0'=archived。對應 API: `status` |
| termination_info | JSONB | NULL | — | 退租結算資訊（僅 status=archived 時有值）。舊欄位：`estate_rent_stop`（TEXT，JSON 字串）→ 新設計：JSONB。結構見下方說明。對應 API: `terminationInfo` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除） |

**termination_info JSONB 結構：**
```json
{
  "reason": "string（退租原因）",
  "terminationDate": "RFC3339 日期時間",
  "operatorUserId": "integer（執行退租的使用者 ID）",
  "initialElectricReading": "float（入住起始電錶度數）",
  "finalElectricReading": "float（退租時電錶度數）",
  "electricityCost": "integer（電費，元）",
  "depositRefund": "integer（退押金，元，負數表示退款）",
  "totalRefund": "integer（總退款，元，負數為退款）",
  "primaryTenantName": "string（主房客姓名）",
  "additionalCharges": {
    "damageFee": "integer（毀損費）",
    "cleaningFee": "integer（清潔費）",
    "otherFee": "integer（其他費用）",
    "rentBack": "integer（未到期租金退還）"
  }
}
```

> 舊欄位：`estate_rent_stop`（TEXT，JSON 字串，結構中的 `uid`→`operatorUserId`、`last_electric`→`initialElectricReading`、`electric`→`finalElectricReading`、`electric_money`→`electricityCost`、`rent_deposit`→`depositRefund`、`refund_total`→`totalRefund`、`money.lost`→`additionalCharges.damageFee`、`money.clean`→`additionalCharges.cleaningFee`、`money.other`→`additionalCharges.otherFee`、`money.rent_back`→`additionalCharges.rentBack`）

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_rents_estate (estate_id)` -- 多租戶隔離查詢
- `INDEX idx_rents_estate_status (estate_id, status)` -- 依狀態過濾（常用：active）
- `INDEX idx_rents_room (room_id)` -- 查詢特定房間的租約
- `INDEX idx_rents_estate_room_active (estate_id, room_id) WHERE status = 'active' AND deleted_at IS NULL` -- 唯一性驗證（同一房間僅一筆現役租約）

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE RESTRICT
- `room_id` → `rooms(id)` ON DELETE RESTRICT

**CHECK 約束：**
- `CHECK (payment_method IN ('yearly', 'halfYearly', 'quarterly', 'monthly'))`
- `CHECK (renewal_status IN ('unset', 'renew', 'no_renew'))`
- `CHECK (status IN ('active', 'archived'))`
- `CHECK (end_date > start_date)`
- `CHECK (early_move_in_date IS NULL OR early_move_in_date <= start_date)`

**唯一性約束（應用層強制）：**
- 同一 `room_id` 在 `status='active'` 且 `deleted_at IS NULL` 時最多只能有一筆（以 partial unique index 保障）

**舊系統對應：**
- 對應舊表：`xx_estate_rent`
- JSONB 轉換：舊欄位 `estate_rent_stop`（TEXT，JSON 字串）→ 新欄位 `termination_info`（JSONB），結構重新命名為英文 camelCase
- 欄位改善：`estate_rent_money` VARCHAR（中文字串「年繳」/「半年」/「季繳」/「月繳」）→ `payment_method` VARCHAR CHECK('yearly','halfYearly','quarterly','monthly')
- 欄位改善：`estate_rent_enable` ENUM('0','1') → `status` VARCHAR CHECK('active','archived')
- 欄位改善：`estate_rent_continue` ENUM('','0','1') → `renewal_status` VARCHAR CHECK('unset','renew','no_renew')
- 新增欄位：`estate_id`（舊系統透過 room → estate 間接關聯，新系統明確加入 estate_id 作為多租戶隔離欄位）

---

### rent_tenant_links

> 說明：租約與房客的多對多關聯中間表。一個租約可對應多個房客（Tenant），同一個 Tenant 可跨多筆租約出現。對應 API 資源：`/v1/estates/{estateId}/rents/{rentId}/tenants`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵（替代複合主鍵，便於關聯操作） |
| rent_id | BIGINT | NOT NULL | — | FK → rents(id)。所屬租約 |
| tenant_id | BIGINT | NOT NULL | — | FK → tenants(id)。關聯房客 |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間（關聯建立時間） |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE (rent_id, tenant_id)` -- 同一租約同一房客只能有一筆關聯
- `INDEX idx_rent_tenant_links_rent (rent_id)` -- 查詢租約下所有房客
- `INDEX idx_rent_tenant_links_tenant (tenant_id)` -- 查詢房客關聯的租約

**外鍵：**
- `rent_id` → `rents(id)` ON DELETE CASCADE
- `tenant_id` → `tenants(id)` ON DELETE RESTRICT

**舊系統對應：**
- 對應舊表：`xx_estate_rent_user`（複合主鍵 estate_rent_id + estate_user_id）
- 命名改善：`estate_rent_id` → `rent_id`、`estate_user_id` → `tenant_id`
- 新增 `id` BIGSERIAL 主鍵（舊系統使用複合主鍵）

---

## 覆蓋率驗證（模組二）

### rents 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | rentId | rents.id | ✅ |
| 2 | roomId | rents.room_id | ✅ |
| 3 | roomNumber | ⏸ 由 rooms 表 JOIN 提供，非 rents 欄位 | ⏸ |
| 4 | startDate | rents.start_date | ✅ |
| 5 | endDate | rents.end_date | ✅ |
| 6 | earlyMoveInDate | rents.early_move_in_date | ✅ |
| 7 | deposit | rents.deposit | ✅ |
| 8 | paymentMethod | rents.payment_method | ✅ |
| 9 | initialElectricReading | rents.initial_electric_reading | ✅ |
| 10 | renewalStatus | rents.renewal_status | ✅ |
| 11 | note | rents.note | ✅ |
| 12 | petInfo | rents.pet_info | ✅ |
| 13 | status | rents.status | ✅ |
| 14 | terminationInfo | rents.termination_info（JSONB） | ✅ |
| 15 | tenants | ⏸ 由 rent_tenant_links JOIN tenants 提供 | ⏸ |
| 16 | daysRemaining（RentSummary） | ⏸ 應用層計算（now() - end_date），非儲存欄位 | ⏸ |
| 17 | primaryTenantName（RentSummary） | ⏸ 應用層查詢第一位關聯 Tenant 取得 | ⏸ |

### tenants 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | tenantId | tenants.id | ✅ |
| 2 | name | tenants.name | ✅ |
| 3 | birthday | tenants.birthday | ✅ |
| 4 | nationalId | tenants.national_id | ✅ |
| 5 | registeredAddress | tenants.registered_address | ✅ |
| 6 | phone | tenants.phone | ✅ |
| 7 | occupation | tenants.occupation | ✅ |
| 8 | emergencyContact | tenants.emergency_contact | ✅ |
| 9 | email | tenants.email | ✅ |
| 10 | note | tenants.note | ✅ |

### rent_tenant_links 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | tenantId（TenantLinkRequest） | rent_tenant_links.tenant_id | ✅ |
| 2 | rentId（路徑參數） | rent_tenant_links.rent_id | ✅ |

### termination_info JSONB 欄位（TerminationInfo schema）

| # | openapi schema 欄位 | 對應 JSONB key | 狀態 |
|---|-------------------|--------------|------|
| 1 | reason | termination_info.reason | ✅ |
| 2 | terminationDate | termination_info.terminationDate | ✅ |
| 3 | operatorUserId | termination_info.operatorUserId | ✅ |
| 4 | initialElectricReading | termination_info.initialElectricReading | ✅ |
| 5 | finalElectricReading | termination_info.finalElectricReading | ✅ |
| 6 | electricityCost | termination_info.electricityCost | ✅ |
| 7 | depositRefund | termination_info.depositRefund | ✅ |
| 8 | totalRefund | termination_info.totalRefund | ✅ |
| 9 | primaryTenantName | termination_info.primaryTenantName | ✅ |
| 10 | additionalCharges.damageFee | termination_info.additionalCharges.damageFee | ✅ |
| 11 | additionalCharges.cleaningFee | termination_info.additionalCharges.cleaningFee | ✅ |
| 12 | additionalCharges.otherFee | termination_info.additionalCharges.otherFee | ✅ |
| 13 | additionalCharges.rentBack | termination_info.additionalCharges.rentBack | ✅ |

---

> 注意：附件相關欄位（`attachments`）由模組八（檔案管理）統一設計，本批次不納入。

---

### 跨模組設計說明：繳費狀態判斷

`PaymentReminder` 與 `PaymentScheduleItem`（openapi.yaml）中的 `isPaid` 欄位為**應用層計算結果**，不建立獨立儲存表格。

**判斷邏輯：**

1. 應用層依 `rents.start_date` + `rents.payment_method` 計算各期應繳日陣列（年/半年/季/月）
2. 對每個應繳日，查詢 `accountings` 表（模組五）：
   ```sql
   SELECT id FROM accountings
   WHERE accounting_code = '{rentId}-{dueDate}'
     AND deleted_at IS NULL
   LIMIT 1
   ```
3. 查到記錄 → `isPaid = true`，`accountingId` = 該記錄 id；否則 `isPaid = false`

**accounting_code 格式：** `{rentId}-{YYYY-MM-DD}`，例如 `42-2026-01-01`

**對模組五（Accounting）的要求：**
- `accountings.accounting_code` 欄位必須存在
- 必須加入 `INDEX (accounting_code)` 支援此查詢
- 設計時需在 schema.md 模組五章節明確標注此欄位與租金繳費判斷的關聯

---

## 模組三：電費管理（Estate Electric）

> 對應 API 資源：`/v1/estates/{estateId}/electric-readings`、`/v1/estates/{estateId}/electric-report`、`/v1/estates/{estateId}/electric-receipt`

---

### electric_readings

> 說明：電錶度數紀錄表。以（room_id + year + month）為唯一鍵，儲存各房間每個月份的電錶**累積度數**（從裝表開始的累積值，非當月用量）。電費差值（當月度數 - 上月度數 × 單價）於應用層計算，不存入 DB。對應 API 資源：`/v1/estates/{estateId}/electric-readings`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。所屬物業（多租戶隔離欄位）。對應 API 路徑參數: `estateId` |
| room_id | BIGINT | NOT NULL | — | FK → rooms(id)。所屬房間。舊欄位：`estate_room_id`。對應 API: `roomId` |
| year | SMALLINT | NOT NULL | — | 記錄年份（如 2026）。舊欄位：`estate_electric_year` YEAR(4)。對應 API: `year` |
| month | SMALLINT | NOT NULL | — | 記錄月份（1-12）。舊欄位：`estate_electric_month` TINYINT。對應 API: `month` |
| degrees | NUMERIC(10,1) | NOT NULL | — | 電錶**累積**度數（從裝表開始的累積值）。舊欄位：`estate_electric_degrees` DECIMAL(10,1)。對應 API: `degrees` |
| recorded_by_user_id | BIGINT | NULL | — | FK → users(id)。記錄者使用者 ID。舊欄位：`estate_electric_uid`。對應 API: `recordedBy` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 最後更新時間（upsert 時更新）。舊欄位：`estate_electric_update` DATETIME。對應 API: `updatedAt` |

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE (estate_id, room_id, year, month)` -- 唯一鍵，支援 upsert（對應舊系統 REPLACE INTO 語意）
- `INDEX idx_electric_readings_estate (estate_id)` -- 多租戶隔離查詢
- `INDEX idx_electric_readings_estate_ym (estate_id, year, month)` -- 依年月查詢整個物業的電錶度數（最常用查詢模式）
- `INDEX idx_electric_readings_room (room_id)` -- 查詢特定房間歷史度數

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE RESTRICT
- `room_id` → `rooms(id)` ON DELETE RESTRICT
- `recorded_by_user_id` → `users(id)` ON DELETE SET NULL

**CHECK 約束：**
- `CHECK (month BETWEEN 1 AND 12)`
- `CHECK (year BETWEEN 2000 AND 9999)`
- `CHECK (degrees >= 0)`

**設計說明：**

1. **estate_id 冗餘設計**：`room_id` 已可透過 JOIN rooms 取得 `estate_id`，但電錶查詢的主要模式是「依物業 + 年月」批次查詢所有房間，因此將 `estate_id` 直接存入本表作為複合 index 首欄，避免 JOIN 開銷並確保多租戶隔離。

2. **累積值而非差值**：`degrees` 儲存累積電錶度數，電費計算（當月度數 - 前月度數 × 單價）在應用層執行。這與舊系統設計一致（已確認為累積值）。

3. **無 deleted_at**：本表以 upsert 語意操作（更新覆蓋，不軟刪除）。若需刪除某筆記錄，直接 DELETE 物理刪除，不需要軟刪除機制。

4. **報表/收據 API 無額外 DB 欄位**：`/electric-report`（Word）和 `/electric-receipt`（PDF）為純讀取計算後 redirect 的端點，無需額外資料表，所需資料來自 `electric_readings` JOIN `rooms` JOIN `rents` JOIN `tenants` 計算得出。

**舊系統對應：**
- 對應舊表：`xx_estate_electric`
- 舊複合主鍵（estate_room_id + estate_electric_degrees + estate_electric_year + estate_electric_month）→ 新設計改為 BIGSERIAL `id` 主鍵 + UNIQUE(estate_id, room_id, year, month)
- 欄位改善：`estate_electric_degrees` DECIMAL(10,1) → `degrees` NUMERIC(10,1)（PostgreSQL 精確數值型別）
- 欄位改善：`estate_electric_year` YEAR(4) → `year` SMALLINT（PostgreSQL 無 YEAR 型別）
- 欄位改善：`estate_electric_month` TINYINT → `month` SMALLINT
- 欄位改善：`estate_electric_update` DATETIME → `updated_at` TIMESTAMPTZ（統一 UTC 儲存）
- 新增欄位：`estate_id`（舊系統未明確存入，透過 room → estate 間接關聯；新系統明確加入作為多租戶隔離欄位及查詢優化）

---

## 覆蓋率驗證（模組三）

### electric_readings 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | roomId（ElectricReadingItem） | electric_readings.room_id | ✅ |
| 2 | roomNumber（ElectricReadingItem） | ⏸ 由 rooms 表 JOIN 提供，非 electric_readings 欄位 | ⏸ |
| 3 | year（ElectricReadingItem） | electric_readings.year | ✅ |
| 4 | month（ElectricReadingItem） | electric_readings.month | ✅ |
| 5 | degrees（ElectricReadingItem） | electric_readings.degrees | ✅ |
| 6 | recordedBy（ElectricReadingItem） | electric_readings.recorded_by_user_id | ✅ |
| 7 | updatedAt（ElectricReadingItem） | electric_readings.updated_at | ✅ |
| 8 | estateId（ElectricReadingListResponse） | ⏸ 路徑參數 / electric_readings.estate_id | ⏸ |
| 9 | electricityRate（ElectricReadingListResponse） | ⏸ 來自 estates.electricity_rate（模組一已定義） | ⏸ |
| 10 | months（ElectricReadingListResponse） | ⏸ 應用層計算的日期範圍清單，非 DB 欄位 | ⏸ |
| 11 | rooms（ElectricReadingListResponse） | ⏸ 應用層聚合 rooms JOIN electric_readings 計算 | ⏸ |
| 12 | roomId（ElectricReadingUpsertItem） | electric_readings.room_id | ✅ |
| 13 | year（ElectricReadingUpsertItem） | electric_readings.year | ✅ |
| 14 | month（ElectricReadingUpsertItem） | electric_readings.month | ✅ |
| 15 | degrees（ElectricReadingUpsertItem） | electric_readings.degrees | ✅ |
| 16 | electric-report API（Word 報表） | ⏸ 無額外 DB 欄位，讀取 electric_readings + rooms + rents + tenants 計算 | ⏸ |
| 17 | electric-receipt API（PDF 收據） | ⏸ 無額外 DB 欄位，同上 | ⏸ |

---

> 注意：報表/收據生成所需的「前期度數」須應用層查詢同一 room_id 的前一個月份記錄，由 electric_readings 表自身 JOIN 或 LAG() 視窗函數計算。

---

## 模組四：日誌/排程管理（Estate Schedule）

> 對應 API 資源：`/v1/estates/{estateId}/schedules`、`/v1/estates/{estateId}/schedules/{scheduleId}/replies`

---

### schedules

> 說明：日誌/工作記錄主檔。每筆記錄代表一個物業的工作事項，可掛在物業整體（room_id 為 NULL）或特定房間（room_id 有值）。對應 API 資源：`/v1/estates/{estateId}/schedules`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。所屬物業（多租戶隔離欄位）。對應 API 路徑參數: `estateId` |
| room_id | BIGINT | NULL | — | FK → rooms(id)。關聯房間（NULL 表示物業整體，不限定特定房間）。舊欄位：`estate_room_id`（0=物業整體）→ 新設計改為 NULL 語意更清晰。對應 API: `roomId` |
| scheduled_at | TIMESTAMPTZ | NOT NULL | — | 辦理日期時間（UTC 儲存）。舊欄位：`estate_schedule_date` DATETIME。對應 API: `scheduledAt` |
| kind | VARCHAR(255) | NOT NULL | — | 日誌分類（如「例行」「叫修」「退租」等，值來自系統設定，未來可異動故不用 ENUM）。舊欄位：`estate_schedule_kind`。對應 API: `kind` |
| status | VARCHAR(255) | NOT NULL | — | 辦理狀況文字（如「處理中」「已完成」，值來自系統設定）。舊欄位：`estate_schedule_status`（格式「狀態名=顏色;」）→ 新設計將狀態與顏色拆分為獨立欄位。對應 API: `status` |
| status_color | VARCHAR(20) | NULL | — | 辦理狀況對應顏色（hex 字串，如 `#FF0000`）。來源：舊欄位 `estate_schedule_status` 儲存「狀態名=顏色;」格式，新設計正規化為獨立欄位。對應 API: `statusColor` |
| content | TEXT | NOT NULL | — | 日誌內容（HTML/RichText，CkEditor 輸出）。舊欄位：`estate_schedule_content`。對應 API: `content` |
| reporter_user_id | BIGINT | NOT NULL | — | FK → users(id)。填報人使用者 ID。舊欄位：`estate_schedule_uid`。對應 API: `reporterUserId` |
| assist_user_id | BIGINT | NULL | — | 協辦人員。NULL=無協辦人，0=全體人員，>0=指定使用者的 user_id。舊欄位：`estate_schedule_assist`（-1=無協辦人）→ 新設計以 NULL 取代 -1，語意更清晰。對應 API: `assistUserId` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除）。注意：刪除日誌需先成功刪除關聯帳務記錄，失敗時日誌保留 |

**設計說明：**

1. **assist_user_id 正規化**：舊欄位 `estate_schedule_assist` 使用 -1/0/>0 三種特殊語意值。新設計以 NULL 替換 -1（無協辦人），保留 0（全體人員）與 >0（指定 userId）。FK 約束對 0 不生效（0 不對應實際 user），應用層負責語意判斷，DB 層以 `CHECK (assist_user_id IS NULL OR assist_user_id >= 0)` 確保值域。

2. **status_color 正規化（設計說明修正）**：舊系統 `estate_schedule_status` DB 欄位儲存的是**純文字狀態名稱**（如「完成」「重要」）。「狀態名=顏色;」格式（如 `重要=#1397DD;完成=#1397DD;`）存在於**模組設定**（`xoopsModuleConfig['status_opt']`），由 PHP 函式 `get_status_arr()` 解析後供 UI 選單使用，顏色碼**不存入每一筆資料列**。因此新設計 `status` 欄位直接映射舊欄位純文字值；`status_color` 欄位目前無對應舊資料（舊系統不在列資料存顏色），遷移時一律設為 NULL，新系統使用者可在建立/編輯排程時選擇顏色。

3. **estate_schedule_facility 排除**：使用者已確認此欄位暫時不需要，不納入新設計。

4. **room_id FK 例外**：`assist_user_id = 0` 為「全體人員」特殊值，不定義對 users 表的 FK（因 0 非有效 user_id）。FK 僅針對 assist_user_id > 0 的情況在應用層驗證。

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_schedules_estate (estate_id)` -- 多租戶隔離查詢
- `INDEX idx_schedules_estate_scheduled (estate_id, scheduled_at DESC)` -- 依日期排序的清單查詢（最常用模式）
- `INDEX idx_schedules_estate_kind (estate_id, kind)` -- 依分類過濾
- `INDEX idx_schedules_estate_room (estate_id, room_id)` -- 依房間過濾（room_id NULL 時查物業整體）
- `INDEX idx_schedules_deleted_at (deleted_at)` -- 軟刪除查詢

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE RESTRICT
- `room_id` → `rooms(id)` ON DELETE RESTRICT（NULL 允許，表示物業整體）
- `reporter_user_id` → `users(id)` ON DELETE RESTRICT

**CHECK 約束：**
- `CHECK (assist_user_id IS NULL OR assist_user_id >= 0)` -- NULL=無，0=全體，>0=指定 user

**遷移說明：**
- **kind 欄位空值策略**：舊系統 `estate_schedule_kind` 有 3577 筆空值（佔 5643 筆 63%）。`kind` 欄位無 CHECK 約束，空字串 `''` 為合法值（PostgreSQL NOT NULL 僅防止 NULL，不防止空字串）。遷移時空值填入 `''`，語意為「未分類」。API 層及前端應以空字串值作為「無分類」的篩選條件。
- **status 欄位空值策略**：舊系統 `estate_schedule_status` 有 2946 筆空值。`status` 欄位無 CHECK 約束，空字串合法。遷移時空值填入 `''`，對應的 `status_color = NULL`。
- **status_color 遷移說明**：舊系統不在資料列中儲存顏色，顏色由模組設定（`status_opt`）決定。遷移時所有 `status_color` 欄位設為 NULL，新系統使用者可在建立/編輯排程時選擇顏色。

**舊系統對應：**
- 對應舊表：`xx_estate_schedule`
- 欄位改善：`estate_schedule_assist` MEDIUMINT（-1/0/>0）→ `assist_user_id` BIGINT NULL（NULL/0/>0）；以 NULL 取代 -1 表示無協辦人
- 欄位改善：`estate_schedule_status` VARCHAR（純文字狀態名稱，顏色存於模組設定非資料列）→ 拆分為 `status` VARCHAR（直接映射舊欄位純文字值）+ `status_color` VARCHAR(20)（遷移時全部為 NULL，新系統使用者可填入）
- 欄位改善：`estate_room_id`（0=物業整體）→ `room_id` BIGINT NULL（NULL=物業整體）
- 欄位廢棄：`estate_schedule_facility`（關聯公共設施）→ 使用者確認暫不需要，不納入新設計

---

### schedule_replies

> 說明：日誌回應記錄。每筆記錄為某個日誌的一則回應，附屬於特定日誌。對應 API 資源：`/v1/estates/{estateId}/schedules/{scheduleId}/replies`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| schedule_id | BIGINT | NOT NULL | — | FK → schedules(id)。所屬日誌 ID。舊欄位：`estate_schedule_id`。對應 API: `scheduleId` |
| content | TEXT | NOT NULL | — | 回應內容（HTML/RichText，CkEditor 輸出）。舊欄位：`estate_reply_content`。對應 API: `content` |
| author_user_id | BIGINT | NOT NULL | — | FK → users(id)。回應者使用者 ID。舊欄位：`estate_reply_uid`。對應 API: `authorUserId` |
| replied_at | TIMESTAMPTZ | NOT NULL | now() | 回應日期時間（由系統寫入當下時間，不允許 client 自訂）。舊欄位：`estate_reply_date` DATETIME。對應 API: `repliedAt` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間（編輯回應時更新）|
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除）。刪除回應時連帶刪除附件 |

**設計說明：**

1. **replied_at vs created_at**：`replied_at` 對應業務語意（回應日期，API 可見），`created_at` 為系統稽核欄位（符合統一慣例）。新增時兩者值相同（now()）；編輯回應時 `replied_at` 更新為當下時間（與舊系統 `update_estate_reply` 行為一致，API 說明已明確標注）。

2. **estate_id 不直接存入**：本表透過 `schedule_id` → `schedules.estate_id` 間接取得物業歸屬。回應的多租戶隔離由父日誌的 estate_id 保障，查詢時必定先有 schedule_id，不需要額外的 estate_id 索引。

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_schedule_replies_schedule (schedule_id)` -- 查詢日誌下所有回應（最常用模式）
- `INDEX idx_schedule_replies_author (author_user_id)` -- 查詢特定使用者的回應

**外鍵：**
- `schedule_id` → `schedules(id)` ON DELETE CASCADE（日誌刪除時連帶刪除所有回應）
- `author_user_id` → `users(id)` ON DELETE RESTRICT

**舊系統對應：**
- 對應舊表：`xx_estate_reply`
- 欄位改善：`estate_reply_uid` → `author_user_id`（命名語意更清晰）
- 欄位改善：`estate_reply_date` DATETIME → `replied_at` TIMESTAMPTZ（統一 UTC 儲存）
- 新增欄位：`created_at`、`updated_at`、`deleted_at`（統一慣例）

---

## 覆蓋率驗證（模組四）

### schedules 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | scheduleId | schedules.id | ✅ |
| 2 | estateId | schedules.estate_id | ✅ |
| 3 | roomId（nullable） | schedules.room_id（NULL=物業整體） | ✅ |
| 4 | roomNumber | ⏸ 由 rooms 表 JOIN 提供，非 schedules 欄位 | ⏸ |
| 5 | scheduledAt | schedules.scheduled_at | ✅ |
| 6 | kind | schedules.kind | ✅ |
| 7 | status | schedules.status | ✅ |
| 8 | statusColor | schedules.status_color | ✅ |
| 9 | content | schedules.content | ✅ |
| 10 | reporterUserId | schedules.reporter_user_id | ✅ |
| 11 | reporterName | ⏸ 由 users 表 JOIN 提供，非 schedules 欄位 | ⏸ |
| 12 | assistUserId（null/0/>0） | schedules.assist_user_id（NULL/0/>0） | ✅ |
| 13 | assistName | ⏸ 應用層依 assist_user_id 值判斷（NULL→null，0→"全體人員"，>0→users JOIN） | ⏸ |
| 14 | replyCount（ScheduleSummary） | ⏸ 應用層 COUNT(schedule_replies WHERE schedule_id=?) | ⏸ |
| 15 | contentSnippet（ScheduleSummary） | ⏸ 應用層截取 content 去除 HTML 後前 100 字元 | ⏸ |
| 16 | replies（ScheduleDetail） | schedule_replies 表（見下方） | ✅ |
| 17 | accountings（ScheduleDetail） | ⏸ 由 accountings 表（模組五）查詢，以 schedule_id 為關聯鍵 | ⏸ |
| 18 | monthGroups（ScheduleListResponse） | ⏸ 應用層 GROUP BY DATE_TRUNC('month', scheduled_at) 計算 | ⏸ |

### schedule_replies 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | replyId | schedule_replies.id | ✅ |
| 2 | scheduleId | schedule_replies.schedule_id | ✅ |
| 3 | content | schedule_replies.content | ✅ |
| 4 | authorUserId | schedule_replies.author_user_id | ✅ |
| 5 | authorName | ⏸ 由 users 表 JOIN 提供，非 schedule_replies 欄位 | ⏸ |
| 6 | repliedAt | schedule_replies.replied_at | ✅ |

---

> 注意：附件相關欄位（`attachments`）由模組八（檔案管理）統一設計，本批次不納入。
> 注意：`ScheduleDetail.accountings` 關聯至模組五（Accounting）的 `accountings` 表，查詢條件為 `linked_resource_type = 'schedule' AND linked_resource_id = schedules.id`。

---

## 模組五：帳務管理（Accounting）

> 對應 API 資源：`/v1/estates/{estateId}/accountings`、`/v1/estates/{estateId}/accounting-titles`

---

### accounting_titles

> 說明：會計科目設定表。儲存系統全域的會計科目清單，為靜態設定資料（以 seed data 填入），不綁定特定物業。物業模組適用科目以前綴分組：46xx=物業費用類、66xx=物業收益類。對應 API 資源：`GET /v1/estates/{estateId}/accounting-titles`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵（系統內部流水號，對應舊表 accounting_id） |
| title_id | INTEGER | NOT NULL | — | 科目編號（業務識別碼，如 4603、6611），為對外 API 使用的 titleId。舊欄位：`accounting_title_id` |
| kind | VARCHAR(10) | NOT NULL | — | 科目類別。CHECK 約束值：`expense`（費用類）、`income`（收益類）。舊欄位：`accounting_kind`（中文「營業費用（成本）類」/「營業收益類」） |
| title | VARCHAR(255) | NOT NULL | — | 科目名稱（如「租金收入」）。舊欄位：`accounting_title` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE (title_id)` -- 科目編號在全系統唯一
- `INDEX idx_accounting_titles_kind (kind)` -- 依類別過濾科目

**外鍵：**
- 無（全域靜態設定表，不關聯特定物業）

**CHECK 約束：**
- `CHECK (kind IN ('expense', 'income'))`

**設計說明：**

1. **建表 vs Seed Data**：科目清單共 123 筆，結構固定（titleId、kind、title），且 `accountings.title_id` 需要 FK 引用。建立獨立表格並以 seed data 填入，可確保 FK 完整性。未來若需新增科目，透過 migration 新增 seed 即可，不需修改程式碼。

2. **欄位 id vs title_id**：`id` 為 BIGSERIAL 系統主鍵，`title_id` 為業務識別碼（4603 等科目編號）。FK 引用（accountings.title_id → accounting_titles.title_id）使用業務識別碼，與 API 設計一致。

3. **物業模組適用科目**：API 說明固定回傳 46xx 費用類與 66xx 收益類科目，應用層依 `title_id / 100` 的前兩碼過濾，不需要在 DB 存「適用模組」欄位。

**舊系統對應：**
- 對應舊表：`xx_accounting_title`
- 欄位改善：`accounting_kind`（中文字串）→ `kind` VARCHAR CHECK('expense', 'income')
- 欄位改善：`accounting_title_id`（科目編號）→ `title_id` INTEGER UNIQUE
- 科目前綴分組（46xx/66xx=物業、41xx/61xx=income、42xx/62xx=代辦）保留語意，由應用層過濾，不在 DB 增設分組欄位

---

### accountings

> 說明：通用帳務記錄表。帳務為跨模組的通用引擎，服務租賃（rent）、日誌（schedule）等多個業務模組。每筆記錄代表一筆收入或支出，並可關聯至產生此帳務的業務物件。對應 API 資源：`/v1/estates/{estateId}/accountings`
>
> **跨模組關聯說明（模組二繳費狀態）：** `code` 欄位格式為 `{rentId}-{YYYY-MM-DD}`（如 `42-2026-01-01`），用於模組二租金繳費狀態判斷。應用層查詢 `WHERE code = '{rentId}-{dueDate}' AND estate_id = ? AND deleted_at IS NULL` 判斷某期租金是否已繳。`INDEX idx_accountings_code` 支援此查詢效率。

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。所屬物業（多租戶隔離欄位）。舊設計：`accounting_main_col='estate_id'` + `accounting_main_sn=estate_id值` 兩個 varchar 欄位 → 新設計改為直接的 BIGINT FK |
| title_id | INTEGER | NULL | — | FK → accounting_titles(title_id)。科目編號（如 4603=租金收入）。舊欄位：`accounting_tid`。對應 API: `titleId` |
| title_name | VARCHAR(255) | NULL | — | 科目名稱快取（冗餘欄位，方便顯示時不需 JOIN accounting_titles）。舊欄位：`accounting_title`。對應 API: `titleName` |
| description | VARCHAR(255) | NULL | — | 科目說明（自訂文字，可由系統自動填入，如「42-2026-01-01 租金」）。舊欄位：`accounting_title`（舊系統同一欄位混用科目說明與自訂文字）。對應 API: `description` |
| income | INTEGER | NOT NULL | 0 | 收入金額（元）。income 與 expenditure 不可同時為非零值。舊欄位：`accounting_income` MEDIUMINT。對應 API: `income` |
| expenditure | INTEGER | NOT NULL | 0 | 支出金額（元）。舊欄位：`accounting_expenditure` MEDIUMINT。對應 API: `expenditure` |
| accounting_date | TIMESTAMPTZ | NOT NULL | — | 帳務日期時間（UTC 儲存）。舊欄位：`accounting_date` DATETIME。對應 API: `accountingDate` |
| payment_method | VARCHAR(255) | NULL | — | 付款方式（如「現金」）。舊欄位：`accounting_method`。對應 API: `paymentMethod` |
| counterparty | VARCHAR(255) | NULL | — | 交易對象（如房客姓名）。舊欄位：`accounting_who`。對應 API: `counterparty` |
| tag | VARCHAR(255) | NULL | — | 帳務標記（業務語意標籤，如「押金」「租金」「電費」「日誌」「退租其他費用」）。舊欄位：`accounting_tag`。對應 API: `tag` |
| code | VARCHAR(255) | NULL | — | 辨識碼。格式：`{rentId}-{YYYY-MM-DD}`（如 `42-2026-01-01`）。用於模組二租金繳費狀態查詢（`isPaid` 判斷）。舊欄位：`accounting_code`。對應 API: `code` |
| linked_resource_type | VARCHAR(50) | NULL | — | 關聯業務資源類型。CHECK 約束值：`rent`（租約）、`schedule`（日誌）。取代舊設計的 polymorphic 三欄（`accounting_table` + `accounting_col_name`），語意更清晰。對應 API: `linkedResourceType` |
| linked_resource_id | BIGINT | NULL | — | 關聯業務資源 ID（對應 rents.id 或 schedules.id）。取代舊欄位：`accounting_col_sn`。需與 `linked_resource_type` 同時提供或同時為 NULL。對應 API: `linkedResourceId` |
| cash_account_id | INTEGER | NULL | — | 零用金帳戶 ID（預留欄位，income 模組啟用後生效）。舊欄位：`accounting_bank`（儲存 income 模組的 income_sn，0 或空值表示未使用）。對應 API: `cashAccountId` |
| created_by_user_id | BIGINT | NOT NULL | — | FK → users(id)。記錄者使用者 ID。舊欄位：`accounting_uid`。對應 API: `createdBy` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間。對應 API: `createdAt` |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除）。刪除日誌時需先成功刪除關聯帳務 |

**設計說明：**

1. **Polymorphic 改為明確欄位**：舊系統以 `accounting_table`（如 "estate_rent"）+ `accounting_col_name`（如 "estate_rent_id"）+ `accounting_col_sn`（ID 值）三欄構成 Polymorphic FK。新系統 API 已標準化為 `linkedResourceType: enum[rent, schedule]` + `linkedResourceId`，故改為兩個明確欄位。值域可控（當前僅 rent、schedule），語意清晰，不依賴資料表名稱字串，易於查詢與 JOIN。

2. **estate_id 直接儲存**：舊系統以 `accounting_main_col='estate_id'` + `accounting_main_sn=estate_id值` 兩個 varchar 欄位表示頂層歸屬。新系統帳務路徑已限定在 `/v1/estates/{estateId}/accountings`，直接以 `estate_id BIGINT FK` 儲存物業歸屬，廢除舊的 main_col/main_sn 設計。

3. **income/expenditure 使用 INTEGER**：API 定義金額為整數（元），與業務一致（舊系統為 MEDIUMINT）。INTEGER 支援約 21 億元，足夠物業管理場景。若未來需要記錄超大金額可升為 BIGINT。

4. **title_name 冗餘欄位**：API response 包含 `titleName`（冗餘欄位，便於顯示）。在 DB 層存入 `title_name` 快取，避免每次查詢都 JOIN `accounting_titles`，適合帳務清單頻繁查詢的場景。寫入時由應用層同步填入（title_id → accounting_titles.title → title_name）。

5. **code 欄位跨模組依賴**：此欄位是模組二（租賃管理）繳費狀態（isPaid）判斷的核心依據。查詢模式：`WHERE code = '{rentId}-{dueDate}' AND estate_id = ? AND deleted_at IS NULL`。Index `idx_accountings_code` 對此查詢至關重要。

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_accountings_estate (estate_id)` -- 多租戶隔離查詢（主要過濾條件）
- `INDEX idx_accountings_estate_date (estate_id, accounting_date)` -- 依日期區間查詢（帳務總覽最常用模式）
- `INDEX idx_accountings_code (code)` -- 租金繳費判斷查詢（`WHERE code = '{rentId}-{dueDate}'`），跨模組關聯查詢效率關鍵
- `INDEX idx_accountings_linked_resource (linked_resource_type, linked_resource_id)` -- 查詢特定業務物件的所有帳務（如某租約的全部帳務）
- `INDEX idx_accountings_estate_tag (estate_id, tag)` -- 依業務標記過濾（如查詢所有「押金」帳務）
- `INDEX idx_accountings_estate_title (estate_id, title_id)` -- 依科目加總（帳務總覽科目分組）
- `INDEX idx_accountings_deleted_at (deleted_at)` -- 軟刪除查詢

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE RESTRICT
- `title_id` → `accounting_titles(title_id)` ON DELETE RESTRICT（NULL 允許，表示未分類帳務）
- `created_by_user_id` → `users(id)` ON DELETE RESTRICT

**CHECK 約束：**
- `CHECK (NOT (income > 0 AND expenditure > 0))` -- income 與 expenditure 不可同時為正值（允許負值以支援退款/修正分錄場景）
- `CHECK (linked_resource_type IN ('rent', 'schedule') OR linked_resource_type IS NULL)`
- `CHECK ((linked_resource_type IS NULL AND linked_resource_id IS NULL) OR (linked_resource_type IS NOT NULL AND linked_resource_id IS NOT NULL))` -- 兩者必須同時提供或同時為 NULL

> **負值金額設計說明**：移除原先 `CHECK (income >= 0)` 與 `CHECK (expenditure >= 0)` 約束。退款、修正分錄等帳務場景需要負值（data-profile 舊系統資料亦有 negative_income=809 筆、negative_expenditure=725 筆）。互斥約束 `NOT (income > 0 AND expenditure > 0)` 仍保留，確保一筆帳務不會同時為正收入又為正支出。負值的業務語意（退款、沖銷）由應用層 UI 說明文件引導。

**舊系統對應：**
- 對應舊表：`xx_accounting`
- Polymorphic 重構：舊欄位 `accounting_table` + `accounting_col_name` + `accounting_col_sn`（三欄 polymorphic）→ 新欄位 `linked_resource_type` VARCHAR(50) + `linked_resource_id` BIGINT（明確兩欄）
- Polymorphic 重構：舊欄位 `accounting_main_col` + `accounting_main_sn`（頂層歸屬）→ 新欄位 `estate_id` BIGINT FK（直接儲存）
- 欄位重命名：`accounting_who` → `counterparty`、`accounting_method` → `payment_method`、`accounting_uid` → `created_by_user_id`、`accounting_code` → `code`、`accounting_tag` → `tag`、`accounting_bank` → `cash_account_id`
- 欄位廢棄：`accounting_tid` SMALLINT → 新欄位 `title_id` INTEGER（FK 引用 accounting_titles.title_id）
- 欄位廢棄：舊 `accounting_title` VARCHAR（混用科目說明與自訂文字）→ 拆分為 `title_name`（科目名稱快取）+ `description`（自訂說明）

---

## 覆蓋率驗證（模組五）

### accounting_titles 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | titleId（AccountingTitle） | accounting_titles.title_id | ✅ |
| 2 | kind（AccountingTitle） | accounting_titles.kind | ✅ |
| 3 | title（AccountingTitle） | accounting_titles.title | ✅ |
| 4 | expenseTitles（AccountingTitleListResponse） | ⏸ 應用層依 kind='expense' 過濾並篩選 46xx，非 DB 欄位 | ⏸ |
| 5 | incomeTitles（AccountingTitleListResponse） | ⏸ 應用層依 kind='income' 過濾並篩選 66xx，非 DB 欄位 | ⏸ |

### accountings 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | accountingId（Accounting） | accountings.id | ✅ |
| 2 | estateId（Accounting） | accountings.estate_id | ✅ |
| 3 | titleId（Accounting） | accountings.title_id | ✅ |
| 4 | titleName（Accounting） | accountings.title_name | ✅ |
| 5 | description（Accounting） | accountings.description | ✅ |
| 6 | income（Accounting） | accountings.income | ✅ |
| 7 | expenditure（Accounting） | accountings.expenditure | ✅ |
| 8 | accountingDate（Accounting） | accountings.accounting_date | ✅ |
| 9 | paymentMethod（Accounting） | accountings.payment_method | ✅ |
| 10 | counterparty（Accounting） | accountings.counterparty | ✅ |
| 11 | tag（Accounting） | accountings.tag | ✅ |
| 12 | code（Accounting） | accountings.code | ✅ |
| 13 | linkedResourceType（Accounting） | accountings.linked_resource_type | ✅ |
| 14 | linkedResourceId（Accounting） | accountings.linked_resource_id | ✅ |
| 15 | cashAccountId（Accounting） | accountings.cash_account_id | ✅ |
| 16 | createdBy（Accounting） | accountings.created_by_user_id | ✅ |
| 17 | createdAt（Accounting） | accountings.created_at | ✅ |
| 18 | AccountingOverview（overview 端點） | ⏸ 純應用層計算（SUM/GROUP BY），無額外 DB 欄位 | ⏸ |
| 19 | titleBreakdown（AccountingOverview） | ⏸ 應用層 GROUP BY title_id 計算，非 DB 欄位 | ⏸ |
| 20 | 查詢過濾：linkedResourceType + linkedResourceId | accountings.linked_resource_type + linked_resource_id | ✅ |
| 21 | 查詢過濾：tag | accountings.tag | ✅ |
| 22 | 查詢過濾：code | accountings.code | ✅ |
| 23 | 查詢過濾：dateFrom / dateTo | accountings.accounting_date | ✅ |
| 24 | 查詢過濾：titleId | accountings.title_id | ✅ |

---

> 注意：`accounting_titles` 表為全系統靜態設定，以 seed data 填入，不屬於多租戶範圍，不需要 `estate_id` 欄位。
> 注意：`AccountingOverview`（帳務總覽）為純查詢彙總端點，所有統計資料從 `accountings` 表聚合計算，無需額外 DB 表格。
> 注意：現金入款自動同步零用金帳戶的邏輯（依賴 income 模組）目前不實作，`cash_account_id` 欄位保留預備未來啟用。

---

## 模組六：會員管理（Users）

> 設計日期：2026-03-15

### users

> 說明：系統使用者帳號主表，儲存所有可登入系統的使用者資料。此表為全系統 FK 基礎，所有業務模組（物業成員、電費記錄者、日誌填報者、帳務記錄者等）均以 `user_id` 引用此表。此表不屬於任何特定物業（無 `estate_id`），為全域資源。
>
> 對應 API 資源：`/v1/users`、`/v1/auth/login`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵。對應舊系統 `uid` mediumint(8)，升級為 BIGINT 以支援未來擴充 |
| username | VARCHAR(25) | NOT NULL | — | 登入帳號（唯一，建立後不可更改）。對應舊系統 `uname`。對應 API: `username` |
| name | VARCHAR(60) | NOT NULL | — | 顯示名稱（真實姓名）。對應舊系統 `name`。對應 API: `name` |
| email | VARCHAR(60) | NOT NULL | — | Email。對應舊系統 `email`。對應 API: `email` |
| password_hash | VARCHAR(255) | NOT NULL | — | 密碼雜湊值。新系統使用 bcrypt（cost=12）或 argon2id 儲存；密碼永不在 API response 出現。對應舊系統 `pass`（MD5，無 salt），遷移時需強制重設密碼 |
| occupation | VARCHAR(100) | NULL | — | 職業。對應舊系統 `user_occ`。對應 API: `occupation` |
| bio | TEXT | NULL | — | 個人簡介。對應舊系統 `bio`（tinytext，升級為 TEXT）。對應 API: `bio` |
| avatar_path | VARCHAR(255) | NULL | — | 大頭貼在 Cloud Storage 的物件路徑（metadata only，實際檔案存 GCS）。對應舊系統 `user_avatar`（僅存檔名如 'blank.gif'） |
| role | VARCHAR(20) | NOT NULL | 'user' | 系統層角色。CHECK 約束值：`admin`（系統管理員，可管理物業/使用者/群組）、`user`（一般使用者，只能存取被授權物業）。對應 JWT claims: `role`。對應 API: `role` |
| is_enabled | BOOLEAN | NOT NULL | TRUE | 帳號啟用狀態（TRUE=啟用，FALSE=停用）。對應舊系統 `level` tinyint(3)（1=啟用，0=停用），語意化重新命名。對應 API: `isEnabled` |
| last_login_at | TIMESTAMPTZ | NULL | — | 最後登入時間（未曾登入時為 NULL）。對應舊系統 `last_login` int Unix timestamp（轉換為 TIMESTAMPTZ）。對應 API: `lastLoginAt` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 帳號建立時間。對應舊系統 `user_regdate` int Unix timestamp（轉換為 TIMESTAMPTZ）。對應 API: `createdAt` |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 最後更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除）。刪除帳號需評估各業務模組的 FK 影響：多數業務記錄以 ON DELETE RESTRICT 保護，需先處理關聯資料後方可軟刪除 |

**設計說明：**

1. **密碼 hash 升級**：舊系統 `pass` 欄位使用 MD5（無 salt），資安風險極高。新系統 `password_hash` 統一使用 bcrypt（cost ≥ 12）或 argon2id。舊系統資料遷移時，MD5 hash 無法反轉，需在使用者下次登入時強制重設密碼，或一次性通知全員重設。

2. **level 語意化**：舊系統 `level` 為 tinyint（0/1），語意不直觀。新系統改為 `is_enabled BOOLEAN`，配合預設值 `TRUE`（新帳號預設啟用），與 API 的 `isEnabled` 欄位名直接對應。

3. **全域資源設計**：`users` 表不含 `estate_id`，因為一個使用者可以管理多個物業（透過 `estate_member_links`），不屬於任何單一物業。

4. **avatar_path 設計**：舊系統 `user_avatar` 只存檔名（如 `blank.gif`），新系統改存 Cloud Storage 物件路徑（如 `avatars/users/42/profile.jpg`）。實際檔案存 GCS，DB 只存 metadata。

5. **user_avatar 的 NOT NULL 預設值取消**：舊系統強制 `NOT NULL DEFAULT 'blank.gif'`，新系統以 NULL 表示「未設定大頭貼」，由應用層決定預設顯示邏輯，DB 不強制預設圖。

6. **role 欄位（新增）**：新系統存取控制分兩層：系統層（`users.role`）+ 物業層（`estate_member_links.member_level`）。`role = 'admin'` 的使用者可執行全系統管理操作（新增/刪除物業、管理使用者與群組）；`role = 'user'` 只能存取被授權的物業。此欄位同步放入 JWT claims 供 middleware 快速判斷，不需每次查 DB。舊系統無此概念（透過 XOOPS `group_type` 判斷），新系統明確化為 DB 欄位。

7. **groups 關聯**：API `UserDetail.groups` 陣列透過 `user_group_links` 中間表管理（模組七設計），`users` 表本身無群組欄位。

7. **排除欄位清單**：下列舊系統欄位確認排除——`url`、`user_icq`、`user_aim`、`user_yim`、`user_msnm`（廢棄通訊軟體）、`posts`、`attachsig`、`rank`、`theme`（XOOPS 原生）、`umode`、`uorder`、`notify_method`、`notify_mode`、`user_mailok`、`user_sig`、`user_viewemail`、`user_from`（無業務用途）、`timezone_offset`（新系統統一 UTC）、`actkey`（借用欄位，改由 estate_member_links 管理）、`user_intrest`（借用欄位，廢棄）。

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_users_username (username)` -- 帳號唯一性約束，也是登入查詢主要條件
- `INDEX idx_users_email (email)` -- 支援 email 模糊搜尋（`GET /v1/users?email=...`）
- `INDEX idx_users_role (role)` -- 支援依系統角色過濾（`GET /v1/users?role=admin`）
- `INDEX idx_users_is_enabled (is_enabled)` -- 支援依啟用狀態過濾（`GET /v1/users?isEnabled=...`）
- `INDEX idx_users_deleted_at (deleted_at)` -- 軟刪除查詢

**外鍵：**
- 此表為全系統 FK 根源，本表無對外 FK。

**CHECK 約束：**
- `CHECK (role IN ('admin', 'user'))`

**舊系統對應：**
- 對應舊表：`xx_users`
- 欄位重命名：`uid` → `id`、`uname` → `username`、`pass` → `password_hash`、`user_occ` → `occupation`、`user_avatar` → `avatar_path`、`user_regdate`（int unix ts）→ `created_at`（TIMESTAMPTZ）、`last_login`（int unix ts）→ `last_login_at`（TIMESTAMPTZ）、`level`（tinyint 0/1）→ `is_enabled`（BOOLEAN）
- 新增欄位：`role VARCHAR(20) NOT NULL DEFAULT 'user'`（舊系統無此欄位，由 XOOPS 群組判斷身份，新系統改為明確的 role 欄位）
- 排除欄位：`url`、`user_icq`、`user_aim`、`user_yim`、`user_msnm`、`posts`、`attachsig`、`rank`、`theme`、`umode`、`uorder`、`notify_method`、`notify_mode`、`user_mailok`、`user_sig`、`user_viewemail`、`user_from`、`timezone_offset`、`actkey`（借用欄位）、`user_intrest`（借用欄位）

---

### 覆蓋率驗證（模組六）

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | userId（UserDetail） | users.id | ✅ |
| 2 | name（UserDetail） | users.name | ✅ |
| 3 | username（UserDetail） | users.username | ✅ |
| 4 | email（UserDetail） | users.email | ✅ |
| 5 | occupation（UserDetail） | users.occupation | ✅ |
| 6 | bio（UserDetail） | users.bio | ✅ |
| 7 | role（UserDetail） | users.role | ✅ |
| 8 | isEnabled（UserDetail） | users.is_enabled | ✅ |
| 9 | lastLoginAt（UserDetail） | users.last_login_at | ✅ |
| 10 | createdAt（UserDetail） | users.created_at | ✅ |
| 11 | groups（UserDetail，陣列） | ⏸ 透過 user_group_links 關聯表（模組七設計） | ⏸ |
| 12 | password（UserCreateRequest，明文輸入） | users.password_hash（bcrypt 儲存） | ✅ |
| 13 | role（UserCreateRequest / UserUpdateRequest） | users.role | ✅ |
| 14 | groupIds（UserCreateRequest/UserUpdateRequest） | ⏸ 操作 user_group_links，無 users 表欄位 | ⏸ |
| 15 | field=isEnabled（BatchUpdateFieldRequest） | users.is_enabled | ✅ |
| 16 | field=occupation（BatchUpdateFieldRequest） | users.occupation | ✅ |
| 17 | field=bio（BatchUpdateFieldRequest） | users.bio | ✅ |
| 18 | access_token（LoginResponse） | ⏸ JWT 由應用層生成，不儲存 DB | ⏸ |
| 19 | expiresAt（LoginResponse） | ⏸ JWT payload，不儲存 DB | ⏸ |
| 20 | username（UsernameCheckResponse 查詢） | users.username（UNIQUE INDEX 支援查詢） | ✅ |
| 21 | exists（UsernameCheckResponse） | ⏸ 應用層查詢結果，非 DB 欄位 | ⏸ |

---

> 注意：`users` 表為全域資源，不含 `estate_id`，不屬於多租戶隔離範圍。
> 注意：群組關聯（`groups` 陣列）由模組七的 `user_group_links` 中間表管理，模組六不重複設計。
> 注意：JWT `access_token` 及其過期時間（`expiresAt`）為應用層邏輯，不儲存於 DB；若未來需要 token 撤銷（revocation），可額外設計 `refresh_tokens` 表，但目前 API 設計不包含此需求。

---

## 模組七：群組/權限管理（Groups）

> 設計日期：2026-03-15
>
> 對應 API 資源：`/v1/groups`、`/v1/groups/{groupId}`
>
> **設計決策：`xx_group_permission` 整體廢棄**
> 舊系統 `xx_group_permission` 是 XOOPS 框架的模組功能權限機制，依賴 `gperm_modid`（xx_modules.mid）與框架耦合。新系統不使用 XOOPS 框架，存取控制由 JWT role（系統管理員 vs 一般使用者）+ `estate_member_links.member_level`（物業層級 admin/readonly）統一處理，不需要對應表格。
>
> **群組用途定位（新系統）**：群組為使用者的分類/篩選機制（如「業主」群組、「專案群組」），供物業成員分配（`GET /v1/users/available-members?groupId=xxx`）及 JWT payload 中的群組資訊（middleware 判斷 isBoss 等）使用。

---

### groups

> 說明：使用者群組定義表。每筆記錄代表一個命名的使用者分組。此表為全域資源，不綁定特定物業（無 `estate_id`）。新系統透過 API 對外只暴露 `groupType = 'Global'` 的群組，`Anonymous` 類型為系統保留群組（舊系統相容），不對外列出但 DB 需保留。對應 API 資源：`/v1/groups`

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵。對應舊系統 `groupid` smallint(5) |
| name | VARCHAR(50) | NOT NULL | — | 群組名稱（系統全域唯一）。對應舊系統 `name`。對應 API: `name` |
| description | TEXT | NULL | — | 群組說明。對應舊系統 `description`。對應 API: `description` |
| group_type | VARCHAR(20) | NOT NULL | 'Global' | 群組類型。CHECK 約束值：`Global`（一般群組，對外列出）、`Anonymous`（匿名群組，系統保留，不對外列出）。對應舊系統 `group_type` VARCHAR(10)。對應 API: `groupType`（對外僅回傳 Global） |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |
| deleted_at | TIMESTAMPTZ | NULL | — | 軟刪除時間（NULL 表示未刪除）。刪除前需確認 `user_group_links` 無關聯記錄（API 層 409 GROUP_HAS_MEMBERS 保護） |

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_groups_name (name)` -- 群組名稱全域唯一（API 409 GroupNameAlreadyExists 依據）
- `INDEX idx_groups_group_type (group_type)` -- 依類型過濾（排除 Anonymous）
- `INDEX idx_groups_deleted_at (deleted_at)` -- 軟刪除查詢

**外鍵：**
- 此表為全域資源，無對外 FK

**CHECK 約束：**
- `CHECK (group_type IN ('Global', 'Anonymous'))`

**設計說明：**

1. **保留 Anonymous 類型**：舊系統有 `group_type='Anonymous'` 的匿名群組。新系統 API 不對外列出（`GET /v1/groups` 自動排除），但 DB 保留此值以避免遷移時資料衝突，並為未來相容性預留。CHECK 約束明確限定兩種合法值。

2. **name UNIQUE 約束**：API 設計有 409 GroupNameAlreadyExists 回應，依賴 `UNIQUE INDEX` 確保資料庫層的唯一性，不只靠應用層驗證。

3. **全域資源（無 estate_id）**：群組是跨物業的使用者分組機制，同一個「業主」群組的成員可能管理不同物業，不屬於任何單一物業範圍。

4. **memberCount 為應用層計算**：API `GroupSummary.memberCount` 由應用層 `COUNT(user_group_links WHERE group_id = ?)` 計算，DB 不存冗餘計數欄位（避免計數與實際記錄不一致的維護問題）。

**舊系統對應：**
- 對應舊表：`xx_groups`
- 欄位重命名：`groupid` → `id`（BIGSERIAL 取代 smallint PK）
- 型別升級：`group_type` VARCHAR(10) → VARCHAR(20)（擴充預留空間）
- 新增欄位：`created_at`、`updated_at`、`deleted_at`（舊系統無時間欄位）
- 廢棄機制：`xx_group_permission`（XOOPS 框架模組權限表）整體廢棄，不對應任何新表格

---

### user_group_links

> 說明：使用者-群組多對多關聯中間表。每筆記錄代表一個使用者屬於一個群組的關係。此表為全域資源（無 `estate_id`），因群組本身不綁定物業。對應 API 資源：`POST /v1/users/actions/batch-add-group`、`POST /v1/users/actions/batch-remove-group`（模組六 API）；`DELETE /v1/groups/{groupId}`（群組有成員時 409 保護）

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵。對應舊系統 `linkid` mediumint(8) |
| user_id | BIGINT | NOT NULL | — | FK → users(id)。使用者 ID。對應舊系統 `uid` |
| group_id | BIGINT | NOT NULL | — | FK → groups(id)。群組 ID。對應舊系統 `groupid` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 關聯建立時間 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新時間 |

**索引：**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_user_group_links_pair (user_id, group_id)` -- 確保同一使用者不會重複加入同一群組；也是批次加入時 upsert 的衝突目標
- `INDEX idx_user_group_links_group (group_id)` -- 查詢某群組的所有成員（GroupDetail 成員清單、batch-add/remove 操作、GROUP_HAS_MEMBERS 判斷）
- `INDEX idx_user_group_links_user (user_id)` -- 查詢某使用者的所有群組（UserDetail.groups、JWT payload 群組資訊）

**外鍵：**
- `user_id` → `users(id)` ON DELETE CASCADE -- 刪除使用者時自動清除群組關聯
- `group_id` → `groups(id)` ON DELETE RESTRICT -- 刪除群組前需先確認無成員（API 層 409 保護，DB 層 RESTRICT 作為最後防線）

**設計說明：**

1. **不含 deleted_at**：群組關聯的「刪除」即為移除記錄（硬刪除），無需軟刪除。加入群組與退出群組均為明確動作，不存在「暫時停用某人在群組中的身份」的業務需求。

2. **UNIQUE (user_id, group_id)**：防止重複加入。`batch-add-group` 操作時，應用層可使用 `INSERT ... ON CONFLICT DO NOTHING`（upsert）避免重複插入報錯，保持冪等性。

3. **ON DELETE CASCADE（user_id）**：使用者刪除（軟刪除或永久刪除）時，群組關聯應同步清除。軟刪除的使用者透過 `users.deleted_at` 標記，群組關聯不需跟著軟刪除，因應用層查詢時已 JOIN `users WHERE deleted_at IS NULL`。硬刪除時 CASCADE 自動處理。

4. **ON DELETE RESTRICT（group_id）**：API 層 DELETE `/v1/groups/{groupId}` 有 409 GROUP_HAS_MEMBERS 邏輯，應用層先檢查後刪除。DB 層 RESTRICT 作為最後防線，防止直接 SQL 刪除造成孤立關聯。

5. **updated_at 欄位**：雖然關聯中間表的 `updated_at` 較少被更新（通常只有 insert/delete），但依照 Schema 設計慣例統一加入，維持架構一致性。

**舊系統對應：**
- 對應舊表：`xx_groups_users_link`
- 欄位重命名：`linkid` → `id`（BIGSERIAL）、`uid` → `user_id`、`groupid` → `group_id`
- FK 正規化：舊系統 FK 無定義，新系統明確定義 FK 並設定 ON DELETE 行為
- 新增欄位：`created_at`、`updated_at`（舊系統無時間欄位）

---

## 覆蓋率驗證（模組七）

### groups 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | groupId（GroupSummary） | groups.id | ✅ |
| 2 | name（GroupSummary） | groups.name | ✅ |
| 3 | description（GroupSummary） | groups.description | ✅ |
| 4 | groupType（GroupSummary） | groups.group_type | ✅ |
| 5 | memberCount（GroupSummary） | ⏸ 應用層 COUNT(user_group_links WHERE group_id=?)，非 DB 欄位 | ⏸ |
| 6 | members（GroupDetail，分頁 UserSummary） | ⏸ 透過 user_group_links JOIN users 查詢，非 groups 表欄位 | ⏸ |
| 7 | name（GroupCreateRequest） | groups.name（UNIQUE 唯一性保障） | ✅ |
| 8 | description（GroupCreateRequest） | groups.description | ✅ |
| 9 | name（GroupUpdateRequest） | groups.name | ✅ |
| 10 | description（GroupUpdateRequest，nullable） | groups.description（NULL 表示清空） | ✅ |
| 11 | DELETE 409 GROUP_HAS_MEMBERS | ⏸ 應用層 COUNT(user_group_links WHERE group_id=?) > 0，觸發 409；DB 層 ON DELETE RESTRICT 為最後防線 | ⏸ |
| 12 | 409 GroupNameAlreadyExists | groups.name UNIQUE INDEX | ✅ |

### user_group_links 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | userIds（BatchGroupRequest） | user_group_links.user_id（批次 INSERT） | ✅ |
| 2 | groupId（BatchGroupRequest） | user_group_links.group_id | ✅ |
| 3 | groupIds（UserCreateRequest） | user_group_links（批次 INSERT 建立關聯） | ✅ |
| 4 | groupIds（UserUpdateRequest，完整取代） | user_group_links（DELETE + INSERT 取代現有關聯） | ✅ |
| 5 | groups（UserDetail，UserGroupRef 陣列） | user_group_links JOIN groups（回傳 groupId + name） | ✅ |
| 6 | groupId（UserGroupRef） | groups.id | ✅ |
| 7 | name（UserGroupRef） | groups.name | ✅ |
| 8 | groupType=Global 過濾（GET /v1/groups） | groups.group_type WHERE group_type != 'Anonymous' | ✅ |
| 9 | name 模糊搜尋（GET /v1/groups?name=...） | groups.name（應用層 ILIKE） | ✅ |

---

> 注意：`groups` 與 `user_group_links` 均為全域資源，不含 `estate_id`，不屬於多租戶隔離範圍。
> 注意：`xx_group_permission` 整體廢棄，不對應任何新表格。新系統存取控制由 JWT role + estate_member_links.member_level 統一處理。
> 注意：群組的 `memberCount` 與 `members` 清單均由應用層查詢 `user_group_links` 計算/取得，不在 `groups` 表存冗餘計數。

---

## 模組八：檔案管理（Attachments）

> 對應 API 資源：`/v1/estates/{estateId}/rooms/{roomId}/attachments`、`/v1/estates/{estateId}/facilities/{facilityName}/attachments`、`/v1/estates/{estateId}/rents/{rentId}/attachments`、`/v1/estates/{estateId}/schedules/{scheduleId}/attachments`、`/v1/estates/{estateId}/schedules/{scheduleId}/replies/{replyId}/attachments`

---

### attachments

> 說明：通用附件 metadata 儲存表。以 `resource_type` + `resource_id` 明確關聯至各業務資源，取代舊系統的 polymorphic col_name/col_sn 設計。實體檔案儲存於 GCP Cloud Storage，本表只存 metadata 與 storage object path。對應 API 資源：上列所有附件子路徑。

| 欄位名稱 | 型別 | Nullable | 預設值 | 說明 |
|----------|------|----------|--------|------|
| id | BIGSERIAL | NOT NULL | — | 主鍵 |
| estate_id | BIGINT | NOT NULL | — | FK → estates(id)。冗餘儲存，用於多租戶隔離查詢，避免跨表 JOIN |
| resource_type | attachment_resource_type | NOT NULL | — | 附件所屬資源類型。ENUM: `room`、`facility`、`rent`、`schedule`、`schedule_reply`、`estate`。對應舊欄位：`col_name` |
| resource_id | BIGINT | NOT NULL | — | 附件所屬資源 ID。對應舊欄位：`col_sn` |
| file_name | VARCHAR(512) | NOT NULL | — | 顯示用檔案名稱（原始上傳檔名）。合併舊欄位：`file_name` + `original_filename`（新系統直接保留原始檔名）。對應 API: `fileName` |
| mime_type | VARCHAR(255) | NOT NULL | — | MIME 類型（如 image/jpeg、application/pdf）。對應舊欄位：`file_type`。對應 API: `mimeType` |
| file_size | BIGINT | NOT NULL | — | 檔案大小（bytes）。使用 BIGINT 支援大檔案（舊欄位 INT unsigned 上限 ~4GB，BIGINT 更安全）。對應 API: `fileSize` |
| storage_object_path | VARCHAR(1024) | NOT NULL | — | GCS object path（如 `estates/1/rooms/5/attachments/uuid-filename.jpg`）。取代舊欄位：`hash_filename` + `sub_dir`。下載時由後端產生 Signed URL，不直接回傳此欄位 |
| description | TEXT | NULL | — | 附件說明（選填）。對應 API: `description` |
| sort_order | INTEGER | NOT NULL | 0 | 同一資源下的附件排序值，支援拖曳排序。對應舊欄位：`sort`。對應 API: `sortOrder` |
| download_count | INTEGER | NOT NULL | 0 | 下載次數計數。對應舊欄位：`counter`。對應 API: `downloadCount` |
| tag | VARCHAR(255) | NULL | — | 額外業務標記（保留給業務邏輯使用，如標記主圖等）。對應舊欄位：`tag`。對應 API: `tag` |
| uploaded_by_user_id | BIGINT | NOT NULL | — | FK → users(id)。上傳者的系統使用者 ID。對應舊欄位：`uid`。對應 API: `uploadedBy` |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 上傳時間（等同舊欄位 `upload_date`）。對應 API: `uploadedAt` |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 最後更新時間（更新說明或排序時更新） |

**注意：本表無 `deleted_at` 軟刪除欄位。** 刪除附件時需同步刪除 GCS 物件，為確保 DB 與 GCS 一致，採用硬刪除。若需要審計紀錄，應由應用層 log 處理，不依賴軟刪除。

**ENUM 型別定義：**
```
CREATE TYPE attachment_resource_type AS ENUM (
  'room',
  'facility',
  'rent',
  'schedule',
  'schedule_reply',
  'estate'
);
```

**索引：**
- `PRIMARY KEY (id)`
- `INDEX idx_attachments_estate (estate_id)` -- 多租戶隔離
- `INDEX idx_attachments_resource (estate_id, resource_type, resource_id, sort_order)` -- 主要查詢模式：依資源取得附件清單，含排序
- `INDEX idx_attachments_uploaded_by (uploaded_by_user_id)` -- 查詢特定使用者上傳的附件
- `INDEX idx_attachments_resource_type_id (resource_type, resource_id)` -- 純資源查詢（無 estate_id 前綴，用於刪除父資源時批次清除）

**外鍵：**
- `estate_id` → `estates(id)` ON DELETE CASCADE（刪除物業時連帶刪除所有附件記錄）
- `uploaded_by_user_id` → `users(id)` ON DELETE RESTRICT（不允許刪除有上傳記錄的使用者；實際業務刪除時應先轉移或標記）

**舊系統對應：**
- 對應舊表：`xx_estate_files_center`
- Polymorphic 重構：舊欄位 `col_name`（VARCHAR，如 "estate_room_id"）+ `col_sn` → 新欄位 `resource_type`（ENUM）+ `resource_id`（BIGINT）
- ENUM 值 `'estate'`：對應舊系統 `col_name='estate_id'` 的 26 筆記錄（附件掛載於物業整體層級）。模組八決定不遷移歷史附件，此值為新系統物業層級附件功能預留，`resource_id` = `estates.id`
- 欄位合併：舊 `file_name`（顯示名）與 `original_filename`（原始上傳名）合併為單一 `file_name`（新系統直接保留原始檔名）
- 欄位重新命名：`file_type` → `mime_type`（語意更清晰）
- 欄位重新命名：`counter` → `download_count`（語意更清晰）
- Storage 路徑重構：舊欄位 `hash_filename`（加密檔名）+ `sub_dir`（子路徑）→ 新欄位 `storage_object_path`（完整 GCS object path）
- 欄位廢棄：舊 `kind` enum('img','file') → 廢棄，由 `mime_type` 判斷（image/* 前綴即為圖片）
- 型別升級：`file_size` INT unsigned → BIGINT（支援更大檔案）

---

### 覆蓋率驗證（模組八）

#### attachments 表

| # | openapi schema 欄位 | 對應 DB 欄位 | 狀態 |
|---|-------------------|------------|------|
| 1 | attachmentId（AttachmentItem） | attachments.id | ✅ |
| 2 | fileName（AttachmentItem） | attachments.file_name | ✅ |
| 3 | mimeType（AttachmentItem） | attachments.mime_type | ✅ |
| 4 | fileSize（AttachmentItem） | attachments.file_size | ✅ |
| 5 | description（AttachmentItem） | attachments.description | ✅ |
| 6 | sortOrder（AttachmentItem） | attachments.sort_order | ✅ |
| 7 | downloadCount（AttachmentItem） | attachments.download_count | ✅ |
| 8 | tag（AttachmentItem） | attachments.tag | ✅ |
| 9 | uploadedAt（AttachmentItem） | attachments.created_at | ✅ |
| 10 | uploadedBy（AttachmentItem） | attachments.uploaded_by_user_id | ✅ |
| 11 | storageObjectPath（內部，/download API 使用） | attachments.storage_object_path | ✅ |
| 12 | file（AttachmentUploadRequest，binary） | ⏸ multipart binary，不存 DB；GCS 上傳後存 storage_object_path | ⏸ |
| 13 | description（AttachmentUploadRequest） | attachments.description | ✅ |
| 14 | tag（AttachmentUploadRequest） | attachments.tag | ✅ |
| 15 | description（AttachmentUpdateRequest，nullable） | attachments.description（NULL 清空） | ✅ |
| 16 | attachmentIds（AttachmentSortRequest） | ⏸ 應用層依序更新 sort_order，不存 DB | ⏸ |
| 17 | 302 Location header（/download API） | ⏸ 應用層以 storage_object_path 產生 Signed URL，動態產生不存 DB | ⏸ |
| 18 | resource_type（路徑參數，如 rooms/rents/schedules） | attachments.resource_type（ENUM） | ✅ |
| 19 | resource_id（路徑參數，如 roomId/rentId/scheduleId） | attachments.resource_id（BIGINT） | ✅ |
| 20 | facility 資源（facilityName 路徑參數） | attachments.resource_type='facility' + resource_id=estate_facility_memos.id（應用層負責 facilityName→id 轉換） | ✅ |

---

## 模組九：Email 通知（Notification）

> 對應 API 資源：無獨立 endpoint。Email 通知為各業務操作的 side effect，不設計 CRUD 資源。
> 舊系統對應：無獨立資料表（純發送邏輯，無持久化記錄）

### 設計決策：本模組不建立任何 DB 表格

經以下三個面向評估，模組九不需要任何新的 PostgreSQL 表格。

---

#### 評估一：發送記錄（email_logs）

**結論：不建立。**

理由：
- feature-list 與 openapi 均無任何「查詢 Email 發送歷史」的業務需求與 API endpoint
- Email 通知為 fire-and-forget side effect，發送失敗不影響主業務操作的成功回應
- 觸發點僅 4 處（新增物業業主帳號開通、新增日誌、更新日誌、新增日誌回應），業務量低
- 若未來有審計需求，應由 Cloud Logging（GCP 平台記錄）或 ESP（如 SendGrid）平台提供發送歷史，不應以 DB 表格承擔平台責任

**若未來需要補入：** 可在需求明確後新增 `email_logs` 表，建議欄位為 `(id, estate_id, trigger_event, recipient_email, subject, status, error_message, sent_at)`，不影響當前其他表格設計。

---

#### 評估二：非同步 Queue（DB-backed job queue）

**結論：不建立。建議使用 Cloud Tasks。**

理由：
- feature-list 已明確建議「以 background job 或 Cloud Tasks 處理發送，避免 API 回應被 Email 服務延遲影響」
- Cloud Tasks 是 GCP 原生的任務佇列服務，提供重試機制、延遲發送、可見性超時，與 Cloud Run 架構天然整合
- DB-backed queue（如 Transactional Outbox Pattern）適用於「必須確保任務至少一次執行」的強一致性場景；本系統 Email 通知允許失敗，不符合此使用情境
- 以 DB 作為 queue 需要 polling 機制，在 Cloud Run stateless 環境中會引入額外複雜度

**建議實作方式：**
1. 業務操作完成後，應用層呼叫 Cloud Tasks API 建立任務（HTTP target 指向 Cloud Run Email worker）
2. Email worker 從任務 payload 讀取收件人清單與內容，呼叫 SMTP/ESP 發送
3. Cloud Tasks 負責重試（最多 N 次），最終失敗記錄由 Cloud Tasks 的 dead-letter queue 保留

---

#### 評估三：通知設定（使用者接收偏好）

**結論：不建立。**

理由：
- feature-list 與 openapi 均無任何通知設定相關的 API 或欄位定義
- 使用者靜音特定物業通知的功能未在任何設計文件中出現

**若未來需要補入：** 可在 `estate_member_links` 表新增 `notify_enabled BOOLEAN NOT NULL DEFAULT TRUE` 欄位擴充，不需獨立表格。這符合「通知設定是成員與物業關聯的屬性」的語意，維持低耦合設計。

---

### 觸發點彙整（應用層設計參考）

> 以下為供 Go 服務層實作的觸發規則，不涉及 DB Schema。

| 觸發操作 | 對應 API Endpoint | 收件對象 | Email 標題格式 | 非同步方式 |
|----------|------------------|----------|----------------|-----------|
| 新增物業且自動建立業主帳號 | POST /v1/estates | 業主本人（estates.owner_email） | 帳號開通通知（無前綴） | Cloud Tasks |
| 新增日誌 | POST /v1/estates/{estateId}/schedules | 物業全體成員（estate_member_links） | 「{estates.short_title}」新進度 | Cloud Tasks |
| 更新日誌 | PUT /v1/estates/{estateId}/schedules/{scheduleId} | 物業全體成員（estate_member_links） | 「{estates.short_title}」新進度 | Cloud Tasks |
| 新增日誌回應 | POST /v1/estates/{estateId}/schedules/{scheduleId}/replies | 物業全體成員（estate_member_links） | 「{estates.short_title}」回應通知 | Cloud Tasks |

**收件人查詢依據：** `estate_member_links` 表的 `estate_id` + `user_id` JOIN `users.email`，取得物業全體成員的 Email 清單。

---

### 覆蓋率驗證（模組九）

| # | feature-list 功能項目 | 對應設計 | 狀態 |
|---|----------------------|----------|------|
| 1 | 發送通知 Email 給物業全體成員（send_to_mems） | 應用層 Cloud Tasks + estate_member_links 查詢，不需 DB 表格 | ⏸ |
| 2 | 新增租約時通知相關成員 | PHP 程式碼確認無此邏輯，api-list 標注「Email 通知：無」 | ⏸ |
| 3 | 新增日誌/排程時通知相關成員 | 應用層 side effect，觸發 Cloud Tasks，不需 DB 表格 | ⏸ |
| 4 | 新增帳務記錄時通知相關成員 | PHP 程式碼確認無此邏輯，api-list 標注「Email 通知：無」 | ⏸ |

