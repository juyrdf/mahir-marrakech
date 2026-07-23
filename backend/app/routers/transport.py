from fastapi import APIRouter, HTTPException
from app.schemas.booking import TransportQuoteRequest, TransportQuoteResponse, BookingRequest, BookingResponse
import uuid
import math
from datetime import datetime, timedelta
import random

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth surface."""
    R = 6371.0 # Radius of earth in kilometers.
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

router = APIRouter()

# Mock Database for Quotes
active_estimates = {}

@router.post("/quote", response_model=TransportQuoteResponse)
async def get_transport_quote(request: TransportQuoteRequest):
    """
    Generates a realistic fixed-price quote using the Haversine distance formula.
    Base price + Per km rate.
    """
    
    distance_km = haversine(
        request.pickup.latitude, request.pickup.longitude,
        request.dropoff.latitude, request.dropoff.longitude
    )
    
    # Base real-world Marrakech pricing logic:
    # Petit Taxi base 7 MAD day. Roughly 3 MAD per km.
    base_fare = 10.0
    price_per_km = 4.0
    
    # Base calculation
    raw_price = base_fare + (distance_km * price_per_km)
    
    # Apply ride_type multiplier
    multiplier = 1.0
    if request.ride_type.lower() == "van":
        multiplier = 1.8 # Grand Taxi / Minivan type
    elif request.ride_type.lower() == "luxury":
        multiplier = 2.5 # VIP transport
        
    avg_price = int(raw_price * multiplier)
    
    # Guarantee minimum fare in MAD
    if avg_price < 20: 
        avg_price = 20
    
    # Create the range
    min_price = int(avg_price * 0.9)
    max_price = int(avg_price * 1.15)
    
    estimate_id = str(uuid.uuid4())
    valid_until = datetime.utcnow() + timedelta(minutes=15)
    
    # Calculate duration assuming 30 km/h average in Marrakech
    estimated_duration_min = max(5, int((distance_km / 30.0) * 60))
    
    quote = TransportQuoteResponse(
        estimate_id=estimate_id,
        min_price=min_price,
        max_price=max_price,
        vehicle_type="Standard" if request.ride_type == "standard" else request.ride_type.capitalize(),
        estimated_duration_min=estimated_duration_min,
        valid_until=valid_until.isoformat()
    )
    
    active_estimates[estimate_id] = quote
    return quote

@router.post("/book", response_model=BookingResponse)
async def book_transport(request: BookingRequest):
    """
    Confirms a booking if the estimate is valid and manages promo codes.
    """
    if request.estimate_id not in active_estimates:
        raise HTTPException(status_code=404, detail="Estimate not found or expired")
    
    estimate = active_estimates[request.estimate_id]
    
    # Assume the driver agrees on the arithmetic mean of min and max initially
    final_price = (estimate.min_price + estimate.max_price) // 2
    
    # Process promotional code
    if request.promo_code and request.promo_code.upper() == "WELCOME10":
        final_price = int(final_price * 0.9) # 10% off
    
    # In a real app, we would dispatch a driver here
    bookings_ref = f"MAHIR-{random.randint(1000, 9999)}"
    
    return BookingResponse(
        booking_reference=bookings_ref,
        status="confirmed",
        driver_name="Karim Benali",
        driver_plate="45-A-12345",
        final_price=final_price,
        message=f"Driver confirmed. Payment method: {request.payment_method}. Final agreed price: {final_price} MAD."
    )
