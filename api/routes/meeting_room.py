from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from database import get_db
from models.meeting_room import MeetingRoom
from schemas.meeting_room import MeetingRoomCreate, MeetingRoomUpdate, MeetingRoom as MeetingRoomSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser
from typing import List

router = APIRouter(prefix="/meeting-rooms", tags=["meeting_rooms"])

@router.get("/", response_model=List[MeetingRoomSchema])
def get_meeting_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取所有可用的會議室"""
    rooms = db.query(MeetingRoom).filter(MeetingRoom.is_active == True).offset(skip).limit(limit).all()
    return rooms

@router.post("/", response_model=MeetingRoomSchema)
def create_meeting_room(
    room: MeetingRoomCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """創建新會議室（僅管理員）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create meeting rooms"
        )
    
    # 檢查會議室名稱是否已存在
    existing_room = db.query(MeetingRoom).filter(MeetingRoom.name == room.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting room name already exists"
        )
    
    db_room = MeetingRoom(**room.model_dump())
    db_room.created_by = current_user.name
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/{room_id}", response_model=MeetingRoomSchema)
def get_meeting_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取特定會議室資訊"""
    room = db.query(MeetingRoom).filter(
        MeetingRoom.id == room_id,
        MeetingRoom.is_active == True
    ).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting room not found"
        )
    return room

@router.put("/{room_id}", response_model=MeetingRoomSchema)
def update_meeting_room(
    room_id: int,
    room_update: MeetingRoomUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """更新會議室資訊（僅管理員）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update meeting rooms"
        )
    
    db_room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting room not found"
        )
    
    update_data = room_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_room, field, value)
    
    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/{room_id}")
def delete_meeting_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """軟刪除會議室（僅管理員）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete meeting rooms"
        )
    
    db_room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting room not found"
        )
    
    db_room.is_active = False
    db.commit()
    return {"message": "Meeting room deleted successfully"}