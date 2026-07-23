import sys
import os

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from app.schemas.chat import ChatRequest

def test_recommendation():
    print("🤖 Simulating Tourist Question...")
    print("Question: 'I am hungry, where should I eat in Marrakech?'")
    print("-" * 50)
    
    request = ChatRequest(
        message="I am hungry, where should I eat in Marrakech? Give me a top recommendation.",
        language="en",
        context_location="Jemaa El Fna"
    )
    
    response = ai_service.get_response(request)
    
    print("\n🧞 Mahir's Response:")
    print(response.message)
    print("-" * 50)
    
    if "Argana" in response.message:
        print("\n✅ SUCCESS: Mahir recommended your partner Café Argana!")
        print("💰 Revenue engine is now active.")
    else:
        print("\n⚠️ Note: Mahir did not mention the partner specifically. Try asking again or check logs.")

if __name__ == "__main__":
    test_recommendation()
