"""
Extended seed script for Mahir Marrakech – adds comprehensive prices and places.
Run: python seed_full_data.py  (from the backend/ directory)
"""
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base, DATABASE_URL
from app.models import Place, ReferencePrice, Tour

IS_SQLITE = DATABASE_URL.startswith("sqlite")

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clear existing
        db.query(ReferencePrice).delete()
        db.query(Place).delete()
        db.query(Tour).delete()
        db.commit()

        # --- REFERENCE PRICES (Fair Guide) ---
        prices = [
            # Transport
            ReferencePrice(item_name="Petit Taxi (up to 3 km)", min_price=15, max_price=25, unit="trip", currency="MAD"),
            ReferencePrice(item_name="Petit Taxi (airport)", min_price=70, max_price=100, unit="trip", currency="MAD"),
            ReferencePrice(item_name="Caleche (horse carriage, 1 hour)", min_price=100, max_price=150, unit="hour", currency="MAD"),
            ReferencePrice(item_name="Bus (city bus)", min_price=4, max_price=4, unit="trip", currency="MAD"),
            # Food & Drink
            ReferencePrice(item_name="Fresh Orange Juice (Jemaa el-Fnaa)", min_price=4, max_price=10, unit="glass", currency="MAD"),
            ReferencePrice(item_name="Mint Tea (traditional)", min_price=10, max_price=20, unit="pot", currency="MAD"),
            ReferencePrice(item_name="Chicken Tajine (restaurant)", min_price=60, max_price=90, unit="plate", currency="MAD"),
            ReferencePrice(item_name="Couscous (Friday special)", min_price=55, max_price=80, unit="plate", currency="MAD"),
            ReferencePrice(item_name="Harira Soup", min_price=10, max_price=20, unit="bowl", currency="MAD"),
            ReferencePrice(item_name="Msemen (Moroccan pancake)", min_price=3, max_price=5, unit="piece", currency="MAD"),
            # Souvenirs & Crafts
            ReferencePrice(item_name="Leather Slippers (Babouche)", min_price=100, max_price=200, unit="pair", currency="MAD"),
            ReferencePrice(item_name="Argan Oil (100ml, genuine)", min_price=80, max_price=120, unit="bottle", currency="MAD"),
            ReferencePrice(item_name="Handmade Carpet (small)", min_price=300, max_price=600, unit="piece", currency="MAD"),
            ReferencePrice(item_name="Ceramic Tagine Bowl", min_price=50, max_price=100, unit="piece", currency="MAD"),
            ReferencePrice(item_name="Fez Hat (Tarboush)", min_price=60, max_price=120, unit="piece", currency="MAD"),
            # Experiences
            ReferencePrice(item_name="Hammam (basic public)", min_price=15, max_price=30, unit="session", currency="MAD"),
            ReferencePrice(item_name="Hammam (tourist/riad)", min_price=150, max_price=300, unit="session", currency="MAD"),
            ReferencePrice(item_name="Guided Medina Tour (4h)", min_price=200, max_price=350, unit="tour", currency="MAD"),
            ReferencePrice(item_name="Cooking Class (half-day)", min_price=350, max_price=500, unit="class", currency="MAD"),
            ReferencePrice(item_name="Camel Ride (Palmeraie, 1h)", min_price=100, max_price=150, unit="hour", currency="MAD"),
        ]

        # --- PLACES (Certified by Mahir) ---
        def loc(lng, lat):
            wkt = f"POINT({lng} {lat})"
            if not IS_SQLITE:
                from geoalchemy2.elements import WKTElement
                return WKTElement(wkt, srid=4326)
            return wkt

        places = [
            Place(name="Jemaa el-Fnaa", category="Market", description="The iconic main square of Marrakech, alive with storytellers, musicians, and food stalls.", address="Jemaa el-Fnaa, Medina, Marrakech", location=loc(-7.9891, 31.6258), is_verified=True, metadata_json={"highlight": True, "open": "24h"}),
            Place(name="Koutoubia Mosque", category="Mosque", description="The largest mosque in Marrakech and a landmark 12th-century minaret.", address="Koutoubia, Marrakech", location=loc(-7.9939, 31.6238), is_verified=True, metadata_json={"historical": True}),
            Place(name="Souks of the Medina", category="Souk", description="Labyrinthine alleys filled with spices, leather, textiles, and crafts.", address="Medina Souks, Marrakech", location=loc(-7.9858, 31.6291), is_verified=True, metadata_json={"bargain": True}),
            Place(name="Bahia Palace", category="Museum", description="Stunning 19th-century palace with intricate Moroccan tilework and carved stucco.", address="Rue Riad Zitoun el Jedid, Marrakech", location=loc(-7.9825, 31.6214), is_verified=True, metadata_json={"entry_fee": "70 MAD"}),
            Place(name="Le Jardin Secret", category="Garden", description="Two restored Islamic gardens in the heart of the Medina. A cool oasis.", address="121 Rue Mouassine, Medina", location=loc(-7.9882, 31.6311), is_verified=True, metadata_json={"entry_fee": "50 MAD", "tranquil": True}),
            Place(name="Café Argana", category="Cafe", description="Historic café overlooking Jemaa el-Fnaa. Perfect for watching the square.", address="Jemaa el-Fnaa, Marrakech", location=loc(-7.9886, 31.6260), is_verified=True, metadata_json={"view": "square"}),
            Place(name="Nomad Restaurant", category="Restaurant", description="Modern Moroccan rooftop restaurant with creative cuisine and panoramic views.", address="1 Rahba Kedima, Marrakech", location=loc(-7.9877, 31.6271), is_verified=True, metadata_json={"rooftop": True, "luxury": True}),
            Place(name="Hammam El Bacha", category="Hammam", description="Authentic traditional hammam frequented by locals since the 20th century.", address="20 Rue Fatima Zohra, Marrakech", location=loc(-7.9905, 31.6305), is_verified=True, metadata_json={"traditional": True, "budget": True}),
        ]

        tours = [
            Tour(title="Sunset Camel Ride & Dinner", category="Adventure", description="Experience the magic of the Agafay Desert at sunset. Includes traditional dinner under the stars.", price=450, currency="MAD", duration_hours=5.0, image_url="https://images.unsplash.com/photo-1542385150-efdd185b5eb3?q=80&w=600", is_premium=True),
            Tour(title="Authentic Tajine Cooking Class", category="Foodie", description="Learn the secrets of Moroccan spices and cook your own delicious tajine in a traditional Riad.", price=350, currency="MAD", duration_hours=4.0, image_url="https://images.unsplash.com/photo-1541518155355-1611c7827303?q=80&w=600", is_premium=False),
            Tour(title="Hidden Medina Walking Tour", category="Cultural", description="Explore the labyrinthine alleys of the Medina and discover hidden palaces and secret workshops.", price=200, currency="MAD", duration_hours=3.5, image_url="https://images.unsplash.com/photo-1548013146-72479768bbaa?q=80&w=600", is_premium=False),
            Tour(title="Hammam & Spa Royal Retreat", category="Relax", description="A journey of absolute relaxation. Traditional scrub followed by a massage with Argan oil.", price=600, currency="MAD", duration_hours=2.5, image_url="https://images.unsplash.com/photo-1544161515-4508f5ad4c94?q=80&w=600", is_premium=True),
            Tour(title="Atlas Mountains Day Trip", category="Adventure", description="Full day excursion to the Ourika Valley. Hike to the waterfalls and visit a Berber home.", price=400, currency="MAD", duration_hours=8.0, image_url="https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?q=80&w=600", is_premium=False),
        ]

        db.add_all(prices)
        db.add_all(places)
        db.add_all(tours)
        db.commit()
        print(f"SUCCESS: Seeded {len(prices)} prices, {len(places)} places, and {len(tours)} tours!")
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
