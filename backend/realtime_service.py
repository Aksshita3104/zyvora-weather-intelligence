# ==========================================
# ZYVORA
# REAL-TIME DATA INGESTION ENGINE
# ==========================================

import json

from datetime import datetime

from sqlalchemy.orm import Session

from models import WeatherReport

from services import (
    analyze_report,
    INDIAN_LOCATIONS
)

from weather_service import (
    get_current_weather
)

from news_service import (
    fetch_live_news,
    parse_news_date
)

from social_service import (
    fetch_live_social_data
)


# ==========================================
# WEATHER CITIES
# ==========================================

LIVE_WEATHER_CITIES = [

    "madurai",

    "chennai",

    "coimbatore",

    "bengaluru",

    "mumbai",

    "hyderabad",

    "kochi",

    "delhi",

    "kolkata",

    "guwahati",

    "visakhapatnam",

    "bhubaneswar",

    "jaipur",

    "lucknow"

]


# ==========================================
# WEATHER EVENT DETECTION
# ==========================================

def detect_event_from_weather(
    weather
):

    if not weather:
        return None


    code = (
        weather.get(
            "weather_code"
        )
    )


    temperature = (
        weather.get(
            "temperature"
        )
    )


    wind_speed = (
        weather.get(
            "wind_speed"
        )
    )


    precipitation = (
        weather.get(
            "precipitation"
        )
        or 0
    )


    rain = (
        weather.get(
            "rain"
        )
        or 0
    )


    # THUNDERSTORM

    if code in [95, 96, 99]:

        return "Thunderstorm"


    # HEAVY RAINFALL

    if (
        code in [65, 82]
        or precipitation >= 5
        or rain >= 5
    ):

        return "Heavy Rainfall"


    # FOG

    if code in [45, 48]:

        return "Fog"


    # HEATWAVE

    if (
        temperature is not None
        and temperature >= 40
    ):

        return "Heatwave"


    # STRONG WIND

    if (
        wind_speed is not None
        and wind_speed >= 40
    ):

        return "Strong Wind"


    return None


# ==========================================
# CHECK EXISTING EXTERNAL DATA
# ==========================================

def external_record_exists(
    db,
    external_id
):

    if not external_id:

        return False


    report = (

        db.query(
            WeatherReport
        )

        .filter(
            WeatherReport.external_id
            == external_id
        )

        .first()

    )


    return report is not None


# ==========================================
# CALCULATE SOCIAL ENGAGEMENT
# ==========================================

def calculate_engagement(
    likes=0,
    replies=0,
    reposts=0
):

    score = (

        (likes * 1)

        +

        (replies * 2)

        +

        (reposts * 3)

    )


    return min(
        round(score, 2),
        10000
    )


# ==========================================
# SAVE REAL DATA REPORT
# ==========================================

def save_live_report(

    db,

    description,

    source,

    source_name=None,

    source_url=None,

    external_id=None,

    published_at=None,

    raw_data=None,

    likes=0,

    replies=0,

    reposts=0,

    city=None,

    state=None,

    latitude=None,

    longitude=None

):

    # ======================================
    # DUPLICATE EXTERNAL RECORD
    # ======================================

    if external_record_exists(
        db,
        external_id
    ):

        return {

            "saved": False,

            "reason":
                "Already ingested"

        }


    # ======================================
    # GET EXISTING REPORTS
    # ======================================

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


    # ======================================
    # AI ANALYSIS
    # ======================================

    analysis = analyze_report(

        description=description,

        existing_reports=existing_reports,

        source=source

    )


    detected_location = (
        analysis.get(
            "location",
            {}
        )
    )


    # ======================================
    # LOCATION
    # ======================================

    final_city = (

        city

        or

        detected_location.get(
            "city"
        )

    )


    final_state = (

        state

        or

        detected_location.get(
            "state"
        )

    )


    final_latitude = (

        latitude

        if latitude is not None

        else

        detected_location.get(
            "latitude"
        )

    )


    final_longitude = (

        longitude

        if longitude is not None

        else

        detected_location.get(
            "longitude"
        )

    )


    # ======================================
    # SOCIAL ENGAGEMENT
    # ======================================

    engagement_score = (
        calculate_engagement(

            likes,

            replies,

            reposts

        )
    )


    # ======================================
    # CREATE REPORT
    # ======================================

    report = WeatherReport(

        description=
            description,

        event_type=
            analysis[
                "event_type"
            ],

        city=
            final_city,

        state=
            final_state,

        latitude=
            final_latitude,

        longitude=
            final_longitude,

        source=
            source,

        source_name=
            source_name,

        source_url=
            source_url,

        external_id=
            external_id,

        is_live_data=
            True,

        raw_data=
            json.dumps(
                raw_data
                or {},
                default=str
            ),

        published_at=
            published_at,

        likes=
            likes or 0,

        replies=
            replies or 0,

        reposts=
            reposts or 0,

        engagement_score=
            engagement_score,

        trust_score=
            analysis[
                "trust_score"
            ],

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
        report
    )


    db.commit()


    db.refresh(
        report
    )


    return {

        "saved": True,

        "report":
            report

    }


# ==========================================
# INGEST LIVE WEATHER
# ==========================================

def ingest_live_weather(
    db
):

    results = []

    processed = 0

    saved = 0


    for city_key in LIVE_WEATHER_CITIES:

        location = (
            INDIAN_LOCATIONS.get(
                city_key
            )
        )


        if not location:
            continue


        processed += 1


        weather_response = (
            get_current_weather(

                location[
                    "latitude"
                ],

                location[
                    "longitude"
                ]

            )
        )


        if not weather_response.get(
            "success"
        ):
            continue


        weather = (
            weather_response.get(
                "data",
                {}
            )
        )


        event_type = (
            detect_event_from_weather(
                weather
            )
        )


        # Only store significant events

        if not event_type:
            continue


        external_id = (

            "weather-"

            f"{city_key}-"

            f"{weather.get('time')}-"

            f"{event_type}"

        )


        description = (

            f"Live weather intelligence detected "
            f"{event_type} conditions in "
            f"{location['city']}, "
            f"{location['state']}. "

            f"Temperature: "
            f"{weather.get('temperature')}°C. "

            f"Precipitation: "
            f"{weather.get('precipitation')} mm. "

            f"Wind Speed: "
            f"{weather.get('wind_speed')} km/h. "

            f"Condition: "
            f"{weather.get('weather_description')}."

        )


        result = save_live_report(

            db=db,

            description=description,

            source="Weather API",

            source_name=
                "Open-Meteo",

            source_url=
                "https://open-meteo.com",

            external_id=
                external_id,

            published_at=
                None,

            raw_data=
                weather,

            city=
                location["city"],

            state=
                location["state"],

            latitude=
                location["latitude"],

            longitude=
                location["longitude"]

        )


        if result.get(
            "saved"
        ):

            saved += 1

            results.append({

                "city":
                    location["city"],

                "event":
                    event_type,

                "weather":
                    weather

            })


    return {

        "success": True,

        "processed":
            processed,

        "saved":
            saved,

        "data":
            results

    }


# ==========================================
# INGEST LIVE NEWS
# ==========================================

def ingest_live_news(

    db,

    max_records=20

):

    response = (
        fetch_live_news(
            max_records
        )
    )


    if not response.get(
        "success"
    ):

        return response


    saved = 0

    skipped = 0

    results = []


    for article in response.get(
        "data",
        []
    ):


        description = (
            article.get(
                "description"
            )
        )


        if not description:
            continue


        external_id = (
            article.get(
                "external_id"
            )
        )


        if external_record_exists(
            db,
            external_id
        ):

            skipped += 1

            continue


        published_at = (
            parse_news_date(

                article.get(
                    "published_at"
                )

            )
        )


        result = save_live_report(

            db=db,

            description=
                description,

            source=
                "News",

            source_name=
                article.get(
                    "source_name"
                ),

            source_url=
                article.get(
                    "source_url"
                ),

            external_id=
                external_id,

            published_at=
                published_at,

            raw_data=
                article.get(
                    "raw"
                )

        )


        if result.get(
            "saved"
        ):

            saved += 1

            report = (
                result[
                    "report"
                ]
            )


            results.append({

                "id":
                    report.id,

                "event":
                    report.event_type,

                "city":
                    report.city,

                "source":
                    report.source_name

            })


    return {

        "success": True,

        "source":
            "GDELT News",

        "fetched":
            response.get(
                "count",
                0
            ),

        "saved":
            saved,

        "skipped":
            skipped,

        "data":
            results

    }


# ==========================================
# PARSE SOCIAL DATE
# ==========================================

def parse_social_date(
    value
):

    if not value:
        return None


    try:

        return datetime.fromisoformat(

            value.replace(
                "Z",
                "+00:00"
            )

        )


    except Exception:

        return None


# ==========================================
# INGEST LIVE SOCIAL DATA
# ==========================================

def ingest_live_social(

    db,

    max_records=20

):

    response = (
        fetch_live_social_data(
            max_records
        )
    )


    if not response.get(
        "success"
    ):

        return response


    saved = 0

    skipped = 0

    results = []


    for post in response.get(
        "data",
        []
    ):


        description = (
            post.get(
                "description"
            )
        )


        if not description:
            continue


        external_id = (
            post.get(
                "external_id"
            )
        )


        if external_record_exists(
            db,
            external_id
        ):

            skipped += 1

            continue


        published_at = (
            parse_social_date(

                post.get(
                    "published_at"
                )

            )
        )


        result = save_live_report(

            db=db,

            description=
                description,

            source=
                "Social Media",

            source_name=
                post.get(
                    "source_name"
                ),

            source_url=
                post.get(
                    "source_url"
                ),

            external_id=
                external_id,

            published_at=
                published_at,

            raw_data=
                post.get(
                    "raw"
                ),

            likes=
                post.get(
                    "likes",
                    0
                ),

            replies=
                post.get(
                    "replies",
                    0
                ),

            reposts=
                post.get(
                    "reposts",
                    0
                )

        )


        if result.get(
            "saved"
        ):

            saved += 1

            report = (
                result[
                    "report"
                ]
            )


            results.append({

                "id":
                    report.id,

                "event":
                    report.event_type,

                "city":
                    report.city,

                "engagement":
                    report.engagement_score

            })


    return {

        "success": True,

        "source":
            "X / Twitter",

        "fetched":
            response.get(
                "count",
                0
            ),

        "saved":
            saved,

        "skipped":
            skipped,

        "data":
            results

    }


# ==========================================
# COMPLETE REAL-TIME INGESTION
# ==========================================

def run_complete_ingestion(

    db,

    include_weather=True,

    include_news=True,

    include_social=True,

    max_news_records=20,

    max_social_records=20

):

    results = {}


    # WEATHER

    if include_weather:

        try:

            results["weather"] = (
                ingest_live_weather(
                    db
                )
            )

        except Exception as error:

            results["weather"] = {

                "success": False,

                "message":
                    str(error)

            }


    # NEWS

    if include_news:

        try:

            results["news"] = (

                ingest_live_news(

                    db,

                    max_news_records

                )

            )

        except Exception as error:

            results["news"] = {

                "success": False,

                "message":
                    str(error)

            }


    # SOCIAL

    if include_social:

        try:

            results["social"] = (

                ingest_live_social(

                    db,

                    max_social_records

                )

            )

        except Exception as error:

            results["social"] = {

                "success": False,

                "message":
                    str(error)

            }


    return {

        "success": True,

        "timestamp":
            datetime.utcnow().isoformat(),

        "results":
            results

    }