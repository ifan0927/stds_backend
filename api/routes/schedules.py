from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import distinct
from typing import List, Optional, Dict
from database import get_db
from datetime import datetime, timezone, timedelta
from models.schedules import Schedule
from models.auth import AuthUser
from schemas.schedules import ScheduleCreate, ScheduleUpdate, Schedule as ScheduleSchema, ScheduleWithReplies
from utils.auth import get_current_active_user

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
# 新增: 根據房間 ID 獲取日誌
@router.get("/room/{room_id}", response_model=List[ScheduleSchema])
def get_schedules_by_room(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    schedules = db.query(Schedule).filter(Schedule.room_id == room_id).order_by(
        Schedule.event_date.desc()
    ).offset(skip).limit(limit).all()
    
    # 添加用戶名到日誌
    for schedule in schedules:
        if schedule.user_id:
            user = db.query(AuthUser).filter(AuthUser.id == schedule.user_id).first()
            if user:
                schedule.user_name = user.name
    
    return schedules

# 新增: 獲取日誌和回覆
@router.get("/{schedule_id}/with-replies", response_model=ScheduleWithReplies)
def get_schedule_with_replies(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    schedule = db.query(Schedule).options(
        joinedload(Schedule.replies).joinedload(ScheduleReply.user)
    ).filter(Schedule.id == schedule_id).first()
    
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # 添加用戶名到日誌
    if schedule.user_id:
        user = db.query(AuthUser).filter(AuthUser.id == schedule.user_id).first()
        if user:
            schedule.user_name = user.name
    
    # 添加用戶名到回覆
    for reply in schedule.replies:
        if reply.user:
            reply.user_name = reply.user.name
    
    return schedule

# 修改創建日誌的端點，加入 user_id
@router.post("/", response_model=ScheduleSchema)
def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    # 如果沒有提供 user_id，使用當前用戶的 ID
    if not schedule.user_id:
        schedule.user_id = current_user.id
    
    db_schedule = Schedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    # 添加用戶名到回覆
    if db_schedule.user_id:
        user = db.query(AuthUser).filter(AuthUser.id == db_schedule.user_id).first()
        if user:
            db_schedule.user_name = user.name
    
    return db_schedule

# 修改更新日誌的端點
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
    
    # 檢查權限：只有創建者或管理員可以更新
    if db_schedule.user_id and db_schedule.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # 更新 event_date 到當前時間
    schedule_update_dict = schedule_update.model_dump(exclude_unset=True)
    schedule_update_dict["event_date"] = datetime.now(tz)
    
    for field, value in schedule_update_dict.items():
        setattr(db_schedule, field, value)
    
    db.commit()
    db.refresh(db_schedule)
    
    # 添加用戶名
    if db_schedule.user_id:
        user = db.query(AuthUser).filter(AuthUser.id == db_schedule.user_id).first()
        if user:
            db_schedule.user_name = user.name
    
    return db_schedule


# 新增: 同時獲取所有唯一的 event_type 和 status 值
@router.get("/unique-values", response_model=Dict[str, List[str]])
def get_unique_values(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    unique_event_types = db.query(distinct(Schedule.event_type)).filter(Schedule.event_type.isnot(None)).all()
    unique_statuses = db.query(distinct(Schedule.status)).filter(Schedule.status.isnot(None)).all()
    
    return {
        "event_types": [event_type[0] for event_type in unique_event_types if event_type[0]],
        "statuses": [status[0] for status in unique_statuses if status[0]]
    }

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

