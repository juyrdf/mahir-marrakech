import sys
from pathlib import Path

# Prevent UnicodeEncodeError on Windows stdout with emojis
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend root to path
sys.path.append(str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models import AIChatLog, UserPreference, InteractionFeedback
import json
import uuid

client = TestClient(app)

def test_feedback_learning_loop():
    print("==================================================")
    print("🧪 Running Feedback & Learning Loop Tests")
    print("==================================================")
    
    db = SessionLocal()
    
    # 1. Create a dummy chat log in the DB
    log_id = str(uuid.uuid4())
    user_id = "test_user_feedback_123"
    
    # Clean up previous tests if any
    db.query(InteractionFeedback).filter(InteractionFeedback.chat_log_id == log_id).delete()
    db.query(AIChatLog).filter(AIChatLog.id == log_id).delete()
    db.query(UserPreference).filter(UserPreference.user_id == user_id).delete()
    db.commit()
    
    chat_log = AIChatLog(
        id=log_id,
        user_id=user_id,
        user_query="بشحال الطاكسي",
        ai_response="سعر التاكسي هو 30 درهم",
        topic_tag=json.dumps(["pricing", "transport"]),
        sentiment="neutral"
    )
    db.add(chat_log)
    db.commit()
    print(f"✅ Created mock AIChatLog: {log_id} with topics: ['pricing', 'transport']")
    
    # 2. Submit positive feedback via the API endpoint
    print("\n👉 Submitting POSITIVE feedback...")
    payload = {
        "chat_log_id": log_id,
        "is_positive": True,
        "feedback_text": "جيد جداً"
    }
    
    response = client.post("/api/v1/learning/feedback", json=payload)
    print(f"  Response Status: {response.status_code}")
    print(f"  Response Content: {response.json()}")
    assert response.status_code == 200
    assert response.json()["is_positive"] is True
    
    # Verify preferences were adjusted (Positive: +0.1)
    db.expire_all()
    pricing_pref = db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.category == "pricing"
    ).first()
    
    transport_pref = db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.category == "transport"
    ).first()
    
    assert pricing_pref is not None
    assert transport_pref is not None
    print(f"✅ Positive adjustment success! pricing weight: {pricing_pref.weight:.2f}, transport weight: {transport_pref.weight:.2f}")
    assert abs(pricing_pref.weight - 1.1) < 0.001
    
    # 3. Submit negative feedback to check subtraction
    print("\n👉 Submitting NEGATIVE feedback...")
    payload_neg = {
        "chat_log_id": log_id,
        "is_positive": False,
        "feedback_text": "ليس دقيقاً"
    }
    response_neg = client.post("/api/v1/learning/feedback", json=payload_neg)
    assert response_neg.status_code == 200
    
    # Verify preferences were adjusted back (Negative: -0.1)
    db.expire_all()
    pricing_pref = db.query(UserPreference).filter(
        UserPreference.user_id == user_id,
        UserPreference.category == "pricing"
    ).first()
    
    print(f"✅ Negative adjustment success! pricing weight: {pricing_pref.weight:.2f}")
    assert abs(pricing_pref.weight - 1.0) < 0.001
    
    # Clean up test data
    db.query(InteractionFeedback).filter(InteractionFeedback.chat_log_id == log_id).delete()
    db.query(AIChatLog).filter(AIChatLog.id == log_id).delete()
    db.query(UserPreference).filter(UserPreference.user_id == user_id).delete()
    db.commit()
    db.close()
    
    print("\n🎉 FEEDBACK LOOP TEST PASSED 100% SUCCESS! 🎉")

if __name__ == "__main__":
    test_feedback_learning_loop()
