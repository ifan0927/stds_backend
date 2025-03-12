from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.sop.sop_articles import SopArticles
from models.sop.sop_categories import SopCategories
from schemas.sop.sop_articles import SopArticlesCreate, SopArticlesUpdate, SopArticles as SopArticleSchema
from schemas.sop.sop_categories import SopCategoriesCreate, SopCategoriesUpdate, SopCategories as SopCategoriesSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/sops", tags=["sops"])

@router.get("/sop_articles", response_model=List[SopArticleSchema])
def get_sop_articles(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    articles = db.query(SopArticles).offset(skip).limit(limit).all()
    return articles

@router.post("/sop_articles", response_model=SopArticleSchema)
def create_sop_article(
    sop_article: SopArticlesCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):                                                            
    db_sop_article = SopArticles(**sop_article.model_dump())
    db_sop_article.created_by = current_user.id
    db.add(db_sop_article)
    db.commit()
    db.refresh(db_sop_article)
    return db_sop_article

@router.get("/sop_articles/{sop_article_id}", response_model=SopArticleSchema)
def get_sop_article(
    sop_article_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    sop_article = db.query(SopArticles).filter(SopArticles.id == sop_article_id).first()
    if sop_article is None:
        raise HTTPException(status_code=404, detail="Sop_article not found")
    return sop_article

@router.get("/sop_articles/category/{sop_category_id}", response_model=List[SopArticleSchema])
def get_sop_articles_by_category(
    sop_category_id : int ,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    articles = db.query(SopArticles).filter(SopArticles.category_id == sop_category_id).offset(skip).limit(limit).all()
    return articles

@router.put("/sop_articles/{sop_article_id}", response_model=SopArticleSchema)
def update_sop_article(
    sop_article_id: int, 
    sop_article_update: SopArticlesUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    sop_article = db.query(SopArticles).filter(SopArticles.id == sop_article_id).first()
    if sop_article is None:
        raise HTTPException(status_code=404, detail="Sop_article not found")
    
    sop_article_update.created_by = current_user.id
    update_data = sop_article_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(sop_article, field, value)

    db.commit()
    db.refresh(sop_article)
    return sop_article

@router.delete("/sop_articles/{sop_article_id}")
def delete_sop_article(
    sop_article_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    sop_article = db.query(SopArticles).filter(SopArticles.id == sop_article_id).first()
    if sop_article is None:
        raise HTTPException(status_code=404, detail="Sop_article not found")
    
    db.delete(sop_article)
    db.commit()
    return {"message": "Sop_article deleted successfully"}

@router.get("/sop_categories", response_model=List[SopCategoriesSchema])
def get_sop_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    sop_categories = db.query(SopCategories).offset(skip).limit(limit).all()
    return sop_categories

@router.post("/sop_categories", response_model=SopCategoriesSchema)
def create_sop_category(
    sop_category: SopCategoriesCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_sop_category = SopCategories(**sop_category.model_dump())
    db.add(db_sop_category)
    db.commit()
    db.refresh(db_sop_category)
    return db_sop_category

@router.get("/sop_categories/{sop_category_id}", response_model=SopCategoriesSchema)
def get_sop_category(
    sop_category_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    sop_category = db.query(SopCategories).filter(SopCategories.id == sop_category_id).first()
    if sop_category is None:
        raise HTTPException(status_code=404, detail="sop_category not found")
    return sop_category

@router.put("/sop_categories/{sop_category_id}", response_model=SopCategoriesSchema)
def update_sop_category(
    sop_category_id: int, 
    sop_category_update: SopCategoriesUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    sop_category = db.query(SopCategories).filter(SopCategories.id == sop_category_id).first()
    if sop_category is None:
        raise HTTPException(status_code=404, detail="sop_categorie not found")
    
    update_data = sop_category_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(sop_category, field, value)

    db.commit()
    db.refresh(sop_category)
    return sop_category

@router.delete("/sop_categories/{sop_category_id}")
def delete_sop_category(
    sop_category_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    sop_category = db.query(SopCategories).filter(SopCategories.id == sop_category_id).first()
    if sop_category is None:
        raise HTTPException(status_code=404, detail="Sop_category not found")
    
    db.delete(sop_category)
    db.commit()
    return {"message": "Sop_category deleted successfully"}