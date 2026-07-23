import os
import asyncio
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_ai():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("No API key found in .env")
        return

    print(f"Testing DeepSeek with key: {api_key[:5]}...")
    try:
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com",
            temperature=0.7
        )
        messages = [
            ("system", "You are a helpful guide."),
            ("human", "What is the best food in Marrakech?")
        ]
        response = llm.invoke(messages)
        print("AI Response:", response.content)
    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai())
