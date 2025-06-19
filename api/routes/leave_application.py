from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from fastapi.params import Query
from typing import List
from database import get_db
from models.leave_application import LeaveApplication, LeaveType
from schemas.leave_application import (
    LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplication as LeaveApplicationSchema,
    LeaveTypeCreate, LeaveTypeUpdate, LeaveType as LeaveTypeSchema
)
from utils.auth import get_current_active_user
from datetime import datetime, timezone, timedelta
from models.auth import AuthUser
import re

router = APIRouter(prefix="/leave_applications", tags=["leave_applications"])
leave_type_router = APIRouter(prefix="/leave_types", tags=["leave_types"])
tz = timezone(timedelta(hours=8))

# ==================== 假別管理 ====================
@leave_type_router.post("/", response_model=LeaveTypeSchema)
def create_leave_type(
    leave_type: LeaveTypeCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """創建新的假別類型（僅管理員可用）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create leave types")
    
    # 檢查假別名稱是否已存在
    existing_type = db.query(LeaveType).filter(LeaveType.name == leave_type.name).first()
    if existing_type:
        raise HTTPException(status_code=400, detail="Leave type name already exists")
    
    db_leave_type = LeaveType(**leave_type.dict())
    db.add(db_leave_type)
    db.commit()
    db.refresh(db_leave_type)
    return db_leave_type

@leave_type_router.get("/", response_model=List[LeaveTypeSchema])
def read_leave_types(
    include_inactive: bool = Query(False, description="Include inactive leave types"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取所有假別類型"""
    query = db.query(LeaveType)
    if not include_inactive:
        query = query.filter(LeaveType.is_active == True)
    
    leave_types = query.all()
    return leave_types

@leave_type_router.put("/{leave_type_id}", response_model=LeaveTypeSchema)
def update_leave_type(
    leave_type_id: int,
    leave_type_update: LeaveTypeUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """更新假別類型（僅管理員可用）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update leave types")
    
    db_leave_type = db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()
    if db_leave_type is None:
        raise HTTPException(status_code=404, detail="Leave type not found")
    
    update_data = leave_type_update.dict(exclude_unset=True)
    
    # 檢查名稱是否重複
    if 'name' in update_data:
        existing_type = db.query(LeaveType).filter(
            LeaveType.name == update_data['name'],
            LeaveType.id != leave_type_id
        ).first()
        if existing_type:
            raise HTTPException(status_code=400, detail="Leave type name already exists")
    
    for field, value in update_data.items():
        setattr(db_leave_type, field, value)
    
    db.commit()
    db.refresh(db_leave_type)
    return db_leave_type

# ==================== 請假申請管理 ====================
@router.post("/", response_model=LeaveApplicationSchema)
def create_leave_application(
    leave_application: LeaveApplicationCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """創建請假申請"""
    # 驗證假別是否存在且啟用
    leave_type = db.query(LeaveType).filter(
        LeaveType.id == leave_application.leave_type_id,
        LeaveType.is_active == True
    ).first()
    if not leave_type:
        raise HTTPException(status_code=400, detail="Invalid or inactive leave type")
    
    db_leave_application = LeaveApplication(**leave_application.dict())
    db_leave_application.user_id = current_user.id
    db.add(db_leave_application)
    db.commit()
    db.refresh(db_leave_application)
    return db_leave_application

@router.get("/", response_model=List[LeaveApplicationSchema])
def read_leave_applications(
    skip: int = 0,
    limit: int = 100,
    status: str = Query(None, description="Filter by status"),
    leave_type_id: int = Query(None, description="Filter by leave type"),
    start_date: str = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取所有請假申請（管理員）或自己的申請"""
    query = db.query(LeaveApplication)
    
    # 非管理員只能看自己的申請
    if current_user.role != "admin":
        query = query.filter(LeaveApplication.user_id == current_user.id)
    
    # 狀態過濾
    if status:
        query = query.filter(LeaveApplication.status == status)
    
    # 假別過濾
    if leave_type_id:
        query = query.filter(LeaveApplication.leave_type_id == leave_type_id)
    
    # 日期範圍過濾
    if start_date:
        query = query.filter(LeaveApplication.start_date >= start_date)
    if end_date:
        query = query.filter(LeaveApplication.end_date <= end_date)
    
    leave_applications = query.offset(skip).limit(limit).all()
    return leave_applications

@router.get("/me", response_model=List[LeaveApplicationSchema])
def read_my_leave_applications(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取我的請假申請"""
    leave_applications = db.query(LeaveApplication).filter(
        LeaveApplication.user_id == current_user.id
    ).all()
    return leave_applications

@router.get("/approved_leaves/{user_id}", response_model=List[LeaveApplicationSchema])
def read_approved_leave_applications_by_user_id(
    user_id: int,
    month: str = Query(None, description="Filter by month in format YYYY-MM"),
    leave_type_id: int = Query(None, description="Filter by leave type"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """根據用戶ID獲取已批准的請假申請"""
    query = db.query(LeaveApplication).filter(
        LeaveApplication.user_id == user_id,
        LeaveApplication.status == 'approved'
    )
    
    if month:
        # 驗證月份格式 (YYYY-MM)
        if not re.match(r'^\d{4}-\d{2}$', month):
            raise HTTPException(status_code=400, detail="Month format should be YYYY-MM")
        query = query.filter(LeaveApplication.start_date.like(f"{month}%"))
    
    if leave_type_id:
        query = query.filter(LeaveApplication.leave_type_id == leave_type_id)
    
    leave_applications = query.all()
    return leave_applications

@router.get("/users/{user_id}/leave-applications", response_model=List[LeaveApplicationSchema])
def read_leave_applications_by_user(
    user_id: int,
    status: str = Query(None, description="Filter by application status"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """根據用戶ID獲取請假申請"""
    query = db.query(LeaveApplication).filter(LeaveApplication.user_id == user_id)
    
    if status:
        query = query.filter(LeaveApplication.status == status)
    
    leave_applications = query.all()
    return leave_applications

@router.get("/{status}", response_model=List[LeaveApplicationSchema])
def read_leave_applications_by_status(
    status: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """根據狀態獲取請假申請"""
    leave_applications = db.query(LeaveApplication).filter(
        LeaveApplication.status == status
    ).all()
    return leave_applications

@router.get("/{leave_application_id}", response_model=LeaveApplicationSchema)
def read_leave_application(
    leave_application_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取特定請假申請"""
    leave_application = db.query(LeaveApplication).filter(
        LeaveApplication.id == leave_application_id
    ).first()
    if leave_application is None:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    # 非管理員只能查看自己的申請
    if current_user.role != "admin" and leave_application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return leave_application

@router.put("/{leave_application_id}", response_model=LeaveApplicationSchema)
def update_leave_application(
    leave_application_id: int,
    leave_application_update: LeaveApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """更新請假申請"""
    db_leave_application = db.query(LeaveApplication).filter(
        LeaveApplication.id == leave_application_id
    ).first()
    if db_leave_application is None:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    # 只有申請人或管理員可以更新
    if current_user.role != "admin" and db_leave_application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 已批准或已拒絕的申請不能修改
    if db_leave_application.status in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Cannot update approved or rejected application")
    
    update_data = leave_application_update.dict(exclude_unset=True)
    
    # 驗證假別
    if 'leave_type_id' in update_data:
        leave_type = db.query(LeaveType).filter(
            LeaveType.id == update_data['leave_type_id'],
            LeaveType.is_active == True
        ).first()
        if not leave_type:
            raise HTTPException(status_code=400, detail="Invalid or inactive leave type")
    
    for field, value in update_data.items():
        setattr(db_leave_application, field, value)
    
    db.commit()
    db.refresh(db_leave_application)
    return db_leave_application

@router.delete("/{leave_application_id}")
def delete_leave_application(
    leave_application_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """刪除請假申請"""
    db_leave_application = db.query(LeaveApplication).filter(
        LeaveApplication.id == leave_application_id
    ).first()
    if db_leave_application is None:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    # 只有申請人或管理員可以刪除
    if current_user.role != "admin" and db_leave_application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 已批准的申請不能刪除
    if db_leave_application.status == "approved":
        raise HTTPException(status_code=400, detail="Cannot delete approved application")
    
    db.delete(db_leave_application)
    db.commit()
    return {"message": "Leave application deleted successfully"}

@router.patch("/{leave_application_id}/status/approve", response_model=LeaveApplicationSchema)
def approve_leave_application(
    leave_application_id: int,
    leave_application_update: LeaveApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """批准請假申請"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can approve leave application")
    
    db_leave_application = db.query(LeaveApplication).filter(
        LeaveApplication.id == leave_application_id
    ).first()
    if db_leave_application is None:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    db_leave_application.status = "approved"
    db_leave_application.approved_by = current_user.id
    db_leave_application.approved_at = datetime.now(tz)
    if leave_application_update.approved_note:
        db_leave_application.approved_note = leave_application_update.approved_note
    
    db.commit()
    db.refresh(db_leave_application)
    return db_leave_application

@router.patch("/{leave_application_id}/status/reject", response_model=LeaveApplicationSchema)
def reject_leave_application(
    leave_application_id: int,
    leave_application_update: LeaveApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """拒絕請假申請"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can reject leave application")
    
    db_leave_application = db.query(LeaveApplication).filter(
        LeaveApplication.id == leave_application_id
    ).first()
    if db_leave_application is None:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    db_leave_application.status = "rejected"
    db_leave_application.approved_by = current_user.id
    db_leave_application.approved_at = datetime.now(tz)
    if leave_application_update.approved_note:
        db_leave_application.approved_note = leave_application_update.approved_note
    
    db.commit()
    db.refresh(db_leave_application)
    return db_leave_application