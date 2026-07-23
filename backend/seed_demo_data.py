import sys
import os
import json
from sqlalchemy.orm import Session
from uuid import uuid4

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base, DATABASE_URL
from app.models import Place, ReferencePrice

# Check if it's SQLite
IS_SQLITE = DATABASE_URL.startswith("sqlite")

def seed_data():
    print("--- Seeding Demo Data for Mahir Marrakech ---")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Seed Reference Prices
        prices = [
            ReferencePrice(item_name="Petit Taxi (3km)", min_price=15.0, max_price=25.0, unit="trip", currency="MAD"),
            ReferencePrice(item_name="Chicken Tajine", min_price=60.0, max_price=90.0, unit="portion", currency="MAD"),
            ReferencePrice(item_name="Leather Slippers (Babouche)", min_price=100.0, max_price=180.0, unit="pair", currency="MAD"),
            ReferencePrice(item_name="Fresh Orange Juice (Square)", min_price=4.0, max_price=10.0, unit="glass", currency="MAD"),
        ]
        
        # 2. Seed Places (Near Marrakech Center)
        from sqlalchemy import text
        
        p1_loc = "POINT(-7.9891 31.6258)"
        p2_loc = "POINT(-7.9877 31.6271)"
        
        if not IS_SQLITE:
            from geoalchemy2.elements import WKTElement
            p1_loc = WKTElement(p1_loc, srid=4326)
            p2_loc = WKTElement(p2_loc, srid=4326)

        places = [
            Place(
                name="Le Grand Balcon du Café Glacier",
                category="Restaurant",
                description="Iconic cafe with the best view of Jemaa el-Fnaa.",
                address="Jemaa el-Fnaa, Marrakech",
                location=p1_loc,
                is_verified=True,
                metadata_json={"wifi": True, "view": "square"} if not IS_SQLITE else json.dumps({"wifi": True, "view": "square"})
            ),
            Place(
                name="Nomad",
                category="Restaurant",
                description="Modern Moroccan cuisine with a beautiful rooftop terrace.",
                address="1 Rahba Kedima, Marrakech",
                location=p2_loc,
                is_verified=True,
                metadata_json={"luxury": True, "rooftop": True} if not IS_SQLITE else json.dumps({"luxury": True, "rooftop": True})
            )
        ]

        print("Adding Reference Prices...")
        db.add_all(prices)
        print("Adding Places...")
        db.add_all(places)
        
        db.commit()
        print("Done: Demo data seeded successfully!")
        
    except Exception as e:
        print(f"Error: Seeding failed - {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
