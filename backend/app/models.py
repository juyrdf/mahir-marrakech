import uuid
from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey, Numeric, Integer, Text, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base, DATABASE_URL

# Conditional Spatial Type
try:
    from geoalchemy2 import Geography
    HAS_POSTGIS = True
except ImportError:
    HAS_POSTGIS = False

# Helper for cross-DB Compatibility
IS_SQLITE = DATABASE_URL.startswith("sqlite")

class User(Base):
    __tablename__ = "users"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        preferences = Column(JSON) 
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        preferences = Column(JSON)
        
    full_name = Column(String(100))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    country_origin = Column(String(50))
    hashed_password = Column(String(255), nullable=True)  # nullable for guests
    is_guest = Column(Boolean, default=False)
    language = Column(String(10), default='ar')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Place(Base):
    __tablename__ = "places"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        location = Column(Text) # Store WKT or Lat,Lng string
        metadata_json = Column(JSON)
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        location = Column(Geography(geometry_type='POINT', srid=4326))
        metadata_json = Column(JSON)

    name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    address = Column(Text)
    is_verified = Column(Boolean, default=False)
    is_partner = Column(Boolean, default=False)
    commission_rate = Column(Float, default=0.0) # e.g. 10.0 for 10%
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Driver(Base):
    __tablename__ = "drivers"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, index=True)
    vehicle_plate = Column(String(20))
    vehicle_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReferencePrice(Base):
    __tablename__ = "reference_prices"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    item_name = Column(String(100), nullable=False)
    category = Column(String(50))
    min_price = Column(Numeric(10, 2))
    max_price = Column(Numeric(10, 2))
    currency = Column(String(10), default='MAD')
    unit = Column(String(50))
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Review(Base):
    __tablename__ = "reviews"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("users.id"))
        place_id = Column(String(36), ForeignKey("places.id"))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
        place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"))

    rating = Column(Integer)
    comment = Column(Text)
    is_verified_visit = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIChatLog(Base):
    __tablename__ = "ai_chat_logs"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("users.id"))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    user_query = Column(Text)
    ai_response = Column(Text)
    topic_tag = Column(Text) # JSON string of detected intents/tags
    sentiment = Column(String(50)) # detected sentiment
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class TransportBooking(Base):
    __tablename__ = "transport_bookings"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("users.id"))
        driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=True)
        pickup_location = Column(Text)
        dropoff_location = Column(Text)
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
        driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True)
        pickup_location = Column(Geography(geometry_type='POINT', srid=4326))
        dropoff_location = Column(Geography(geometry_type='POINT', srid=4326))

    status = Column(String(20))
    agreed_price = Column(Numeric(10, 2))
    qr_code = Column(Text, nullable=True)  # QR confirmation code
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScamZone(Base):
    __tablename__ = "scam_zones"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(150), nullable=False)
    name_ar = Column(String(150))
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=500)
    severity = Column(String(20), default='medium')  # low, medium, high, reported
    tips = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TripPlan(Base):
    __tablename__ = "trip_plans"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    num_days = Column(Integer, default=3)
    interests = Column(Text)  # JSON string
    plan_data = Column(Text)  # JSON string of day plans
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Tour(Base):
    __tablename__ = "tours"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    currency = Column(String(10), default='MAD')
    duration_hours = Column(Float)
    image_url = Column(Text)
    is_premium = Column(Boolean, default=False)
    category = Column(String(50), default='Adventure')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TourBooking(Base):
    __tablename__ = "tour_bookings"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("users.id"))
        tour_id = Column(String(36), ForeignKey("tours.id"))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
        tour_id = Column(UUID(as_uuid=True), ForeignKey("tours.id"))

    booking_date = Column(DateTime(timezone=True))
    status = Column(String(20), default='pending') # pending, confirmed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Restaurant(Base):
    __tablename__ = "restaurants"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(150), nullable=False)
    description = Column(Text)
    cuisine_type = Column(String(100)) # e.g. Moroccan, French, Fusion
    price_level = Column(Integer) # 1-4 ($, $$, $$$, $$$$)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(Text)
    is_verified = Column(Boolean, default=True)
    is_partner = Column(Boolean, default=False)
    must_try_dish = Column(String(150))
    rating = Column(Float, default=4.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InteractionFeedback(Base):
    __tablename__ = "interaction_feedback"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        chat_log_id = Column(String(36), ForeignKey("ai_chat_logs.id"))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        chat_log_id = Column(UUID(as_uuid=True), ForeignKey("ai_chat_logs.id"))

    is_positive = Column(Boolean, nullable=False) # True for Up, False for Down
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserPreference(Base):
    __tablename__ = "user_preferences"

    if IS_SQLITE:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("users.id"))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    category = Column(String(100), index=True) # e.g. 'food', 'history', 'tajine'
    weight = Column(Float, default=1.0) # Importance score
    last_interaction = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
