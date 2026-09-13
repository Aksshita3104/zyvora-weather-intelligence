from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func

from database import Base


class WeatherReport(Base):

    __tablename__ = "weather_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    description = Column(
        Text,
        nullable=False
    )

    event_type = Column(
        String,
        nullable=False
    )

    city = Column(
        String,
        nullable=True
    )

    state = Column(
        String,
        nullable=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    source = Column(
        String,
        default="Citizen"
    )

    trust_score = Column(
        Float,
        default=0
    )

    verification_status = Column(
        String,
        default="Under Review"
    )

    duplicate_score = Column(
        Float,
        default=0.0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )