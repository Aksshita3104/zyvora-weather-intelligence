# ==========================================
# ZYVORA
# REAL-TIME SOCIAL INTELLIGENCE SERVICE
# ==========================================

import os

import requests

from dotenv import load_dotenv


load_dotenv()


X_API_URL = (
    "https://api.x.com/"
    "2/tweets/search/recent"
)

# ==========================================
# WEATHER QUERY
# ==========================================

SOCIAL_WEATHER_QUERY = (
    "("
    "flood OR flooding OR "
    "\"heavy rain\" OR rainfall OR "
    "thunderstorm OR lightning OR "
    "heatwave OR cyclone OR "
    "\"strong wind\" OR fog"
    ") India "
    "lang:en "
    "-is:retweet"
)


# ==========================================
# FETCH REAL SOCIAL DATA
# ==========================================

def fetch_live_social_data(
    max_results=20
):

    bearer_token = os.getenv(
        "X_BEARER_TOKEN"
    )


    # ======================================
    # TOKEN NOT CONFIGURED
    # ======================================

    if not bearer_token:

        return {

            "success": False,

            "configured": False,

            "message":
                (
                    "X API is not configured. "
                    "Add X_BEARER_TOKEN to .env"
                ),

            "data": []

        }


    try:

        headers = {

            "Authorization":
                f"Bearer {bearer_token}"

        }


        params = {

            "query":
                SOCIAL_WEATHER_QUERY,

            "max_results":
                max_results,

            "tweet.fields":
                (
                    "created_at,"
                    "public_metrics,"
                    "author_id,"
                    "lang"
                ),

            "expansions":
                "author_id",

            "user.fields":
                (
                    "username,"
                    "verified"
                )

        }


        response = requests.get(

            X_API_URL,

            headers=headers,

            params=params,

            timeout=20

        )


        response.raise_for_status()


        data = response.json()


        tweets = (
            data.get("data", [])
        )


        users = {

            user.get("id"):
            user

            for user in
            data.get(
                "includes",
                {}
            ).get(
                "users",
                []
            )

        }


        results = []


        for tweet in tweets:

            metrics = (
                tweet.get(
                    "public_metrics",
                    {}
                )
            )


            author_id = (
                tweet.get(
                    "author_id"
                )
            )


            user = (
                users.get(
                    author_id,
                    {}
                )
            )


            username = (
                user.get(
                    "username",
                    "Unknown"
                )
            )


            tweet_id = (
                tweet.get("id")
            )


            results.append({

                "external_id":
                    f"x-{tweet_id}",

                "description":
                    tweet.get(
                        "text",
                        ""
                    ),

                "source":
                    "Social Media",

                "source_name":
                    f"X / Twitter - @{username}",

                "source_url":
                    (
                        "https://x.com/"
                        f"{username}/status/"
                        f"{tweet_id}"
                    ),

                "published_at":
                    tweet.get(
                        "created_at"
                    ),

                "likes":
                    metrics.get(
                        "like_count",
                        0
                    ),

                "replies":
                    metrics.get(
                        "reply_count",
                        0
                    ),

                "reposts":
                    metrics.get(
                        "retweet_count",
                        0
                    ),

                "quotes":
                    metrics.get(
                        "quote_count",
                        0
                    ),

                "raw":
                    tweet

            })


        return {

            "success": True,

            "configured": True,

            "source":
                "X / Twitter",

            "count":
                len(results),

            "data":
                results

        }


    except requests.exceptions.HTTPError as error:

        return {

            "success": False,

            "configured": True,

            "message":
                (
                    "X API returned an error: "
                    f"{str(error)}"
                ),

            "data": []

        }


    except Exception as error:

        return {

            "success": False,

            "configured": True,

            "message":
                (
                    "Social media processing error: "
                    f"{str(error)}"
                ),

            "data": []

        }