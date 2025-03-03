from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.params import Query
from typing import List
from database import get_db
from models.overtime_payment import OvertimePayment
from schemas.overtime_payment import OvertimePaymentCreate, OvertimePaymentUpdate, OvertimePayment as OvertimePaymentSchema
from utils.auth import get_current_active_user
from datetime import datetime, timezone, timedelta
from models.auth import AuthUser
import re

router = APIRouter(prefix="/overtime_payments", tags=["overtime_payments"])
tz = timezone(timedelta(hours=8))

@router.post("/", response_model=OvertimePaymentSchema)
def create_overtime_payment(
    overtime_payment: OvertimePaymentCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_overtime_payment = OvertimePayment(**overtime_payment.dict())
    db_overtime_payment.user_id = current_user.id
    db.add(db_overtime_payment)
    db.commit()
    db.refresh(db_overtime_payment)
    return db_overtime_payment

@router.get("/", response_model=List[OvertimePaymentSchema])
def read_overtime_payments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    overtime_payments = db.query(OvertimePayment).offset(skip).limit(limit).all()
    return overtime_payments

@router.get("/me", response_model=List[OvertimePaymentSchema])
def read_my_overtime_payments(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    overtime_payments = db.query(OvertimePayment).filter(OvertimePayment.user_id == current_user.id).all()
    return overtime_payments

@router.get("/approved_overtime/{user_id}", response_model=List[OvertimePaymentSchema])
def read_overtime_payments_by_user_id(
    user_id: int, 
    month: str = Query(None, description="Filter by month in format YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    if month:
        # Validate month format (YYYY-MM)
        if not re.match(r'^\d{4}-\d{2}$', month):
            raise HTTPException(status_code=400, detail="Month format should be YYYY-MM")
            
        overtime_payments = db.query(OvertimePayment).filter(
            OvertimePayment.user_id == user_id, 
            OvertimePayment.status == 'approved', 
            OvertimePayment.date.like(f"{month}%")
        ).all()
    else:
        overtime_payments = db.query(OvertimePayment).filter(
            OvertimePayment.user_id == user_id, 
            OvertimePayment.status == 'approved'
        ).all()
    return overtime_payments

@router.get("/{overtime_payment_status}", response_model=List[OvertimePaymentSchema])
def read_overtime_payments_by_status(
    overtime_payment_status: str, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    overtime_payments = db.query(OvertimePayment).filter(OvertimePayment.status == overtime_payment_status).all()
    return overtime_payments

@router.get("/{overtime_payment_id}", response_model=OvertimePaymentSchema)
def read_overtime_payment(
    overtime_payment_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    overtime_payment = db.query(OvertimePayment).filter(OvertimePayment.id == overtime_payment_id).first()
    if overtime_payment is None:
        raise HTTPException(status_code=404, detail="Overtime payment not found")

    return overtime_payment

@router.get("/users/{user_id}/overtime-payments", response_model=List[OvertimePaymentSchema])
def read_overtime_payments_by_user(
    user_id: int,
    status: str = Query(None, description="Filter by payment status"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    query = db.query(OvertimePayment).filter(OvertimePayment.user_id == user_id)
    
    if status:
        query = query.filter(OvertimePayment.status == status)
    
    overtime_payments = query.all()
    return overtime_payments

@router.put("/{overtime_payment_id}", response_model=OvertimePaymentSchema)
def update_overtime_payment(
    overtime_payment_id: int, 
    overtime_payment_update: OvertimePaymentUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_overtime_payment = db.query(OvertimePayment).filter(OvertimePayment.id == overtime_payment_id).first()
    if db_overtime_payment is None:
        raise HTTPException(status_code=404, detail="Overtime payment not found")
    
    update_data = overtime_payment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_overtime_payment, field, value)
    
    db.commit()
    db.refresh(db_overtime_payment)
    return db_overtime_payment

@router.delete("/{overtime_payment_id}")
def delete_overtime_payment(
    overtime_payment_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_overtime_payment = db.query(OvertimePayment).filter(OvertimePayment.id == overtime_payment_id).first()
    if db_overtime_payment is None:
        raise HTTPException(status_code=404, detail="Overtime payment not found")
    
    db.delete(db_overtime_payment)
    db.commit()
    return {"message": "Overtime payment deleted successfully"}

@router.patch("/{overtime_payment_id}/status/approve", response_model=OvertimePaymentSchema)
def approve_overtime_payment(
    overtime_payment_id: int, 
    overtime_payment_update: OvertimePaymentUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can approve overtime payment")
    
    db_overtime_payment = db.query(OvertimePayment).filter(OvertimePayment.id == overtime_payment_id).first()
    if db_overtime_payment is None:
        raise HTTPException(status_code=404, detail="Overtime payment not found")
    
    db_overtime_payment.status = "approved"
    db_overtime_payment.approved_by = current_user.id
    db_overtime_payment.approved_at = datetime.now(tz)
    db_overtime_payment.approved_note = overtime_payment_update.approved_note
    db.commit()
    db.refresh(db_overtime_payment)
    return db_overtime_payment

@router.patch("/{overtime_payment_id}/status/reject", response_model=OvertimePaymentSchema) 
def reject_overtime_payment(
    overtime_payment_id: int, 
    overtime_payment_update: OvertimePaymentUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can reject overtime payment")
    
    db_overtime_payment = db.query(OvertimePayment).filter(OvertimePayment.id == overtime_payment_id).first()
    if db_overtime_payment is None:
        raise HTTPException(status_code=404, detail="Overtime payment not found")
    
    db_overtime_payment.status = "rejected"
    db_overtime_payment.approved_by = current_user.id
    db_overtime_payment.approved_at = datetime.now(tz)
    db_overtime_payment.approved_note = overtime_payment_update.approved_note
    db.commit()
    db.refresh(db_overtime_payment)
    return db_overtime_payment