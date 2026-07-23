from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import ReferencePrice
from app.schemas.admin import ReferencePriceResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ReferencePriceResponse])
def get_all_prices(db: Session = Depends(get_db)):
    """
    Get all reference prices for the 'Fair Guide' in the mobile app.
    """
    return db.query(ReferencePrice).all()

@router.get("/search", response_model=List[ReferencePriceResponse])
def search_prices(query: str, db: Session = Depends(get_db)):
    """
    Search for a specific item price.
    """
    return db.query(ReferencePrice).filter(ReferencePrice.item_name.ilike(f"%{query}%")).all()
