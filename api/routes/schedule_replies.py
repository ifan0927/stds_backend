from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.schedules import ScheduleReply, Schedule
from models.auth import AuthUser
from schemas.schedule_replies import ScheduleReplyCreate, ScheduleReply as ScheduleReplySchema
from utils.auth import get_current_active_user

router = APIRouter(prefix="/schedules/replies", tags=["schedule_replies"])

@router.get("/{schedule_id}", response_model=List[ScheduleReplySchema])
def get_schedule_replies(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    # 先檢查 schedule 是否存在
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # 獲取回覆並添加用戶名
    replies = db.query(ScheduleReply).filter(ScheduleReply.schedule_id == schedule_id).all()
    
    # 添加用戶名到回覆
    for reply in replies:
        if reply.user_id:
            user = db.query(AuthUser).filter(AuthUser.id == reply.user_id).first()
            if user:
                reply.user_name = user.name
    
    return replies

@router.post("/", response_model=ScheduleReplySchema)
def create_schedule_reply(
    reply: ScheduleReplyCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    # 檢查 schedule 是否存在
    schedule = db.query(Schedule).filter(Schedule.id == reply.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # 創建回覆
    db_reply = ScheduleReply(
        schedule_id=reply.schedule_id,
        user_id=current_user.id,
        content=reply.content
    )
    
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    
    # 添加用戶名到回覆
    db_reply.user_name = current_user.name
    
    return db_reply

@router.delete("/{reply_id}")
def delete_schedule_reply(
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    reply = db.query(ScheduleReply).filter(ScheduleReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    # 檢查權限：只有回覆的創建者或管理員可以刪除
    if reply.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    db.delete(reply)
    db.commit()
    return {"message": "Reply deleted successfully"}