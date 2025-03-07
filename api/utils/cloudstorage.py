from google.cloud import storage
import os
import uuid
from datetime import datetime, timedelta
import logging
from typing import Dict, Any

class StorageService:
    """Google Cloud Storage 服務類"""
    
    def __init__(self):
        """初始化 Storage 服務"""
        self.bucket_name = os.environ.get("GCP_BUCKET_NAME")
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        # URL 過期時間 
        self.url_expiration_days = int(os.environ.get("GCP_URL_EXPIRATION_DAYS", "7"))
        self.client = self._get_storage_client()
        
        if not self.bucket_name:
            logging.error("GCP_BUCKET_NAME environment variable is not set")
            raise ValueError("GCP_BUCKET_NAME environment variable is not set")
    
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
    
    def upload_file(self, file_content: bytes, content_type: str, 
                    original_filename: str, category: str) -> Dict[str, Any]:
        try:
            # 生成唯一檔名
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
            unique_filename = f"{uuid.uuid4().hex}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if file_extension:
                unique_filename = f"{unique_filename}.{file_extension}"
                
            # 設定安全的存儲路徑（根據用戶隔離）
            blob_path = f"uploads/{category}/{unique_filename}"
            
            # 獲取存儲桶並創建 blob
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            
            # 設定檔案類型並上傳
            blob.content_type = content_type
            blob.upload_from_string(file_content, content_type=content_type)
            
            # 生成帶簽名的 URL (較長有效期)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=self.url_expiration_days),
                method="GET",
                # 可以設定只允許特定域名的請求
                # 這會提高安全性，防止他人直接使用 URL
                # response_disposition=f"inline; filename={unique_filename}",
                # response_type=content_type
            )
            
            # 返回上傳結果
            return {
                "success": True,
                "url": signed_url,  # 使用簽名 URL
                "blob_path": blob_path,
                "filename": unique_filename,
                "original_filename": original_filename,
                "content_type": content_type,
                "size": len(file_content),
                "expires_at": (datetime.now() + timedelta(days=self.url_expiration_days)).isoformat()
            }
            
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            raise ValueError(f"File upload to GCP failed: {str(e)}")
    
    def get_file_url(self, blob_path: str) -> str:
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            
            if not blob.exists():
                raise ValueError("File not found")
                
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=self.url_expiration_days),
                method="GET"
            )
            
            return signed_url
            
        except Exception as e:
            logging.error(f"Error generating URL: {str(e)}")
            raise ValueError(f"Could not generate file URL: {str(e)}")
    
    def delete_file(self, blob_path: str, user_id: int) -> Dict[str, Any]:
        try:
                
            # 刪除檔案
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            
            if not blob.exists():
                raise ValueError("File not found")
                
            blob.delete()
            
            return {
                "success": True,
                "message": "File deleted successfully"
            }
            
        except Exception as e:
            logging.error(f"Delete error: {str(e)}")
            raise ValueError(f"Failed to delete file: {str(e)}")