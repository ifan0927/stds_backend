from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone, timedelta
from database import get_db
from models.room import Room
from schemas.room import RoomCreate, RoomUpdate, Room as RoomSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/rooms", tags=["rooms"])
tz = timezone(timedelta(hours=8))

@router.get("/estate/{estate_id}", response_model=List[RoomSchema])
def get_rooms_by_estate(
    estate_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    rooms = db.query(Room).filter(Room.estate_id == estate_id, Room.deleted_at == None).all()
    return rooms

@router.post("/", response_model=RoomSchema)
def create_room(
    room: RoomCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_room = Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/{room_id}", response_model=RoomSchema)
def get_room(
    room_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    room = db.query(Room).filter(Room.id == room_id, Room.deleted_at == None).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/{room_id}", response_model=RoomSchema)
def update_room(
    room_id: int, 
    room_update: RoomUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_room = db.query(Room).filter(Room.id == room_id, Room.deleted_at == None).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    update_data = room_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_room, field, value)
    
    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/{room_id}")
def delete_room(
    room_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_room = db.query(Room).filter(Room.id == room_id, Room.deleted_at == None).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    db_room.deleted_at = datetime.now(tz)
    db.commit()
    return {"message": "Room deleted successfully"}