from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timezone, timedelta, date
from database import get_db
from models.meeting_room import MeetingRoom
from models.meeting_reservation import MeetingReservation
from schemas.meeting_reservation import (
    MeetingReservationCreate, 
    MeetingReservationUpdate, 
    MeetingReservationResponse,
    MeetingReservationSimple
)
from utils.auth import get_current_active_user
from models.auth import AuthUser
from typing import List, Optional

router = APIRouter(prefix="/meeting_reservations", tags=["meeting_reservations"])

def check_time_conflict(db: Session, room_id: int, start_time: datetime, end_time: datetime, exclude_id: Optional[int] = None):
    """檢查時間衝突"""
    query = db.query(MeetingReservation).filter(
        MeetingReservation.room_id == room_id,
        MeetingReservation.is_active == True,
        or_(
            # 新預約的開始時間在現有預約範圍內
            and_(MeetingReservation.start_time < start_time, MeetingReservation.end_time > start_time),
            # 新預約的結束時間在現有預約範圍內
            and_(MeetingReservation.start_time < end_time, MeetingReservation.end_time > end_time),
            # 新預約完全包含現有預約
            and_(MeetingReservation.start_time >= start_time, MeetingReservation.end_time <= end_time),
            # 現有預約完全包含新預約
            and_(MeetingReservation.start_time <= start_time, MeetingReservation.end_time >= end_time)
        )
    )
    
    # 如果是更新操作，排除當前記錄
    if exclude_id:
        query = query.filter(MeetingReservation.id != exclude_id)
    
    return query.first()

@router.get("/", response_model=List[MeetingReservationResponse])
def get_reservations(
    start_date: Optional[date] = Query(None, description="開始日期篩選 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="結束日期篩選 (YYYY-MM-DD)"),
    room_id: Optional[int] = Query(None, description="會議室ID篩選"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取預約列表，支援日期範圍和會議室篩選"""
    query = db.query(MeetingReservation).filter(MeetingReservation.is_active == True)
    
    # 日期範圍篩選
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(MeetingReservation.start_time >= start_datetime)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(MeetingReservation.end_time <= end_datetime)
    
    # 會議室篩選
    if room_id:
        query = query.filter(MeetingReservation.room_id == room_id)
    
    reservations = query.offset(skip).limit(limit).all()
    return reservations

@router.post("/", response_model=MeetingReservationResponse)
def create_reservation(
    reservation: MeetingReservationCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """創建新預約"""
    # 檢查會議室是否存在且可用
    room = db.query(MeetingRoom).filter(
        MeetingRoom.id == reservation.room_id,
        MeetingRoom.is_active == True
    ).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting room not found or inactive"
        )
    
    # 檢查時間衝突
    conflict = check_time_conflict(
        db, reservation.room_id, reservation.start_time, reservation.end_time
    )
    
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"時間衝突：會議室在 {conflict.start_time} 到 {conflict.end_time} 已被預約"
        )
    
    # 創建預約
    db_reservation = MeetingReservation(**reservation.model_dump())
    db_reservation.created_by_id = current_user.id
    db_reservation.created_by_name = current_user.name
    
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.get("/{reservation_id}", response_model=MeetingReservationResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取特定預約詳情"""
    reservation = db.query(MeetingReservation).filter(
        MeetingReservation.id == reservation_id,
        MeetingReservation.is_active == True
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    return reservation

@router.put("/{reservation_id}", response_model=MeetingReservationResponse)
def update_reservation(
    reservation_id: int,
    reservation_update: MeetingReservationUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """更新預約（僅預約人或管理員）"""
    db_reservation = db.query(MeetingReservation).filter(
        MeetingReservation.id == reservation_id,
        MeetingReservation.is_active == True
    ).first()
    
    if not db_reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    # 權限檢查：只有預約人或管理員可以修改
    if current_user.role != "admin" and db_reservation.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reservation"
        )
    
    update_data = reservation_update.model_dump(exclude_unset=True)
    
    # 如果更新時間，需要檢查衝突
    if 'start_time' in update_data or 'end_time' in update_data:
        new_start = update_data.get('start_time', db_reservation.start_time)
        new_end = update_data.get('end_time', db_reservation.end_time)
        
        # 驗證結束時間晚於開始時間
        if new_end <= new_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="結束時間必須晚於開始時間"
            )
        
        # 檢查時間衝突（排除當前預約）
        conflict = check_time_conflict(
            db, db_reservation.room_id, new_start, new_end, exclude_id=reservation_id
        )
        
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"時間衝突：會議室在 {conflict.start_time} 到 {conflict.end_time} 已被預約"
            )
    
    # 更新資料
    for field, value in update_data.items():
        setattr(db_reservation, field, value)
    
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.delete("/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """取消預約（僅預約人或管理員）"""
    db_reservation = db.query(MeetingReservation).filter(
        MeetingReservation.id == reservation_id,
        MeetingReservation.is_active == True
    ).first()
    
    if not db_reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    # 權限檢查：只有預約人或管理員可以取消
    if current_user.role != "admin" and db_reservation.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this reservation"
        )
    
    # 軟刪除
    db_reservation.is_active = False
    db.commit()
    return {"message": "Reservation cancelled successfully"}

@router.get("/my/reservations", response_model=List[MeetingReservationSimple])
def get_my_reservations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取當前用戶的預約列表"""
    reservations = db.query(MeetingReservation).filter(
        MeetingReservation.created_by_id == current_user.id,
        MeetingReservation.is_active == True
    ).offset(skip).limit(limit).all()
    
    return reservations