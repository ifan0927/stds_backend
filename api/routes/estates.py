from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.estate import Estate
from schemas.estate import EstateCreate, EstateUpdate, Estate as EstateSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/estates", tags=["estates"])

@router.get("/", response_model=List[EstateSchema])
def get_estates(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):

    estates = db.query(Estate).offset(skip).limit(limit).all()
    return estates

@router.post("/", response_model=EstateSchema)
def create_estate(
    estate: EstateCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_estate = Estate(**estate.model_dump())
    db.add(db_estate)
    db.commit()
    db.refresh(db_estate)
    return db_estate

@router.get("/{estate_id}", response_model=EstateSchema)
def get_estate(
    estate_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    estate = db.query(Estate).filter(Estate.id == estate_id).first()
    if estate is None:
        raise HTTPException(status_code=404, detail="Estate not found")
    return estate

@router.put("/{estate_id}", response_model=EstateSchema)
def update_estate(
    estate_id: int, 
    estate_update: EstateUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_estate = db.query(Estate).filter(Estate.id == estate_id).first()
    if db_estate is None:
        raise HTTPException(status_code=404, detail="Estate not found")
    
    update_data = estate_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_estate, field, value)
    
    db.commit()
    db.refresh(db_estate)
    return db_estate

@router.delete("/{estate_id}")
def delete_estate(
    estate_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_estate = db.query(Estate).filter(Estate.id == estate_id).first()
    if db_estate is None:
        raise HTTPException(status_code=404, detail="Estate not found")
    
    db.delete(db_estate)
    db.commit()
    return {"message": "Estate deleted successfully"}