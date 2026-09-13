# ==========================================
# ZYVORA WEATHER INTELLIGENCE PLATFORM
# REAL WEATHER DATA VERIFICATION SERVICE
# ==========================================

import requests


# ==========================================
# OPEN-METEO API
# ==========================================

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


# ==========================================
# WMO WEATHER CODE MAPPING
# ==========================================

WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Rime Fog",

    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Heavy Drizzle",

    56: "Light Freezing Drizzle",
    57: "Heavy Freezing Drizzle",

    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",

    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",

    71: "Slight Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",

    77: "Snow Grains",

    80: "Light Rain Showers",
    81: "Moderate Rain Showers",
    82: "Heavy Rain Showers",

    85: "Light Snow Showers",
    86: "Heavy Snow Showers",

    95: "Thunderstorm",
    96: "Thunderstorm With Hail",
    99: "Severe Thunderstorm With Hail"
}


# ==========================================
# GET CURRENT REAL WEATHER
# ==========================================

def get_current_weather(latitude, longitude):

    if latitude is None or longitude is None:
        return {
            "success": False,
            "message": "Coordinates are required for weather verification",
            "data": None
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

        response = requests.get(
            WEATHER_API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})

        weather_code = current.get("weather_code")

        weather_description = WEATHER_CODES.get(
            weather_code,
            "Unknown"
        )

        weather_data = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "rain": current.get("rain"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": weather_code,
            "weather_description": weather_description,
            "time": current.get("time")
        }

        return {
            "success": True,
            "message": "Real weather data retrieved successfully",
            "data": weather_data
        }

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "message": "Weather API request timed out",
            "data": None
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "message": f"Weather API error: {str(error)}",
            "data": None
        }

    except Exception as error:

        return {
            "success": False,
            "message": f"Weather verification failed: {str(error)}",
            "data": None
        }


# ==========================================
# VERIFY FLOOD
# ==========================================

def verify_flood(weather_data):

    score = 35
    details = []

    rain = weather_data.get("rain") or 0
    precipitation = weather_data.get("precipitation") or 0
    weather_code = weather_data.get("weather_code")

    if rain > 0:
        score += 20
        details.append("Current rainfall detected")

    if precipitation >= 1:
        score += 15
        details.append("Measurable precipitation detected")

    if weather_code in [61, 63, 65, 80, 81, 82]:
        score += 30
        details.append("Rain-related weather condition detected")

    score = min(score, 100)

    return score, details


# ==========================================
# VERIFY HEAVY RAINFALL
# ==========================================

def verify_heavy_rainfall(weather_data):

    score = 30
    details = []

    rain = weather_data.get("rain") or 0
    precipitation = weather_data.get("precipitation") or 0
    weather_code = weather_data.get("weather_code")

    if rain > 0:
        score += 25
        details.append("Current rainfall detected")

    if precipitation >= 1:
        score += 15
        details.append("Measurable precipitation detected")

    if weather_code in [61, 63, 65, 80, 81, 82]:
        score += 30
        details.append("Rain condition detected")

    score = min(score, 100)

    return score, details


# ==========================================
# VERIFY THUNDERSTORM
# ==========================================

def verify_thunderstorm(weather_data):

    score = 30
    details = []

    weather_code = weather_data.get("weather_code")
    precipitation = weather_data.get("precipitation") or 0

    if weather_code in [95, 96, 99]:
        score += 60
        details.append("Thunderstorm detected in real weather data")

    if precipitation > 0:
        score += 10
        details.append("Precipitation detected")

    score = min(score, 100)

    return score, details


# ==========================================
# VERIFY HEATWAVE
# ==========================================

def verify_heatwave(weather_data):

    score = 30
    details = []

    temperature = weather_data.get("temperature")

    if temperature is not None:

        if temperature >= 45:
            score += 65
            details.append("Extreme temperature detected")

        elif temperature >= 40:
            score += 50
            details.append("Very high temperature detected")

        elif temperature >= 35:
            score += 25
            details.append("High temperature detected")

    score = min(score, 100)

    return score, details


# ==========================================
# VERIFY FOG
# ==========================================

def verify_fog(weather_data):

    score = 30
    details = []

    weather_code = weather_data.get("weather_code")
    humidity = weather_data.get("humidity") or 0

    if weather_code in [45, 48]:
        score += 55
        details.append("Fog detected in real weather data")

    if humidity >= 85:
        score += 15
        details.append("High humidity detected")

    score = min(score, 100)

    return score, details


# ==========================================
# VERIFY STRONG WIND
# ==========================================

def verify_strong_wind(weather_data):

    score = 30
    details = []

    wind_speed = weather_data.get("wind_speed") or 0

    if wind_speed >= 60:
        score += 65
        details.append("Very strong wind detected")

    elif wind_speed >= 40:
        score += 50
        details.append("Strong wind detected")

    elif wind_speed >= 25:
        score += 25
        details.append("Moderate to strong wind detected")

    score = min(score, 100)

    return score, details


# ==========================================
# VERIFY CYCLONE
# ==========================================

def verify_cyclone(weather_data):

    score = 25
    details = []

    wind_speed = weather_data.get("wind_speed") or 0
    precipitation = weather_data.get("precipitation") or 0
    weather_code = weather_data.get("weather_code")

    if wind_speed >= 60:
        score += 35
        details.append("High wind speed detected")

    if precipitation >= 1:
        score += 20
        details.append("Significant precipitation detected")

    if weather_code in [63, 65, 80, 81, 82, 95, 96, 99]:
        score += 25
        details.append("Severe weather condition detected")

    score = min(score, 100)

    return score, details


# ==========================================
# MAIN WEATHER EVENT VERIFICATION
# ==========================================

def verify_weather_event(event_type, weather_data):

    if not weather_data:
        return {
            "weather_verified": False,
            "weather_consistency_score": 50,
            "verification_message": "Weather data unavailable",
            "verification_details": []
        }

    score = 50
    details = []

    if event_type == "Flood":

        score, details = verify_flood(weather_data)

    elif event_type == "Heavy Rainfall":

        score, details = verify_heavy_rainfall(weather_data)

    elif event_type == "Thunderstorm":

        score, details = verify_thunderstorm(weather_data)

    elif event_type == "Heatwave":

        score, details = verify_heatwave(weather_data)

    elif event_type == "Fog":

        score, details = verify_fog(weather_data)

    elif event_type == "Strong Wind":

        score, details = verify_strong_wind(weather_data)

    elif event_type == "Cyclone":

        score, details = verify_cyclone(weather_data)

    else:

        details.append(
            "No specialized verification rule available"
        )

    weather_verified = score >= 65

    if weather_verified:

        message = (
            "Real weather conditions support "
            "the reported weather event"
        )

    else:

        message = (
            "Real weather conditions provide limited "
            "support for the reported event"
        )

    return {
        "weather_verified": weather_verified,
        "weather_consistency_score": score,
        "verification_message": message,
        "verification_details": details
    }


# ==========================================
# COMPLETE WEATHER VERIFICATION
# ==========================================

def perform_weather_verification(
    event_type,
    latitude,
    longitude
):

    weather_response = get_current_weather(
        latitude,
        longitude
    )

    if not weather_response["success"]:

        return {
            "weather_data_available": False,
            "weather_verified": False,
            "weather_consistency_score": 50,
            "weather_message": weather_response["message"],
            "verification_details": [],
            "real_weather_data": None
        }

    weather_data = weather_response["data"]

    verification = verify_weather_event(
        event_type,
        weather_data
    )

    return {
        "weather_data_available": True,
        "weather_verified": verification["weather_verified"],
        "weather_consistency_score": verification[
            "weather_consistency_score"
        ],
        "weather_message": verification[
            "verification_message"
        ],
        "verification_details": verification[
            "verification_details"
        ],
        "real_weather_data": weather_data
    }