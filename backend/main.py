# ============================================================
# ZYVORA WEATHER INTELLIGENCE PLATFORM
# MAIN FASTAPI APPLICATION
# ============================================================

from datetime import datetime, timezone
from typing import Optional

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

# ============================================================
# INTERNAL IMPORTS
# ============================================================

from database import engine, SessionLocal, Base

from models import WeatherReport

from schemas import (
    ReportCreate,
    SocialReportCreate,
    VerificationUpdate,
)

from services import (
    analyze_report,
    get_live_weather,
)

from auth import (
    router as auth_router,
    get_current_admin,
)

from realtime_router import (
    router as realtime_router,
)

from ml_service import (
    predict_rain,
)

# Optional social ingestion service
try:
    from social_ingestion import collect_social_signals
except ImportError:
    collect_social_signals = None


# ============================================================
# ML REQUEST SCHEMA
# ============================================================

class RainPredictionRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100)
    max_temp: float
    min_temp: float
    season: str = Field(..., min_length=1, max_length=50)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ZYVORA Weather Intelligence API",
    version="2.0.0",
    description=(
        "AI-powered National Weather Intelligence Platform "
        "for real-time weather reports, trust analysis, "
        "social intelligence and machine learning."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origin_regex=(
        r"https?://"
        r"(localhost|127\.0\.0\.1|0\.0\.0\.0)"
        r":\d+"
    ),

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        "http://localhost:5174",
        "http://127.0.0.1:5174",

        "http://localhost:3000",
        "http://127.0.0.1:3000",

        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# DATABASE MIGRATION
# ============================================================

def migrate_database():
    """
    Safely add newly required columns to existing SQLite database.

    Existing data is preserved.
    """

    new_columns = {
        "source_name": "VARCHAR",
        "source_url": "TEXT",
        "external_id": "VARCHAR",
        "is_live_data": "BOOLEAN DEFAULT 0",
        "raw_data": "TEXT",
        "published_at": "DATETIME",
        "ingested_at": "DATETIME",
        "likes": "INTEGER DEFAULT 0",
        "replies": "INTEGER DEFAULT 0",
        "reposts": "INTEGER DEFAULT 0",
        "engagement_score": "FLOAT DEFAULT 0",
    }

    try:
        with engine.begin() as connection:

            result = connection.execute(
                text("PRAGMA table_info(weather_reports)")
            )

            existing_columns = {
                row[1]
                for row in result
            }

            for column, column_type in new_columns.items():

                if column not in existing_columns:

                    connection.execute(
                        text(
                            f"ALTER TABLE weather_reports "
                            f"ADD COLUMN {column} {column_type}"
                        )
                    )

                    print(
                        f"[DB MIGRATION] Added column: {column}"
                    )

    except Exception as error:

        print(
            "[DB MIGRATION ERROR]",
            str(error)
        )


migrate_database()


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)

app.include_router(realtime_router)


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_round(
    value,
    digits: int = 2
):
    """
    Safely round nullable numeric values.
    """

    if value is None:
        return 0

    try:
        return round(float(value), digits)

    except (TypeError, ValueError):
        return 0


def serialize_datetime(value):
    """
    Convert datetime to ISO format safely.
    """

    if value is None:
        return None

    try:
        return value.isoformat()

    except Exception:
        return str(value)


def serialize_report(report):
    """
    Convert WeatherReport SQLAlchemy object
    into frontend-friendly JSON.
    """

    return {
        "id": report.id,

        "description": report.description,

        "event_type": report.event_type,

        "city": report.city,

        "state": report.state,

        "latitude": report.latitude,

        "longitude": report.longitude,

        "source": report.source,

        "trust_score": safe_round(
            report.trust_score
        ),

        "verification_status": (
            report.verification_status
            or "Under Review"
        ),

        "duplicate_score": safe_round(
            report.duplicate_score
        ),

        "created_at": serialize_datetime(
            report.created_at
        ),

        # Optional fields.
        # These are returned only when they exist
        # in the current database/model.

        "source_name": getattr(
            report,
            "source_name",
            None
        ),

        "source_url": getattr(
            report,
            "source_url",
            None
        ),

        "external_id": getattr(
            report,
            "external_id",
            None
        ),

        "is_live_data": getattr(
            report,
            "is_live_data",
            False
        ),

        "published_at": serialize_datetime(
            getattr(
                report,
                "published_at",
                None
            )
        ),

        "ingested_at": serialize_datetime(
            getattr(
                report,
                "ingested_at",
                None
            )
        ),

        "likes": getattr(
            report,
            "likes",
            0
        ),

        "replies": getattr(
            report,
            "replies",
            0
        ),

        "reposts": getattr(
            report,
            "reposts",
            0
        ),

        "engagement_score": safe_round(
            getattr(
                report,
                "engagement_score",
                0
            )
        ),
    }


def get_recent_reports(
    db: Session,
    limit: int = 500
):
    """
    Get recent reports for AI analysis.
    """

    limit = max(
        1,
        min(limit, 1000)
    )

    return (
        db.query(WeatherReport)
        .order_by(
            WeatherReport.created_at.desc()
        )
        .limit(limit)
        .all()
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": (
            "ZYVORA Weather Intelligence "
            "Platform API is running"
        ),

        "status": "online",

        "version": "2.0.0",

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "services": {
            "weather_intelligence": True,
            "trust_analysis": True,
            "social_intelligence": True,
            "machine_learning": True,
            "admin_verification": True,
        },
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    database_status = "unknown"

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

            database_status = "connected"

    except Exception:

        database_status = "disconnected"

    return {
        "status": "online",

        "service": (
            "ZYVORA Weather Intelligence"
        ),

        "database": database_status,

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }


# ============================================================
# CREATE CITIZEN WEATHER REPORT
# ============================================================

@app.post("/api/reports")
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
):

    try:

        # ----------------------------------------------------
        # GET EXISTING REPORTS
        # ----------------------------------------------------

        existing_reports = get_recent_reports(
            db,
            500
        )

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        analysis = analyze_report(
            description=report_data.description,

            existing_reports=existing_reports,

            source=report_data.source,
        )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        detected_location = (
            analysis.get(
                "location",
                {}
            )
        )

        city = (
            report_data.city
            or detected_location.get("city")
        )

        state = (
            report_data.state
            or detected_location.get("state")
        )

        latitude = (
            report_data.latitude
            if report_data.latitude is not None
            else detected_location.get("latitude")
        )

        longitude = (
            report_data.longitude
            if report_data.longitude is not None
            else detected_location.get("longitude")
        )

        # ----------------------------------------------------
        # CREATE DATABASE RECORD
        # ----------------------------------------------------

        new_report = WeatherReport(

            description=(
                report_data.description
            ),

            event_type=(
                analysis.get(
                    "event_type",
                    "Unknown"
                )
            ),

            city=city,

            state=state,

            latitude=latitude,

            longitude=longitude,

            source=(
                report_data.source
                or "Citizen"
            ),

            trust_score=(
                analysis.get(
                    "trust_score",
                    0
                )
            ),

            verification_status=(
                analysis.get(
                    "verification_status",
                    "Under Review"
                )
            ),

            duplicate_score=(
                analysis.get(
                    "duplicate_score",
                    0
                )
            ),
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        db.add(new_report)

        db.commit()

        db.refresh(new_report)

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "status": "success",

            "message": (
                "Report processed successfully"
            ),

            "report": {
                "id": new_report.id,

                "description": (
                    new_report.description
                ),

                "event_type": (
                    new_report.event_type
                ),

                "location": {
                    "city": new_report.city,

                    "state": new_report.state,

                    "latitude": new_report.latitude,

                    "longitude": new_report.longitude,
                },

                "source": new_report.source,

                "trust_score": safe_round(
                    new_report.trust_score
                ),

                "verification_status": (
                    new_report.verification_status
                ),

                "duplicate_score": safe_round(
                    new_report.duplicate_score
                ),

                "weather": analysis.get(
                    "weather",
                    {}
                ),

                "trust_analysis": analysis.get(
                    "trust_analysis",
                    {}
                ),
            },
        }

    except HTTPException:
        raise

    except Exception as error:

        db.rollback()

        print(
            "[CREATE REPORT ERROR]",
            str(error)
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Unable to process weather report"
            ),
        )


# ============================================================
# GET ALL REPORTS
# ============================================================

@app.get("/api/reports")
def get_reports(
    limit: int = Query(
        100,
        ge=1,
        le=1000
    ),

    offset: int = Query(
        0,
        ge=0
    ),

    db: Session = Depends(get_db),
):

    reports = (
        db.query(WeatherReport)

        .order_by(
            WeatherReport.created_at.desc()
        )

        .offset(offset)

        .limit(limit)

        .all()
    )

    return [
        serialize_report(report)
        for report in reports
    ]


# ============================================================
# GET SINGLE REPORT
# ============================================================

@app.get("/api/reports/{report_id}")
def get_report(
    report_id: int,

    db: Session = Depends(get_db),
):

    report = (
        db.query(WeatherReport)

        .filter(
            WeatherReport.id == report_id
        )

        .first()
    )

    if not report:

        raise HTTPException(
            status_code=404,

            detail="Report not found",
        )

    return serialize_report(report)


# ============================================================
# DASHBOARD ANALYTICS
# ============================================================

@app.get("/api/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
):

    reports = (
        db.query(WeatherReport)
        .all()
    )

    total_reports = len(
        reports
    )

    verified_reports = sum(
        1
        for report in reports
        if report.verification_status
        == "Verified"
    )

    under_review_reports = sum(
        1
        for report in reports
        if report.verification_status
        == "Under Review"
    )

    suspicious_reports = sum(
        1
        for report in reports
        if report.verification_status
        == "Suspicious"
    )

    rejected_reports = sum(
        1
        for report in reports
        if report.verification_status
        == "Rejected"
    )

    duplicate_reports = sum(
        1
        for report in reports
        if (
            report.verification_status
            == "Duplicate"
        )
        or (
            (report.duplicate_score or 0)
            >= 75
        )
    )

    active_events = len(
        {
            report.event_type
            for report in reports
            if report.event_type
        }
    )

    social_reports = sum(
        1
        for report in reports
        if report.source
        == "Social Media"
    )

    citizen_reports = sum(
        1
        for report in reports
        if report.source
        == "Citizen"
    )

    average_trust_score = 0

    if reports:

        average_trust_score = round(
            sum(
                report.trust_score or 0
                for report in reports
            )
            / len(reports),
            2
        )

    # --------------------------------------------------------
    # STATUS DISTRIBUTION
    # --------------------------------------------------------

    status_distribution = {}

    for report in reports:

        status = (
            report.verification_status
            or "Unknown"
        )

        status_distribution[status] = (
            status_distribution.get(
                status,
                0
            )
            + 1
        )

    # --------------------------------------------------------
    # EVENT DISTRIBUTION
    # --------------------------------------------------------

    event_distribution = {}

    for report in reports:

        event = (
            report.event_type
            or "Unknown"
        )

        event_distribution[event] = (
            event_distribution.get(
                event,
                0
            )
            + 1
        )

    # --------------------------------------------------------
    # SOURCE DISTRIBUTION
    # --------------------------------------------------------

    source_distribution = {}

    for report in reports:

        source = (
            report.source
            or "Unknown"
        )

        source_distribution[source] = (
            source_distribution.get(
                source,
                0
            )
            + 1
        )

    return {

        "total_reports":
            total_reports,

        "verified_reports":
            verified_reports,

        "under_review_reports":
            under_review_reports,

        "suspicious_reports":
            suspicious_reports,

        "rejected_reports":
            rejected_reports,

        "duplicate_reports":
            duplicate_reports,

        "active_events":
            active_events,

        "social_reports":
            social_reports,

        "citizen_reports":
            citizen_reports,

        "average_trust_score":
            average_trust_score,

        "status_distribution":
            status_distribution,

        "event_distribution":
            event_distribution,

        "source_distribution":
            source_distribution,

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


# ============================================================
# SOCIAL INTELLIGENCE
# ============================================================

@app.post("/api/social/analyze")
def analyze_social_report(
    social_data: SocialReportCreate,

    db: Session = Depends(get_db),
):

    try:

        # ----------------------------------------------------
        # EXISTING REPORTS
        # ----------------------------------------------------

        existing_reports = get_recent_reports(
            db,
            500
        )

        source = "Social Media"

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        analysis = analyze_report(

            description=(
                social_data.description
            ),

            existing_reports=(
                existing_reports
            ),

            source=source,
        )

        location = analysis.get(
            "location",
            {}
        )

        # ----------------------------------------------------
        # CREATE SOCIAL REPORT
        # ----------------------------------------------------

        new_report = WeatherReport(

            description=(
                social_data.description
            ),

            event_type=(
                analysis.get(
                    "event_type",
                    "Unknown"
                )
            ),

            city=location.get(
                "city"
            ),

            state=location.get(
                "state"
            ),

            latitude=location.get(
                "latitude"
            ),

            longitude=location.get(
                "longitude"
            ),

            source=source,

            trust_score=(
                analysis.get(
                    "trust_score",
                    0
                )
            ),

            verification_status=(
                analysis.get(
                    "verification_status",
                    "Under Review"
                )
            ),

            duplicate_score=(
                analysis.get(
                    "duplicate_score",
                    0
                )
            ),
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        db.add(new_report)

        db.commit()

        db.refresh(new_report)

        return {

            "status": "success",

            "message": (
                "Social signal processed successfully"
            ),

            "platform": (
                social_data.platform
            ),

            "report": {

                "id":
                    new_report.id,

                "description":
                    new_report.description,

                "event_type":
                    new_report.event_type,

                "location": {

                    "city":
                        new_report.city,

                    "state":
                        new_report.state,

                    "latitude":
                        new_report.latitude,

                    "longitude":
                        new_report.longitude,
                },

                "source":
                    new_report.source,

                "trust_score":
                    safe_round(
                        new_report.trust_score
                    ),

                "verification_status":
                    new_report.verification_status,

                "duplicate_score":
                    safe_round(
                        new_report.duplicate_score
                    ),

                "weather":
                    analysis.get(
                        "weather",
                        {}
                    ),

                "trust_analysis":
                    analysis.get(
                        "trust_analysis",
                        {}
                    ),
            },
        }

    except Exception as error:

        db.rollback()

        print(
            "[SOCIAL ANALYSIS ERROR]",
            str(error)
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Unable to process social intelligence"
            ),
        )


# ============================================================
# SOCIAL INTELLIGENCE ALIAS
# ============================================================

@app.post("/api/social-intelligence")
def social_intelligence_alias(
    social_data: SocialReportCreate,

    db: Session = Depends(get_db),
):

    return analyze_social_report(
        social_data,
        db
    )


# ============================================================
# GET SOCIAL REPORTS
# ============================================================

@app.get("/api/social/reports")
def get_social_reports(
    limit: int = Query(
        100,
        ge=1,
        le=1000
    ),

    db: Session = Depends(get_db),
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

        .limit(limit)

        .all()
    )

    return [
        serialize_report(report)
        for report in reports
    ]


# ============================================================
# LIVE WEATHER API
# ============================================================

@app.get("/api/weather/current")
def get_current_weather(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180
    ),
):

    try:

        weather = get_live_weather(
            latitude,
            longitude
        )

        return {

            "status": "success",

            "latitude":
                latitude,

            "longitude":
                longitude,

            "weather":
                weather,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }

    except Exception as error:

        print(
            "[LIVE WEATHER ERROR]",
            str(error)
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Unable to fetch live weather"
            ),
        )


# ============================================================
# WEATHER FOR SPECIFIC REPORT
# ============================================================

@app.get("/api/reports/{report_id}/weather")
def get_report_weather(

    report_id: int,

    db: Session = Depends(get_db),
):

    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.id
            == report_id
        )

        .first()
    )

    if not report:

        raise HTTPException(
            status_code=404,

            detail="Report not found"
        )

    if (
        report.latitude is None
        or report.longitude is None
    ):

        raise HTTPException(
            status_code=400,

            detail=(
                "Report does not contain "
                "valid coordinates"
            )
        )

    try:

        weather = get_live_weather(

            report.latitude,

            report.longitude
        )

        return {

            "report_id":
                report.id,

            "city":
                report.city,

            "state":
                report.state,

            "latitude":
                report.latitude,

            "longitude":
                report.longitude,

            "weather":
                weather,
        }

    except Exception as error:

        print(
            "[REPORT WEATHER ERROR]",
            str(error)
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Unable to fetch weather "
                "for this report"
            )
        )


# ============================================================
# ADMIN VERIFY REPORT
# ============================================================

@app.put("/api/reports/{report_id}/verify")
def verify_report(

    report_id: int,

    update: VerificationUpdate,

    db: Session = Depends(get_db),

    admin=Depends(
        get_current_admin
    ),
):

    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.id
            == report_id
        )

        .first()
    )

    if not report:

        raise HTTPException(
            status_code=404,

            detail="Report not found"
        )

    allowed_statuses = [

        "Verified",

        "Under Review",

        "Suspicious",

        "Rejected",

        "Duplicate",
    ]

    if update.status not in allowed_statuses:

        raise HTTPException(
            status_code=400,

            detail=(
                "Invalid verification status. "
                f"Allowed values: "
                f"{', '.join(allowed_statuses)}"
            )
        )

    try:

        report.verification_status = (
            update.status
        )

        db.commit()

        db.refresh(report)

        return {

            "status": "success",

            "message":
                "Report verification updated",

            "report":
                serialize_report(report),
        }

    except Exception as error:

        db.rollback()

        print(
            "[VERIFY REPORT ERROR]",
            str(error)
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Unable to update report verification"
            )
        )


# ============================================================
# DELETE REPORT
# ============================================================

@app.delete("/api/reports/{report_id}")
def delete_report(

    report_id: int,

    db: Session = Depends(get_db),

    admin=Depends(
        get_current_admin
    ),
):

    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.id
            == report_id
        )

        .first()
    )

    if not report:

        raise HTTPException(
            status_code=404,

            detail="Report not found"
        )

    try:

        db.delete(report)

        db.commit()

        return {

            "status": "success",

            "message":
                "Report deleted successfully",

            "report_id":
                report_id,
        }

    except Exception as error:

        db.rollback()

        print(
            "[DELETE REPORT ERROR]",
            str(error)
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Unable to delete report"
            )
        )


# ============================================================
# ADMIN REPORT QUEUE
# ============================================================

@app.get("/api/admin/reports")
def get_admin_reports(

    limit: int = Query(
        200,
        ge=1,
        le=2000
    ),

    db: Session = Depends(get_db),

    admin=Depends(
        get_current_admin
    ),
):

    reports = (

        db.query(
            WeatherReport
        )

        .order_by(
            WeatherReport.created_at.desc()
        )

        .limit(limit)

        .all()
    )

    return [

        serialize_report(report)

        for report in reports
    ]


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.get("/api/admin/dashboard")
def get_admin_dashboard(

    db: Session = Depends(get_db),

    admin=Depends(
        get_current_admin
    ),
):

    reports = (
        db.query(
            WeatherReport
        )
        .all()
    )

    total = len(
        reports
    )

    verified = sum(
        1
        for r in reports
        if r.verification_status
        == "Verified"
    )

    pending = sum(
        1
        for r in reports
        if r.verification_status
        == "Under Review"
    )

    suspicious = sum(
        1
        for r in reports
        if r.verification_status
        == "Suspicious"
    )

    rejected = sum(
        1
        for r in reports
        if r.verification_status
        == "Rejected"
    )

    duplicate = sum(
        1
        for r in reports
        if (
            r.verification_status
            == "Duplicate"
        )
        or (
            (r.duplicate_score or 0)
            >= 75
        )
    )

    average_trust = 0

    if reports:

        average_trust = round(

            sum(
                r.trust_score or 0
                for r in reports
            )
            / total,

            2
        )

    return {

        "total_reports":
            total,

        "verified":
            verified,

        "pending":
            pending,

        "suspicious":
            suspicious,

        "rejected":
            rejected,

        "duplicate":
            duplicate,

        "average_trust_score":
            average_trust,
    }


# ============================================================
# ML RAIN / NO-RAIN PREDICTION
# ============================================================

@app.post("/api/ml/rain-prediction")
def rain_prediction(
    data: RainPredictionRequest
):

    try:

        if data.min_temp > data.max_temp:

            raise HTTPException(
                status_code=400,

                detail=(
                    "Minimum temperature cannot "
                    "be greater than maximum temperature"
                )
            )

        result = predict_rain(

            city=data.city,

            max_temp=data.max_temp,

            min_temp=data.min_temp,

            season=data.season,
        )

        return {

            "status":
                "success",

            "model":
                "Rain / No-Rain "
                "Random Forest Classifier",

            "input": {

                "city":
                    data.city,

                "max_temp":
                    data.max_temp,

                "min_temp":
                    data.min_temp,

                "season":
                    data.season,
            },

            "data":
                result,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)
        )

    except Exception as error:

        print(
            "[ML PREDICTION ERROR]",
            str(error)
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Unable to generate "
                "rain prediction"
            )
        )


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/api")
def api_information():

    return {

        "name":
            "ZYVORA Weather Intelligence API",

        "version":
            "2.0.0",

        "status":
            "online",

        "modules": {

            "weather":
                True,

            "citizen_reports":
                True,

            "social_intelligence":
                True,

            "trust_score":
                True,

            "duplicate_detection":
                True,

            "admin_verification":
                True,

            "live_weather":
                True,

            "rain_prediction":
                True,
        },

        "endpoints": {

            "health":
                "/api/health",

            "dashboard":
                "/api/dashboard",

            "reports":
                "/api/reports",

            "social":
                "/api/social/analyze",

            "social_reports":
                "/api/social/reports",

            "live_weather":
                "/api/weather/current",

            "rain_prediction":
                "/api/ml/rain-prediction",

            "admin_reports":
                "/api/admin/reports",

            "admin_dashboard":
                "/api/admin/dashboard",
        },
    }


# ============================================================
# APPLICATION STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
async def startup_event():

    print("=" * 60)

    print(
        "ZYVORA WEATHER INTELLIGENCE PLATFORM"
    )

    print(
        "FastAPI backend started successfully"
    )

    print(
        "API Docs: /docs"
    )

    print(
        "Health: /api/health"
    )

    print(
        "Dashboard: /api/dashboard"
    )

    print(
        "Reports: /api/reports"
    )

    print(
        "Social Intelligence: /api/social/analyze"
    )

    print(
        "ML Prediction: /api/ml/rain-prediction"
    )

    print("=" * 60)


# ============================================================
# END OF MAIN.PY
# ============================================================