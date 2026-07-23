from pydantic import BaseModel
from typing import Optional

class LocationPoint(BaseModel):
    latitude: float
    longitude: float
    address: str

class TransportQuoteRequest(BaseModel):
    pickup: LocationPoint
    dropoff: LocationPoint
    passenger_count: int = 1
    ride_type: str = "standard"  # standard, van, luxury

class TransportQuoteResponse(BaseModel):
    estimate_id: str
    min_price: int
    max_price: int
    vehicle_type: str
    estimated_duration_min: int
    valid_until: str

class BookingRequest(BaseModel):
    estimate_id: str
    ride_type: str = "standard"
    payment_method: str = "cash"
    promo_code: Optional[str] = None

class BookingResponse(BaseModel):
    booking_reference: str
    status: str
    driver_name: str
    driver_plate: str
    final_price: Optional[int] = None
    message: str
