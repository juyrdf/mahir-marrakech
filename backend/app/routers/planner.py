"""
Marrakech Companion - Smart Planner Router
FR-005: مخطط الرحلات الذكي (خطة يومية تلقائية)
"""
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.models import TripPlan, Place
from app.services.ai_service import ai_service

router = APIRouter()


# ─── Schemas ───────────────────────────────────────────
class PlanRequest(BaseModel):
    num_days: int = 3
    interests: List[str] = ["history", "food", "shopping"]
    budget_level: str = "medium"  # low, medium, high
    language: str = "ar"

class DayActivity(BaseModel):
    time: str
    place_name: str
    description: str
    category: str
    duration_minutes: int = 60
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DayPlan(BaseModel):
    day_number: int
    title: str
    activities: List[DayActivity]

class PlanResponse(BaseModel):
    plan_id: str
    num_days: int
    days: List[DayPlan]


# ─── Pre-built Marrakech Plans ───────────────────────────
MARRAKECH_PLANS = {
    "history": [
        DayActivity(time="09:00", place_name="قصر البديع", description="استكشف أطلال القصر الذهبي من القرن 16", category="history", duration_minutes=90, latitude=31.6189, longitude=-7.9854),
        DayActivity(time="11:00", place_name="مقابر السعديين", description="مقابر ملكية مزخرفة بالفسيفساء", category="history", duration_minutes=60, latitude=31.6166, longitude=-7.9882),
        DayActivity(time="14:00", place_name="مدرسة بن يوسف", description="أجمل مدرسة إسلامية في المغرب", category="history", duration_minutes=75, latitude=31.6317, longitude=-7.9870),
    ],
    "food": [
        DayActivity(time="10:00", place_name="سوق التوابل", description="تذوق التوابل المغربية الأصيلة", category="food", duration_minutes=60, latitude=31.6295, longitude=-7.9890),
        DayActivity(time="12:30", place_name="مطعم نارنج", description="طاجين تقليدي في قلب المدينة القديمة", category="food", duration_minutes=90, latitude=31.6310, longitude=-7.9830),
        DayActivity(time="16:00", place_name="مقهى الحاجة", description="أفضل عصير برتقال طازج في جامع الفنا", category="food", duration_minutes=45, latitude=31.6256, longitude=-7.9891),
    ],
    "shopping": [
        DayActivity(time="10:00", place_name="سوق الصباغين", description="الأقمشة والأصباغ التقليدية", category="shopping", duration_minutes=60, latitude=31.6304, longitude=-7.9872),
        DayActivity(time="12:00", place_name="سوق النحاسيين", description="الأواني النحاسية والمصابيح المغربية", category="shopping", duration_minutes=75, latitude=31.6320, longitude=-7.9855),
        DayActivity(time="15:00", place_name="كراميل مراكش", description="هدايا ومنتجات مغربية أصيلة", category="shopping", duration_minutes=60, latitude=31.6290, longitude=-7.9808),
    ],
    "nature": [
        DayActivity(time="09:00", place_name="حديقة ماجوريل", description="حديقة إيف سان لوران الشهيرة", category="nature", duration_minutes=90, latitude=31.6416, longitude=-8.0031),
        DayActivity(time="12:00", place_name="حدائق المنارة", description="حدائق تاريخية مع حوض ماء كبير", category="nature", duration_minutes=60, latitude=31.6230, longitude=-8.0220),
        DayActivity(time="15:00", place_name="واحة النخيل", description="100,000 نخلة شمال مراكش", category="nature", duration_minutes=120, latitude=31.6610, longitude=-8.0100),
    ],
}


# ─── Generate Plan ───────────────────────────────────────
@router.post("/generate", response_model=PlanResponse)
async def generate_plan(req: PlanRequest, db: Session = Depends(get_db)):
    """توليد خطة رحلة ذكية حسب الاهتمامات"""
    plan_id = str(uuid.uuid4())
    
    # Try AI Generation first
    ai_plans = await ai_service.generate_itinerary(req.num_days, req.interests, req.language)
    
    if ai_plans:
        days = []
        for d in ai_plans:
            # Ensure proper schema mapping
            activities = [DayActivity(**act) for act in d.get('activities', [])]
            days.append(DayPlan(
                day_number=d.get('day_number', 1),
                title=d.get('title', "Daily Plan"),
                activities=activities
            ))
    else:
        # Fallback to Template Logic
        days = []
        # ... (rest of existing template logic)
    
    # Mix activities based on interests
    all_activities = []
    for interest in req.interests:
        if interest in MARRAKECH_PLANS:
            all_activities.extend(MARRAKECH_PLANS[interest])
    
    # If no matching interests, use all
    if not all_activities:
        for acts in MARRAKECH_PLANS.values():
            all_activities.extend(acts)
    
    # Distribute across days
    activities_per_day = max(3, len(all_activities) // req.num_days)
    
    for day_num in range(1, req.num_days + 1):
        start_idx = (day_num - 1) * activities_per_day
        end_idx = start_idx + activities_per_day
        day_activities = all_activities[start_idx:end_idx]
        
        if not day_activities:
            # Wrap around
            day_activities = all_activities[:activities_per_day]
        
        # Update times for the day
        for i, act in enumerate(day_activities):
            hours = 9 + (i * 2)
            act.time = f"{hours:02d}:00"
        
        day_titles = {
            1: "🕌 استكشاف المدينة القديمة",
            2: "🍽️ مذاقات مراكش",
            3: "🛍️ التسوق والحرف التقليدية",
            4: "🌿 الطبيعة والاسترخاء",
            5: "🎭 الثقافة والفن",
        }
        
        days.append(DayPlan(
            day_number=day_num,
            title=day_titles.get(day_num, f"📅 اليوم {day_num}"),
            activities=day_activities
        ))
    
    # Save to DB
    trip = TripPlan(
        id=plan_id,
        num_days=req.num_days,
        interests=json.dumps(req.interests),
        plan_data=json.dumps([d.model_dump() for d in days]),
    )
    db.add(trip)
    db.commit()
    
    return PlanResponse(plan_id=plan_id, num_days=req.num_days, days=days)


# ─── Get Saved Plan ─────────────────────────────────────
@router.get("/{plan_id}")
def get_plan(plan_id: str, db: Session = Depends(get_db)):
    """استرجاع خطة رحلة محفوظة"""
    trip = db.query(TripPlan).filter(TripPlan.id == plan_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="الخطة غير موجودة / Plan not found")
    
    return {
        "plan_id": trip.id,
        "num_days": trip.num_days,
        "interests": json.loads(trip.interests),
        "days": json.loads(trip.plan_data),
        "created_at": str(trip.created_at)
    }
