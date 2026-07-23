import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from uuid import uuid4

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base, DATABASE_URL

IS_SQLITE = DATABASE_URL.startswith("sqlite")

def verify_setup():
    print("--- Mahir Marrakech DB Verification ---")
    
    # 1. Check Extensions (Only for Postgres)
    if not IS_SQLITE:
        try:
            with engine.connect() as conn:
                print("Checking for PostGIS extension...")
                result = conn.execute(text("SELECT PostGIS_Version();")).fetchone()
                print(f"PostGIS Version: {result[0]}")
                
                print("Checking for uuid-ossp extension...")
                conn.execute(text("SELECT uuid_generate_v4();"))
                print("uuid-ossp is working")
        except Exception as e:
            print(f"Extension Error: {e}")
            print("Tip: Run 'CREATE EXTENSION IF NOT EXISTS postgis;' in your DB.")
            # We continue anyway if we are in demo mode
    else:
        print("Demo Mode: SQLite detected. Skipping extension checks.")

    # 2. Check Tables
    try:
        print("Verifying table creation...")
        Base.metadata.create_all(bind=engine)
        print("All tables created or already exist.")
    except Exception as e:
        print(f"Table Creation Error: {e}")
        return

    # 3. Test Insertion
    db: Session = SessionLocal()
    try:
        from app.models import User
        print("Testing record insertion...")
        new_user = User(
            full_name="Verification Bot",
            email=f"bot_{uuid4().hex[:6]}@mahir.test",
            phone_number="+212000000000"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created with ID: {new_user.id}")
        
        # Cleanup
        db.delete(new_user)
        db.commit()
        print("Verification cleanup successful")
        
    except Exception as e:
        print(f"Insertion Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_setup()
