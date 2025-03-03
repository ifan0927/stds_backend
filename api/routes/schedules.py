from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.schedules import Schedule
from schemas.schedules import ScheduleCreate, ScheduleUpdate, Schedule as ScheduleSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("/", response_model=List[ScheduleSchema])
def get_schedules(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
):
    schedules = db.query(Schedule).offset(skip).limit(limit).all()
    return schedules

@router.post("/", response_model=ScheduleSchema)
def create_schedule(
    schedule: ScheduleCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_schedule = Schedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.get("/estate-room", response_model=List[ScheduleSchema])
def get_schedules_by_estate_room(
    estate_id: Optional[int] = None, 
    room_id: Optional[int] = None, 
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    query = db.query(Schedule)
    if estate_id:
        query = query.filter(Schedule.estate_id == estate_id)
    if room_id:
        query = query.filter(Schedule.room_id == room_id)
    
    schedules = query.offset(skip).limit(limit).all()
    return schedules

@router.get("/{schedule_id}", response_model=ScheduleSchema)
def get_schedule(
    schedule_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleSchema)
def update_schedule(
    schedule_id: int, 
    schedule_update: ScheduleUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}



