from pydantic import BaseModel
from typing import Optional

class FeaturesConfig(BaseModel):
    ai_chat: bool = True
    voice_mode: bool = True
    offline_maps: bool = True
    scam_shield: bool = True

class CoinsConfig(BaseModel):
    ride_earn: int = 10
    review_earn: int = 15
    review_with_photo_earn: int = 20
    report_scam_earn: int = 20

class AppConfigData(BaseModel):
    min_app_version: str = "1.0.0"
    force_update: bool = False
    maintenance_mode: bool = False
    features: FeaturesConfig
    coins_config: CoinsConfig

class AppConfigResponse(BaseModel):
    success: bool = True
    data: AppConfigData
