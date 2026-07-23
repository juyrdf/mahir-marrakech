import sys
import os
import uuid

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import Place
from app.schemas.admin import PartnerOnboard

def debug_onboard():
    print("🔍 Testing Partner Onboard Logic...")
    db = SessionLocal()
    try:
        partner = PartnerOnboard(
            place_id="test_id_123",
            name="Debug Restaurant",
            category="Restaurant",
            address="123 Test St",
            commission_rate=10.0
        )
        
        print(f"📦 Creating DB object for: {partner.name}")
        
        # Manually replicate the router logic
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
        
        print("✅ Record created successfully!")
        print(f"   ID: {db_place.id}")
        print(f"   Metadata: {db_place.metadata_json}")
        
    except Exception as e:
        import traceback
        print("❌ CRASH DETECTED!")
        print(traceback.format_exc())
        with open("onboard_crash.txt", "w") as f:
            f.write(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    debug_onboard()
