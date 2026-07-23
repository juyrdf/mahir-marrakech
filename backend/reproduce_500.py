
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.schemas.chat import ChatRequest
from app.services.ai_service import ai_service
import sys

async def reproduce():
    print("Testing ai_service.get_response directly...")
    db = SessionLocal()
    try:
        request = ChatRequest(
            message="Salam! Who are you?",
            context_location="Jemaa el-Fnaa"
        )
        response = await ai_service.get_response(request, db)
        print("Response:", response.response)
    except Exception as e:
        print("Caught Exception:")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(reproduce())
