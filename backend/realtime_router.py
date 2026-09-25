# ==========================================
# ZYVORA
# REAL-TIME API ROUTES
# ==========================================

import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from weather_service import (
    get_live_weather_dashboard
)

from sqlalchemy.orm import Session

from database import (
    SessionLocal
)

from models import (
    WeatherReport
)

from realtime_service import (

    ingest_live_weather,

    ingest_live_news,

    ingest_live_social,

    run_complete_ingestion

)

from news_service import (
    fetch_live_news
)

from social_service import (
    fetch_live_social_data
)


# ==========================================
# ROUTER
# ==========================================

router = APIRouter(

    prefix="/api/realtime",

    tags=[
        "Real-Time Intelligence"
    ]

)


# ==========================================
# DATABASE SESSION
# ==========================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ==========================================
# SERIALIZER
# ==========================================

def serialize_live_report(
    report
):

    return {

        "id":
            report.id,

        "description":
            report.description,

        "event_type":
            report.event_type,

        "location": {

            "city":
                report.city,

            "state":
                report.state,

            "latitude":
                report.latitude,

            "longitude":
                report.longitude

        },

        "source":
            report.source,

        "source_name":
            report.source_name,

        "source_url":
            report.source_url,

        "is_live_data":
            report.is_live_data,

        "trust_score":
            report.trust_score,

        "verification_status":
            report.verification_status,

        "duplicate_score":
            report.duplicate_score,

        "likes":
            report.likes,

        "replies":
            report.replies,

        "reposts":
            report.reposts,

        "engagement_score":
            report.engagement_score,

        "published_at":

            report.published_at.isoformat()

            if report.published_at

            else None,

        "created_at":

            report.created_at.isoformat()

            if report.created_at

            else None

    }


# ==========================================
# REAL-TIME STATUS
# ==========================================

@router.get(
    "/status"
)

def realtime_status(

    db: Session = Depends(
        get_db
    )

):

    live_reports = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.is_live_data
            == True
        )

        .count()

    )


    news_reports = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.source
            == "News"
        )

        .count()

    )


    social_reports = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.source
            == "Social Media"
        )

        .count()

    )


    weather_reports = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.source
            == "Weather API"
        )

        .count()

    )


    return {

        "status":
            "online",

        "live_reports":
            live_reports,

        "weather_reports":
            weather_reports,

        "news_reports":
            news_reports,

        "social_reports":
            social_reports

    }


# ==========================================
# PREVIEW LIVE NEWS
# ==========================================

@router.get(
    "/news/preview"
)

def preview_live_news():

    return fetch_live_news(
        max_records=20
    )


# ==========================================
# INGEST NEWS
# ==========================================

@router.post(
    "/news/ingest"
)

def ingest_news(

    max_records: int = 20,

    db: Session = Depends(
        get_db
    )

):

    return ingest_live_news(

        db,

        max_records

    )


# ==========================================
# PREVIEW SOCIAL
# ==========================================

@router.get(
    "/social/preview"
)

def preview_social():

    return fetch_live_social_data(
        max_results=20
    )


# ==========================================
# INGEST SOCIAL
# ==========================================

@router.post(
    "/social/ingest"
)

def ingest_social(

    max_records: int = 20,

    db: Session = Depends(
        get_db
    )

):

    return ingest_live_social(

        db,

        max_records

    )


# ==========================================
# INGEST LIVE WEATHER
# ==========================================

@router.post(
    "/weather/ingest"
)

def ingest_weather(

    db: Session = Depends(
        get_db
    )

):

    return ingest_live_weather(
        db
    )


# ==========================================
# COMPLETE INGESTION
# ==========================================

@router.post(
    "/ingest"
)

def ingest_everything(

    include_weather: bool = True,

    include_news: bool = True,

    include_social: bool = True,

    db: Session = Depends(
        get_db
    )

):

    return run_complete_ingestion(

        db=db,

        include_weather=
            include_weather,

        include_news=
            include_news,

        include_social=
            include_social

    )


# ==========================================
# GET LIVE REPORTS
# ==========================================

@router.get(
    "/reports"
)

def get_live_reports(

    limit: int = 100,

    db: Session = Depends(
        get_db
    )

):

    reports = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.is_live_data
            == True
        )

        .order_by(
            WeatherReport.created_at.desc()
        )

        .limit(
            limit
        )

        .all()

    )


    return [

        serialize_live_report(
            report
        )

        for report in reports

    ]


# ==========================================
# LIVE NEWS REPORTS
# ==========================================

@router.get(
    "/news/reports"
)

def get_news_reports(

    limit: int = 100,

    db: Session = Depends(
        get_db
    )

):

    reports = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.source
            == "News"
        )

        .order_by(
            WeatherReport.created_at.desc()
        )

        .limit(
            limit
        )

        .all()

    )


    return [

        serialize_live_report(
            report
        )

        for report in reports

    ]


# ==========================================
# LIVE SOCIAL REPORTS
# ==========================================

@router.get(
    "/social/reports"
)

def get_live_social_reports(

    limit: int = 100,

    db: Session = Depends(
        get_db
    )

):

    reports = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.source
            == "Social Media"
        )

        .order_by(
            WeatherReport.created_at.desc()
        )

        .limit(
            limit
        )

        .all()

    )


    return [

        serialize_live_report(
            report
        )

        for report in reports

    ]
# ==========================================
# LIVE WEATHER DASHBOARD
# ==========================================

@router.get(
    "/weather/current"
)
def get_current_live_weather(

    latitude: float,

    longitude: float

):

    result = (
        get_live_weather_dashboard(

            latitude,

            longitude

        )
    )

    return result