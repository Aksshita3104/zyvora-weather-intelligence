# ==========================================
# ZYVORA WEATHER INTELLIGENCE PLATFORM
# MAIN FASTAPI APPLICATION
# ==========================================


from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from sqlalchemy.orm import (
    Session
)

from typing import Optional


# ==========================================
# DATABASE
# ==========================================

from database import (
    engine,
    SessionLocal,
    Base
)


# ==========================================
# MODELS
# ==========================================

from models import (
    WeatherReport
)


# ==========================================
# SCHEMAS
# ==========================================

from schemas import (

    ReportCreate,

    SocialReportCreate,

    VerificationUpdate

)


# ==========================================
# SERVICES
# ==========================================

from services import (

    analyze_report,

    get_live_weather

)


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

Base.metadata.create_all(
    bind=engine
)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(

    title=
        "ZYVORA Weather Intelligence API",

    version=
        "1.0.0",

    description=
        (
            "AI-powered National Weather "
            "Intelligence Platform"
        )

)


# ==========================================
# CORS
# ==========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
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
# HELPER
# REPORT SERIALIZER
# ==========================================

def serialize_report(
    report
):

    return {

        "id":
            report.id,

        "description":
            report.description,

        "event_type":
            report.event_type,

        "city":
            report.city,

        "state":
            report.state,

        "latitude":
            report.latitude,

        "longitude":
            report.longitude,

        "source":
            report.source,

        "trust_score":
            round(
                report.trust_score or 0,
                2
            ),

        "verification_status":
            report.verification_status,

        "duplicate_score":
            round(
                report.duplicate_score or 0,
                2
            ),

        "created_at":

            report.created_at.isoformat()

            if report.created_at

            else None

    }


# ==========================================
# ROOT
# ==========================================

@app.get("/")

def root():

    return {

        "message":
            (
                "ZYVORA Weather Intelligence "
                "Platform API is running"
            ),

        "status":
            "online"

    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/api/health")

def health():

    return {

        "status":
            "online",

        "service":
            "ZYVORA Weather Intelligence"

    }


# ==========================================
# CREATE CITIZEN REPORT
# ==========================================

@app.post("/api/reports")

def create_report(

    report_data: ReportCreate,

    db: Session = Depends(
        get_db
    )

):

    # Get existing reports

    existing_reports = (

        db.query(
            WeatherReport
        )

        .order_by(
            WeatherReport.created_at.desc()
        )

        .limit(
            500
        )

        .all()

    )


    # AI ANALYSIS

    analysis = analyze_report(

        description=
            report_data.description,

        existing_reports=
            existing_reports,

        source=
            report_data.source

    )


    # DETECTED LOCATION

    detected_location = (
        analysis["location"]
    )


    # USE USER LOCATION IF PROVIDED

    city = (

        report_data.city

        or

        detected_location.get(
            "city"
        )

    )


    state = (

        report_data.state

        or

        detected_location.get(
            "state"
        )

    )


    latitude = (

        report_data.latitude

        if report_data.latitude is not None

        else

        detected_location.get(
            "latitude"
        )

    )


    longitude = (

        report_data.longitude

        if report_data.longitude is not None

        else

        detected_location.get(
            "longitude"
        )

    )


    # CREATE DATABASE REPORT

    new_report = WeatherReport(

        description=
            report_data.description,

        event_type=
            analysis["event_type"],

        city=
            city,

        state=
            state,

        latitude=
            latitude,

        longitude=
            longitude,

        source=
            report_data.source,

        trust_score=
            analysis["trust_score"],

        verification_status=
            analysis[
                "verification_status"
            ],

        duplicate_score=
            analysis[
                "duplicate_score"
            ]

    )


    # SAVE

    db.add(
        new_report
    )

    db.commit()

    db.refresh(
        new_report
    )


    # RESPONSE

    return {

        "message":
            "Report processed successfully",

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
                    new_report.longitude

            },

            "source":
                new_report.source,

            "trust_score":
                new_report.trust_score,

            "verification_status":
                new_report.verification_status,

            "duplicate_score":
                new_report.duplicate_score,

            "weather":
                analysis[
                    "weather"
                ],

            "trust_analysis":
                analysis[
                    "trust_analysis"
                ]

        }

    }


# ==========================================
# GET ALL REPORTS
# ==========================================

@app.get("/api/reports")

def get_reports(

    limit: int = 100,

    db: Session = Depends(
        get_db
    )

):

    reports = (

        db.query(
            WeatherReport
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

        serialize_report(
            report
        )

        for report in reports

    ]


# ==========================================
# GET SINGLE REPORT
# ==========================================

@app.get("/api/reports/{report_id}")

def get_report(

    report_id: int,

    db: Session = Depends(
        get_db
    )

):

    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.id == report_id
        )

        .first()

    )


    if not report:

        raise HTTPException(

            status_code=404,

            detail=
                "Report not found"

        )


    return serialize_report(
        report
    )


# ==========================================
# DASHBOARD ANALYTICS
# ==========================================

@app.get("/api/dashboard")

def get_dashboard(

    db: Session = Depends(
        get_db
    )

):

    reports = (

        db.query(
            WeatherReport
        )

        .all()

    )


    total_reports = len(
        reports
    )


    verified_reports = len(

        [

            report

            for report in reports

            if report.verification_status
            == "Verified"

        ]

    )


    under_review_reports = len(

        [

            report

            for report in reports

            if report.verification_status
            == "Under Review"

        ]

    )


    suspicious_reports = len(

        [

            report

            for report in reports

            if report.verification_status
            == "Suspicious"

        ]

    )


    duplicate_reports = len(

        [

            report

            for report in reports

            if (

                report.verification_status
                == "Duplicate"

                or

                (report.duplicate_score or 0)
                >= 75

            )

        ]

    )


    active_events = len(

        set(

            report.event_type

            for report in reports

            if report.event_type

        )

    )


    social_reports = len(

        [

            report

            for report in reports

            if report.source
            == "Social Media"

        ]

    )


    citizen_reports = len(

        [

            report

            for report in reports

            if report.source
            == "Citizen"

        ]

    )


    average_trust_score = 0

    if reports:

        average_trust_score = round(

            sum(

                report.trust_score or 0

                for report in reports

            )

            /

            len(reports),

            2

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

        "duplicate_reports":
            duplicate_reports,

        "active_events":
            active_events,

        "social_reports":
            social_reports,

        "citizen_reports":
            citizen_reports,

        "average_trust_score":
            average_trust_score

    }


# ==========================================
# SOCIAL INTELLIGENCE
# ==========================================

@app.post("/api/social/analyze")

def analyze_social_report(

    social_data: SocialReportCreate,

    db: Session = Depends(
        get_db
    )

):

    existing_reports = (

        db.query(
            WeatherReport
        )

        .order_by(
            WeatherReport.created_at.desc()
        )

        .limit(
            500
        )

        .all()

    )


    source = "Social Media"


    # ANALYZE SOCIAL TEXT

    analysis = analyze_report(

        description=
            social_data.description,

        existing_reports=
            existing_reports,

        source=
            source

    )


    location = (
        analysis["location"]
    )


    # SAVE SOCIAL REPORT

    new_report = WeatherReport(

        description=
            social_data.description,

        event_type=
            analysis["event_type"],

        city=
            location.get(
                "city"
            ),

        state=
            location.get(
                "state"
            ),

        latitude=
            location.get(
                "latitude"
            ),

        longitude=
            location.get(
                "longitude"
            ),

        source=
            source,

        trust_score=
            analysis["trust_score"],

        verification_status=
            analysis[
                "verification_status"
            ],

        duplicate_score=
            analysis[
                "duplicate_score"
            ]

    )


    db.add(
        new_report
    )

    db.commit()

    db.refresh(
        new_report
    )


    return {

        "message":
            "Social signal processed successfully",

        "platform":
            social_data.platform,

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
                    new_report.longitude

            },

            "source":
                new_report.source,

            "trust_score":
                new_report.trust_score,

            "verification_status":
                new_report.verification_status,

            "duplicate_score":
                new_report.duplicate_score,

            "weather":
                analysis[
                    "weather"
                ],

            "trust_analysis":
                analysis[
                    "trust_analysis"
                ]

        }

    }


# ==========================================
# SOCIAL INTELLIGENCE ALIAS
# ==========================================

@app.post("/api/social-intelligence")

def social_intelligence_alias(

    social_data: SocialReportCreate,

    db: Session = Depends(
        get_db
    )

):

    return analyze_social_report(

        social_data,

        db

    )


# ==========================================
# GET SOCIAL REPORTS
# ==========================================

@app.get("/api/social/reports")

def get_social_reports(

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

        .all()

    )


    return [

        serialize_report(
            report
        )

        for report in reports

    ]


# ==========================================
# LIVE WEATHER API
# ==========================================

@app.get("/api/weather/current")

def get_current_weather(

    latitude: float,

    longitude: float

):

    weather = get_live_weather(

        latitude,

        longitude

    )


    return {

        "latitude":
            latitude,

        "longitude":
            longitude,

        "weather":
            weather

    }


# ==========================================
# WEATHER FOR REPORT
# ==========================================

@app.get("/api/reports/{report_id}/weather")

def get_report_weather(

    report_id: int,

    db: Session = Depends(
        get_db
    )

):

    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.id == report_id
        )

        .first()

    )


    if not report:

        raise HTTPException(

            status_code=404,

            detail=
                "Report not found"

        )


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

        "weather":
            weather

    }


# ==========================================
# ADMIN VERIFY REPORT
# ==========================================

@app.put("/api/reports/{report_id}/verify")

def verify_report(

    report_id: int,

    update: VerificationUpdate,

    db: Session = Depends(
        get_db
    )

):

    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.id == report_id
        )

        .first()

    )


    if not report:

        raise HTTPException(

            status_code=404,

            detail=
                "Report not found"

        )


    allowed_statuses = [

        "Verified",

        "Under Review",

        "Suspicious",

        "Rejected",

        "Duplicate"

    ]


    if update.status not in allowed_statuses:

        raise HTTPException(

            status_code=400,

            detail=(
                "Invalid verification status"
            )

        )


    report.verification_status = (
        update.status
    )


    db.commit()

    db.refresh(
        report
    )


    return {

        "message":
            "Report verification updated",

        "report":
            serialize_report(
                report
            )

    }


# ==========================================
# DELETE REPORT
# ==========================================

@app.delete("/api/reports/{report_id}")

def delete_report(

    report_id: int,

    db: Session = Depends(
        get_db
    )

):

    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.id == report_id
        )

        .first()

    )


    if not report:

        raise HTTPException(

            status_code=404,

            detail=
                "Report not found"

        )


    db.delete(
        report
    )

    db.commit()


    return {

        "message":
            "Report deleted successfully"

    }


# ==========================================
# ADMIN REPORT QUEUE
# ==========================================

@app.get("/api/admin/reports")

def get_admin_reports(

    db: Session = Depends(
        get_db
    )

):

    reports = (

        db.query(
            WeatherReport
        )

        .order_by(
            WeatherReport.created_at.desc()
        )

        .all()

    )


    return [

        serialize_report(
            report
        )

        for report in reports

    ]