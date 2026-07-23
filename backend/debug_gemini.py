import os
import sys

# Add backend directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService
from app.schemas.chat import ChatRequest
import asyncio

os.environ["GOOGLE_API_KEY"] = "AIzaSyAi7k_WE1WQ-hkSBGDxBpVpG8SabweSd6E"

async def test():
    print("Initializing AIService...")
    service = AIService()
    req = ChatRequest(message="فين نقدر نتعشى", context_location="unknown", language="en")
    
    print("\nCalling get_response...")
    # Passing None for db since get_response only uses db for prices
    try:
        res = await service.get_response(req, None)
        print("Final Response:", res.response)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
