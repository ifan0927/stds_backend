from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from schemas.accouting import Accounting, AccountingCreate, AccountingUpdate
import models

router = APIRouter()

# 根據物業ID獲取所有會計記錄
@router.get("/estate/{estate_id}", response_model=List[Accounting])
def get_estate_accounting(
    estate_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # 先獲取該物業的所有房間
    rooms = db.query(models.Room).filter(models.Room.estate_id == estate_id).all()
    room_ids = [room.id for room in rooms]
    
    # 獲取這些房間的所有租約
    rentals = db.query(models.Rental).filter(models.Rental.room_id.in_(room_ids)).all()
    rental_ids = [rental.id for rental in rentals]
    
    # 查詢條件
    query = db.query(models.Accounting).filter(models.Accounting.rental_id.in_(rental_ids))
    
    # 如果提供了日期範圍，則進行過濾
    if start_date:
        query = query.filter(models.Accounting.date >= start_date)
    if end_date:
        query = query.filter(models.Accounting.date <= end_date)
    
    # 排序並返回
    accounting_records = query.order_by(models.Accounting.date.asc()).all()
    
    # 為每條記錄添加房間號
    for record in accounting_records:
        if record.rental_id:
            rental = db.query(models.Rental).filter(models.Rental.id == record.rental_id).first()
            if rental:
                room = db.query(models.Room).filter(models.Room.id == rental.room_id).first()
                if room:
                    record.room_number = room.room_number
    
    return accounting_records

# 根據房間ID獲取租金記錄
@router.get("/rent-payments/room/{room_id}", response_model=List[Accounting])
def get_room_rent_payments(
    room_id: int,
    db: Session = Depends(get_db)
):
    # 首先獲取該房間的所有租約ID
    rentals = db.query(models.Rental).filter(models.Rental.room_id == room_id).all()
    rental_ids = [rental.id for rental in rentals]
    
    if not rental_ids:
        return []
    
    # 查詢租金相關記錄 (租金和押金)
    rent_payments = db.query(models.Accounting).filter(
        models.Accounting.rental_id.in_(rental_ids),
        models.Accounting.accounting_tag.in_(["租金", "押金"])
    ).order_by(models.Accounting.date.desc()).all()
    
    # 添加房間號
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if room:
        for payment in rent_payments:
            payment.room_number = room.room_number
    
    return rent_payments

# 根據租約ID獲取租金記錄
@router.get("/rent-payments/rental/{rental_id}", response_model=List[Accounting])
def get_rental_rent_payments(
    rental_id: int,
    db: Session = Depends(get_db)
):
    # 查詢租金相關記錄 (租金和押金)
    rent_payments = db.query(models.Accounting).filter(
        models.Accounting.rental_id == rental_id,
        models.Accounting.accounting_tag.in_(["租金", "押金"])
    ).order_by(models.Accounting.date.desc()).all()
    
    # 添加房間號
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if rental:
        room = db.query(models.Room).filter(models.Room.id == rental.room_id).first()
        if room:
            for payment in rent_payments:
                payment.room_number = room.room_number
    
    return rent_payments

# 根據房間ID獲取電費記錄
@router.get("/electricity-payments/room/{room_id}", response_model=List[Accounting])
def get_room_electricity_payments(
    room_id: int,
    db: Session = Depends(get_db)
):
    # 首先獲取該房間的所有租約ID
    rentals = db.query(models.Rental).filter(models.Rental.room_id == room_id).all()
    rental_ids = [rental.id for rental in rentals]
    
    if not rental_ids:
        return []
    
    # 查詢電費記錄
    electricity_payments = db.query(models.Accounting).filter(
        models.Accounting.rental_id.in_(rental_ids),
        models.Accounting.accounting_tag == "電費"
    ).order_by(models.Accounting.date.desc()).all()
    
    # 添加房間號
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if room:
        for payment in electricity_payments:
            payment.room_number = room.room_number
    
    return electricity_payments

# 根據租約ID獲取電費記錄
@router.get("/electricity-payments/rental/{rental_id}", response_model=List[Accounting])
def get_rental_electricity_payments(
    rental_id: int,
    db: Session = Depends(get_db)
):
    # 查詢電費記錄
    electricity_payments = db.query(models.Accounting).filter(
        models.Accounting.rental_id == rental_id,
        models.Accounting.accounting_tag == "電費"
    ).order_by(models.Accounting.date.desc()).all()
    
    # 添加房間號
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if rental:
        room = db.query(models.Room).filter(models.Room.id == rental.room_id).first()
        if room:
            for payment in electricity_payments:
                payment.room_number = room.room_number
    
    return electricity_payments

# 新增付款記錄
@router.post("/payments", response_model=Accounting)
def create_payment(
    payment: AccountingCreate,
    db: Session = Depends(get_db)
):
    # 檢查租約是否存在
    if payment.rental_id:
        rental = db.query(models.Rental).filter(models.Rental.id == payment.rental_id).first()
        if not rental:
            raise HTTPException(status_code=404, detail="租約不存在")
    
    # 如果提供了記錄人ID但沒有提供名稱，則獲取用戶名稱
    if payment.recorder_id and not payment.recorder_name:
        user = db.query(models.User).filter(models.User.id == payment.recorder_id).first()
        if user:
            payment.recorder_name = user.name
    
    # 創建新記錄
    db_payment = models.Accounting(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return db_payment

# 更新付款記錄
@router.put("/payments/{payment_id}", response_model=Accounting)
def update_payment(
    payment_id: int,
    payment_update: AccountingUpdate,
    db: Session = Depends(get_db)
):
    # 檢查記錄是否存在
    db_payment = db.query(models.Accounting).filter(models.Accounting.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="付款記錄不存在")
    
    # 更新記錄
    for key, value in payment_update.dict(exclude_unset=True).items():
        setattr(db_payment, key, value)
    
    db.commit()
    db.refresh(db_payment)
    
    return db_payment

# 刪除付款記錄
@router.delete("/payments/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    # 檢查記錄是否存在
    db_payment = db.query(models.Accounting).filter(models.Accounting.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="付款記錄不存在")
    
    # 刪除記錄
    db.delete(db_payment)
    db.commit()
    
    return {"detail": "付款記錄已刪除"}