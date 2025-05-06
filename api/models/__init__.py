# 檔案位置: models/__init__.py
# 正確加載所有模型，解決循環引用問題

from database import Base

# 基本用戶模型
from models.auth import AuthUser  # 系統用戶
from models.users import User     # 租戶

# 基本資源模型
from models.estate import Estate  # 物業
from models.room import Room      # 房間

# 關聯模型
from models.rental import Rental  # 租約

# 交易和記錄模型
from models.accouting import Accounting        # 會計記錄
from models.electric_record import ElectricRecord  # 電表記錄

# 其他模型
from models.schedules import Schedule, ScheduleReply  # 排程和回覆
from models.entry_table import EntryTable             # 條目表
from models.file import Files                         # 檔案
from models.overtime_payment import OvertimePayment   # 加班費