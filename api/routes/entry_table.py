from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from database import get_db
from models.entry_table import EntryTable
from schemas.entry_table import EntryTableCreate, EntryTableUpdate, EntryTable as EntryTableSchema
from utils.auth import get_current_active_user
from utils.bot import linebot
from models.auth import AuthUser
from dotenv import load_dotenv
from typing import List
import os 

load_dotenv()
router = APIRouter(prefix="/entry_table", tags=["entry_table"])
tz = timezone(timedelta(hours=8))
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")

@router.get("/", response_model=List[EntryTableSchema])
def get_entries(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    entries = db.query(EntryTable).offset(skip).limit(limit).all()
    return entries

@router.post("/", response_model=EntryTableSchema)
def create_entry(
    entry: EntryTableCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    if entry.type == "system":
        bot = linebot(LINE_GROUP_ID)
        bot.add_message('text', '系統更新通知:網頁功能更新')
        bot.add_message('text', entry.content)  
        bot.send_line_message()    
    db_entry = EntryTable(**entry.model_dump())
    db_entry.created_by = current_user.name
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/{entry_id}", response_model=EntryTableSchema)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    entry = db.query(EntryTable).filter(EntryTable.id == entry_id).first()   

    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.put("/{entry_id}", response_model=EntryTableSchema)
def update_entry(
    entry_id: int,
    entry_update: EntryTableUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_entry = db.query(EntryTable).filter(EntryTable.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entry, field, value)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

