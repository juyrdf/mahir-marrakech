"""
Marrakech Companion - بيانات أولية لمناطق النصب في مراكش
يُشغَّل مرة واحدة لملء قاعدة البيانات
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, engine, Base
from app.models import ScamZone
import uuid

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

SCAM_ZONES = [
    {
        "name": "ساحة جامع الفنا - باعة متجولون",
        "description": "بعض الباعة يفرضون أسعاراً مبالغة على السياح. لا تقبل أي شيء من يد أحد دون السؤال عن السعر أولاً.",
        "latitude": 31.6256,
        "longitude": -7.9891,
        "radius_meters": 300,
        "severity": "high",
        "tips": "اسأل عن السعر قبل لمس أي منتج. تفاوض دائماً. السعر العادل عادة 30-50% من السعر الأول المعروض."
    },
    {
        "name": "مدخل السوق الكبير - مرشدون وهميون",
        "description": "أشخاص يعرضون إرشادك داخل الأسواق ثم يطلبون مبالغ كبيرة. لا تتبع أي شخص لا تعرفه.",
        "latitude": 31.6295,
        "longitude": -7.9867,
        "radius_meters": 200,
        "severity": "high",
        "tips": "ارفض بأدب وقل 'لا شكراً'. استخدم GPS التطبيق بدلاً من المرشدين العشوائيين."
    },
    {
        "name": "محيط مقهى فرنسا - صرف العملات",
        "description": "بعض المحلات تعرض صرف عملات بأسعار سيئة جداً.",
        "latitude": 31.6260,
        "longitude": -7.9885,
        "radius_meters": 150,
        "severity": "medium",
        "tips": "استخدم فقط مكاتب الصرف الرسمية أو ATM البنكية. سعر الصرف الرسمي: 1 EUR ≈ 11 MAD."
    },
    {
        "name": "سوق الجلد (الدباغين)",
        "description": "يُعطونك نعناع ثم يطلبون رسوم دخول مبالغة. الدخول مجاني فعلياً.",
        "latitude": 31.6340,
        "longitude": -7.9830,
        "radius_meters": 200,
        "severity": "medium",
        "tips": "الدخول مجاني. 10-20 درهم كافية كإكرامية. لا تقبل 'المرشد' الذي يقودك إلى متجر جلد بعينه."
    },
    {
        "name": "محطة التاكسي - سعر زائد",
        "description": "بعض سائقي التاكسي لا يستخدمون العداد ويطلبون أضعاف السعر الحقيقي.",
        "latitude": 31.6300,
        "longitude": -7.9920,
        "radius_meters": 250,
        "severity": "high",
        "tips": "اطلب تشغيل العداد دائماً (Compteur). السعر داخل المدينة: 10-20 MAD. من المطار: 70-100 MAD فقط."
    },
    {
        "name": "حدائق ماجوريل - بائعو تذاكر وهمية",
        "description": "أشخاص يبيعون تذاكر مزيفة أمام المدخل. اشترِ فقط من الشباك الرسمي.",
        "latitude": 31.6416,
        "longitude": -8.0031,
        "radius_meters": 150,
        "severity": "low",
        "tips": "التذاكر فقط من الشباك الرسمي أمام المدخل. السعر: 70 MAD. لا تشترِ من أي شخص في الشارع."
    },
    {
        "name": "باب أغناو - حناء قسرية",
        "description": "نساء يمسكن يدك ويرسمن الحناء دون إذنك ثم يطلبن 200-500 درهم.",
        "latitude": 31.6183,
        "longitude": -7.9870,
        "radius_meters": 200,
        "severity": "high",
        "tips": "لا تمد يدك لأي شخص. إذا أردتِ حناء، اذهبي لمحل معروف. السعر العادل: 50-100 MAD لتصميم صغير."
    },
]

# Clear old data
db.query(ScamZone).delete()
db.commit()

for zone_data in SCAM_ZONES:
    zone = ScamZone(
        id=str(uuid.uuid4()),
        is_active=True,
        **zone_data
    )
    db.add(zone)

db.commit()
print(f"✅ تم إدخال {len(SCAM_ZONES)} منطقة نصب في قاعدة البيانات")
db.close()
