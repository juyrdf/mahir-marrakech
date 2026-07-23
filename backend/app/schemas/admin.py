from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Any, Dict
from datetime import datetime

class DriverBase(BaseModel):
    full_name: str
    phone_number: str
    vehicle_plate: str
    vehicle_type: str

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    id: UUID
    is_active: bool
    is_verified: bool
    rating: float
    created_at: datetime

    class Config:
        from_attributes = True

class PlaceBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    address: Optional[str] = None
    is_verified: bool = False
    is_partner: bool = False
    commission_rate: float = 0.0
    metadata_json: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class PlaceResponse(PlaceBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ReferencePriceBase(BaseModel):
    item_name: str
    min_price: float
    max_price: float
    currency: str = "MAD"
    unit: str

class ReferencePriceCreate(ReferencePriceBase):
    pass

class ReferencePriceResponse(ReferencePriceBase):
    id: UUID
    last_updated: datetime

    class Config:
        from_attributes = True

class PartnerOnboard(BaseModel):
    place_id: str # Google Place ID
    name: str
    category: str = "Restaurant"
    address: Optional[str] = None
    commission_rate: float = 10.0
    is_partner: bool = True

class ScamZoneBase(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float
    radius_meters: int = 500
    severity: str = "medium"
    tips: Optional[str] = None
    is_active: bool = True

class ScamZoneCreate(ScamZoneBase):
    pass

class ScamZoneResponse(ScamZoneBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
