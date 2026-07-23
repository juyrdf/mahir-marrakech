from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to Mahir AI.
    """
    return await ai_service.get_response(request, db)
