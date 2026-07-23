from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Driver, Place, ReferencePrice, ScamZone
from app.schemas.admin import (
    DriverCreate, DriverResponse, 
    PlaceCreate, PlaceResponse,
    ReferencePriceCreate, ReferencePriceResponse,
    ScamZoneCreate, ScamZoneResponse,
    PartnerOnboard
)
from app.services.places_service import places_service
from typing import List
from uuid import UUID

router = APIRouter()

# --- Reference Prices (Fair Price Engine) ---

@router.post("/reference-prices", response_model=ReferencePriceResponse)
def create_reference_price(price: ReferencePriceCreate, db: Session = Depends(get_db)):
    db_price = ReferencePrice(
        item_name=price.item_name,
        min_price=price.min_price,
        max_price=price.max_price,
        currency=price.currency,
        unit=price.unit
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

@router.get("/reference-prices", response_model=List[ReferencePriceResponse])
def read_reference_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prices = db.query(ReferencePrice).offset(skip).limit(limit).all()
    return prices

@router.delete("/reference-prices/{price_id}")
def delete_reference_price(price_id: UUID, db: Session = Depends(get_db)):
    price = db.query(ReferencePrice).filter(ReferencePrice.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price entry not found")
    db.delete(price)
    db.commit()
    return {"message": "Price entry deleted successfully"}

# --- Drivers ---

@router.post("/drivers", response_model=DriverResponse)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    db_driver = Driver(
        full_name=driver.full_name,
        phone_number=driver.phone_number,
        vehicle_plate=driver.vehicle_plate,
        vehicle_type=driver.vehicle_type,
        is_verified=True # Auto-verify for Admin creation
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.get("/drivers", response_model=List[DriverResponse])
def read_drivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    drivers = db.query(Driver).offset(skip).limit(limit).all()
    return drivers

@router.delete("/drivers/{driver_id}")
def delete_driver(driver_id: UUID, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(driver)
    db.commit()
    return {"message": "Driver deleted successfully"}

# --- Places (Formerly Services) ---

@router.post("/places", response_model=PlaceResponse)
def create_place(place: PlaceCreate, db: Session = Depends(get_db)):
    db_place = Place(
        name=place.name,
        category=place.category,
        description=place.description,
        address=place.address,
        metadata_json=place.metadata_json,
        is_verified=True
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@router.get("/places", response_model=List[PlaceResponse])
def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    places = db.query(Place).offset(skip).limit(limit).all()
    return places

@router.delete("/places/{place_id}")
def delete_place(place_id: UUID, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    db.delete(place)
    db.commit()
    return {"message": "Place deleted successfully"}

# --- Scam Zones (Safety Shield) ---

@router.post("/scam-zones", response_model=ScamZoneResponse)
def create_scam_zone(zone: ScamZoneCreate, db: Session = Depends(get_db)):
    db_zone = ScamZone(
        name=zone.name,
        description=zone.description,
        latitude=zone.latitude,
        longitude=zone.longitude,
        radius_meters=zone.radius_meters,
        severity=zone.severity,
        tips=zone.tips,
        is_active=zone.is_active
    )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.get("/scam-zones", response_model=List[ScamZoneResponse])
def read_scam_zones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    zones = db.query(ScamZone).offset(skip).limit(limit).all()
    return zones

@router.delete("/scam-zones/{zone_id}")
def delete_scam_zone(zone_id: UUID, db: Session = Depends(get_db)):
    zone = db.query(ScamZone).filter(ScamZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Scam zone not found")
    db.delete(zone)
    db.commit()
    return {"message": "Scam zone deleted successfully"}

# --- Partner Discovery & Onboarding ---

@router.get("/discover-partners")
def discover_partners(query: str = "top restaurants in Marrakech"):
    """Search Google Maps for potential partners."""
    return places_service.search_restaurants(query)

@router.post("/onboard-partner", response_model=PlaceResponse)
def onboard_partner(partner: PartnerOnboard, db: Session = Depends(get_db)):
    """Convert a discovered Google Place into a local Partner."""
    # Check if already exists
    existing = db.query(Place).filter(Place.name == partner.name).first()
    if existing:
        existing.is_partner = True
        existing.commission_rate = partner.commission_rate
        db.commit()
        db.refresh(existing)
        return existing
    
    db_place = Place(
        name=partner.name,
        category=partner.category,
        address=partner.address,
        is_partner=True,
        is_verified=True,
        commission_rate=partner.commission_rate,
        metadata_json={"google_place_id": partner.place_id}
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@router.get("/partners", response_model=List[PlaceResponse])
def get_partners(db: Session = Depends(get_db)):
    """List all commission partners."""
    return db.query(Place).filter(Place.is_partner == True).all()
