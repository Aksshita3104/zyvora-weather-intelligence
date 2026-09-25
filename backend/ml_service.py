import os
import joblib
import numpy as np


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "rain_no_rain_classifier.joblib"
)

FEATURE_PATH = os.path.join(
    MODEL_DIR,
    "rain_classifier_feature_list.joblib"
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

rain_model = joblib.load(MODEL_PATH)
feature_list = joblib.load(FEATURE_PATH)


# ============================================================
# SUPPORTED CITIES
# ============================================================

SUPPORTED_CITIES = [
    "Bengaluru",
    "Chennai",
    "Delhi",
    "Guwahati",
    "Hyderabad",
    "Jaipur",
    "Kolkata",
    "Mumbai",
    "Shimla",
    "Srinagar"
]


# ============================================================
# SUPPORTED SEASONS
# ============================================================

SUPPORTED_SEASONS = [
    "Autumn",
    "Spring",
    "Summer",
    "Winter"
]


# ============================================================
# NORMALIZE CITY
# ============================================================

def normalize_city(city: str):

    if not city:
        raise ValueError("City is required")

    city = city.strip().lower()

    city_map = {
        "bengaluru": "Bengaluru",
        "bangalore": "Bengaluru",

        "chennai": "Chennai",
        "madras": "Chennai",

        "delhi": "Delhi",
        "new delhi": "Delhi",

        "guwahati": "Guwahati",

        "hyderabad": "Hyderabad",

        "jaipur": "Jaipur",

        "kolkata": "Kolkata",
        "calcutta": "Kolkata",

        "mumbai": "Mumbai",
        "bombay": "Mumbai",

        "shimla": "Shimla",

        "srinagar": "Srinagar"
    }

    normalized = city_map.get(city)

    if normalized is None:
        raise ValueError(
            f"City '{city}' is not supported by the trained rain model"
        )

    return normalized


# ============================================================
# BUILD EXACT 18 FEATURES
# ============================================================

def build_features(
    city: str,
    max_temp: float,
    min_temp: float,
    season: str
):

    city = normalize_city(city)

    if season not in SUPPORTED_SEASONS:
        raise ValueError(
            f"Season '{season}' is not supported"
        )

    max_temp = float(max_temp)
    min_temp = float(min_temp)

    mean_temp = (max_temp + min_temp) / 2
    temp_range = max_temp - min_temp

    # Create all 18 features with 0
    data = {
        feature: 0.0
        for feature in feature_list
    }

    # Temperature features
    data["max_temp"] = max_temp
    data["min_temp"] = min_temp
    data["mean_temp"] = mean_temp
    data["temp_range"] = temp_range

    # City one-hot feature
    city_feature = f"city_{city}"

    if city_feature in data:
        data[city_feature] = 1.0

    # Season one-hot feature
    season_feature = f"season_{season}"

    if season_feature in data:
        data[season_feature] = 1.0

    # IMPORTANT:
    # Keep exactly the same order as the training feature list.
    values = [
        data[feature]
        for feature in feature_list
    ]

    return np.array(
        [values],
        dtype=float
    )


# ============================================================
# RAIN PREDICTION
# ============================================================

def predict_rain(
    city: str,
    max_temp: float,
    min_temp: float,
    season: str
):

    features = build_features(
        city=city,
        max_temp=max_temp,
        min_temp=min_temp,
        season=season
    )

    prediction = rain_model.predict(features)[0]

    probabilities = rain_model.predict_proba(features)[0]

    class_probabilities = {
        int(cls): float(probability)
        for cls, probability in zip(
            rain_model.classes_,
            probabilities
        )
    }

    rain_probability = class_probabilities.get(
        1,
        0.0
    )

    no_rain_probability = class_probabilities.get(
        0,
        0.0
    )

    return {
        "prediction": int(prediction),

        "result": (
            "Rain Expected"
            if prediction == 1
            else "No Rain Expected"
        ),

        "rain_probability": round(
            rain_probability * 100,
            2
        ),

        "no_rain_probability": round(
            no_rain_probability * 100,
            2
        ),

        "city": city,

        "max_temp": max_temp,

        "min_temp": min_temp,

        "mean_temp": round(
            (max_temp + min_temp) / 2,
            2
        ),

        "temp_range": round(
            max_temp - min_temp,
            2
        ),

        "season": season
    }