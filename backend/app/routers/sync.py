from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Place
from app.services.ai_service import ai_service

router = APIRouter()

@router.get("/local-data")
def get_offline_package(db: Session = Depends(get_db)):
    """
    Returns a 'Lite Data Package' for offline usage.
    Includes:
    1. Top Landmarks (Static/Mocked for now)
    2. Verified Places (From DB)
    3. Essential Safety Tips
    """
    
    # 1. Fetch Places (Restaurants/Shops) from DB
    services = db.query(Place).filter(Place.is_verified == True).all()
    
    # 2. Static Landmarks (Simulated 'Vector Tile' metadata or just POIs)
    landmarks = [
        {
            "id": "l_1",
            "name": "Jemaa el-Fnaa",
            "description": "The main square and market place in Marrakesh's medina quarter.",
            "coordinates": {"lat": 31.6258, "lng": -7.9891},
            "type": "Must Visit"
        },
        {
            "id": "l_2",
            "name": "Koutoubia Mosque",
            "description": "The largest mosque in Marrakesh, Morocco.",
            "coordinates": {"lat": 31.6236, "lng": -7.9936},
            "type": "Culture"
        },
        {
            "id": "l_3",
            "name": "Majorelle Garden",
            "description": "A two and a half acre botanical garden and artist's landscape garden.",
            "coordinates": {"lat": 31.6415, "lng": -8.0025},
            "type": "Nature"
        }
    ]

    # 3. Safety Tips (Hardcoded for offline access)
    safety_tips = [
        "Avoid 'free' tours from strangers.",
        "Always agree on a taxi price before entering (or use the meter).",
        "Take photos of snake charmers only if you pay (20 MAD is fair)."
    ]

    return {
        "version": "1.0.0",
        "landmarks": landmarks,
        "services": services,
        "safety_tips": safety_tips
    }
