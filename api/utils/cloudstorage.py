from google.cloud import storage
import os
import uuid
from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any, Optional, Tuple
from fastapi import UploadFile
import io
from dotenv import load_dotenv

load_dotenv() 

class StorageService:
    """Google Cloud Storage 服務類"""
    
    def __init__(self):
        """初始化 Storage 服務"""
        self.bucket_name = os.environ.get("GCP_BUCKET_NAME")
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        # URL 過期時間 
        self.url_expiration_days = int(os.environ.get("GCP_URL_EXPIRATION_DAYS", "7"))
        self.tz = timezone(timedelta(hours=8))  # 使用台灣時區
        
        if not self.bucket_name:
            logging.error("GCP_BUCKET_NAME environment variable is not set")
            raise ValueError("GCP_BUCKET_NAME environment variable is not set")
            
        self.client = self._get_storage_client()
    
    def _get_storage_client(self):
        """獲取 GCP Storage 客戶端"""
        try:
            creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if not creds_path:
                logging.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
                
            return storage.Client.from_service_account_json(creds_path)
        except Exception as e:
            logging.error(f"Error initializing GCP client: {e}")
            raise ValueError(f"Could not initialize GCP Storage client: {str(e)}")
    
    async def upload_fastapi_file(self, upload_file: UploadFile, 
                                  category: str, 
                                  file_type: str,
                                  uploader_id: int,
                                  ref_id: Optional[int] = None) -> Dict[str, Any]:
        """從 FastAPI UploadFile 處理上傳"""
        try:
            # 讀取檔案內容
            content = await upload_file.read()
            
            # 獲取 content_type (MIME type)
            content_type = upload_file.content_type or "application/octet-stream"
            
            # 進行實際上傳
            return self.upload_file(
                file_content=content,
                content_type=content_type,
                original_filename=upload_file.filename,
                category=category,
                file_type=file_type,
                uploader_id=uploader_id,
                ref_id=ref_id
            )
        except Exception as e:
            logging.error(f"FastAPI file upload error: {str(e)}")
            raise ValueError(f"Failed to process uploaded file: {str(e)}")
    
    def upload_file(self, file_content: bytes, content_type: str, 
                    original_filename: str, category: str, file_type: str,
                    uploader_id: int, ref_id: Optional[int] = None) -> Dict[str, Any]:
        """上傳檔案到 GCP Storage"""
        try:
            # 生成唯一檔名
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
            unique_filename = f"{uuid.uuid4().hex}-{datetime.now(self.tz).strftime('%Y%m%d%H%M%S')}"
            if file_extension:
                unique_filename = f"{unique_filename}.{file_extension}"
                
            # 設定安全的存儲路徑（根據分類和用戶隔離）
            blob_path = f"uploads/{category}/{file_type}/{uploader_id}/{unique_filename}"
            
            # 獲取存儲桶並創建 blob
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            
            # 設定檔案類型並上傳
            blob.content_type = content_type
            blob.upload_from_string(file_content, content_type=content_type)
            
            # 生成帶簽名的 URL
            url_expires_at = datetime.now(self.tz) + timedelta(days=self.url_expiration_days)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=self.url_expiration_days),
                method="GET"
            )
            
            # 返回上傳結果
            return {
                "success": True,
                "url": signed_url,  # 使用簽名 URL
                "blob_path": blob_path,
                "filename": unique_filename,
                "original_filename": original_filename,
                "content_type": content_type,
                "file_size": len(file_content),
                "file_type": file_type,
                "category": category,
                "ref_id": ref_id,
                "uploader_id": uploader_id,
                "url_expires_at": url_expires_at.isoformat()
            }
            
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            raise ValueError(f"File upload to GCP failed: {str(e)}")
    
    def refresh_signed_url(self, blob_path: str) -> Tuple[str, datetime]:
        """重新生成具有有效期的簽名 URL"""
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            
            if not blob.exists():
                raise ValueError("File not found in GCP Storage")
            
            url_expires_at = datetime.now(self.tz) + timedelta(days=self.url_expiration_days)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=self.url_expiration_days),
                method="GET"
            )
            
            return signed_url, url_expires_at
            
        except Exception as e:
            logging.error(f"Error generating URL: {str(e)}")
            raise ValueError(f"Could not generate file URL: {str(e)}")
    
    def delete_file(self, blob_path: str) -> Dict[str, Any]:
        """從 GCP Storage 刪除檔案"""
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            
            if not blob.exists():
                raise ValueError("File not found in GCP Storage")
                
            blob.delete()
            
            return {
                "success": True,
                "message": "File deleted successfully from GCP Storage"
            }
            
        except Exception as e:
            logging.error(f"Delete error: {str(e)}")
            raise ValueError(f"Failed to delete file from GCP Storage: {str(e)}")