from pydantic import (
    BaseModel,
    Field
)

from typing import Optional


# ==========================================
# CITIZEN REPORT
# ==========================================

class ReportCreate(BaseModel):

    description: str = Field(
        min_length=3
    )

    city: Optional[str] = None

    state: Optional[str] = None

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    source: str = "Citizen"


# ==========================================
# MANUAL SOCIAL REPORT
# KEPT FOR BACKWARD COMPATIBILITY
# ==========================================

class SocialReportCreate(BaseModel):

    description: str = Field(
        min_length=3
    )

    platform: str = "X / Twitter"


# ==========================================
# ADMIN VERIFICATION
# ==========================================

class VerificationUpdate(BaseModel):

    status: str


# ==========================================
# WEATHER QUERY
# ==========================================

class WeatherQuery(BaseModel):

    latitude: float

    longitude: float


# ==========================================
# REAL-TIME INGESTION
# ==========================================

class RealtimeIngestionRequest(BaseModel):

    include_weather: bool = True

    include_news: bool = True

    include_social: bool = True

    max_news_records: int = Field(
        default=20,
        ge=1,
        le=50
    )

    max_social_records: int = Field(
        default=20,
        ge=1,
        le=100
    )