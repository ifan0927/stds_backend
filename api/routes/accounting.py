from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.accouting import Accounting
from schemas.accouting import AccountingCreate, AccountingUpdate, Accounting as AccountingSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/accounting", tags=["accounting"])

@router.post("/", response_model=AccountingSchema)
def create_accounting(
    accounting: AccountingCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_accounting = Accounting(**accounting.dict())
    db.add(db_accounting)
    db.commit()
    db.refresh(db_accounting)
    return db_accounting

@router.get("/", response_model=List[AccountingSchema])
def read_accountings(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    accountings = db.query(Accounting).offset(skip).limit(limit).all()
    return accountings

@router.get("/{accounting_id}", response_model=AccountingSchema)
def read_accounting(
    accounting_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    accounting = db.query(Accounting).filter(Accounting.id == accounting_id).first()
    if accounting is None:
        raise HTTPException(status_code=404, detail="Accounting not found")
    return accounting

@router.put("/{accounting_id}", response_model=AccountingSchema)
def update_accounting(
    accounting_id: int, 
    accounting_update: AccountingUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_accounting = db.query(Accounting).filter(Accounting.id == accounting_id).first()
    if db_accounting is None:
        raise HTTPException(status_code=404, detail="Accounting not found")
    
    update_data = accounting_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_accounting, field, value)
    
    db.commit()
    db.refresh(db_accounting)
    return db_accounting

@router.delete("/{accounting_id}")
def delete_accounting(
    accounting_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_accounting = db.query(Accounting).filter(Accounting.id == accounting_id).first()
    if db_accounting is None:
        raise HTTPException(status_code=404, detail="Accounting not found")
    
    db.delete(db_accounting)
    db.commit()
    return {"message": "Accounting deleted successfully"}

@router.get("/estate/{estate_id}", response_model=List[AccountingSchema])
def read_accountings_by_estate(
    estate_id: int, 
    year: Optional[int] = None, 
    month: Optional[int] = None, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    query = db.query(Accounting).filter(Accounting.estate_id == estate_id)
    if year:
        query = query.filter(func.extract('year', Accounting.date) == year)
    if month:
        query = query.filter(func.extract('month', Accounting.date) == month)
    accountings = query.all()
    return accountings

@router.get("/rental/{rental_id}", response_model=List[AccountingSchema])
def read_accountings_by_rental( 
    rental_id: int, 
    year: Optional[int] = None, 
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    query = db.query(Accounting).filter(Accounting.rental_id == rental_id)
    if year:
        query = query.filter(func.extract('year', Accounting.date) == year)
    if month:
        query = query.filter(func.extract('month', Accounting.date) == month)
    accountings = query.all()
    return accountings

