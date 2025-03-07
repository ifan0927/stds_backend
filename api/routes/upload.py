from fastapi import APIRouter, UploadFile, Depends, HTTPException, File as FastAPIFile
from sqlalchemy.orm import Session
from typing import Optional
from utils.auth import get_current_active_user
from database import get_db
from models.auth import AuthUser
from utils.cloudstorage import StorageService
import logging

router = APIRouter(prefix="/upload", tags=["upload"])

# 全局 StorageService 實例
storage_service = StorageService()

storage_service = StorageService()

@router.post("/to-gcp/{category}", response_model=dict)
async def upload_file_to_gcp(
    category: str,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    上傳檔案到 Google Cloud Storage
    """
    try:
        # 讀取檔案內容
        file_content = await file.read()
        content_type = file.content_type
        original_filename = file.filename
        
        # 使用 StorageService 上傳檔案
        result = storage_service.upload_file(
            file_content=file_content,
            content_type=content_type,
            original_filename=original_filename,
            category=category,
        )
        
        return result
        
    except ValueError as e:
        # 處理來自 StorageService 的錯誤
        logging.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 處理其他未預期的錯誤
        logging.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during upload")

@router.get("/get-url/{blob_path:path}", response_model=dict)
async def get_file_url(
    blob_path: str,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    為已存在的檔案生成新的簽名 URL
    """
    try:
        # 安全檢查：確保用戶只能獲取自己的檔案 URL
        expected_prefix = f"uploads/{current_user.id}/"
        if not blob_path.startswith(expected_prefix) and current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this file"
            )
        
        url = storage_service.get_file_url(blob_path)
        
        return {
            "success": True,
            "url": url
        }
        
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error getting file URL: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete("/from-gcp/{blob_path:path}", response_model=dict)
async def delete_file_from_gcp(
    blob_path: str,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    從 Google Cloud Storage 刪除檔案
    """
    try:
        # 使用 StorageService 刪除檔案
        result = storage_service.delete_file(
            blob_path=blob_path,
            user_id=current_user.id
        )
        
        return result
        
    except ValueError as e:
        # 決定適當的狀態碼
        if "permission" in str(e).lower():
            status_code = 403
        elif "not found" in str(e).lower():
            status_code = 404
        else:
            status_code = 400
            
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error during file deletion: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")