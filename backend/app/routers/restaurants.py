from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Restaurant
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

router = APIRouter(tags=["Restaurants"])

class RestaurantResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    cuisine_type: Optional[str]
    price_level: Optional[int]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    image_url: Optional[str]
    is_verified: bool
    is_partner: bool
    must_try_dish: Optional[str]
    rating: float

    class Config:
        from_attributes = True

@router.get("/", response_model=List[RestaurantResponse])
def get_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant
