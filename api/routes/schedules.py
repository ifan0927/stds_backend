from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional, Dict
from database import get_db
from datetime import datetime, timezone , timedelta
from models.schedules import Schedule
from schemas.schedules import ScheduleCreate, ScheduleUpdate, Schedule as ScheduleSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/schedules", tags=["schedules"])
tz = timezone(timedelta(hours=8))

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
    
    schedules = query.order_by(Schedule.event_date.desc()).offset(skip).limit(limit).all()
    return schedules

@router.get("/counts", response_model=Dict[str, int])
def get_schedules_counts(
    estate_id: Optional[int] = None, 
    room_id: Optional[int] = None, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    query = db.query(Schedule)
    if estate_id:
        query = query.filter(Schedule.estate_id == estate_id)
    if room_id:
        query = query.filter(Schedule.room_id == room_id)
    
    schedules_count = query.count()
    return {
        "count": schedules_count
    }

# 新增: 取得所有唯一的 event_type 值
@router.get("/event-types", response_model=List[str])
def get_unique_event_types(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    unique_event_types = db.query(distinct(Schedule.event_type)).filter(Schedule.event_type.isnot(None)).all()
    # 將查詢結果轉換為單一列表
    return [event_type[0] for event_type in unique_event_types]

# 新增: 取得所有唯一的 status 值
@router.get("/statuses", response_model=List[str])
def get_unique_statuses(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    unique_statuses = db.query(distinct(Schedule.status)).filter(Schedule.status.isnot(None)).all()
    # 將查詢結果轉換為單一列表
    return [status[0] for status in unique_statuses]

# 新增: 同時獲取所有唯一的 event_type 和 status 值
@router.get("/unique-values", response_model=Dict[str, List[str]])
def get_unique_values(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    unique_event_types = db.query(distinct(Schedule.event_type)).filter(Schedule.event_type.isnot(None)).all()
    unique_statuses = db.query(distinct(Schedule.status)).filter(Schedule.status.isnot(None)).all()
    
    return {
        "event_types": [event_type[0] for event_type in unique_event_types],
        "statuses": [status[0] for status in unique_statuses]
    }


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
    
    schedule_update.event_date = datetime.now(tz)
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



