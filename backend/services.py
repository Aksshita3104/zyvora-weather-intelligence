# ==========================================
# ZYVORA WEATHER INTELLIGENCE PLATFORM
# AI + WEATHER INTELLIGENCE SERVICES
# ==========================================

import json
import re

from difflib import SequenceMatcher
from urllib.parse import urlencode
from urllib.request import urlopen


# ==========================================
# INDIAN LOCATION DATABASE
# ==========================================

INDIAN_LOCATIONS = {

    # Tamil Nadu

    "madurai": {
        "city": "Madurai",
        "state": "Tamil Nadu",
        "latitude": 9.9252,
        "longitude": 78.1198
    },

    "chennai": {
        "city": "Chennai",
        "state": "Tamil Nadu",
        "latitude": 13.0827,
        "longitude": 80.2707
    },

    "coimbatore": {
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "latitude": 11.0168,
        "longitude": 76.9558
    },

    "trichy": {
        "city": "Tiruchirappalli",
        "state": "Tamil Nadu",
        "latitude": 10.7905,
        "longitude": 78.7047
    },

    "tiruchirappalli": {
        "city": "Tiruchirappalli",
        "state": "Tamil Nadu",
        "latitude": 10.7905,
        "longitude": 78.7047
    },

    "salem": {
        "city": "Salem",
        "state": "Tamil Nadu",
        "latitude": 11.6643,
        "longitude": 78.1460
    },

    "tirunelveli": {
        "city": "Tirunelveli",
        "state": "Tamil Nadu",
        "latitude": 8.7139,
        "longitude": 77.7567
    },

    "thanjavur": {
        "city": "Thanjavur",
        "state": "Tamil Nadu",
        "latitude": 10.7870,
        "longitude": 79.1378
    },

    "vellore": {
        "city": "Vellore",
        "state": "Tamil Nadu",
        "latitude": 12.9165,
        "longitude": 79.1325
    },

    "erode": {
        "city": "Erode",
        "state": "Tamil Nadu",
        "latitude": 11.3410,
        "longitude": 77.7172
    },

    "kodaikanal": {
        "city": "Kodaikanal",
        "state": "Tamil Nadu",
        "latitude": 10.2381,
        "longitude": 77.4892
    },

    "ooty": {
        "city": "Ooty",
        "state": "Tamil Nadu",
        "latitude": 11.4102,
        "longitude": 76.6950
    },

    "nilgiris": {
        "city": "Nilgiris",
        "state": "Tamil Nadu",
        "latitude": 11.4916,
        "longitude": 76.7337
    },

    # Karnataka

    "bengaluru": {
        "city": "Bengaluru",
        "state": "Karnataka",
        "latitude": 12.9716,
        "longitude": 77.5946
    },

    "bangalore": {
        "city": "Bengaluru",
        "state": "Karnataka",
        "latitude": 12.9716,
        "longitude": 77.5946
    },

    "mysuru": {
        "city": "Mysuru",
        "state": "Karnataka",
        "latitude": 12.2958,
        "longitude": 76.6394
    },

    # Maharashtra

    "mumbai": {
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.0760,
        "longitude": 72.8777
    },

    "pune": {
        "city": "Pune",
        "state": "Maharashtra",
        "latitude": 18.5204,
        "longitude": 73.8567
    },

    "nagpur": {
        "city": "Nagpur",
        "state": "Maharashtra",
        "latitude": 21.1458,
        "longitude": 79.0882
    },

    # Telangana

    "hyderabad": {
        "city": "Hyderabad",
        "state": "Telangana",
        "latitude": 17.3850,
        "longitude": 78.4867
    },

    # Kerala

    "kochi": {
        "city": "Kochi",
        "state": "Kerala",
        "latitude": 9.9312,
        "longitude": 76.2673
    },

    "thiruvananthapuram": {
        "city": "Thiruvananthapuram",
        "state": "Kerala",
        "latitude": 8.5241,
        "longitude": 76.9366
    },

    # Delhi

    "delhi": {
        "city": "New Delhi",
        "state": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090
    },

    "new delhi": {
        "city": "New Delhi",
        "state": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090
    },

    # West Bengal

    "kolkata": {
        "city": "Kolkata",
        "state": "West Bengal",
        "latitude": 22.5726,
        "longitude": 88.3639
    },

    # Rajasthan

    "jaipur": {
        "city": "Jaipur",
        "state": "Rajasthan",
        "latitude": 26.9124,
        "longitude": 75.7873
    },

    # Uttar Pradesh

    "lucknow": {
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "latitude": 26.8467,
        "longitude": 80.9462
    },

    "varanasi": {
        "city": "Varanasi",
        "state": "Uttar Pradesh",
        "latitude": 25.3176,
        "longitude": 82.9739
    },

    # Assam

    "guwahati": {
        "city": "Guwahati",
        "state": "Assam",
        "latitude": 26.1445,
        "longitude": 91.7362
    },

    # Odisha

    "bhubaneswar": {
        "city": "Bhubaneswar",
        "state": "Odisha",
        "latitude": 20.2961,
        "longitude": 85.8245
    },

    # Bihar

    "patna": {
        "city": "Patna",
        "state": "Bihar",
        "latitude": 25.5941,
        "longitude": 85.1376
    },

    # Gujarat

    "ahmedabad": {
        "city": "Ahmedabad",
        "state": "Gujarat",
        "latitude": 23.0225,
        "longitude": 72.5714
    },

    # Madhya Pradesh

    "bhopal": {
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "latitude": 23.2599,
        "longitude": 77.4126
    },

    # Andhra Pradesh

    "visakhapatnam": {
        "city": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "latitude": 17.6868,
        "longitude": 83.2185
    },

    "vijayawada": {
        "city": "Vijayawada",
        "state": "Andhra Pradesh",
        "latitude": 16.5062,
        "longitude": 80.6480
    }
}


# ==========================================
# WEATHER EVENT KEYWORDS
# ==========================================

WEATHER_EVENTS = {

    "Flood": [
        "flood",
        "flooding",
        "waterlogged",
        "water logging",
        "inundation",
        "overflow",
        "submerged"
    ],

    "Heavy Rainfall": [
        "heavy rain",
        "heavy rainfall",
        "continuous rain",
        "torrential rain",
        "intense rainfall",
        "rainfall"
    ],

    "Thunderstorm": [
        "thunderstorm",
        "thunder",
        "lightning",
        "electric storm"
    ],

    "Heatwave": [
        "heatwave",
        "heat wave",
        "extreme heat",
        "scorching heat",
        "very high temperature",
        "severe heat"
    ],

    "Fog": [
        "fog",
        "dense fog",
        "low visibility",
        "mist"
    ],

    "Strong Wind": [
        "strong wind",
        "high wind",
        "gust",
        "gale",
        "wind speed"
    ],

    "Cyclone": [
        "cyclone",
        "cyclonic storm",
        "cyclonic",
        "hurricane",
        "landfall"
    ],

    "Dust Storm": [
        "dust storm",
        "sandstorm",
        "dust"
    ],

    "Cold Wave": [
        "cold wave",
        "freezing",
        "extreme cold"
    ]
}


# ==========================================
# DETECT WEATHER EVENT
# ==========================================

def detect_weather_event(description):

    text = description.lower()

    scores = {}

    for event, keywords in WEATHER_EVENTS.items():

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        scores[event] = score

    detected_event = max(
        scores,
        key=scores.get
    )

    if scores[detected_event] > 0:
        return detected_event

    return "Other"


# ==========================================
# EVENT CONFIDENCE
# ==========================================

def calculate_event_confidence(
    description,
    event_type
):

    text = description.lower()

    if event_type == "Other":
        return 45

    keywords = WEATHER_EVENTS.get(
        event_type,
        []
    )

    matches = sum(
        1
        for keyword in keywords
        if keyword in text
    )

    confidence = 70 + (matches * 10)

    return min(
        confidence,
        100
    )


# ==========================================
# LOCATION DETECTION
# ==========================================

def detect_location(description):

    text = description.lower()

    # Sort longest names first
    # Example: New Delhi before Delhi
    locations = sorted(
        INDIAN_LOCATIONS.keys(),
        key=len,
        reverse=True
    )

    for location in locations:

        details = INDIAN_LOCATIONS[location]

        pattern = (
            r"\b" +
            re.escape(location) +
            r"\b"
        )

        if re.search(pattern, text):

            return {
                "city": details["city"],
                "state": details["state"],
                "latitude": details["latitude"],
                "longitude": details["longitude"]
            }

    return {
        "city": None,
        "state": None,
        "latitude": None,
        "longitude": None
    }


# ==========================================
# TEXT SIMILARITY
# ==========================================

def calculate_similarity(
    text1,
    text2
):

    text1 = text1.lower().strip()
    text2 = text2.lower().strip()

    similarity = SequenceMatcher(
        None,
        text1,
        text2
    ).ratio()

    return round(
        similarity * 100,
        2
    )


# ==========================================
# DUPLICATE DETECTION
# ==========================================

def detect_duplicate(
    description,
    existing_reports
):

    highest_score = 0
    duplicate_report_id = None

    for report in existing_reports:

        report_description = getattr(
            report,
            "description",
            ""
        )

        report_id = getattr(
            report,
            "id",
            None
        )

        similarity = calculate_similarity(
            description,
            report_description
        )

        if similarity > highest_score:

            highest_score = similarity
            duplicate_report_id = report_id

    is_duplicate = (
        highest_score >= 75
    )

    return {

        "is_duplicate": is_duplicate,

        "duplicate_score": round(
            highest_score,
            2
        ),

        "duplicate_report_id":
            duplicate_report_id
            if is_duplicate
            else None
    }


# ==========================================
# SUSPICIOUS CONTENT
# ==========================================

def detect_suspicious_content(
    description
):

    text = description.lower()

    suspicious_patterns = [

        "100% true",
        "share immediately",
        "share this urgently",
        "breaking!!!",
        "government hiding",
        "media hiding",
        "secret disaster",
        "do not trust imd",
        "forward to everyone",
        "guaranteed disaster",
        "everyone will die"

    ]

    for pattern in suspicious_patterns:

        if pattern in text:
            return True

    return False


# ==========================================
# SOURCE RELIABILITY
# ==========================================

def calculate_source_reliability(
    source
):

    source = (
        source or
        "Citizen"
    ).lower()

    reliability = {

        "government": 95,
        "sensor": 90,
        "public dataset": 85,
        "news website": 80,
        "news": 80,

        "citizen": 65,

        "social media": 50,
        "x / twitter": 50,
        "twitter": 50,
        "x": 50,
        "instagram": 45,
        "facebook": 45,
        "youtube community": 50,
        "other social media": 40
    }

    return reliability.get(
        source,
        55
    )


# ==========================================
# REPORT COMPLETENESS
# ==========================================

def calculate_report_completeness(
    description,
    location
):

    score = 40

    words = len(
        description.split()
    )

    if words >= 8:
        score += 20

    if words >= 15:
        score += 10

    if location.get("city"):
        score += 20

    if location.get("latitude") is not None:
        score += 10

    return min(
        score,
        100
    )


# ==========================================
# LOCATION CONSISTENCY
# ==========================================

def calculate_location_consistency(
    location
):

    if (
        location.get("city")
        and
        location.get("latitude") is not None
        and
        location.get("longitude") is not None
    ):
        return 100

    if location.get("city"):
        return 70

    return 35


# ==========================================
# OPEN-METEO WEATHER CODE
# ==========================================

def weather_code_description(
    code
):

    weather_codes = {

        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Depositing rime fog",

        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",

        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        66: "Light freezing rain",
        67: "Heavy freezing rain",

        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        77: "Snow grains",

        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",

        85: "Snow showers",
        86: "Heavy snow showers",

        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Severe thunderstorm"
    }

    return weather_codes.get(
        code,
        "Unknown"
    )


# ==========================================
# REAL LIVE WEATHER DATA
# OPEN-METEO API
# ==========================================

def get_live_weather(
    latitude,
    longitude
):

    if (
        latitude is None
        or
        longitude is None
    ):

        return {

            "available": False,

            "reason":
                "Location coordinates unavailable"
        }

    try:

        params = {

            "latitude": latitude,

            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "rain,"
                "weather_code,"
                "wind_speed_10m"
            ),

            "timezone": "auto"
        }

        url = (
            "https://api.open-meteo.com/v1/forecast?"
            + urlencode(params)
        )

        with urlopen(
            url,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        current = data.get(
            "current",
            {}
        )

        weather_code = current.get(
            "weather_code"
        )

        return {

            "available": True,

            "temperature":
                current.get(
                    "temperature_2m"
                ),

            "humidity":
                current.get(
                    "relative_humidity_2m"
                ),

            "precipitation":
                current.get(
                    "precipitation"
                ),

            "rain":
                current.get(
                    "rain"
                ),

            "wind_speed":
                current.get(
                    "wind_speed_10m"
                ),

            "weather_code":
                weather_code,

            "weather_condition":
                weather_code_description(
                    weather_code
                )
        }

    except Exception as error:

        return {

            "available": False,

            "reason":
                str(error)
        }


# ==========================================
# WEATHER CONSISTENCY
# ==========================================

def calculate_weather_consistency(
    event_type,
    weather
):

    if not weather.get(
        "available"
    ):
        return 50

    rain = float(
        weather.get("rain")
        or 0
    )

    precipitation = float(
        weather.get("precipitation")
        or 0
    )

    wind_speed = float(
        weather.get("wind_speed")
        or 0
    )

    temperature = weather.get(
        "temperature"
    )

    weather_code = weather.get(
        "weather_code"
    )

    if event_type == "Flood":

        if (
            rain > 0
            or precipitation > 0
        ):
            return 85

        return 45


    if event_type == "Heavy Rainfall":

        if rain >= 2:
            return 100

        if precipitation > 0:
            return 80

        return 35


    if event_type == "Thunderstorm":

        if weather_code in [
            95,
            96,
            99
        ]:
            return 100

        if rain > 0:
            return 70

        return 40


    if event_type == "Strong Wind":

        if wind_speed >= 35:
            return 100

        if wind_speed >= 20:
            return 75

        return 45


    if event_type == "Heatwave":

        if (
            temperature is not None
            and
            temperature >= 38
        ):
            return 100

        if (
            temperature is not None
            and
            temperature >= 32
        ):
            return 70

        return 35


    if event_type == "Fog":

        if weather_code in [
            45,
            48
        ]:
            return 100

        return 40


    if event_type == "Cyclone":

        if wind_speed >= 50:
            return 95

        if wind_speed >= 30:
            return 70

        return 40


    if event_type == "Dust Storm":

        if wind_speed >= 30:
            return 85

        return 45


    if event_type == "Cold Wave":

        if (
            temperature is not None
            and
            temperature <= 10
        ):
            return 90

        return 40


    return 60


# ==========================================
# FINAL TRUST SCORE
# ==========================================

def calculate_final_trust_score(

    source_reliability,

    location_consistency,

    report_completeness,

    weather_consistency,

    event_confidence,

    duplicate_score,

    suspicious

):

    score = (

        source_reliability * 0.15

        +

        location_consistency * 0.20

        +

        report_completeness * 0.15

        +

        weather_consistency * 0.20

        +

        event_confidence * 0.20
    )

    duplicate_penalty = (
        duplicate_score * 0.10
    )

    score -= duplicate_penalty

    if suspicious:
        score -= 25

    score = max(
        0,
        min(
            score,
            100
        )
    )

    return round(
        score,
        2
    )


# ==========================================
# VERIFICATION STATUS
# ==========================================

def get_verification_status(

    trust_score,

    is_duplicate=False,

    suspicious=False

):

    if suspicious:
        return "Suspicious"

    if is_duplicate:
        return "Duplicate"

    if trust_score >= 85:
        return "Verified"

    if trust_score >= 55:
        return "Under Review"

    return "Suspicious"


# ==========================================
# EXPLAINABLE AI
# ==========================================

def generate_explanation(

    source_reliability,

    location_consistency,

    report_completeness,

    weather_consistency,

    event_confidence,

    duplicate_score,

    suspicious,

    weather_available

):

    explanation = []


    # SOURCE

    if source_reliability >= 80:

        explanation.append(
            "Report source has high reliability"
        )

    elif source_reliability >= 60:

        explanation.append(
            "Source requires additional verification"
        )

    else:

        explanation.append(
            "Low-reliability source requires stronger verification"
        )


    # LOCATION

    if location_consistency >= 90:

        explanation.append(
            "Location information is complete and GPS coordinates are available"
        )

    else:

        explanation.append(
            "Location information is incomplete"
        )


    # COMPLETENESS

    if report_completeness >= 80:

        explanation.append(
            "Report contains sufficient descriptive information"
        )

    else:

        explanation.append(
            "Report description contains limited contextual information"
        )


    # WEATHER

    if weather_available:

        if weather_consistency >= 80:

            explanation.append(
                "Live weather conditions support the reported event"
            )

        elif weather_consistency >= 55:

            explanation.append(
                "Live weather data partially supports the reported event"
            )

        else:

            explanation.append(
                "Live weather conditions do not strongly support the reported event"
            )

    else:

        explanation.append(
            "Live weather verification unavailable; fallback confidence applied"
        )


    # EVENT

    if event_confidence >= 85:

        explanation.append(
            "Weather event was detected with high confidence"
        )


    # DUPLICATE

    if duplicate_score >= 75:

        explanation.append(
            "High similarity with an existing report detected"
        )

    elif duplicate_score >= 40:

        explanation.append(
            "Possible similarity with an existing report detected"
        )

    else:

        explanation.append(
            "No significant duplicate report detected"
        )


    # SUSPICIOUS

    if suspicious:

        explanation.append(
            "Suspicious language patterns were detected"
        )


    return explanation


# ==========================================
# COMPLETE AI REPORT ANALYSIS
# ==========================================

def analyze_report(

    description,

    existing_reports,

    source="Citizen"

):

    # EVENT

    event_type = detect_weather_event(
        description
    )


    # LOCATION

    location = detect_location(
        description
    )


    # DUPLICATE

    duplicate = detect_duplicate(

        description,

        existing_reports

    )


    # SUSPICIOUS CONTENT

    suspicious = detect_suspicious_content(
        description
    )


    # SOURCE RELIABILITY

    source_reliability = (
        calculate_source_reliability(
            source
        )
    )


    # LOCATION SCORE

    location_consistency = (
        calculate_location_consistency(
            location
        )
    )


    # REPORT COMPLETENESS

    report_completeness = (
        calculate_report_completeness(

            description,

            location

        )
    )


    # EVENT CONFIDENCE

    event_confidence = (
        calculate_event_confidence(

            description,

            event_type

        )
    )


    # LIVE WEATHER

    weather = get_live_weather(

        location.get(
            "latitude"
        ),

        location.get(
            "longitude"
        )

    )


    # WEATHER CONSISTENCY

    weather_consistency = (
        calculate_weather_consistency(

            event_type,

            weather

        )
    )


    # FINAL TRUST SCORE

    final_trust_score = (
        calculate_final_trust_score(

            source_reliability,

            location_consistency,

            report_completeness,

            weather_consistency,

            event_confidence,

            duplicate[
                "duplicate_score"
            ],

            suspicious

        )
    )


    # STATUS

    verification_status = (
        get_verification_status(

            final_trust_score,

            duplicate[
                "is_duplicate"
            ],

            suspicious

        )
    )


    # EXPLANATION

    explanation = generate_explanation(

        source_reliability,

        location_consistency,

        report_completeness,

        weather_consistency,

        event_confidence,

        duplicate[
            "duplicate_score"
        ],

        suspicious,

        weather.get(
            "available",
            False
        )

    )


    return {

        "event_type":
            event_type,

        "location":
            location,

        "weather":
            weather,

        "trust_analysis": {

            "final_trust_score":
                final_trust_score,

            "verification_status":
                verification_status,

            "source_reliability":
                source_reliability,

            "location_consistency":
                location_consistency,

            "report_completeness":
                report_completeness,

            "weather_consistency":
                weather_consistency,

            "event_confidence":
                event_confidence,

            "duplicate_score":
                duplicate[
                    "duplicate_score"
                ],

            "explanation":
                explanation

        },

        "trust_score":
            final_trust_score,

        "verification_status":
            verification_status,

        "duplicate_score":
            duplicate[
                "duplicate_score"
            ],

        "is_duplicate":
            duplicate[
                "is_duplicate"
            ],

        "duplicate_report_id":
            duplicate[
                "duplicate_report_id"
            ],

        "suspicious":
            suspicious

    }