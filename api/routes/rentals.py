from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.rental import Rental
from schemas.rental import RentalCreate, RentalUpdate, Rental as RentalSchema
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.get("/room/{room_id}/status/{status}", response_model=List[RentalSchema])
def get_rentals_by_room_status(
    room_id: int, 
    status: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    if status == 1:
        status = "active"
    elif status == 0:
        status = "inactive"
    rentals = db.query(Rental).filter(Rental.room_id == room_id, Rental.status == status).all()
    return rentals

@router.post("/", response_model=RentalSchema)
def create_rental(
    rental: RentalCreate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_rental = Rental(**rental.model_dump())
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

@router.get("/{rental_id}", response_model=RentalSchema)
def get_rental(
    rental_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental

@router.put("/{rental_id}", response_model=RentalSchema)
def update_rental(
    rental_id: int, 
    rental_update: RentalUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    update_data = rental_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rental, field, value)
    
    db.commit()
    db.refresh(db_rental)
    return db_rental

@router.delete("/{rental_id}")
def delete_rental(
    rental_id: int, 
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    db.delete(db_rental)
    db.commit()
    return {"message": "Rental deleted successfully"}