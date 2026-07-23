from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    latitude: float
    longitude: float

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    language: str = "en"
    location: Optional[Location] = None
    image_url: Optional[str] = None
    context_location: str = "unknown"  # Keeping for backward compatibility

class ChatResponse(BaseModel):
    id: Optional[str] = None
    response: str
    conversation_id: Optional[str] = None
    safety_alert: bool = False
    results_cards: Optional[list] = []

