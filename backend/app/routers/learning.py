from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import InteractionFeedback, UserPreference, AIChatLog
from app.schemas.learning import FeedbackRequest, FeedbackResponse, PreferenceUpdate
import uuid

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    # Verify chat log exists
    chat_log = db.query(AIChatLog).filter(AIChatLog.id == request.chat_log_id).first()
    if not chat_log:
        raise HTTPException(status_code=404, detail="Chat log not found")
    
    feedback = InteractionFeedback(
        id=str(uuid.uuid4()),
        chat_log_id=request.chat_log_id,
        is_positive=request.is_positive,
        feedback_text=request.feedback_text
    )
    db.add(feedback)
    
    # Update user preferences based on feedback
    if chat_log.topic_tag:
        import json
        try:
            tags = json.loads(chat_log.topic_tag)
            for tag in tags:
                pref = db.query(UserPreference).filter(
                    UserPreference.user_id == chat_log.user_id,
                    UserPreference.category == tag
                ).first()
                
                delta = 0.1 if request.is_positive else -0.1
                if pref:
                    pref.weight = max(0.0, pref.weight + delta)
                else:
                    new_pref = UserPreference(
                        id=str(uuid.uuid4()),
                        user_id=chat_log.user_id,
                        category=tag,
                        weight=1.0 + delta
                    )
                    db.add(new_pref)
        except:
            pass # Invalid JSON in topic_tag

    db.commit()
    db.refresh(feedback)
    return feedback

@router.get("/preferences/{user_id}")
def get_user_preferences(user_id: str, db: Session = Depends(get_db)):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).all()
    return prefs
