from sqlalchemy.orm import Session
from app.models import ScamZone, Tour, ReferencePrice, Restaurant
import uuid

SCAM_ZONES = [
    {
        "name": "Jemaa el-Fnaa - Vendor Overcharge",
        "name_ar": "ساحة جامع الفنا - باعة متجولون",
        "description": "Some vendors may charge excessive prices. Always ask for the price first.",
        "latitude": 31.6256,
        "longitude": -7.9891,
        "radius_meters": 300,
        "severity": "high",
        "tips": "Negotiate everything. Valid price is usually 30-50% of first offer."
    },
    {
        "name": "Souk Entrance - Fake Guides",
        "name_ar": "مدخل السوق الكبير - مرشدون وهميون",
        "description": "Unlicensed guides may offer help and then demand high fees. Do not follow strangers.",
        "latitude": 31.6295,
        "longitude": -7.9867,
        "radius_meters": 200,
        "severity": "high",
        "tips": "Say 'No thank you' politely. Use the app's GPS instead."
    },
    {
        "name": "Tannery Area (Tanneries)",
        "name_ar": "سوق الجلد (الدباغين)",
        "description": "Common 'mint scam': you're given mint and led to a shop with pressure to buy.",
        "latitude": 31.6340,
        "longitude": -7.9830,
        "radius_meters": 200,
        "severity": "medium",
        "tips": "Entrance is free. 10-20 MAD tip is enough for a view. Avoid 'free' tours."
    },
    {
        "name": "Taxi Stand - Overcharge",
        "name_ar": "محطة التاكسي - سعر زائد",
        "description": "Refusing to use the meter (compteur) is common here.",
        "latitude": 31.6300,
        "longitude": -7.9920,
        "radius_meters": 250,
        "severity": "high",
        "tips": "Insist on the meter or use the app's price guide. City fare: 10-30 MAD."
    }
]

SAMPLE_TOURS = [
    {
        "title": "Secrets of the Medina",
        "description": "A deep dive into the hidden history and architecture of the old city with a certified historian.",
        "price": 250.00,
        "duration_hours": 3.5,
        "is_premium": True,
        "image_url": "https://images.unsplash.com/photo-1539650116574-8efeb43e2750"
    },
    {
        "title": "Marrakech Street Food Tour",
        "description": "Taste the authentic flavors of Marrakech in the hidden corners of Jemaa el-Fnaa.",
        "price": 350.00,
        "duration_hours": 4.0,
        "is_premium": True,
        "image_url": "https://images.unsplash.com/photo-1541544741938-0af808871cc0"
    },
    {
        "title": "Atlas Mountains Day Trip",
        "description": "Escape the city and enjoy the fresh air and stunning views of the Atlas Mountains.",
        "price": 500.00,
        "duration_hours": 8.0,
        "is_premium": False,
        "image_url": "https://images.unsplash.com/photo-1489749798305-4fea3ae63d43"
    }
]

FAIR_PRICES = [
    {"item_name": "Leather Handbag (Standard)", "category": "souvenirs", "min_price": 150.0, "max_price": 300.0, "unit": "piece"},
    {"item_name": "Leather Pouf (Unstuffed)", "category": "souvenirs", "min_price": 100.0, "max_price": 200.0, "unit": "piece"},
    {"item_name": "Argan Oil (100ml)", "category": "cosmetics", "min_price": 60.0, "max_price": 120.0, "unit": "bottle"},
    {"item_name": "Traditional Tagine (Medium)", "category": "kitchenware", "min_price": 40.0, "max_price": 80.0, "unit": "piece"},
    {"item_name": "Petit Taxi (Medina to Gueliz)", "category": "transport", "min_price": 15.0, "max_price": 30.0, "unit": "ride"},
    {"item_name": "Fresh Orange Juice (Jemaa el-Fnaa)", "category": "food", "min_price": 4.0, "max_price": 10.0, "unit": "glass"},
    {"item_name": "Henna Tattoo (Small Hand)", "category": "services", "min_price": 30.0, "max_price": 70.0, "unit": "hand"},
]

SAMPLE_RESTAURANTS = [
    {
        "name": "Al Fassia",
        "description": "Authentic Moroccan cuisine served in a sophisticated atmosphere. Famous for being run entirely by women.",
        "cuisine_type": "Traditional Moroccan",
        "price_level": 3,
        "address": "55 Bd Mohamed Zerktouni, Marrakech",
        "latitude": 31.6369,
        "longitude": -8.0147,
        "image_url": "https://images.unsplash.com/photo-1541167760496-1628856ab772",
        "is_verified": True,
        "must_try_dish": "Slow-cooked Lamb Shoulder (Mechoui)",
        "rating": 4.8
    },
    {
        "name": "Le Jardin",
        "description": "A green oasis in the heart of the Medina. Perfect for a peaceful lunch away from the hustle.",
        "cuisine_type": "Moroccan-French Fusion",
        "price_level": 2,
        "address": "32 Souk El Jeld, Sidi Abdelaziz, Marrakech",
        "latitude": 31.6315,
        "longitude": -7.9892,
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
        "is_verified": True,
        "must_try_dish": "Lemon Chicken Tagine",
        "rating": 4.5
    },
    {
        "name": "Nomad",
        "description": "Modern Moroccan cuisine with a stunning rooftop view of the Medina and Atlas Mountains.",
        "cuisine_type": "Modern Moroccan",
        "price_level": 3,
        "address": "1 Derb Aarjan, Marrakech",
        "latitude": 31.6285,
        "longitude": -7.9868,
        "image_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de",
        "is_verified": True,
        "must_try_dish": "Nomad Burger with Harissa Mayo",
        "rating": 4.7
    }
]

def seed_db(db: Session):
    # Seed Scam Zones
    if not db.query(ScamZone).first():
        print("[INFO] Seeding Scam Zones...")
        for zone_data in SCAM_ZONES:
            zone = ScamZone(id=str(uuid.uuid4()), is_active=True, **zone_data)
            db.add(zone)
    
    # Seed Tours
    if not db.query(Tour).first():
        print("[INFO] Seeding Tours...")
        for tour_data in SAMPLE_TOURS:
            tour = Tour(id=str(uuid.uuid4()), **tour_data)
            db.add(tour)

    # Seed Reference Prices
    if not db.query(ReferencePrice).first():
        print("[INFO] Seeding Reference Prices...")
        for price_data in FAIR_PRICES:
            price = ReferencePrice(id=str(uuid.uuid4()), **price_data)
            db.add(price)
    
    # Seed Restaurants
    if not db.query(Restaurant).first():
        print("[INFO] Seeding Restaurants...")
        for rest_data in SAMPLE_RESTAURANTS:
            restaurant = Restaurant(id=str(uuid.uuid4()), **rest_data)
            db.add(restaurant)
    
    db.commit()
    print("[OK] Seeding complete.")
