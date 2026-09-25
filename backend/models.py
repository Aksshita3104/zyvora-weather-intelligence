from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean
)

from sqlalchemy.sql import func

from database import Base


class WeatherReport(Base):

    __tablename__ = "weather_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==========================================
    # CORE REPORT DATA
    # ==========================================

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

    # ==========================================
    # SOURCE
    # ==========================================

    source = Column(
        String,
        default="Citizen"
    )

    source_name = Column(
        String,
        nullable=True
    )

    source_url = Column(
        Text,
        nullable=True
    )

    external_id = Column(
        String,
        nullable=True,
        index=True
    )

    # ==========================================
    # LIVE DATA
    # ==========================================

    is_live_data = Column(
        Boolean,
        default=False
    )

    raw_data = Column(
        Text,
        nullable=True
    )

    published_at = Column(
        DateTime,
        nullable=True
    )

    ingested_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ==========================================
    # SOCIAL METRICS
    # ==========================================

    likes = Column(
        Integer,
        default=0
    )

    replies = Column(
        Integer,
        default=0
    )

    reposts = Column(
        Integer,
        default=0
    )

    engagement_score = Column(
        Float,
        default=0
    )

    # ==========================================
    # AI TRUST ANALYSIS
    # ==========================================

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

    # ==========================================
    # CREATED
    # ==========================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )