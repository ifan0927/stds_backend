from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.file import File
from schemas.file import FileCreate, FileUpdate, File as FileSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/", response_model=List[FileSchema])
def get_files(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    files = db.query(File).offset(skip).limit(limit).all()
    return files

@router.post("/", response_model=FileSchema)
def create_file(
    file: FileCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_file = File(**file.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

@router.get("/{file_id}", response_model=FileSchema)
def get_file(
    file_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.put("/{file_id}", response_model=FileSchema)
def update_file(
    file_id: int, 
    file_update: FileUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_file = db.query(File).filter(File.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    update_data = file_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_file, field, value)
    
    db.commit()
    db.refresh(db_file)
    return db_file

@router.delete("/{file_id}")
def delete_file(
    file_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    db.delete(file)
    db.commit()
    return {"message": "File deleted successfully"}