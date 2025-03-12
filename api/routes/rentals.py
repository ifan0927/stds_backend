from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.rental import Rental
from models.users import User
from models.accouting import Accounting
from schemas.users import UserCreate, User as UserSchema
from schemas.rental import RentalCreate, RentalUpdate, Rental as RentalSchema, RentalInfoDetails, RentalResponse
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