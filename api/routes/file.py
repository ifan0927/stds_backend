from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.file import Files as File
from schemas.file import FileCreate, FileUpdate, FileResponse, FileUploadInfo
from utils.auth import get_current_active_user
from models.auth import AuthUser
from datetime import datetime, timezone, timedelta
from utils.cloudstorage import StorageService
import json
from utils.validators import validate_file_type, validate_file_size

router = APIRouter(prefix="/files", tags=["files"])
tz = timezone(timedelta(hours=8))
storage_service = StorageService()

# Background task to check for expired URLs and refresh them
def refresh_expired_urls(db: Session):
    """檢查並更新過期的簽名 URL"""
    now = datetime.now(tz)
    # 選取即將過期的 URL (例如：剩餘 1 天有效期)
    expiration_threshold = now + timedelta(days=1)
    
    files_to_refresh = db.query(File).filter(
        File.url_expires_at <= expiration_threshold,
        File.blob_path != None
    ).all()
    
    for file in files_to_refresh:
        try:
            signed_url, expires_at = storage_service.refresh_signed_url(file.blob_path)
            file.signed_url = signed_url
            file.url_expires_at = expires_at
        except Exception as e:
            print(f"Failed to refresh URL for file {file.id}: {e}")
    
    db.commit()

@router.get("/", response_model=List[FileResponse])
def get_files(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    ref_id: Optional[int] = None,
    file_type: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取檔案列表，支持過濾條件"""
    query = db.query(File)
    
    # 應用過濾條件
    if category:
        query = query.filter(File.category == category)
    if ref_id is not None:
        query = query.filter(File.ref_id == ref_id)
    if file_type:
        query = query.filter(File.file_type == file_type)
    
    # 排序和分頁
    files = query.order_by(File.upload_time.desc()).offset(skip).limit(limit).all()
    
    # 背景刷新即將過期的 URL
    if background_tasks:
        background_tasks.add_task(refresh_expired_urls, db)
        
    return files

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    category: str = Form(...),
    ref_id: Optional[int] = Form(None),
    file_type: str = Form(...),
    file_info: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """上傳文件到 GCP 並存儲元數據"""
    
    # 驗證檔案類型
    validate_file_type(file_type)
    
    # 在此處可以添加檔案大小、類型等驗證
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # 上傳檔案到 GCP
    upload_result = await storage_service.upload_fastapi_file(
        upload_file=file,
        category=category,
        file_type=file_type,
        uploader_id=current_user.id,
        ref_id=ref_id
    )

    if not upload_result["success"]:
        raise HTTPException(status_code=500, detail="Failed to upload file to storage")
    
    # 將 URL 有效期格式化為日期時間
    url_expires_at = datetime.fromisoformat(upload_result["url_expires_at"])
    
    # 構建文件記錄
    db_file = File(
        category=category,
        ref_id=ref_id,
        file_type=file_type,
        filename=upload_result["filename"],
        original_filename=upload_result["original_filename"],
        content_type=upload_result["content_type"],
        file_size=upload_result["file_size"],
        blob_path=upload_result["blob_path"],
        signed_url=upload_result["url"],
        url_expires_at=url_expires_at,
        file_info=file_info,
        uploader_id=current_user.id,
        upload_time=datetime.now(tz),
        last_modified=datetime.now(tz)
    )
    
    # 保存到資料庫
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file

@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: int,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取單個檔案並更新下載次數"""
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 檢查 URL 是否過期，如果過期則更新
    now = datetime.now(tz)
    if file.url_expires_at and file.url_expires_at <= now and file.blob_path:
        try:
            signed_url, expires_at = storage_service.refresh_signed_url(file.blob_path)
            file.signed_url = signed_url
            file.url_expires_at = expires_at
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to refresh file URL: {str(e)}")
    
    # 更新下載次數
    file.download_count += 1
    db.commit()
    
    return file

@router.put("/{file_id}", response_model=FileResponse)
def update_file(
    file_id: int, 
    file_update: FileUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """更新檔案元數據"""
    db_file = db.query(File).filter(File.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 安全檢查：確保只能更新自己上傳的檔案或管理員
    if db_file.uploader_id != current_user.id and not current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Permission denied: cannot modify files uploaded by other users")
    
    # 準備更新數據
    update_data = file_update.model_dump(exclude_unset=True)
    
    # 更新最後修改時間
    update_data["last_modified"] = datetime.now(tz)
    
    # 應用更新
    for field, value in update_data.items():
        setattr(db_file, field, value)
    
    db.commit()
    db.refresh(db_file)
    return db_file

@router.delete("/{file_id}")
async def delete_file(
    file_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """刪除檔案記錄和實際存儲"""
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 安全檢查：確保只能刪除自己上傳的檔案或管理員
    if file.uploader_id != current_user.id and not current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Permission denied: cannot delete files uploaded by other users")
    
    # 如果有 blob_path，從 GCP 刪除檔案
    if file.blob_path:
        try:
            storage_service.delete_file(file.blob_path)
        except Exception as e:
            # 記錄錯誤但繼續從資料庫中刪除
            print(f"Error deleting file from storage: {str(e)}")
    
    # 從資料庫中刪除檔案記錄
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted successfully"}

@router.post("/update-refs", response_model=dict)
def update_file_references(
    data: dict, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """批量更新檔案參照ID"""
    file_ids = data.get("file_ids", [])
    ref_id = data.get("ref_id")
    
    if not file_ids or ref_id is None:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    updated_count = 0
    for file_id in file_ids:
        db_file = db.query(File).filter(File.id == file_id).first()
        # 安全檢查：確保只能更新自己上傳的檔案或管理員
        if db_file and (db_file.uploader_id == current_user.id or current_user.role =="admin"):
            db_file.ref_id = ref_id
            db_file.last_modified = datetime.now(tz)
            updated_count += 1
    
    db.commit()
    return {"success": True, "updated_count": updated_count}

@router.post("/refresh-urls", response_model=dict)
def refresh_file_urls(
    data: dict,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """手動刷新檔案 URL"""
    file_ids = data.get("file_ids", [])
    
    if not file_ids:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    refreshed_count = 0
    for file_id in file_ids:
        db_file = db.query(File).filter(File.id == file_id).first()
        if db_file and db_file.blob_path:
            try:
                signed_url, expires_at = storage_service.refresh_signed_url(db_file.blob_path)
                db_file.signed_url = signed_url
                db_file.url_expires_at = expires_at
                refreshed_count += 1
            except Exception as e:
                print(f"Failed to refresh URL for file {file_id}: {e}")
    
    db.commit()
    return {"success": True, "refreshed_count": refreshed_count}