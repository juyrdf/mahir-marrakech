from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db, DATABASE_URL
from app.models import Place
from app.schemas.admin import PlaceResponse
from typing import List

# Helper for cross-DB Compatibility
IS_SQLITE = DATABASE_URL.startswith("sqlite")

try:
    from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
    HAS_GEOALCHEMY = True
except ImportError:
    HAS_GEOALCHEMY = False

router = APIRouter()

@router.get("/nearby", response_model=List[PlaceResponse])
def get_nearby_places(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius: float = Query(1000, description="Search radius in meters"),
    db: Session = Depends(get_db)
):
    """
    Find places within a specific radius. 
    Uses PostGIS for PostgreSQL, falls back to basic filtering for SQLite demo.
    """
    if not IS_SQLITE and HAS_GEOALCHEMY:
        # PostgreSQL / PostGIS Path
        user_location = ST_SetSRID(ST_MakePoint(lng, lat), 4326)
        nearby_places = db.query(Place).filter(
            ST_DWithin(Place.location, user_location, radius)
        ).all()
        return nearby_places
    else:
        # SQLite Fallback Path (Simplified Demo)
        # In a real app, you'd parse the 'location' string and calculate distance
        return db.query(Place).all()

@router.get("/{place_id}", response_model=PlaceResponse)
def get_place_detail(place_id: str, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place
