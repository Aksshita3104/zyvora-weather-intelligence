import os
import re
import requests
from datetime import datetime, timezone


# =========================================================
# ZYVORA IMD HASHTAGS
# =========================================================

IMD_HASHTAGS = {
    "#imdweatheralert",
    "#imdalert",
    "#imdweather",
    "#indiaweatheralert",
    "#indiaweather",
    "#indiarainalert",
    "#rainalertindia",
    "#indianweather",
    "#indiarain",
    "#indianmonsoon",
    "#indiafloodalert",
    "#indiaflood",
    "#indiathunderstorm",
    "#indiaheatwave",
    "#indiafog",
    "#indiaduststorm",
    "#indiastrongwinds",
    "#indiaweatherupdate",
    "#indiathunderstormalert",
    "#indiaheavyrain",
    "#indiaheavyrainfall",
    "#indiacyclone",
    "#indiadustraisingwinds",
    "#indiaweatherwarning",
    "#monsoonindia",
}


# =========================================================
# HASHTAG DETECTOR
# =========================================================

def detect_imd_hashtags(text: str):

    if not text:
        return []

    hashtags = re.findall(
        r"#[A-Za-z0-9_]+",
        text
    )

    detected = []

    for tag in hashtags:

        normalized = tag.lower()

        if normalized in IMD_HASHTAGS:
            detected.append(normalized)

    return list(dict.fromkeys(detected))


# =========================================================
# WEATHER EVENT DETECTOR
# =========================================================

def detect_weather_event(text: str):

    text_lower = text.lower()

    event_keywords = {

        "Heavy Rain": [
            "heavy rain",
            "heavy rainfall",
            "very heavy rain",
            "rainfall"
        ],

        "Flood": [
            "flood",
            "flooding",
            "waterlogging",
            "water logged"
        ],

        "Thunderstorm": [
            "thunderstorm",
            "thunder",
            "lightning"
        ],

        "Cyclone": [
            "cyclone",
            "cyclonic storm"
        ],

        "Heatwave": [
            "heatwave",
            "heat wave",
            "extreme heat"
        ],

        "Fog": [
            "fog",
            "dense fog"
        ],

        "Strong Winds": [
            "strong winds",
            "gusty winds",
            "high winds"
        ],

        "Dust Storm": [
            "dust storm",
            "dust raising winds"
        ],

        "Monsoon": [
            "monsoon"
        ]
    }

    for event, keywords in event_keywords.items():

        for keyword in keywords:

            if keyword in text_lower:
                return event

    return "Weather"


# =========================================================
# TELEGRAM
# =========================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)


def fetch_telegram_posts():

    if not TELEGRAM_BOT_TOKEN:
        return []

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/getUpdates"
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        posts = []

        for update in data.get("result", []):

            message = update.get("message")

            if not message:
                continue

            text = message.get("text", "")

            if not text:
                continue

            detected_hashtags = detect_imd_hashtags(
                text
            )

            if not detected_hashtags:
                continue

            posts.append({

                "platform": "Telegram",

                "external_id":
                    str(update.get("update_id")),

                "text": text,

                "hashtags":
                    detected_hashtags,

                "event_type":
                    detect_weather_event(text),

                "published_at":
                    datetime.fromtimestamp(
                        message.get(
                            "date",
                            datetime.now(
                                timezone.utc
                            ).timestamp()
                        ),
                        tz=timezone.utc
                    ).isoformat(),

                "source_name":
                    (
                        message
                        .get("chat", {})
                        .get("title")
                    ),

            })

        return posts

    except Exception as error:

        print(
            "Telegram API error:",
            error
        )

        return []


# =========================================================
# FACEBOOK GRAPH API
# =========================================================

FACEBOOK_ACCESS_TOKEN = os.getenv(
    "FACEBOOK_ACCESS_TOKEN"
)

FACEBOOK_PAGE_ID = os.getenv(
    "FACEBOOK_PAGE_ID"
)


def fetch_facebook_posts():

    if not FACEBOOK_ACCESS_TOKEN:
        return []

    if not FACEBOOK_PAGE_ID:
        return []

    url = (
        f"https://graph.facebook.com/"
        f"v23.0/{FACEBOOK_PAGE_ID}/posts"
    )

    params = {

        "access_token":
            FACEBOOK_ACCESS_TOKEN,

        "fields":
            "id,message,created_time,permalink_url",

        "limit":
            50
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        posts = []

        for post in data.get(
            "data",
            []
        ):

            text = post.get(
                "message",
                ""
            )

            if not text:
                continue

            detected_hashtags = detect_imd_hashtags(
                text
            )

            if not detected_hashtags:
                continue

            posts.append({

                "platform": "Facebook",

                "external_id":
                    post.get("id"),

                "text":
                    text,

                "hashtags":
                    detected_hashtags,

                "event_type":
                    detect_weather_event(text),

                "published_at":
                    post.get(
                        "created_time"
                    ),

                "source_url":
                    post.get(
                        "permalink_url"
                    ),

            })

        return posts

    except Exception as error:

        print(
            "Facebook API error:",
            error
        )

        return []


# =========================================================
# COLLECT ALL SOCIAL SIGNALS
# =========================================================

def collect_social_signals():

    telegram_posts = (
        fetch_telegram_posts()
    )

    facebook_posts = (
        fetch_facebook_posts()
    )

    return (
        telegram_posts +
        facebook_posts
    )