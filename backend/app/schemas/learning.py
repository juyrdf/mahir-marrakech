from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackRequest(BaseModel):
    chat_log_id: str
    is_positive: bool
    feedback_text: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    chat_log_id: str
    is_positive: bool
    created_at: datetime

class PreferenceUpdate(BaseModel):
    category: str
    weight_delta: float = 0.1

class UserPreferenceSchema(BaseModel):
    category: str
    weight: float
    last_interaction: datetime

    class Config:
        from_attributes = True
