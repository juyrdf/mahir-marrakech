from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Tour, TourBooking
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(tags=["tours"])

class TourSchema(BaseModel):
    id: str
    title: str
    description: Optional[str]
    price: float
    currency: str = "MAD"
    duration_hours: float
    image_url: Optional[str]
    is_premium: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TourSchema])
def get_tours(db: Session = Depends(get_db)):
    """Retrieve all available tours."""
    return db.query(Tour).all()

@router.post("/book")
def book_tour(tour_id: str, user_id: str, db: Session = Depends(get_db)):
    """Book a specific tour for a user."""
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    
    booking = TourBooking(
        tour_id=tour_id,
        user_id=user_id,
        booking_date=datetime.now(),
        status="pending"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"status": "success", "booking_id": str(booking.id)}
