from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.planner import router as planner_router
from app.routers.config import router as config_router
from app.routers.chat import router as chat_router
from app.routers.transport import router as transport_router
from app.routers.admin import router as admin_router
from app.routers.sync import router as sync_router
from app.routers.places import router as places_router
from app.routers.prices import router as prices_router
from app.routers.scam import router as scam_router
from app.routers.tours import router as tours_router
from app.routers.restaurants import router as restaurants_router
from app.routers.learning import router as learning_router
from app.core.seeding import seed_db
from app.core.database import engine, Base, SessionLocal
from app.models import Driver, Place, ScamZone, TripPlan

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Create Database Tables
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_populate():
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    
    # DEBUG: Print all registered routes on startup
    print("\n🚀 Registered Routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.path}")
    print("======================\n")

# Resolve paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Mount Static Files
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir()

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(planner_router, prefix="/api/v1/planner", tags=["planner"])
app.include_router(config_router, prefix="/api/v1/config", tags=["config"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(transport_router, prefix="/api/v1/transport", tags=["transport"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(sync_router, prefix="/api/v1/sync", tags=["sync"])
app.include_router(places_router, prefix="/api/v1/places", tags=["places"])
app.include_router(prices_router, prefix="/api/v1/prices", tags=["prices"])
app.include_router(scam_router, prefix="/api/v1/scam", tags=["scam"])
app.include_router(tours_router, prefix="/api/v1/tours", tags=["tours"])
app.include_router(restaurants_router, prefix="/api/v1/restaurants", tags=["restaurants"])
app.include_router(learning_router, prefix="/api/v1/learning", tags=["learning"])
# app.include_router(planner.router, prefix="/api/v1/planner", tags=["planner"])

@app.get("/")
def root():
    return {"message": "Welcome to Marrakech Companion API v2", "status": "active", "version": "2.0.0"}

@app.get("/admin", include_in_schema=False)
async def admin_dashboard():
    return FileResponse(STATIC_DIR / "admin.html")

# Serve Mobile PWA
MOBILE_WEB_DIR = BASE_DIR.parent / "mobile_web"
print(f"DEBUG: Mounting PWA from {MOBILE_WEB_DIR} (Exists: {MOBILE_WEB_DIR.exists()})")

if not MOBILE_WEB_DIR.exists():
    MOBILE_WEB_DIR.mkdir()

app.mount("/pwa", StaticFiles(directory=str(MOBILE_WEB_DIR)), name="pwa")

@app.get("/app", include_in_schema=False)
async def mobile_app():
    return FileResponse(MOBILE_WEB_DIR / "index.html")

@app.get("/pwa/sw.js", include_in_schema=False)
async def service_worker():
    sw_path = MOBILE_WEB_DIR / "sw.js"
    content = sw_path.read_text()
    return Response(content, media_type="application/javascript")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
