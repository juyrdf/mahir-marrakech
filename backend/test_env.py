from app.core.config import settings

print(f"GOOGLE_API_KEY loaded: {bool(settings.GOOGLE_API_KEY)}")
if settings.GOOGLE_API_KEY:
    print(f"Key length: {len(settings.GOOGLE_API_KEY)}")
    print(f"Key starts with: {settings.GOOGLE_API_KEY[:10]}...")
else:
    print("ERROR: No API key found!")
