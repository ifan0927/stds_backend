from fastapi import HTTPException, UploadFile
import os
from typing import List

# 檔案類型白名單
ALLOWED_FILE_TYPES = ["image", "document", "video", "audio", "other"]

# 檔案擴展名白名單
ALLOWED_EXTENSIONS = {
    "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
    "document": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"],
    "video": ["mp4", "avi", "mov", "webm", "mkv"],
    "audio": ["mp3", "wav", "ogg", "m4a"],
    "other": []  # 可以填入其他允許的擴展名
}

# MIME 類型白名單
ALLOWED_MIME_TYPES = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"],
    "document": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "text/plain", "text/csv"],
    "video": ["video/mp4", "video/avi", "video/quicktime", "video/webm", "video/x-matroska"],
    "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4"],
    "other": []  # 可以填入其他允許的 MIME 類型
}

# 檔案大小限制（單位：MB）
MAX_FILE_SIZE = {
    "image": 10,  # 10MB
    "document": 20,  # 20MB
    "video": 100,  # 100MB
    "audio": 50,  # 50MB
    "other": 30   # 30MB
}

def validate_file_type(file_type: str) -> None:
    """驗證檔案類型是否在允許列表中"""
    if file_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file_type. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
        )

def validate_file_extension(filename: str, file_type: str) -> None:
    """驗證檔案擴展名是否在允許列表中"""
    if not filename or "." not in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    extension = filename.split(".")[-1].lower()
    
    # 如果是 "other" 類型，允許任何擴展名
    if file_type == "other":
        return
    
    if extension not in ALLOWED_EXTENSIONS[file_type]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension for {file_type}. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS[file_type])}"
        )

def validate_mime_type(content_type: str, file_type: str) -> None:
    """驗證 MIME 類型是否在允許列表中"""
    # 如果是 "other" 類型，允許任何 MIME 類型
    if file_type == "other":
        return
    
    if content_type not in ALLOWED_MIME_TYPES[file_type]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MIME type for {file_type}. Allowed MIME types: {', '.join(ALLOWED_MIME_TYPES[file_type])}"
        )

def validate_file_size(file_size: int, file_type: str) -> None:
    """驗證檔案大小是否在允許範圍內"""
    max_size_bytes = MAX_FILE_SIZE[file_type] * 1024 * 1024  # 轉換為位元組
    
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size for {file_type} is {MAX_FILE_SIZE[file_type]}MB"
        )

async def validate_file(file: UploadFile, file_type: str) -> None:
    """綜合驗證檔案"""
    # 驗證檔案類型
    validate_file_type(file_type)
    
    # 驗證檔案擴展名
    validate_file_extension(file.filename, file_type)
    
    # 驗證 MIME 類型
    validate_mime_type(file.content_type, file_type)
    
    # 讀取檔案內容來獲取大小
    content = await file.read()
    file_size = len(content)
    
    # 重置檔案讀取位置，以便後續處理能重新讀取
    await file.seek(0)
    
    # 驗證檔案大小
    validate_file_size(file_size, file_type)