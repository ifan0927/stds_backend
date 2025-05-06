from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from schemas.electric_record import ElectricRecord, ElectricRecordCreate, ElectricRecordUpdate
from schemas.accouting import AccountingCreate
import models

router = APIRouter()

# 根據房間ID獲取電表記錄
@router.get("/electric-records/room/{room_id}", response_model=List[ElectricRecord])
def get_room_electric_records(
    room_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.ElectricRecord).filter(models.ElectricRecord.room_id == room_id)
    
    if year:
        query = query.filter(models.ElectricRecord.record_year == year)
    
    if month:
        query = query.filter(models.ElectricRecord.record_month == month)
    
    records = query.order_by(
        models.ElectricRecord.record_year.desc(),
        models.ElectricRecord.record_month.desc()
    ).all()
    
    return records

# 計算電費並創建電費繳納記錄
@router.post("/electric-records/calculate-fee")
def calculate_electric_fee(
    room_id: int,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
    current_user_id: int,
    db: Session = Depends(get_db)
):
    # 1. 驗證房間存在
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房間不存在")
    
    # 2. 獲取開始和結束電表記錄
    start_record = db.query(models.ElectricRecord).filter(
        models.ElectricRecord.room_id == room_id,
        models.ElectricRecord.record_year == start_year,
        models.ElectricRecord.record_month == start_month
    ).first()
    
    end_record = db.query(models.ElectricRecord).filter(
        models.ElectricRecord.room_id == room_id,
        models.ElectricRecord.record_year == end_year,
        models.ElectricRecord.record_month == end_month
    ).first()
    
    if not start_record or not end_record:
        raise HTTPException(status_code=404, detail="無法找到指定期間的電表記錄")
    
    # 3. 計算用電量和電費
    usage = end_record.reading - start_record.reading
    
    if usage < 0:
        raise HTTPException(status_code=400, detail="電表讀數錯誤：結束讀數小於開始讀數")
    
    # 計算電費 (根據您的電費計算方式調整)
    fee = round(usage * 4.5, 2)  # 假設每度電4.5元
    
    # 4. 獲取相關租約 (假設是最新的有效租約)
    rental = db.query(models.Rental).filter(
        models.Rental.room_id == room_id,
        models.Rental.status == 1  # 假設1代表有效租約
    ).order_by(models.Rental.start_date.desc()).first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="找不到相關租約")
    
    # 5. 獲取記錄人信息
    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="找不到用戶信息")
    
    # 6. 創建電費標題
    title = f"{start_year}年{start_month}、{end_month}月電費"
    
    # 7. 組合結果數據
    result = {
        "start_reading": start_record.reading,
        "end_reading": end_record.reading,
        "usage": usage,
        "fee": fee,
        "title": title,
        "rental_id": rental.id,
        "estate_id": room.estate_id,
        "room_id": room_id,
        "room_number": room.room_number,
        "recorder_id": current_user_id,
        "recorder_name": user.name
    }
    
    return result

# 創建電費繳納記錄
@router.post("/electricity-payments")
def create_electricity_payment(
    payment: AccountingCreate,
    db: Session = Depends(get_db)
):
    # 1. 創建電費繳納記錄
    accounting_record = models.Accounting(**payment.dict())
    accounting_record.accounting_tag = "電費"  # 確保標記為電費
    
    db.add(accounting_record)
    db.commit()
    db.refresh(accounting_record)
    
    return accounting_record

# 添加電表讀數記錄
@router.post("/electric-records", response_model=ElectricRecord)
def create_electric_record(
    record: ElectricRecordCreate,
    db: Session = Depends(get_db)
):
    # 檢查房間是否存在
    room = db.query(models.Room).filter(models.Room.id == record.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房間不存在")
    
    # 檢查是否已存在相同年月的記錄
    existing_record = db.query(models.ElectricRecord).filter(
        models.ElectricRecord.room_id == record.room_id,
        models.ElectricRecord.record_year == record.record_year,
        models.ElectricRecord.record_month == record.record_month
    ).first()
    
    if existing_record:
        raise HTTPException(status_code=400, detail="該年月已有電表記錄")
    
    # 創建新記錄
    db_record = models.ElectricRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record

# 更新電表讀數記錄
@router.put("/electric-records/{record_id}", response_model=ElectricRecord)
def update_electric_record(
    record_id: int,
    record_update: ElectricRecordUpdate,
    db: Session = Depends(get_db)
):
    # 檢查記錄是否存在
    db_record = db.query(models.ElectricRecord).filter(models.ElectricRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="電表記錄不存在")
    
    # 更新記錄
    for key, value in record_update.dict(exclude_unset=True).items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    
    return db_record

# 刪除電表讀數記錄
@router.delete("/electric-records/{record_id}")
def delete_electric_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    # 檢查記錄是否存在
    db_record = db.query(models.ElectricRecord).filter(models.ElectricRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="電表記錄不存在")
    
    # 刪除記錄
    db.delete(db_record)
    db.commit()
    
    return {"detail": "電表記錄已刪除"}