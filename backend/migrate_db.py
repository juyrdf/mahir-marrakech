import sqlite3
import os
from app.core.database import DATABASE_URL

def migrate():
    print("==================================================")
    print("🔄 Running Database Schema Migrations")
    print("==================================================")
    
    # Resolve sqlite path
    if "sqlite" in DATABASE_URL:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_path = os.path.abspath(db_path)
        print(f"📁 Target Database file: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns of ai_chat_logs
        cursor.execute("PRAGMA table_info(ai_chat_logs);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns in 'ai_chat_logs': {columns}")
        
        # Add sentiment if missing
        if "sentiment" not in columns:
            print("➕ Column 'sentiment' is missing. Adding it...")
            cursor.execute("ALTER TABLE ai_chat_logs ADD COLUMN sentiment VARCHAR(50);")
            conn.commit()
            print("✅ Column 'sentiment' added successfully!")
        else:
            print("👌 Column 'sentiment' already exists.")
            
        conn.close()
    else:
        print("ℹ️ PostGIS/PostgreSQL detected. Migration should be handled via Alembic.")
    print("==================================================")

if __name__ == "__main__":
    migrate()
