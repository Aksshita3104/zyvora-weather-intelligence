import os
import time
import logging
import re
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================================================
# NEWS SERVICE
# =========================================================

class NewsService:

    def __init__(self):

        # =================================================
        # API CONFIGURATION
        # =================================================

        self.news_api_key = os.getenv("NEWS_API_KEY")

        self.newsapi_url = (
            "https://newsapi.org/v2/everything"
        )

        self.gdelt_url = (
            "https://api.gdeltproject.org/api/v2/doc/doc"
        )

        # =================================================
        # CACHE
        # =================================================

        self.cache = []
        self.cache_time = None
        self.cache_duration = 300

        # =================================================
        # GDELT RATE LIMIT
        # =================================================

        self.last_gdelt_request = None
        self.gdelt_min_interval = 6

        # =================================================
        # WEATHER EVENT DEFINITIONS
        #
        # Order matters.
        # Specific events must come before general events.
        # =================================================

        self.event_mapping = {

            "Flood": [
                "flash flood",
                "flash flooding",
                "river flood",
                "river flooding",
                "flood waters",
                "floodwater",
                "floodwaters",
                "severe flooding",
                "major flooding",
                "flooding",
                "flood"
            ],

            "Landslide": [
                "landslide",
                "landslides",
                "mudslide",
                "mudslides"
            ],

            "Cyclone": [
                "cyclonic storm",
                "tropical cyclone",
                "cyclone"
            ],

            "Thunderstorm": [
                "severe thunderstorms",
                "severe thunderstorm",
                "thunderstorms",
                "thunderstorm"
            ],

            "Heavy Rainfall": [
                "extremely heavy rainfall",
                "extremely heavy rain",
                "very heavy rainfall",
                "very heavy rain",
                "heavy rainfall",
                "heavy showers",
                "heavy rain",
                "torrential rainfall",
                "torrential rain",
                "downpour",
                "downpours"
            ],

            "Heatwave": [
                "severe heatwave",
                "heatwave",
                "heat wave",
                "extreme heat",
                "heat alert"
            ],

            "Drought": [
                "severe drought",
                "drought",
                "water scarcity",
                "water shortage"
            ],

            "Storm": [
                "severe storm",
                "storm warning",
                "strong winds",
                "strong wind",
                "gusty winds",
                "high winds"
            ],

            "Fog": [
                "dense fog",
                "thick fog",
                "fog warning"
            ]
        }

        # =================================================
        # WEATHER CONTEXT KEYWORDS
        # =================================================

        self.weather_context_keywords = [

            "imd",
            "india meteorological department",
            "meteorological department",
            "weather department",
            "weather office",
            "met department",

            "weather forecast",
            "forecast",
            "weather warning",
            "weather alert",

            "monsoon",

            "rainfall",
            "temperature",
            "humidity",

            "weather conditions",

            "red alert",
            "orange alert",
            "yellow alert",

            "waterlogging",

            "gusty winds",
            "strong winds",

            "heavy showers",

            "rescue",
            "evacuated",
            "evacuation",

            "affected",
            "damage",
            "damaged",

            "traffic disruption",
            "roads flooded",

            "danger level",
            "warning level"
        ]

        # =================================================
        # IRRELEVANT CONTEXT
        #
        # These are checked carefully.
        # We do NOT automatically reject "minister"
        # because a genuine weather report may quote one.
        # =================================================

        self.hard_irrelevant_keywords = [

            # Entertainment

            "oscar",
            "cannes",
            "box office",
            "movie trailer",
            "film trailer",
            "new movie",
            "new film",
            "episode",
            "season finale",
            "netflix series",
            "album release",

            # War / Military

            "airstrike",
            "air strike",
            "missile attack",
            "missile strike",
            "russian strikes",
            "military operation",
            "military offensive",
            "troops deployed",
            "soldiers killed",
            "putin",
            "nato",

            # Financial / Business

            "stock market",
            "share market",
            "cryptocurrency",
            "bitcoin price",

            # Figurative patterns

            "market flooded with",
            "markets flooded with",
            "flooded the market",
            "flood of products",
            "flood of messages",
            "flood of posts",
            "flood of comments",
            "flood social media"
        ]

        # =================================================
        # POLITICAL / COMMENTARY CONTEXT
        #
        # These are not automatically rejected.
        # Instead we check whether weather evidence is weak.
        # =================================================

        self.commentary_keywords = [

            "slams centre",
            "slams government",
            "seeks tag",
            "seeks national disaster",
            "stepmotherly treatment",
            "political response",
            "political row",
            "political controversy",
            "blames government",
            "blames centre",
            "opposition leader",
            "leader of opposition"
        ]

        # =================================================
        # INCIDENTAL WEATHER CONTEXT
        #
        # Weather exists in article but is not the main event.
        # =================================================

        self.incidental_context_keywords = [

            "ganesh idol",
            "idol toppled",
            "procession",
            "devotees",
            "festival accident",
            "vehicle accident",
            "car accident",
            "road accident",
            "concert",
            "celebration"
        ]

        # =================================================
        # NEGATION PATTERNS
        #
        # Example:
        # Heavy rain unlikely
        # No heavy rain expected
        # Flood threat recedes
        # =================================================

        self.negation_patterns = [

            r"\bheavy rain\b.{0,50}\bunlikely\b",
            r"\bheavy rainfall\b.{0,50}\bunlikely\b",
            r"\bflood\b.{0,50}\bunlikely\b",

            r"\bunlikely\b.{0,50}\bheavy rain\b",
            r"\bunlikely\b.{0,50}\bheavy rainfall\b",
            r"\bunlikely\b.{0,50}\bflood\b",

            r"\bno heavy rain\b",
            r"\bno heavy rainfall\b",
            r"\bno rain expected\b",
            r"\bno major rain\b",

            r"\brain unlikely\b",
            r"\brain not expected\b",
            r"\bheavy spells unlikely\b",

            r"\bflood threat recedes\b",
            r"\bflood threat has receded\b",
            r"\bflood situation improves\b",
            r"\bflood situation improved\b"
        ]

        # =================================================
        # HISTORICAL EVENT PATTERNS
        # =================================================

        self.historical_patterns = [

            r"\bin\s+(18\d{2}|19\d{2})\b",

            r"\bmore than a century\b",

            r"\ba century ago\b",

            r"\bcentury ago\b",

            r"\bdecades ago\b",

            r"\byears ago\b",

            r"\bhistorical flood\b",

            r"\bhistoric flood of\b",

            r"\bremembering the\b",

            r"\banniversary of\b",

            r"\barchive\b",

            r"\bthen and now\b"
        ]

        # =================================================
        # FOREIGN LOCATIONS
        # =================================================

        self.foreign_locations = [

            "nepal",
            "china",
            "pakistan",
            "bangladesh",
            "sri lanka",
            "bhutan",
            "myanmar",
            "afghanistan",

            "ukraine",
            "russia",

            "united states",
            "usa",
            "america",
            "canada",

            "united kingdom",
            "england",
            "france",
            "germany",
            "italy",
            "spain",

            "japan",
            "australia",
            "new zealand",

            "middle east",
            "iran",
            "iraq",
            "israel",
            "gaza",

            "europe",
            "africa"
        ]

        # =================================================
        # INDIAN STATES / UTs
        # =================================================

        self.indian_states = [

            "andhra pradesh",
            "arunachal pradesh",
            "assam",
            "bihar",
            "chhattisgarh",
            "goa",
            "gujarat",
            "haryana",
            "himachal pradesh",
            "jharkhand",
            "karnataka",
            "kerala",
            "madhya pradesh",
            "maharashtra",
            "manipur",
            "meghalaya",
            "mizoram",
            "nagaland",
            "odisha",
            "punjab",
            "rajasthan",
            "sikkim",
            "tamil nadu",
            "telangana",
            "tripura",
            "uttar pradesh",
            "uttarakhand",
            "west bengal",

            "delhi",
            "jammu and kashmir",
            "ladakh",
            "puducherry"
        ]

        # =================================================
        # MAJOR INDIAN CITIES
        # =================================================

        self.indian_cities = [

            # Tamil Nadu

            "chennai",
            "coimbatore",
            "madurai",
            "tiruchirappalli",
            "trichy",
            "salem",
            "tirunelveli",
            "erode",
            "vellore",
            "thanjavur",
            "tiruppur",
            "dindigul",
            "thoothukudi",

            # Maharashtra

            "mumbai",
            "pune",
            "nagpur",
            "nashik",
            "kolhapur",

            # Karnataka

            "bengaluru",
            "bangalore",
            "mysore",
            "mangaluru",
            "belagavi",

            # Telangana

            "hyderabad",

            # Kerala

            "kochi",
            "thiruvananthapuram",
            "kozhikode",

            # West Bengal

            "kolkata",

            # Bihar

            "patna",
            "gaya",

            # Uttar Pradesh

            "lucknow",
            "kanpur",
            "agra",
            "varanasi",
            "noida",

            # Rajasthan

            "jaipur",
            "jodhpur",
            "udaipur",

            # Gujarat

            "ahmedabad",
            "surat",
            "vadodara",

            # Odisha

            "bhubaneswar",
            "cuttack",

            # Assam

            "guwahati",
            "sivasagar",

            # Punjab

            "amritsar",
            "ludhiana",

            # Uttarakhand

            "dehradun",

            # Himachal

            "shimla",

            # Jammu and Kashmir

            "srinagar"
        ]


    # =====================================================
    # CACHE
    # =====================================================

    def get_cached_news(self):

        if not self.cache or not self.cache_time:
            return None

        cache_age = (
            datetime.now()
            - self.cache_time
        )

        if cache_age < timedelta(
            seconds=self.cache_duration
        ):

            logger.info(
                "Using cached weather intelligence"
            )

            return self.cache

        return None


    def save_cache(self, news):

        if news:

            self.cache = news

            self.cache_time = datetime.now()

            logger.info(
                f"Cached {len(news)} valid articles"
            )


    # =====================================================
    # MAIN FUNCTION
    # =====================================================

    def fetch_weather_news(
        self,
        max_records=10
    ):

        cached_news = self.get_cached_news()

        if cached_news:

            return {

                "success": True,

                "source": "CACHE",

                "message":
                "Using cached weather intelligence",

                "data": cached_news
            }


        # =================================================
        # PRIMARY SOURCE
        # =================================================

        newsapi_result = self.fetch_from_newsapi(
            max_records
        )

        if newsapi_result:

            processed_news = self.remove_duplicates(
                newsapi_result
            )

            self.save_cache(
                processed_news
            )

            return {

                "success": True,

                "source": "NewsAPI",

                "message":
                "Live weather intelligence fetched successfully",

                "data": processed_news
            }


        # =================================================
        # GDELT FALLBACK
        # =================================================

        logger.warning(
            "NewsAPI returned no valid articles. "
            "Trying GDELT."
        )

        gdelt_result = self.fetch_from_gdelt(
            max_records
        )

        if gdelt_result:

            processed_news = self.remove_duplicates(
                gdelt_result
            )

            self.save_cache(
                processed_news
            )

            return {

                "success": True,

                "source": "GDELT",

                "message":
                "Live weather intelligence fetched successfully",

                "data": processed_news
            }


        return {

            "success": False,

            "source": "NONE",

            "message":
            "Unable to fetch valid live weather intelligence.",

            "data": []
        }


    # =====================================================
    # NEWSAPI
    # =====================================================

    def fetch_from_newsapi(
        self,
        max_records
    ):

        if not self.news_api_key:

            logger.warning(
                "NEWS_API_KEY not found"
            )

            return []


        # -------------------------------------------------
        # More targeted search query
        # -------------------------------------------------

        query = (

            "("

            "\"heavy rain\" OR "

            "\"heavy rainfall\" OR "

            "\"very heavy rainfall\" OR "

            "flood OR flooding OR "

            "cyclone OR "

            "thunderstorm OR "

            "landslide OR "

            "heatwave OR "

            "drought OR "

            "\"weather warning\" OR "

            "\"IMD forecast\""

            ") AND India"
        )


        params = {

            "q": query,

            "language": "en",

            "sortBy": "publishedAt",

            "pageSize":
            min(max_records * 8, 100),

            "apiKey":
            self.news_api_key
        }


        try:

            logger.info(
                "Fetching live weather news "
                "from NewsAPI..."
            )


            response = requests.get(

                self.newsapi_url,

                params=params,

                timeout=20
            )


            if response.status_code != 200:

                logger.warning(

                    f"NewsAPI Error: "
                    f"{response.status_code}"
                )

                return []


            result = response.json()

            articles = result.get(
                "articles",
                []
            )


            logger.info(
                f"Raw NewsAPI articles: "
                f"{len(articles)}"
            )


            processed_news = []


            for article in articles:

                news_item = (
                    self.process_news_article(
                        article,
                        source_type="NewsAPI"
                    )
                )


                if news_item:

                    processed_news.append(
                        news_item
                    )


                if (
                    len(processed_news)
                    >= max_records
                ):

                    break


            logger.info(

                f"Final valid articles: "
                f"{len(processed_news)}"
            )


            return processed_news


        except requests.exceptions.Timeout:

            logger.error(
                "NewsAPI request timed out"
            )

            return []


        except requests.exceptions.RequestException as e:

            logger.error(
                f"NewsAPI request error: {e}"
            )

            return []


        except Exception as e:

            logger.exception(
                f"Unexpected NewsAPI error: {e}"
            )

            return []


    # =====================================================
    # GDELT FALLBACK
    # =====================================================

    def fetch_from_gdelt(
        self,
        max_records
    ):

        if self.last_gdelt_request:

            elapsed = (
                time.time()
                - self.last_gdelt_request
            )

            if elapsed < self.gdelt_min_interval:

                logger.warning(
                    "Skipping GDELT to avoid rate limit"
                )

                return []


        query = (

            "("

            "flood OR flooding OR "

            "\"heavy rain\" OR "

            "\"heavy rainfall\" OR "

            "thunderstorm OR "

            "cyclone OR "

            "landslide OR "

            "heatwave OR "

            "drought"

            ") India"
        )


        params = {

            "query": query,

            "mode": "artlist",

            "maxrecords":
            min(max_records * 8, 50),

            "timespan": "24h",

            "sort": "datedesc",

            "format": "json"
        }


        try:

            logger.info(
                "Fetching GDELT fallback..."
            )

            self.last_gdelt_request = time.time()


            response = requests.get(

                self.gdelt_url,

                params=params,

                timeout=20,

                headers={

                    "User-Agent":

                    "ZYVORA Weather Intelligence/1.0"
                }
            )


            if response.status_code == 429:

                logger.warning(
                    "GDELT rate limit reached"
                )

                return []


            if response.status_code != 200:

                logger.warning(

                    f"GDELT Error: "
                    f"{response.status_code}"
                )

                return []


            result = response.json()

            articles = result.get(
                "articles",
                []
            )


            processed_news = []


            for article in articles:


                converted_article = {

                    "title":

                    article.get(
                        "title",
                        ""
                    ),

                    "description":

                    article.get(
                        "title",
                        ""
                    ),

                    "url":

                    article.get(
                        "url",
                        ""
                    ),

                    "source": {

                        "name":

                        article.get(
                            "domain",
                            "GDELT"
                        )
                    },

                    "publishedAt":

                    article.get(
                        "seendate",
                        ""
                    )
                }


                news_item = (
                    self.process_news_article(
                        converted_article,
                        source_type="GDELT"
                    )
                )


                if news_item:

                    processed_news.append(
                        news_item
                    )


                if (
                    len(processed_news)
                    >= max_records
                ):

                    break


            return processed_news


        except Exception as e:

            logger.error(
                f"GDELT Error: {e}"
            )

            return []


    # =====================================================
    # CORE NEWS INTELLIGENCE PROCESSOR
    # =====================================================

    def process_news_article(
        self,
        article,
        source_type
    ):

        title = (

            article.get(
                "title",
                ""
            )
            or ""

        ).strip()


        description = (

            article.get(
                "description",
                ""
            )
            or ""

        ).strip()


        if not title:

            return None


        combined_text = (
            title
            + " "
            + description
        ).lower()


        title_lower = title.lower()


        # =================================================
        # 1. HISTORICAL EVENT FILTER
        # =================================================

        if self.is_historical_article(
            title_lower,
            combined_text
        ):

            logger.info(
                f"REJECTED HISTORICAL: {title}"
            )

            return None


        # =================================================
        # 2. HARD IRRELEVANT FILTER
        # =================================================

        if self.is_hard_irrelevant_article(
            combined_text
        ):

            logger.info(
                f"REJECTED IRRELEVANT: {title}"
            )

            return None


        # =================================================
        # 3. NEGATION FILTER
        # =================================================

        if self.has_weather_negation(
            title_lower,
            combined_text
        ):

            logger.info(
                f"REJECTED NEGATED WEATHER: {title}"
            )

            return None


        # =================================================
        # 4. DETECT WEATHER EVENT
        # =================================================

        event_type = self.detect_event_type(
            combined_text
        )


        if event_type is None:

            logger.info(
                f"REJECTED NO EVENT: {title}"
            )

            return None


        # =================================================
        # 5. FIGURATIVE FLOOD CHECK
        # =================================================

        if (
            event_type == "Flood"
            and self.is_figurative_flood(
                combined_text
            )
        ):

            logger.info(
                f"REJECTED FIGURATIVE FLOOD: {title}"
            )

            return None


        # =================================================
        # 6. FOREIGN EVENT CHECK
        # =================================================

        if self.is_foreign_event(
            title_lower,
            combined_text
        ):

            logger.info(
                f"REJECTED FOREIGN EVENT: {title}"
            )

            return None


        # =================================================
        # 7. LOCATION DETECTION
        # =================================================

        location = self.detect_location(
            combined_text
        )


        if location == "Unknown":

            if not self.has_india_context(
                combined_text
            ):

                logger.info(
                    f"REJECTED NO INDIA CONTEXT: {title}"
                )

                return None

            location = "India"


        # =================================================
        # 8. REQUIRE VALID WEATHER CONTEXT
        # =================================================

        if not self.is_valid_weather_context(
            combined_text,
            event_type
        ):

            logger.info(
                f"REJECTED WEAK WEATHER CONTEXT: {title}"
            )

            return None


        # =================================================
        # 9. REJECT COMMENTARY-FIRST ARTICLES
        # =================================================

        if self.is_commentary_article(
            combined_text,
            event_type
        ):

            logger.info(
                f"REJECTED COMMENTARY ARTICLE: {title}"
            )

            return None


        # =================================================
        # 10. REJECT INCIDENTAL WEATHER
        # =================================================

        if self.is_incidental_weather_article(
            combined_text,
            event_type
        ):

            logger.info(
                f"REJECTED INCIDENTAL WEATHER: {title}"
            )

            return None


        # =================================================
        # 11. FRESHNESS CHECK
        # =================================================

        published_at = article.get(
            "publishedAt",
            ""
        )


        if not self.is_reasonably_recent(
            published_at
        ):

            logger.info(
                f"REJECTED OLD ARTICLE: {title}"
            )

            return None


        # =================================================
        # 12. CONFIDENCE
        # =================================================

        confidence = self.calculate_confidence(

            combined_text,

            event_type,

            location
        )


        # =================================================
        # 13. RISK
        # =================================================

        risk_level = self.calculate_risk(

            combined_text,

            event_type
        )


        # =================================================
        # SOURCE
        # =================================================

        source_data = article.get(
            "source",
            {}
        )


        if isinstance(
            source_data,
            dict
        ):

            source_name = (

                source_data.get(
                    "name",
                    source_type
                )
                or source_type
            )

        else:

            source_name = source_type


        # =================================================
        # FINAL CLEAN RESULT
        # =================================================

        return {

            "title":
            title,

            "description":
            description,

            "url":

            article.get(
                "url",
                ""
            ),

            "source":
            source_name,

            "published_at":
            published_at,

            "event_type":
            event_type,

            "location":
            location,

            "risk_level":
            risk_level,

            "confidence":
            confidence,

            "data_source":
            source_type
        }


    # =====================================================
    # HISTORICAL ARTICLE DETECTION
    # =====================================================

    def is_historical_article(
        self,
        title,
        text
    ):

        # Historical pattern in title
        # is a strong indicator.

        for pattern in self.historical_patterns:

            if re.search(
                pattern,
                title,
                re.IGNORECASE
            ):

                return True


        # Check first 250 characters.
        # Avoid rejecting a current article
        # that briefly mentions history later.

        first_part = text[:250]


        for pattern in self.historical_patterns:

            if re.search(
                pattern,
                first_part,
                re.IGNORECASE
            ):

                return True


        return False


    # =====================================================
    # HARD IRRELEVANT CHECK
    # =====================================================

    def is_hard_irrelevant_article(
        self,
        text
    ):

        for keyword in (
            self.hard_irrelevant_keywords
        ):

            if keyword in text:

                return True


        return False


    # =====================================================
    # NEGATION DETECTION
    # =====================================================

    def has_weather_negation(
        self,
        title,
        text
    ):

        # Title has strongest importance

        for pattern in self.negation_patterns:

            if re.search(
                pattern,
                title,
                re.IGNORECASE
            ):

                return True


        # Also check combined text

        for pattern in self.negation_patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):

                return True


        return False


    # =====================================================
    # WEATHER EVENT DETECTION
    # =====================================================

    def detect_event_type(
        self,
        text
    ):

        text = text.lower()


        for (
            event_type,
            keywords
        ) in self.event_mapping.items():

            for keyword in keywords:

                pattern = (

                    r"\b"

                    + re.escape(keyword)

                    + r"\b"
                )


                if re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                ):

                    return event_type


        return None


    # =====================================================
    # FIGURATIVE FLOOD DETECTION
    # =====================================================

    def is_figurative_flood(
        self,
        text
    ):

        figurative_patterns = [

            r"\bflood\w*\s+market",

            r"\bmarket\w*\s+flood\w*",

            r"\bflood of\s+",

            r"\bflooded with\s+products",

            r"\bflooded with\s+goods",

            r"\bflooded with\s+messages",

            r"\bflooded with\s+comments",

            r"\bflooded with\s+posts",

            r"\bflooded social media"
        ]


        for pattern in figurative_patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):

                # If there are strong real flood
                # indicators, don't reject.

                real_flood_indicators = [

                    "water level",

                    "river",

                    "inundated",

                    "flood waters",

                    "floodwater",

                    "evacuated",

                    "rescue",

                    "homes flooded",

                    "villages flooded",

                    "roads flooded",

                    "flood-hit"
                ]


                if not any(
                    indicator in text
                    for indicator in
                    real_flood_indicators
                ):

                    return True


        return False


    # =====================================================
    # FOREIGN EVENT DETECTION
    # =====================================================

    def is_foreign_event(
        self,
        title,
        text
    ):

        # Foreign country in title means
        # high probability event is outside India.

        for country in self.foreign_locations:

            pattern = (
                r"\b"
                + re.escape(country)
                + r"\b"
            )

            if re.search(
                pattern,
                title,
                re.IGNORECASE
            ):

                return True


        # Check beginning of article

        first_part = text[:300]


        for country in self.foreign_locations:

            pattern = (
                r"\b"
                + re.escape(country)
                + r"\b"
            )

            if re.search(
                pattern,
                first_part,
                re.IGNORECASE
            ):

                indian_location = (
                    self.detect_location(
                        first_part
                    )
                )

                if (
                    indian_location
                    == "Unknown"
                ):

                    return True


        return False


    # =====================================================
    # INDIAN LOCATION DETECTION
    # =====================================================

    def detect_location(
        self,
        text
    ):

        # Cities first

        for city in self.indian_cities:

            pattern = (
                r"\b"
                + re.escape(city)
                + r"\b"
            )

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):

                if city == "bangalore":
                    return "Bengaluru"

                if city == "trichy":
                    return "Tiruchirappalli"

                return city.title()


        # States next

        for state in self.indian_states:

            pattern = (
                r"\b"
                + re.escape(state)
                + r"\b"
            )

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):

                return state.title()


        return "Unknown"


    # =====================================================
    # INDIA CONTEXT
    # =====================================================

    def has_india_context(
        self,
        text
    ):

        india_context_words = [

            "india",

            "indian",

            "imd",

            "india meteorological department"
        ]


        return any(

            word in text

            for word in
            india_context_words
        )


    # =====================================================
    # VALID WEATHER CONTEXT
    # =====================================================

    def is_valid_weather_context(
        self,
        text,
        event_type
    ):

        strong_events = [

            "Flood",

            "Landslide",

            "Cyclone",

            "Thunderstorm",

            "Heavy Rainfall",

            "Heatwave",

            "Drought"
        ]


        if event_type not in strong_events:

            return False


        context_count = 0


        for keyword in (
            self.weather_context_keywords
        ):

            if keyword in text:

                context_count += 1


        # Strong events with at least one
        # supporting weather/disaster signal.

        disaster_context = [

            "affected",

            "damage",

            "damaged",

            "rescue",

            "evacuated",

            "warning",

            "alert",

            "forecast",

            "imd",

            "rainfall",

            "weather",

            "water level",

            "river",

            "roads",

            "traffic"
        ]


        if any(
            word in text
            for word in disaster_context
        ):

            return True


        return context_count >= 1


    # =====================================================
    # COMMENTARY ARTICLE DETECTION
    # =====================================================

    def is_commentary_article(
        self,
        text,
        event_type
    ):

        commentary_found = any(

            keyword in text

            for keyword in
            self.commentary_keywords
        )


        if not commentary_found:

            return False


        # If commentary exists but there is
        # strong current weather evidence,
        # allow it.

        current_weather_signals = [

            "imd forecast",

            "weather warning",

            "heavy rainfall today",

            "rainfall today",

            "currently flooded",

            "currently affected",

            "rescue operation",

            "evacuation underway",

            "red alert",

            "orange alert"
        ]


        if any(
            signal in text
            for signal in
            current_weather_signals
        ):

            return False


        return True


    # =====================================================
    # INCIDENTAL WEATHER DETECTION
    # =====================================================

    def is_incidental_weather_article(
        self,
        text,
        event_type
    ):

        incidental_found = any(

            keyword in text

            for keyword in
            self.incidental_context_keywords
        )


        if not incidental_found:

            return False


        # If weather is clearly the primary
        # event, do not reject.

        primary_weather_signals = [

            "imd",

            "weather warning",

            "weather alert",

            "rainfall forecast",

            "heavy rainfall warning",

            "flood warning",

            "evacuation",

            "waterlogging",

            "roads flooded",

            "rescue operation"
        ]


        if any(
            signal in text
            for signal in
            primary_weather_signals
        ):

            return False


        return True


    # =====================================================
    # FRESHNESS CHECK
    # =====================================================

    def is_reasonably_recent(
        self,
        date_string
    ):

        if not date_string:

            # Do not reject because
            # GDELT format may vary.

            return True


        parsed_date = parse_news_date(
            date_string
        )


        if parsed_date is None:

            return True


        # Make timezone aware

        if parsed_date.tzinfo is None:

            parsed_date = (
                parsed_date.replace(
                    tzinfo=timezone.utc
                )
            )


        now = datetime.now(
            timezone.utc
        )


        age = now - parsed_date


        # Live intelligence:
        # Allow maximum 7 days.

        if age > timedelta(days=7):

            return False


        # Future dates can sometimes
        # occur due to API timezone issues.
        # Allow small difference.

        if age < timedelta(days=-1):

            return False


        return True


    # =====================================================
    # CONFIDENCE
    # =====================================================

    def calculate_confidence(
        self,
        text,
        event_type,
        location
    ):

        score = 50


        # Valid event

        if event_type:

            score += 20


        # Indian location

        if location != "Unknown":

            score += 15


        # Event evidence

        event_matches = 0


        event_keywords = (
            self.event_mapping.get(
                event_type,
                []
            )
        )


        for keyword in event_keywords:

            if keyword in text:

                event_matches += 1


        score += min(
            event_matches * 4,
            10
        )


        # Official / weather authority

        authority_words = [

            "imd",

            "india meteorological department",

            "meteorological department",

            "weather department",

            "forecast",

            "warning",

            "alert"
        ]


        if any(
            word in text
            for word in authority_words
        ):

            score += 5


        return min(
            score,
            100
        )


    # =====================================================
    # RISK ENGINE
    # =====================================================

    def calculate_risk(
        self,
        text,
        event_type
    ):

        text = text.lower()


        critical_words = [

            "multiple deaths",

            "people killed",

            "death toll",

            "fatalities",

            "mass evacuation",

            "major disaster",

            "state of emergency",

            "red alert"
        ]


        high_words = [

            "death",

            "deaths",

            "dead",

            "killed",

            "fatal",

            "severe",

            "evacuated",

            "evacuation",

            "danger level",

            "major damage",

            "disaster",

            "rescue operation"
        ]


        medium_words = [

            "affected",

            "damage",

            "waterlogging",

            "traffic disruption",

            "heavy rain",

            "heavy rainfall",

            "strong winds",

            "gusty winds",

            "warning",

            "alert",

            "schools closed"
        ]


        # -------------------------------------------------
        # CRITICAL
        # -------------------------------------------------

        if any(
            word in text
            for word in critical_words
        ):

            return "CRITICAL"


        # -------------------------------------------------
        # HIGH
        # -------------------------------------------------

        if any(
            word in text
            for word in high_words
        ):

            return "HIGH"


        # -------------------------------------------------
        # EVENT BASED
        # -------------------------------------------------

        if event_type in [

            "Flood",

            "Landslide",

            "Cyclone"
        ]:

            return "HIGH"


        if event_type in [

            "Heavy Rainfall",

            "Thunderstorm",

            "Storm",

            "Heatwave"
        ]:

            return "MEDIUM"


        # -------------------------------------------------
        # MEDIUM CONTEXT
        # -------------------------------------------------

        if any(
            word in text
            for word in medium_words
        ):

            return "MEDIUM"


        return "LOW"


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    def remove_duplicates(
        self,
        news_list
    ):

        unique_news = []

        seen_titles = set()


        for news in news_list:

            title = (

                news.get(
                    "title",
                    ""
                )
                .lower()
                .strip()
            )


            if (
                title
                and title
                not in seen_titles
            ):

                seen_titles.add(
                    title
                )

                unique_news.append(
                    news
                )


        return unique_news


# =========================================================
# SERVICE INSTANCE
# =========================================================

news_service = NewsService()


# =========================================================
# COMPATIBILITY FUNCTION
#
# realtime_service.py imports this.
# DO NOT REMOVE.
# =========================================================

def fetch_live_news(
    max_records=10
):

    return news_service.fetch_weather_news(
        max_records=max_records
    )


# =========================================================
# DATE PARSER
#
# realtime_service.py imports this.
# DO NOT REMOVE.
# =========================================================

def parse_news_date(
    date_string
):

    if not date_string:

        return None


    date_string = (
        str(date_string)
        .strip()
    )


    # Remove milliseconds if necessary

    if "." in date_string:

        date_string = (
            date_string.split(".")[0]
            + (
                "Z"
                if date_string.endswith("Z")
                else ""
            )
        )


    date_formats = [

        "%Y%m%dT%H%M%SZ",

        "%Y%m%d%H%M%S",

        "%Y-%m-%dT%H:%M:%SZ",

        "%Y-%m-%dT%H:%M:%S%z",

        "%Y-%m-%dT%H:%M:%S",

        "%Y-%m-%d %H:%M:%S",

        "%Y-%m-%d"
    ]


    for date_format in date_formats:

        try:

            return datetime.strptime(
                date_string,
                date_format
            )

        except (
            ValueError,
            TypeError
        ):

            continue


    logger.warning(
        f"Could not parse date: "
        f"{date_string}"
    )


    return None