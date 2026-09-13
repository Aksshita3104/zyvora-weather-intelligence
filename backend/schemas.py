from pydantic import BaseModel, Field
from typing import Optional


class ReportCreate(BaseModel):

    description: str = Field(
        min_length=3
    )

    city: Optional[str] = None

    state: Optional[str] = None

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    source: str = "Citizen"


class SocialReportCreate(BaseModel):

    description: str = Field(
        min_length=3
    )

    platform: str = "X / Twitter"


class VerificationUpdate(BaseModel):

    status: str


class WeatherQuery(BaseModel):

    latitude: float

    longitude: float