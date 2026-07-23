from fastapi import APIRouter
from app.schemas.config import AppConfigResponse, AppConfigData, FeaturesConfig, CoinsConfig

router = APIRouter()

@router.get("/app-settings", response_model=AppConfigResponse)
async def get_app_settings():
    """
    Returns application configuration, minimum app versions, feature flags, and coin settings.
    This endpoint should be fetched by the mobile app on startup.
    """
    return AppConfigResponse(
        success=True,
        data=AppConfigData(
            min_app_version="1.0.0",
            force_update=False,
            maintenance_mode=False,
            features=FeaturesConfig(
                ai_chat=True,
                voice_mode=True,
                offline_maps=True,
                scam_shield=True
            ),
            coins_config=CoinsConfig(
                ride_earn=10,
                review_earn=15,
                review_with_photo_earn=20,
                report_scam_earn=20
            )
        )
    )
