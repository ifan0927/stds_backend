# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timezone,timedelta
from typing import List
from database import get_db
from models.auth import AuthUser
from schemas.auth import AuthUserCreate, AuthUserUpdate, Token, TokenRefresh, AuthUser as AuthUserSchema
from utils.auth import (
    SECRET_KEY,
    ALGORITHM,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

tz = timezone(timedelta(hours=8))
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthUserSchema)
def register_user(
    user: AuthUserCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    # 只有管理員可以創建新用戶
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can register new users"
        )

    # 檢查郵箱是否已存在
    if db.query(AuthUser).filter(AuthUser.email == user.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # 創建新用戶
    db_user = AuthUser(
        email=user.email,
        password_hash=get_password_hash(user.password),
        name=user.name,
        nickname=user.nickname,
        group=user.group,
        job_title=user.job_title,
        role=user.role,
        hire_date=user.hire_date,
        leave_date=user.leave_date,
        id_number=user.id_number,
        birthday=user.birthday,
        phone=user.phone,
        address=user.address,
        notes=user.notes
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(AuthUser).filter(AuthUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    

    user.last_login = datetime.now(tz)
    db.commit()
    

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "name": user.name,
            "id" : user.id 
        }, 
        expires_delta=access_token_expires
    )
    

    refresh_token = create_refresh_token(
        data={
            "sub": user.email,
            "user_id": user.id
        }
    )
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/users", response_model=List[AuthUserSchema])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 只有管理員可以查看用戶列表
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can view user list"
        )
    users = db.query(AuthUser).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=AuthUserSchema)
def get_user(
    user_id: int,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 管理員可以查看任何用戶，普通用戶只能查看自己
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information"
        )
    
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/me", response_model=AuthUserSchema)
def read_current_user(current_user: AuthUser = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=AuthUserSchema)
def update_user_info(
    user_update: AuthUserUpdate,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 允許用戶更新自己的部分信息
    
    # 如果提供了密碼則更新
    if user_update.password:
        current_user.password_hash = get_password_hash(user_update.password)
    
    # 普通用戶可以更新的基本信息
    updatable_fields = [
        "nickname", "phone", "email", "address"
    ]
    
    # 管理員可以更新的所有字段
    admin_fields = [
        "name", "group", "job_title", "role", "hire_date", "leave_date", 
        "id_number", "birthday", "notes", "is_active"
    ]
    
    # 更新基本信息
    for field in updatable_fields:
        value = getattr(user_update, field)
        if value is not None:
            setattr(current_user, field, value)
    
    # 如果是管理員，還可以更新以下字段
    if current_user.role == "admin":
        for field in admin_fields:
            value = getattr(user_update, field)
            if value is not None:
                setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/users/{user_id}", response_model=AuthUserSchema)
def update_user(
    user_id: int,
    user_update: AuthUserUpdate,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 只有管理員可以更新其他用戶
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update other users"
        )
    
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 如果提供了密碼則更新
    if user_update.password:
        user.password_hash = get_password_hash(user_update.password)
    
    # 更新所有可更新字段
    update_fields = [
        "name", "nickname", "group", "job_title", "role", "hire_date", 
        "leave_date", "email", "id_number", "birthday", "phone", 
        "address", "notes", "is_active"
    ]
    
    for field in update_fields:
        value = getattr(user_update, field)
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 只有管理員可以刪除用戶
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete users"
        )
    
    # 不能刪除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/refresh", response_model=Token)
def refresh_access_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码并验证刷新令牌
        payload = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("token_type")
        
        # 确保是刷新令牌类型
        if email is None or token_type != "refresh":
            raise credentials_exception
            
        # 查找用户
        user = db.query(AuthUser).filter(AuthUser.email == email).first()
        if user is None or not user.is_active:
            raise credentials_exception
            
        # 生成新的访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.email,
                "role": user.role,
                "name": user.name
            }, 
            expires_delta=access_token_expires
        )
        
        # 可选：生成新的刷新令牌（轮换刷新令牌以提高安全性）
        refresh_token = create_refresh_token(
            data={
                "sub": user.email,
                "user_id": user.id
            }
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise credentials_exception
    
    ## 尋找用戶根據role
    @router.get("/users/role/{role}", response_model=List[AuthUserSchema])
    def get_users_by_role(
        role: str,
        current_user: AuthUser = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):      
    # 只有管理員可以查看特定角色的用戶  
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can view users by role"
            )
        
        users = db.query(AuthUser).filter(AuthUser.role == role).all()
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No users found with role {role}"
            )
        
        return users