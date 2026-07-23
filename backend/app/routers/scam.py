"""
Marrakech Companion - Scam Shield Router
FR-006: درع النصب (مناطق النصب، تنبيهات، إبلاغ)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.models import ScamZone

router = APIRouter()


# ─── Schemas ───────────────────────────────────────────
class ScamZoneCreate(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float
    radius_meters: int = 500
    severity: str = "medium"  # low, medium, high
    tips: Optional[str] = None

class ScamZoneResponse(BaseModel):
    id: str
    name: str
    description: str
    latitude: float
    longitude: float
    radius_meters: int
    severity: str
    tips: Optional[str]

    class Config:
        from_attributes = True

class ScamReportRequest(BaseModel):
    latitude: float
    longitude: float
    description: str
    scam_type: Optional[str] = None


class NearbyCheckRequest(BaseModel):
    latitude: float
    longitude: float


# ─── GET All Scam Zones ──────────────────────────────────
@router.get("/zones", response_model=List[ScamZoneResponse])
def get_scam_zones(db: Session = Depends(get_db)):
    """الحصول على جميع مناطق النصب المعروفة"""
    zones = db.query(ScamZone).filter(ScamZone.is_active == True).all()
    return zones


# ─── Check Nearby Scam Zones ─────────────────────────────
@router.post("/check-nearby")
def check_nearby_scams(req: NearbyCheckRequest, db: Session = Depends(get_db)):
    """التحقق من وجود مناطق نصب قريبة من موقع المستخدم"""
    import math
    
    zones = db.query(ScamZone).filter(ScamZone.is_active == True).all()
    nearby = []
    
    for zone in zones:
        # Haversine distance calculation
        lat1, lon1 = math.radians(req.latitude), math.radians(req.longitude)
        lat2, lon2 = math.radians(zone.latitude), math.radians(zone.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_meters = 6371000 * c  # Earth radius in meters
        
        if distance_meters <= zone.radius_meters:
            nearby.append({
                "zone": ScamZoneResponse.model_validate(zone),
                "distance_meters": round(distance_meters),
                "alert": True
            })
    
    return {
        "is_safe": len(nearby) == 0,
        "nearby_zones": nearby,
        "total_alerts": len(nearby)
    }


# ─── Report Scam (Anonymous) ────────────────────────────
@router.post("/report")
def report_scam(req: ScamReportRequest, db: Session = Depends(get_db)):
    """إبلاغ مجهول عن عملية نصب"""
    import uuid
    
    report = ScamZone(
        id=str(uuid.uuid4()),
        name=f"تبليغ مستخدم - {req.scam_type or 'عام'}",
        description=req.description,
        latitude=req.latitude,
        longitude=req.longitude,
        radius_meters=200,
        severity="reported",
        is_active=False  # Needs admin review
    )
    db.add(report)
    db.commit()
    
    return {"status": "تم الإبلاغ بنجاح / Report submitted", "report_id": report.id}
