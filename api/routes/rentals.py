from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.rental import Rental
from models.users import User
from models.room import Room
from models.electric_record import ElectricRecord
from models.accouting import Accounting
from schemas.users import UserCreate, User as UserSchema
from schemas.rental import RentalCreate, RentalUpdate, Rental as RentalSchema, RentalInfoDetails, RentalResponse
from models.checkout_record import CheckoutRecord
from schemas.checkout import CheckoutRequest, CheckoutResponse, CheckoutRecord as CheckoutRecordSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone, date
import logging
from dateutil.relativedelta import relativedelta
from utils.redis_config import get_cache, set_cache, delete_cache, delete_pattern
import json

router = APIRouter(prefix="/rentals", tags=["rentals"])
tz = timezone(timedelta(hours=8))


class RentalWithTenantCreate(BaseModel):
    rental: RentalCreate
    tenant: UserCreate

class RentalWithTenantSchema(BaseModel):
    rental: RentalSchema
    tenant: UserCreate

@router.get("/room/{room_id}/status/{status}", response_model=List[RentalSchema])
def get_rentals_by_room_status(
    room_id: int, 
    status: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    # 定義快取金鑰
    cache_key = f"rentals:room:{room_id}:status:{status}"
    
    # 嘗試從快取獲取資料
    cached_data = get_cache(cache_key)
    if cached_data:
        logging.info(f"Cache hit for {cache_key}")
        # 將快取的字典數據轉換為Pydantic模型
        return [RentalSchema(**item) for item in cached_data]
    
    # 快取未命中，從資料庫獲取資料
    logging.info(f"Cache miss for {cache_key}, querying database")
    status_str = "active" if status == 1 else "inactive"
    rentals = db.query(Rental).filter(Rental.room_id == room_id, Rental.status == status_str).all()
    
    # 將ORM對象轉換為可序列化字典
    serializable_rentals = []
    for rental in rentals:
        rental_dict = {c.name: getattr(rental, c.name) for c in rental.__table__.columns}
        # 處理日期/時間類型
        for key, value in rental_dict.items():
            if isinstance(value, (datetime, date)):
                rental_dict[key] = value.isoformat()
        serializable_rentals.append(rental_dict)
    
    # 存入快取（設定1小時過期）
    set_cache(cache_key, serializable_rentals, 3600)
    
    return rentals

@router.post("/", response_model=RentalWithTenantSchema)
def create_rental(
    data: RentalWithTenantCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    rental_data = data.rental.model_dump()
    rentals = db.query(Rental).filter(Rental.room_id == rental_data['room_id'], Rental.status == "active").all()
    if rentals:
        print("" + str(rental_data['room_id']) + " has active rental already , post rental fail")
        logging.error(f"{str(rental_data['room_id'])} has active rental already , post rental fail")
        raise HTTPException(status_code=400, detail=f"{str(rental_data['room_id'])} 已有成立的租約")
    db_user = User(**data.tenant.model_dump())
    db_user.created_at = datetime.now(tz)
    db.add(db_user)
    db.flush()

    tenant_id = db_user.id
    
    rental_data["user_id"] = tenant_id
    rental_data["created_at"] = datetime.now(tz)

    db_rental = Rental(**rental_data)
    db.add(db_rental)

    db.commit()

    db.refresh(db_rental)
    db.refresh(db_user)
    
    # 刪除相關的快取
    delete_pattern(f"rentals:room:{rental_data['room_id']}:*")
    
    return{
        "rental" : db_rental,
        "tenant" : db_user
    }

@router.get("/{rental_id}", response_model=RentalSchema)
def get_rental(
    rental_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental

@router.put("/{rental_id}", response_model=RentalSchema)
def update_rental(
    rental_id: int, 
    rental_update: RentalUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    update_data = rental_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rental, field, value)
    
    db.commit()
    db.refresh(db_rental)
    
    # 清除與此租約相關的所有快取
    delete_pattern(f"rentals:room:{db_rental.room_id}:*")
    delete_pattern(f"rentals:payment_info:{rental_id}")
    
    return db_rental

@router.delete("/{rental_id}")
def delete_rental(
    rental_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    room_id = db_rental.room_id  # 在刪除前保存room_id
    
    db.delete(db_rental)
    db.commit()
    
    # 清除與此租約相關的所有快取
    delete_pattern(f"rentals:room:{room_id}:*")
    delete_pattern(f"rentals:payment_info:{rental_id}")
    
    return {"message": "Rental deleted successfully"}

@router.get("/payment_info/{rental_id}", response_model=List[date])
def get_payment_info_by_rental_id(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    # 定義快取金鑰
    cache_key = f"rentals:payment_info:{rental_id}"
    
    # 嘗試從快取獲取資料
    cached_data = get_cache(cache_key)
    if cached_data:
        logging.info(f"Cache hit for {cache_key}")
        # 將快取的ISO日期格式轉回date對象
        return [date.fromisoformat(d) for d in cached_data]
    
    # 快取未命中，從資料庫獲取資料
    logging.info(f"Cache miss for {cache_key}, calculating payment dates")
    
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    response = RentalResponse.model_validate(rental, from_attributes=True)
    rental_info = response.get_rental_info_details()
    payment_freq = rental_info.money

    next_dates = []
    current_date = datetime.now().date()
    
    interval = None
    if payment_freq == "月繳":
        interval = relativedelta(months=1)
    elif payment_freq == "季繳":
        interval = relativedelta(months=3)
    elif payment_freq == "半年":
        interval = relativedelta(months=6)
    elif payment_freq == "年繳":
        interval = relativedelta(years=1)
    else:
        return []  
    
    next_payment = response.start_date
    
    while next_payment <= response.end_date:
        if next_payment >= current_date:
            next_dates.append(next_payment)
        next_payment += interval
    
    # 將日期轉換為可序列化的ISO格式字符串
    serializable_dates = [d.isoformat() for d in next_dates]
    
    # 存入快取（設定24小時過期）
    set_cache(cache_key, serializable_dates, 86400)  # 24小時 = 86400秒
    
    return next_dates


@router.post("/checkout/{rental_id}", response_model=CheckoutResponse)
def checkout_rental(
    rental_id: int,
    checkout_data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """執行退租流程"""
    
    # 1. 檢查租約是否存在且為 active 狀態
    rental = db.query(Rental).filter(
        Rental.id == rental_id,
        Rental.status == "active"
    ).first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="找不到有效的租約")
    
    # 2. 取得房間資訊
    room = db.query(Room).filter(Room.id == rental.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="找不到相關房間")
    
    try:
        # 3. 創建退租記錄
        checkout_record = CheckoutRecord(
            rental_id=rental_id,
            room_id=rental.room_id,
            checkout_reason=checkout_data.checkout_reason,
            checkout_date=checkout_data.checkout_date,
            final_electric_reading=checkout_data.final_electric_reading,
            total_settlement_amount=checkout_data.total_settlement_amount,
            notes=checkout_data.notes,
            recorder_id=current_user.id,
            recorder_name=current_user.name  # 或其他名稱欄位
        )
        db.add(checkout_record)
        db.flush()  # 取得 ID
        
        # 4. 更新租約狀態為 inactive
        rental.status = "inactive"
        rental.end_date = checkout_data.checkout_date.date()
        
        # 5. 新增最終電錶記錄
        electric_record = None
        if checkout_data.final_electric_reading and checkout_data.final_electric_reading > 0:
            checkout_month = checkout_data.checkout_date.month
            checkout_year = checkout_data.checkout_date.year
            
            electric_record = ElectricRecord(
                room_id=rental.room_id,
                reading=checkout_data.final_electric_reading,
                record_year=checkout_year,
                record_month=checkout_month,
                recorder_id=current_user.id
            )
            db.add(electric_record)
            db.flush()  # 取得 ID
        
        # 6. 新增結算會計記錄
        accounting_record = None
        if checkout_data.total_settlement_amount != 0:
            # 決定會計記錄的標題和性質
            if checkout_data.total_settlement_amount > 0:
                title = f"退租結算-收費 ({checkout_data.checkout_reason})"
            else:
                title = f"退租結算-退費 ({checkout_data.checkout_reason})"
            
            accounting_record = Accounting(
                title=title,
                income=checkout_data.total_settlement_amount,
                date=checkout_data.checkout_date,
                estate_id=room.estate_id,
                rental_id=rental_id,
                accounting_tag="退租結算",
                recorder_id=current_user.id,
                recorder_name=current_user.name  # 或其他名稱欄位
            )
            db.add(accounting_record)
            db.flush()  # 取得 ID
        
        # 7. 提交所有變更
        db.commit()
        
        # 8. 清除相關快取
        delete_pattern(f"rentals:room:{rental.room_id}:*")
        delete_pattern(f"rentals:payment_info:{rental_id}")
        
        return CheckoutResponse(
            success=True,
            message="退租完成",
            rental_id=rental_id,
            room_id=rental.room_id,
            checkout_date=checkout_data.checkout_date,
            settlement_amount=checkout_data.total_settlement_amount,
            checkout_record_id=checkout_record.id,
            electric_record_id=electric_record.id if electric_record else None,
            accounting_record_id=accounting_record.id if accounting_record else None
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"退租處理失敗: {str(e)}")

# ===== 5. 新增退租記錄查詢 API =====

@router.get("/checkout-records/room/{room_id}", response_model=List[CheckoutRecordSchema])
def get_room_checkout_records(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """取得指定房間的所有退租記錄"""
    
    checkout_records = db.query(CheckoutRecord).filter(
        CheckoutRecord.room_id == room_id
    ).order_by(CheckoutRecord.checkout_date.desc()).all()
    
    return checkout_records

@router.get("/checkout-records/rental/{rental_id}", response_model=CheckoutRecordSchema)
def get_rental_checkout_record(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """取得指定租約的退租記錄"""
    
    checkout_record = db.query(CheckoutRecord).filter(
        CheckoutRecord.rental_id == rental_id
    ).first()
    
    if not checkout_record:
        raise HTTPException(status_code=404, detail="找不到退租記錄")
    
    return checkout_record

@router.get("/checkout-records", response_model=List[CheckoutRecordSchema])
def get_all_checkout_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    room_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """取得所有退租記錄，支援日期和房間篩選"""
    
    query = db.query(CheckoutRecord)
    
    if room_id:
        query = query.filter(CheckoutRecord.room_id == room_id)
    
    if start_date:
        query = query.filter(CheckoutRecord.checkout_date >= start_date)
    
    if end_date:
        query = query.filter(CheckoutRecord.checkout_date <= end_date)
    
    checkout_records = query.order_by(CheckoutRecord.checkout_date.desc()).all()
    
    return checkout_records

# ===== 6. 修改預覽 API，加入房間資訊 =====
@router.get("/checkout-preview/{rental_id}")
def get_checkout_preview(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """取得退租前的結算預覽資訊"""
    
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="找不到租約")
    
    # 取得房間資訊
    room = db.query(Room).filter(Room.id == rental.room_id).first()
    
    # 取得最新電錶讀數
    latest_electric = db.query(ElectricRecord).filter(
        ElectricRecord.room_id == rental.room_id
    ).order_by(
        ElectricRecord.record_year.desc(),
        ElectricRecord.record_month.desc()
    ).first()
    
    # 取得押金資訊
    deposit_amount = float(rental.deposit) if rental.deposit else 0
    
    # 檢查是否已有退租記錄
    existing_checkout = db.query(CheckoutRecord).filter(
        CheckoutRecord.rental_id == rental_id
    ).first()
    
    return {
        "rental_id": rental_id,
        "room_id": rental.room_id,
        "room_number": room.room_number if room else None,
        "deposit_amount": deposit_amount,
        "latest_electric_reading": latest_electric.reading if latest_electric else None,
        "latest_electric_date": f"{latest_electric.record_year}/{latest_electric.record_month}" if latest_electric else None,
        "start_date": rental.start_date,
        "current_end_date": rental.end_date,
        "already_checked_out": existing_checkout is not None,
        "checkout_info": {
            "checkout_date": existing_checkout.checkout_date,
            "settlement_amount": existing_checkout.total_settlement_amount,
            "checkout_reason": existing_checkout.checkout_reason
        } if existing_checkout else None
    }