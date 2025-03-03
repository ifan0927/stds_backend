from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.electric_record import ElectricRecord
from schemas.electric_record import ElectricRecordCreate, ElectricRecordUpdate, ElectricRecord as ElectricRecordSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/electric_records", tags=["electric_records"])
tz = timezone(timedelta(hours=8))


@router.get("/search", response_model=List[ElectricRecordSchema])
def search_electric_records(
    room_id: int, 
    record_year: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    records = db.query(ElectricRecord).filter(ElectricRecord.room_id == room_id).filter(ElectricRecord.record_year == record_year).all()
    return records

@router.get("/", response_model=List[ElectricRecordSchema])
def get_electric_records(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    records = db.query(ElectricRecord).offset(skip).limit(limit).all()
    return records

@router.post("/", response_model=ElectricRecordSchema)
def create_electric_record(
    record: ElectricRecordCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_record = ElectricRecord(
        **record.model_dump(),
        updated_at=datetime.utcnow()  # 明確設置時間戳
    )
    db_record.recorder_id = current_user.id
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/{record_id}", response_model=ElectricRecordSchema)
def get_electric_record(
    record_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    record = db.query(ElectricRecord).filter(ElectricRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Electric record not found")
    return record

@router.put("/{record_id}", response_model=ElectricRecordSchema)
def update_electric_record(
    record_id: int, 
    record_update: ElectricRecordUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_record = db.query(ElectricRecord).filter(ElectricRecord.id == record_id).first()
    if db_record is None:
        raise HTTPException(status_code=404, detail="Electric record not found")
    
    update_data = record_update.model_dump(exclude_unset=True)
    db_record.recorder_id = current_user.id
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db_record.updated_at = datetime.now()  # 更新時間戳
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{record_id}")
def delete_electric_record(
    record_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    record = db.query(ElectricRecord).filter(ElectricRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Electric record not found")
    
    db.delete(record)
    db.commit()
    return {"message": "Electric record deleted successfully"}