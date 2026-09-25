import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
// import "./App.css";
import "./Appprofessional.css";
import AdminLogin from "./pages/AdminLogin";

const API_URL = "http://127.0.0.1:8000";

const INDIA_CENTER = [22.5937, 78.9629];
// =====================================================
// ZYVORA LIVE WEATHER LOCATIONS
// =====================================================

const WEATHER_CITIES = {

  Madurai: {
    latitude: 9.9252,
    longitude: 78.1198,
  },

  Chennai: {
    latitude: 13.0827,
    longitude: 80.2707,
  },

  Mumbai: {
    latitude: 19.0760,
    longitude: 72.8777,
  },

  Delhi: {
    latitude: 28.6139,
    longitude: 77.2090,
  },

  Kolkata: {
    latitude: 22.5726,
    longitude: 88.3639,
  },

  Bengaluru: {
    latitude: 12.9716,
    longitude: 77.5946,
  },

  Hyderabad: {
    latitude: 17.3850,
    longitude: 78.4867,
  },

};
const EVENTS = {
  Flood: { icon: "🌊", color: "#2563eb" },
  "Heavy Rainfall": { icon: "🌧️", color: "#0ea5e9" },
  Thunderstorm: { icon: "⛈️", color: "#7c3aed" },
  Heatwave: { icon: "🔥", color: "#f97316" },
  Fog: { icon: "🌫️", color: "#64748b" },
  "Dust Storm": { icon: "🌪️", color: "#d97706" },
  "Strong Wind": { icon: "💨", color: "#06b6d4" },
  Cyclone: { icon: "🌀", color: "#0f766e" },
  Other: { icon: "🌤️", color: "#64748b" },
};


// =====================================================
// MAP AUTO CENTER
// =====================================================

function AutoCenter({ reports }) {

  const map = useMap();

  useEffect(() => {

    if (reports.length === 1) {

      const only = reports[0];

      map.flyTo(
        [
          Number(only.latitude),
          Number(only.longitude),
        ],
        7,
        {
          duration: 0.8,
        }
      );

      return;
    }

    if (reports.length > 1) {

      const bounds = reports.map((report) => [
        Number(report.latitude),
        Number(report.longitude),
      ]);

      map.fitBounds(bounds, {
        padding: [36, 36],
        maxZoom: 7,
        animate: true,
        duration: 0.8,
      });

    }

  }, [reports, map]);

  return null;

}


// =====================================================
// HELPER FUNCTIONS
// =====================================================

const eventInfo = (type) =>
  EVENTS[type] || EVENTS.Other;


const score = (value) =>
  Math.round(Number(value || 0));


const statusClass = (status) =>
  `status status-${String(
    status || "Under Review"
  )
    .toLowerCase()
    .replace(/\s+/g, "-")}`;


const weatherMood = (description) => {

  const d = String(description || "").toLowerCase();

  if (/thunder|storm/.test(d)) return "storm";
  if (/snow|sleet|ice pellet/.test(d)) return "snow";
  if (/fog|mist|haze/.test(d)) return "fog";
  if (/drizzle|rain|shower/.test(d)) return "rain";
  if (/overcast|cloud/.test(d)) return "cloudy";
  if (/clear|sun/.test(d)) return "sunny";

  return "default";

};


// Online weather images for Live Weather News cards.
// The image is selected from the event/title/description so every
// weather condition gets a visually relevant image instead of one
// repeated dark-cloud fallback.
const WEATHER_NEWS_IMAGES = {
  sunny: "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1400&q=85",
  cloudy: "https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1400&q=85",
  rain: "https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=1400&q=85",
  storm: "https://images.unsplash.com/photo-1461511669078-d46bf351cd6e?auto=format&fit=crop&w=1400&q=85",
  fog: "https://loremflickr.com/1400/800/fog,weather?lock=21",
  heatwave: "https://loremflickr.com/1400/800/heatwave,weather?lock=22",
  wind: "https://loremflickr.com/1400/800/wind,weather?lock=23",
  cyclone: "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?auto=format&fit=crop&w=1400&q=85",
  default: "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1400&q=85",
};

const weatherNewsImage = (news) => {
  const text = [
    news?.event_type,
    news?.title,
    news?.description,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  if (/cyclone|hurricane|tropical storm/.test(text)) return WEATHER_NEWS_IMAGES.cyclone;
  if (/thunderstorm|lightning|severe storm|storm/.test(text)) return WEATHER_NEWS_IMAGES.storm;
  if (/heavy rain|rainfall|rain|drizzle|shower|flood/.test(text)) return WEATHER_NEWS_IMAGES.rain;
  if (/fog|mist|haze/.test(text)) return WEATHER_NEWS_IMAGES.fog;
  if (/heatwave|heat wave|extreme heat|hot weather|temperature/.test(text)) return WEATHER_NEWS_IMAGES.heatwave;
  if (/strong wind|high wind|windstorm|gust|wind/.test(text)) return WEATHER_NEWS_IMAGES.wind;
  if (/overcast|cloudy|cloud cover|cloud/.test(text)) return WEATHER_NEWS_IMAGES.cloudy;
  if (/clear|sunny|sunshine|bright/.test(text)) return WEATHER_NEWS_IMAGES.sunny;

  return WEATHER_NEWS_IMAGES.default;
};




// =====================================================
// MAIN APP
// =====================================================

function App() {


  // =====================================================
  // APP STATE
  // =====================================================

  const [activePage, setActivePage] =
    useState("Dashboard");


  // =====================================================
  // ADMIN AUTHENTICATION
  // =====================================================

  const [isAdmin, setIsAdmin] =
    useState(() => {
      try {
        return Boolean(localStorage.getItem("admin_token"));
      } catch {
        return false;
      }
    });

  const [adminReports, setAdminReports] =
    useState([]);

  const [adminLoading, setAdminLoading] =
    useState(false);

  useEffect(() => {
    try {
      localStorage.setItem("zyvora-active-page", activePage);
    } catch {
      // Ignore storage errors and keep normal navigation working.
    }
  }, [activePage]);


  const [reports, setReports] =
    useState([]);


  const [dashboard, setDashboard] =
    useState({});


  const [loading, setLoading] =
    useState(false);


  const [backendError, setBackendError] =
    useState("");


  const [selectedReport, setSelectedReport] =
    useState(null);



  // =====================================================
  // CITIZEN REPORT STATE
  // =====================================================

  const [description, setDescription] =
    useState("");


  const [source, setSource] =
    useState("Citizen");


  const [submitResult, setSubmitResult] =
    useState(null);



  // =====================================================
  // SOCIAL INTELLIGENCE STATE
  // =====================================================

  const [socialText, setSocialText] =
    useState("");


  const [platform, setPlatform] =
    useState("X / Twitter");


  const [socialResult, setSocialResult] =
    useState(null);


  // =====================================================
  // LIVE WEATHER NEWS STATE
  // =====================================================

  const [liveNews, setLiveNews] =
    useState([]);


  const [newsLoading, setNewsLoading] =
    useState(false);


  const [newsError, setNewsError] =
    useState("");


  const [newsUpdatedAt, setNewsUpdatedAt] =
    useState(null);


// =====================================================
// REAL-TIME WEATHER STATE
// =====================================================

const [selectedWeatherCity, setSelectedWeatherCity] =
  useState("Madurai");


const [liveWeather, setLiveWeather] =
  useState(null);


const [weatherLoading, setWeatherLoading] =
  useState(false);


const [weatherError, setWeatherError] =
  useState("");


const [weatherUpdatedAt, setWeatherUpdatedAt] =
  useState(null);
  // =====================================================
  // FILTER STATE
  // =====================================================

  const [filters, setFilters] =
    useState({

      event: "All Events",

      location: "",

      state: "All States",

      district: "All Districts",

      status: "All Status",

      source: "All Sources",

    });



  // =====================================================
  // FETCH HELPER
  // =====================================================

  const fetchJSON =
    async (path, options = {}) => {

      const response =
        await fetch(
          `${API_URL}${path}`,
          options
        );


      if (!response.ok) {

        const error =
          await response.text();

        throw new Error(
          error || "Request failed"
        );

      }


      return response.json();

    };



  // =====================================================
  // LOAD PROTECTED ADMIN REPORTS
  // =====================================================

  const loadAdminReports =
    async () => {

      const token = localStorage.getItem("admin_token");

      if (!token) {
        return;
      }

      try {

        setAdminLoading(true);

        const response = await fetch(
          `${API_URL}/api/admin/reports`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 401 || response.status === 403) {
          localStorage.removeItem("admin_token");
          localStorage.removeItem("admin_role");
          setIsAdmin(false);
          setActivePage("Admin Panel");
          return;
        }

        if (!response.ok) {
          throw new Error("Unable to load admin reports");
        }

        const data = await response.json();
        setAdminReports(Array.isArray(data) ? data : []);

      } catch (error) {
        console.error("Admin reports error:", error);
      } finally {
        setAdminLoading(false);
      }
    };

  useEffect(() => {
    if (activePage === "Admin Panel" && isAdmin) {
      loadAdminReports();
    }
  }, [activePage, isAdmin]);


  // =====================================================
  // LOAD REPORTS + DASHBOARD
  // =====================================================

  const loadData =
    async () => {

      try {

        const [
          reportData,
          dashboardData,
        ] = await Promise.all([

          fetchJSON(
            "/api/reports"
          ),

          fetchJSON(
            "/api/dashboard"
          ),

        ]);


        setReports(

          Array.isArray(reportData)
            ? reportData
            : []

        );


        setDashboard(
          dashboardData || {}
        );


        setBackendError("");


      } catch (error) {

        console.error(error);


        setBackendError(

          "Cannot connect to the backend. Please check that FastAPI is running on http://127.0.0.1:8000."

        );

      }

    };



  // =====================================================
  // FETCH LIVE WEATHER NEWS
  // =====================================================

  const loadLiveNews =
    async () => {

      try {

        setNewsLoading(true);

        setNewsError("");

       const paths = [
  "/api/realtime/news/preview",
];

        let result = null;
        let lastError = null;

        for (const path of paths) {

          try {

            const response =
              await fetch(
                `${API_URL}${path}`
              );

            if (!response.ok) {

              throw new Error(
                `${response.status} ${response.statusText}`
              );

            }

            result =
              await response.json();

            break;

          } catch (error) {

            lastError = error;

          }

        }

        if (!result) {

          throw (
            lastError ||
            new Error(
              "Unable to fetch live weather news"
            )
          );

        }

        const newsData =
          Array.isArray(result)
            ? result
            : (
                Array.isArray(result.data)
                  ? result.data
                  : []
              );

        setLiveNews(newsData);

        setNewsUpdatedAt(
          new Date()
        );

      } catch (error) {

        console.error(
          "Live news error:",
          error
        );

        setNewsError(
          "Cannot connect to the live news service. Please check that the FastAPI realtime service is running."
        );

      } finally {

        setNewsLoading(false);

      }

    };
    // =====================================================
// FETCH REAL-TIME WEATHER
// =====================================================

const loadLiveWeather =
  async (
    city = selectedWeatherCity
  ) => {

    try {

      setWeatherLoading(true);

      setWeatherError("");

      const coordinates =
        WEATHER_CITIES[city];


      if (!coordinates) {

        throw new Error(
          "Selected city coordinates not found"
        );

      }


      const query =

        `/api/realtime/weather/current?latitude=${coordinates.latitude}&longitude=${coordinates.longitude}`;


      const data =
        await fetchJSON(query);


      if (!data.success) {

        throw new Error(

          data.message
          ||
          "Unable to load live weather"

        );

      }


      setLiveWeather(
        data.data
      );


      setWeatherUpdatedAt(
        new Date()
      );


    }
    catch (error) {

      console.error(
        "Live weather error:",
        error
      );


      setWeatherError(
        error.message
        ||
        "Unable to connect to live weather service"
      );

    }
    finally {

      setWeatherLoading(false);

    }

  };



  // =====================================================
  // INITIAL LOAD
  // =====================================================

  useEffect(() => {

    loadData();


    const timer =
      setInterval(
        loadData,
        15000
      );


    return () =>
      clearInterval(timer);


  }, []);


  // =====================================================
  // LIVE NEWS AUTO REFRESH
  // =====================================================

  useEffect(() => {

    loadLiveNews();

    const newsTimer =
      setInterval(
        loadLiveNews,
        300000
      );

    return () =>
      clearInterval(newsTimer);

  }, []);

// =====================================================
// INITIAL LIVE WEATHER LOAD
// =====================================================

useEffect(() => {

  loadLiveWeather(
    selectedWeatherCity
  );


  const weatherTimer =
    setInterval(

      () => {

        loadLiveWeather(
          selectedWeatherCity
        );

      },

      300000

    );


  return () =>
    clearInterval(
      weatherTimer
    );


}, [
  selectedWeatherCity
]);


  // =====================================================
  // MAP REPORTS
  // =====================================================

  const mappedReports =
    useMemo(
      () =>
        reports.filter(

          (report) =>

            Number.isFinite(
              Number(
                report.latitude
              )
            )

            &&

            Number.isFinite(
              Number(
                report.longitude
              )
            )

        ),

      [reports]

    );




  // =====================================================
  // FILTERED REPORTS
  // =====================================================

  const filteredReports =
    useMemo(() => {

      return reports.filter(
        (report) => {

          const location =
            `${report.city || ""}
             ${report.state || ""}`
              .toLowerCase();


          return (

            (
              filters.event ===
                "All Events"

              ||

              report.event_type ===
                filters.event
            )

            &&

            (
              !filters.location

              ||

              location.includes(
                filters.location
                  .toLowerCase()
              )
            )

            &&

            (
              filters.state ===
                "All States"

              ||

              String(report.state || "") ===
                filters.state
            )

            &&

            (
              filters.district ===
                "All Districts"

              ||

              String(
                report.district ||
                report.city ||
                ""
              ) === filters.district
            )

            &&

            (
              filters.status ===
                "All Status"

              ||

              report.verification_status ===
                filters.status
            )

            &&

            (
              filters.source ===
                "All Sources"

              ||

              report.source ===
                filters.source
            )

          );

        }
      );

    }, [

      reports,

      filters,

    ]);




  // =====================================================
  // EVENT TYPES
  // =====================================================

  const filteredMappedReports =
    useMemo(
      () =>
        filteredReports.filter(
          (report) =>
            Number.isFinite(Number(report.latitude)) &&
            Number.isFinite(Number(report.longitude))
        ),
      [filteredReports]
    );


  const states =
    useMemo(
      () =>
        [
          ...new Set(
            reports
              .map((report) => String(report.state || "").trim())
              .filter(Boolean)
          ),
        ].sort(),
      [reports]
    );

  const districts =
    useMemo(
      () =>
        [
          ...new Set(
            reports
              .filter(
                (report) =>
                  filters.state === "All States" ||
                  String(report.state || "") === filters.state
              )
              .map((report) =>
                String(
                  report.district ||
                  report.city ||
                  ""
                ).trim()
              )
              .filter(Boolean)
          ),
        ].sort(),
      [reports, filters.state]
    );

  const eventTypes =
    useMemo(

      () =>

        [
          ...new Set(

            reports
              .map(
                (report) =>
                  report.event_type
              )
              .filter(Boolean)

          ),
        ],

      [reports]

    );




  // =====================================================
  // SOURCES
  // =====================================================

  const sources =
    useMemo(

      () =>

        [
          ...new Set(

            reports
              .map(
                (report) =>
                  report.source
              )
              .filter(Boolean)

          ),
        ],

      [reports]

    );




  // =====================================================
  // EVENT DISTRIBUTION
  // =====================================================

  const eventDistribution =
    useMemo(() => {

      const counts = {};


      reports.forEach(
        (report) => {

          const event =
            report.event_type ||
            "Other";


          counts[event] =
            (
              counts[event] ||
              0
            ) + 1;

        }
      );


      return Object.entries(
        counts
      )
        .sort(
          (a, b) =>
            b[1] - a[1]
        );

    }, [reports]);




  // =====================================================
  // REFRESH
  // =====================================================

  const refresh =
    async () => {

      setLoading(true);


      await loadData();


      setLoading(false);

    };




  // =====================================================
  // SUBMIT CITIZEN REPORT
  // =====================================================

  const submitReport =
    async (e) => {

      e.preventDefault();


      if (
        description.trim().length < 8
      ) {

        setBackendError(

          "Please enter a more detailed weather report."

        );

        return;

      }


      setLoading(true);


      setSubmitResult(null);


      setBackendError("");


      try {

        const result =
          await fetchJSON(

            "/api/reports",

            {

              method: "POST",


              headers: {

                "Content-Type":
                  "application/json",

              },


              body:

                JSON.stringify({

                  description:
                    description.trim(),

                  source:

                    source,

                }),

            }

          );


        setSubmitResult(
          result
        );


        setDescription(
          ""
        );


        await loadData();


      } catch (error) {

        console.error(error);


        setBackendError(

          `Report submission failed: ${error.message}`

        );


      } finally {

        setLoading(false);

      }

    };




  // =====================================================
  // SUBMIT SOCIAL MEDIA REPORT
  // =====================================================

  const submitSocial =
    async (e) => {

      e.preventDefault();


      if (
        socialText.trim().length < 8
      ) {

        setBackendError(

          "Please enter a more detailed social media post."

        );

        return;

      }


      setLoading(true);


      setSocialResult(null);


      setBackendError("");


      try {

        const result =
          await fetchJSON(

            "/api/reports",

            {

              method:
                "POST",


              headers: {

                "Content-Type":
                  "application/json",

              },


              body:

                JSON.stringify({

                  description:
                    socialText.trim(),

                  source:
                    "Social Media",

                }),

            }

          );


        setSocialResult(
          result
        );


        setSocialText(
          ""
        );


        await loadData();


      } catch (error) {

        console.error(error);


        setBackendError(

          `Social post processing failed: ${error.message}`

        );


      } finally {

        setLoading(false);

      }

    };




  // =====================================================
  // DELETE REPORT
  // =====================================================

  const deleteReport =
    async (id) => {

      const confirmed =
        window.confirm(
          "Delete this weather report?"
        );


      if (!confirmed) {

        return;

      }


      try {

        await fetchJSON(

          `/api/reports/${id}`,

          {

            method:
              "DELETE",

            headers: {
              Authorization:
                `Bearer ${localStorage.getItem("admin_token") || ""}`,
            },

          }

        );


        setSelectedReport(
          null
        );


        await loadData();


      } catch (error) {

        console.error(error);


        setBackendError(

          "Unable to delete the report."

        );

      }

    };




  // =====================================================
  // ADMIN LOGOUT
  // =====================================================

  const handleAdminLogout = () => {

    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_role");

    setAdminReports([]);
    setIsAdmin(false);
    setActivePage("Dashboard");
  };


  // =====================================================
  // SIDEBAR
  // =====================================================

  const Sidebar = () => {


    const items = [

      [
        "Dashboard",
        "▦",
      ],

      [
        "Live Weather Map",
        "🗺️",
      ],

      [
        "Live Weather News",
        "📰",
      ],

      [
        "Reports",
        "📋",
      ],

      [
        "Submit Report",
        "➕",
      ],

      [
        "Social Intelligence",
        "📡",
      ],

      [
        "Admin Panel",
        "⚙️",
      ],

    ];


    return (

      <aside
        className="sidebar"
      >


        <div
          className="brand"
        >

          <div
            className="brand-icon"
          >
            🌦️
          </div>


          <div>

            <h1>
              ZYVORA
            </h1>


            <p>
              WEATHER INTELLIGENCE
            </p>

          </div>

        </div>



        <nav>

          {items.map(

            ([name, icon]) => (

              <button

                key={name}

                className={
                  `nav-button ${
                    activePage === name
                      ? "active"
                      : ""
                  }`
                }

                onClick={() =>
                  setActivePage(name)
                }

              >

                <span>
                  {icon}
                </span>


                {name}

              </button>

            )

          )}

        </nav>



        <div
          className="sidebar-bottom"
        >

          <div
            className="online"
          >

            <i />

            SYSTEM ONLINE

          </div>


          <p>

            National Weather Big Data
            Analytics Platform

          </p>

        </div>


      </aside>

    );

  };




  // =====================================================
  // PAGE HEADER
  // =====================================================

  const Header = ({
    eyebrow,
    title,
    description,
    action = true,
  }) => (

    <header
      className="page-header"
    >

      <div>

        {eyebrow && (

          <div
            className="eyebrow"
          >

            {eyebrow}

          </div>

        )}


        <h2>
          {title}
        </h2>


        <p>
          {description}
        </p>

      </div>



      {action && (

        <button

          className="refresh-button"

          onClick={refresh}

          disabled={loading}

        >

          {loading

            ? "Processing..."

            : "↻ Refresh Intelligence"

          }

        </button>

      )}

    </header>

  );




  // =====================================================
  // DASHBOARD
  // =====================================================

  const Dashboard = () => {


    const averageTrust =
      reports.length > 0

        ? Math.round(

            reports.reduce(

              (total, report) =>

                total +

                Number(
                  report.trust_score ||
                  0
                ),

              0

            )

            /

            reports.length

          )

        : 0;


    return (

      <section>


        <Header

          eyebrow={
            "NATIONAL WEATHER INTELLIGENCE"
          }

          title={
            "Weather Intelligence Dashboard"
          }

          description={
            "Real-time analytics and AI-powered weather intelligence across India."
          }

        />



        {backendError && (

          <div
            className="alert"
          >

            {backendError}

          </div>

        )}



        <div
          className="stats-grid"
        >

          <Stat

            icon="📋"

            label="Total Reports"

            value={
              dashboard.total_reports || 0
            }

            text="Collected nationwide"

          />


          <Stat

            icon="⚡"

            label="Active Events"

            value={
              dashboard.active_events || 0
            }

            text="Weather categories"

          />


          <Stat

            icon="✓"

            label="Verified Reports"

            value={
              dashboard.verified_reports || 0
            }

            text="Trusted intelligence"

          />


          <Stat

            icon="⚠"

            label="Under Review"

            value={
              dashboard.under_review_reports || 0
            }

            text="Awaiting verification"

          />

        </div>
          {/* =====================================================
    REAL-TIME WEATHER INTELLIGENCE
===================================================== */}

<div className="live-weather-section">

  <div className="live-weather-header">

    <div>
      <h2>🌦️ Real-Time Weather Intelligence</h2>

      <p>
        Live weather conditions powered by Open-Meteo
      </p>
    </div>


    <div className="weather-controls">

      <select
        value={selectedWeatherCity}
        onChange={(e) =>
          setSelectedWeatherCity(
            e.target.value
          )
        }
        className="weather-city-select"
      >

        {Object.keys(
          WEATHER_CITIES
        ).map((city) => (

          <option
            key={city}
            value={city}
          >

            {city}

          </option>

        ))}

      </select>


      <button
        className="weather-refresh-btn"
        onClick={() =>
          loadLiveWeather(
            selectedWeatherCity
          )
        }
      >

        🔄 Refresh

      </button>

    </div>

  </div>


  {/* ================= LOADING ================= */}

  {weatherLoading && (

    <div className="weather-status loading">

      🌦️ Fetching live weather data...

    </div>

  )}


  {/* ================= ERROR ================= */}

  {weatherError && (

    <div className="weather-status error">

      ⚠️ {weatherError}

    </div>

  )}


  {/* ================= WEATHER DATA ================= */}

  {liveWeather &&
    !weatherLoading && (

      <>

        {/* WEATHER MAIN CARD */}

        <div
          className={`weather-main-card mood-${weatherMood(
            liveWeather.current_weather
              ?.weather_description
          )}`}
        >

          <div className="weather-main-left">

            <div className="weather-city">

              📍 {selectedWeatherCity}

            </div>


            <div className="weather-temperature">

              {Math.round(
                liveWeather.current_weather
                  ?.temperature ?? 0
              )}
              °C

            </div>


            <div className="weather-condition">

              {
                liveWeather.current_weather
                  ?.weather_description
                  || "Unknown"
              }

            </div>


            <div className="weather-feels">

              Feels like{" "}

              <strong>

                {Math.round(
                  liveWeather.current_weather
                    ?.apparent_temperature ?? 0
                )}
                °C

              </strong>

            </div>

          </div>


          {/* RISK ANALYSIS */}

          <div className="weather-risk-box">

            <span className="risk-title">

              ZYVORA WEATHER RISK

            </span>


            <div
              className={`weather-risk-level ${(
                liveWeather.risk_analysis
                  ?.risk_level || "LOW"
              ).toLowerCase()}`}
            >

              {
                liveWeather.risk_analysis
                  ?.risk_level || "LOW"
              }

            </div>


            <div className="risk-reasons">

              {(
                liveWeather.risk_analysis
                  ?.reasons || []
              ).map((reason, index) => (

                <div key={index}>

                  • {reason}

                </div>

              ))}

            </div>

          </div>

        </div>


        {/* WEATHER METRICS */}

        <div className="weather-metrics-grid">


          <div className="weather-metric-card">

            <span className="metric-icon">

              💧

            </span>

            <span className="metric-label">

              Humidity

            </span>

            <strong>

              {
                liveWeather.current_weather
                  ?.humidity ?? "--"
              }%

            </strong>

          </div>


          <div className="weather-metric-card">

            <span className="metric-icon">

              🌧️

            </span>

            <span className="metric-label">

              Precipitation

            </span>

            <strong>

              {
                liveWeather.current_weather
                  ?.precipitation ?? "--"
              } mm

            </strong>

          </div>


          <div className="weather-metric-card">

            <span className="metric-icon">

              💨

            </span>

            <span className="metric-label">

              Wind Speed

            </span>

            <strong>

              {
                liveWeather.current_weather
                  ?.wind_speed ?? "--"
              } km/h

            </strong>

          </div>


          <div className="weather-metric-card">

            <span className="metric-icon">

              ☁️

            </span>

            <span className="metric-label">

              Cloud Cover

            </span>

            <strong>

              {
                liveWeather.current_weather
                  ?.cloud_cover ?? "--"
              }%

            </strong>

          </div>


          <div className="weather-metric-card">

            <span className="metric-icon">

              👁️

            </span>

            <span className="metric-label">

              Visibility

            </span>

            <strong>

              {
                liveWeather.current_weather
                  ?.visibility
                  ? `${(
                      liveWeather.current_weather
                        .visibility / 1000
                    ).toFixed(1)} km`
                  : "--"
              }

            </strong>

          </div>


          <div className="weather-metric-card">

            <span className="metric-icon">

              🧭

            </span>

            <span className="metric-label">

              Wind Direction

            </span>

            <strong>

              {
                liveWeather.current_weather
                  ?.wind_direction ?? "--"
              }°

            </strong>

          </div>

        </div>


        {/* LAST UPDATED */}

        <div className="weather-last-updated">

          🟢 Live Data

          {weatherUpdatedAt && (

            <>
              {" "}
              • Last updated{" "}

              {
                weatherUpdatedAt
                  .toLocaleTimeString()
              }

            </>

          )}

          {" "}
          • Source: Open-Meteo

        </div>


        {/* ================= HOURLY FORECAST ================= */}

        <div className="hourly-weather-section">

          <h3>

            ⏰ Next Hours Forecast

          </h3>


          <div className="hourly-weather-grid">

            {(
              liveWeather.hourly_forecast
              || []
            ).slice(0, 8)
              .map((hour, index) => (

                <div
                  className="hourly-weather-card"
                  key={index}
                >

                  <span className="hour-time">

                    {
                      hour.time
                        ? new Date(
                            hour.time
                          ).toLocaleTimeString(
                            [],
                            {
                              hour: "2-digit",
                              minute: "2-digit"
                            }
                          )
                        : "--"
                    }

                  </span>


                  <span className="hour-temp">

                    {Math.round(
                      hour.temperature ?? 0
                    )}°C

                  </span>


                  <span className="hour-condition">

                    {
                      hour.weather_description
                      || "Unknown"
                    }

                  </span>


                  <span className="hour-rain">

                    🌧️ {
                      hour.rain_probability
                      ?? 0
                    }%

                  </span>


                  <span className="hour-wind">

                    💨 {
                      hour.wind_speed
                      ?? 0
                    } km/h

                  </span>

                </div>

              ))}

          </div>

        </div>

      </>

    )}

</div>



        <div
          className="dashboard-layout"
        >


          <div
            className="panel"
          >

            <div
              className="panel-heading"
            >

              <div>

                <div
                  className="eyebrow"
                >
                  ANALYTICS
                </div>


                <h3>
                  Weather Event Distribution
                </h3>

              </div>


              <button

                className="icon-button"

                onClick={() =>
                  setActivePage(
                    "Reports"
                  )
                }

              >
                ↗
              </button>

            </div>



            {eventDistribution.length > 0

              ? eventDistribution.map(

                  ([event, count]) => (

                    <div

                      className="distribution"

                      key={event}

                    >

                      <div
                        className="distribution-top"
                      >

                        <span>

                          {
                            eventInfo(event)
                              .icon
                          }

                          {" "}

                          {event}

                        </span>


                        <b>
                          {count}
                        </b>

                      </div>


                      <div
                        className="bar"
                      >

                        <i

                          style={{

                            width:
                              `${
                                (
                                  count /
                                  reports.length
                                ) *
                                100
                              }%`,

                          }}

                        />

                      </div>

                    </div>

                  )

                )

              : (

                <Empty

                  text={
                    "No weather intelligence collected yet."
                  }

                />

              )

            }

          </div>




          <div
            className="panel intelligence-panel"
          >

            <div
              className="panel-heading"
            >

              <div>

                <div
                  className="eyebrow"
                >
                  AI ENGINE
                </div>


                <h3>
                  ZYVORA Intelligence
                </h3>

              </div>


              <span
                className="live-pill"
              >
                ● LIVE
              </span>

            </div>



            <div
              className="confidence-box"
            >

              <div
                className="confidence-ring"
              >

                <span>
                  {averageTrust}%
                </span>

              </div>


              <div>

                <h4>
                  Verification Confidence
                </h4>


                <p>

                  Average trust score
                  generated by the
                  multi-factor verification
                  engine.

                </p>

              </div>

            </div>



            <div
              className="mini-stats"
            >

              <Mini

                label="Verified"

                value={
                  dashboard.verified_reports || 0
                }

                icon="✓"

              />


              <Mini

                label="Review"

                value={
                  dashboard.under_review_reports || 0
                }

                icon="⚠"

              />


              <Mini

                label="Suspicious"

                value={
                  dashboard.suspicious_reports || 0
                }

                icon="🚨"

              />

            </div>



            <div
              className="engine-flow"
            >

              🤖 Event Detection

              →

              Location Intelligence

              →

              Trust Analysis

              →

              Duplicate Detection

            </div>

          </div>

        </div>




        <div
          className="panel"
        >

          <div
            className="panel-heading"
          >

            <div>

              <div
                className="eyebrow"
              >
                GEO-SPATIAL INTELLIGENCE
              </div>


              <h3>
                India Weather Intelligence Map
              </h3>

            </div>


            <button

              className="secondary"

              onClick={() =>
                setActivePage(
                  "Live Weather Map"
                )
              }

            >

              Open Live Map →

            </button>

          </div>


          <WeatherMap

            reports={
              mappedReports.slice(0, 20)
            }

            height={360}

          />

        </div>




        <div
          className="panel"
        >

          <div
            className="panel-heading"
          >

            <div>

              <div
                className="eyebrow"
              >
                RECENT INTELLIGENCE
              </div>


              <h3>
                Latest Weather Reports
              </h3>

            </div>


            <button

              className="secondary"

              onClick={() =>
                setActivePage(
                  "Reports"
                )
              }

            >

              View All

            </button>

          </div>



          <div
            className="recent-list"
          >

            {reports
              .slice(0, 5)
              .map(
                (report) => (

                  <ReportRow

                    key={report.id}

                    report={report}

                    onClick={() =>
                      setSelectedReport(
                        report
                      )
                    }

                  />

                )
              )}

          </div>



          {reports.length === 0 && (

            <Empty

              text={
                "Submit your first report to begin intelligence collection."
              }

            />

          )}

        </div>


      </section>

    );

  };




  // =====================================================
  // LIVE MAP
  // =====================================================

  const LiveMap = () => (

    <section>


      <Header

        eyebrow={
          "LIVE GEO-SPATIAL MONITORING"
        }

        title={
          "Live Weather Map"
        }

        description={
          "Interactive nationwide map of AI-analyzed and geo-tagged weather events."
        }

      />



      <div className="map-filter-panel panel">
        <div className="map-filter-heading">
          <div>
            <div className="eyebrow">MAP FILTERS</div>
            <h3>Filter Weather Intelligence</h3>
            <p>Select state and district to focus the live map. Multiple filters work together.</p>
          </div>
          <button
            className="secondary"
            onClick={() =>
              setFilters({
                ...filters,
                state: "All States",
                district: "All Districts",
              })
            }
          >
            Clear Location
          </button>
        </div>

        <div className="map-filter-grid">
          <label>
            <span>Event</span>
            <select
              value={filters.event}
              onChange={(e) =>
                setFilters({ ...filters, event: e.target.value })
              }
            >
              <option>All Events</option>
              {eventTypes.map((event) => (
                <option key={event}>{event}</option>
              ))}
            </select>
          </label>

          <label>
            <span>State</span>
            <select
              value={filters.state}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  state: e.target.value,
                  district: "All Districts",
                })
              }
            >
              <option>All States</option>
              {states.map((state) => (
                <option key={state}>{state}</option>
              ))}
            </select>
          </label>

          <label>
            <span>District / City</span>
            <select
              value={filters.district}
              onChange={(e) =>
                setFilters({ ...filters, district: e.target.value })
              }
            >
              <option>All Districts</option>
              {districts.map((district) => (
                <option key={district}>{district}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Status</span>
            <select
              value={filters.status}
              onChange={(e) =>
                setFilters({ ...filters, status: e.target.value })
              }
            >
              <option>All Status</option>
              <option>Verified</option>
              <option>Under Review</option>
              <option>Suspicious</option>
              <option>Duplicate</option>
            </select>
          </label>

          <label>
            <span>Source</span>
            <select
              value={filters.source}
              onChange={(e) =>
                setFilters({ ...filters, source: e.target.value })
              }
            >
              <option>All Sources</option>
              {sources.map((sourceItem) => (
                <option key={sourceItem}>{sourceItem}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Search</span>
            <input
              value={filters.location}
              placeholder="Search city or state..."
              onChange={(e) =>
                setFilters({ ...filters, location: e.target.value })
              }
            />
          </label>
        </div>

        <div className="map-filter-result">
          <strong>{filteredMappedReports.length}</strong> matching mapped report(s)
        </div>
      </div>

      <div
        className="map-summary"
      >

        <Summary

          label="Total"

          value={
            reports.length
          }

          icon="📋"

        />


        <Summary

          label="Mapped"

          value={
            filteredMappedReports.length
          }

          icon="📍"

        />


        <Summary

          label="Verified"

          value={
            dashboard.verified_reports || 0
          }

          icon="✓"

        />

      </div>



      <div
        className="panel"
      >

        <WeatherMap

          reports={
            filteredMappedReports
          }

          height={620}

        />


        {filteredMappedReports.length === 0 && (

          <Empty

            text={
              filteredReports.length === 0
                ? "No matching reports found for the selected filters."
                : "Matching reports were found, but none has valid map coordinates."
            }

          />

        )}

      </div>



      <div
        className="legend"
      >

        {Object.entries(EVENTS)
          .slice(0, 7)
          .map(
            ([name, info]) => (

              <span
                key={name}
              >

                {info.icon}

                {" "}

                {name}

              </span>

            )
          )}

      </div>


    </section>

  );




  // =====================================================
  // LIVE WEATHER NEWS
  // =====================================================

  const LiveWeatherNews = () => (

    <section>

      <Header
        eyebrow={"REAL-TIME NEWS INTELLIGENCE"}
        title={"Live Weather News"}
        description={"Live weather and disaster intelligence collected from NewsAPI and processed by ZYVORA."}
        action={false}
      />

      <div className="live-news-toolbar">

        <div className="news-live-status">
          <span className="news-live-dot" />
          LIVE NEWS DATA
        </div>

        <div className="news-toolbar-right">

          {newsUpdatedAt && (
            <span className="news-updated">
              Updated: {newsUpdatedAt.toLocaleTimeString()}
            </span>
          )}

          <button
            className="refresh-button"
            onClick={loadLiveNews}
            disabled={newsLoading}
          >
            {newsLoading ? "Loading..." : "↻ Refresh News"}
          </button>

        </div>

      </div>

      {newsError && (
        <div className="alert">
          ⚠️ {newsError}
        </div>
      )}

      {newsLoading && liveNews.length === 0 && (
        <div className="news-loading">
          <div className="news-spinner" />
          <p>Fetching real-time weather intelligence...</p>
        </div>
      )}

      {liveNews.length > 0 && (
        <div className="live-news-grid">

          {liveNews.map((news, index) => {

            const info = eventInfo(news.event_type);
            const risk = String(news.risk_level || "LOW").toLowerCase();

            return (
              <article
                className="live-news-card"
                key={news.url || `${news.title}-${index}`}
              >

                <div
                  className="news-image"
                  style={{
                    backgroundImage: `url("${weatherNewsImage(news)}")`,
                  }}
                  aria-hidden="true"
                />

                <div className="news-card-top">
                  <span className="news-event">
                    {info.icon} {news.event_type || "Weather Event"}
                  </span>

                  <span className={`risk-badge ${risk}`}>
                    ⚠️ {news.risk_level || "LOW"}
                  </span>
                </div>

                <h3>{news.title}</h3>

                <p className="news-description">
                  {news.description || "No description available."}
                </p>

                <div className="news-location">
                  📍 {news.location || "Location not detected"}
                </div>

                <div className="news-meta">
                  <span>📰 {news.source || "News Source"}</span>
                  <span>🎯 {Math.round(Number(news.confidence || 0))}%</span>
                </div>

                <div className="news-date">
                  🕒 {news.published_at
                    ? new Date(news.published_at).toLocaleString()
                    : "Recently"}
                </div>

                <div className="news-source-row">
                  <span>ZYVORA Source</span>
                  <strong>{news.data_source || "Live News"}</strong>
                </div>

                {news.url && (
                  <a
                    href={news.url}
                    target="_blank"
                    rel="noreferrer"
                    className="news-link"
                  >
                    Read Original Article →
                  </a>
                )}

              </article>
            );

          })}

        </div>
      )}

      {!newsLoading &&
        liveNews.length === 0 &&
        !newsError && (
          <div className="news-empty">
            📰
            <h3>No Live Weather News Available</h3>
            <p>Click Refresh News to fetch the latest weather intelligence.</p>
          </div>
        )}

    </section>

  );




  // =====================================================
  // REPORTS PAGE
  // =====================================================

  const Reports = () => (

    <section>


      <Header

        eyebrow={
          "INTELLIGENCE REPOSITORY"
        }

        title={
          "Weather Reports"
        }

        description={
          "Search, filter and inspect collected weather intelligence."
        }

        action={false}

      />



      <div
        className="filters"
      >


        <select

          value={
            filters.event
          }

          onChange={(e) =>

            setFilters({

              ...filters,

              event:
                e.target.value,

            })

          }

        >

          <option>
            All Events
          </option>


          {eventTypes.map(
            (event) => (

              <option
                key={event}
              >

                {event}

              </option>

            )
          )}

        </select>



        <input

          placeholder="Search city or state..."

          value={
            filters.location
          }

          onChange={(e) =>

            setFilters({

              ...filters,

              location:
                e.target.value,

            })

          }

        />



        <select

          value={
            filters.status
          }

          onChange={(e) =>

            setFilters({

              ...filters,

              status:
                e.target.value,

            })

          }

        >

          <option>
            All Status
          </option>

          <option>
            Verified
          </option>

          <option>
            Under Review
          </option>

          <option>
            Suspicious
          </option>

          <option>
            Duplicate
          </option>

        </select>



        <select

          value={
            filters.source
          }

          onChange={(e) =>

            setFilters({

              ...filters,

              source:
                e.target.value,

            })

          }

        >

          <option>
            All Sources
          </option>


          {sources.map(
            (sourceItem) => (

              <option
                key={sourceItem}
              >

                {sourceItem}

              </option>

            )
          )}

        </select>



        <button

          className="secondary"

          onClick={() =>

            setFilters({

              event:
                "All Events",

              location:
                "",

              state:
                "All States",

              district:
                "All Districts",

              status:
                "All Status",

              source:
                "All Sources",

            })

          }

        >

          Clear Filters

        </button>

      </div>



      <div
        className="report-count"
      >

        {
          filteredReports.length
        }

        {" "}

        intelligence report(s)

      </div>



      <div
        className="reports-table-wrap"
      >

        <table
          className="reports-table"
        >

          <thead>

            <tr>

              <th>ID</th>

              <th>Event</th>

              <th>Location</th>

              <th>Trust</th>

              <th>Duplicate</th>

              <th>Status</th>

              <th>Source</th>

              <th>Action</th>

            </tr>

          </thead>



          <tbody>

            {filteredReports.map(
              (report) => (

                <tr
                  key={report.id}
                >

                  <td>
                    #{report.id}
                  </td>


                  <td>

                    {
                      eventInfo(
                        report.event_type
                      ).icon
                    }

                    {" "}

                    {report.event_type}

                  </td>


                  <td>

                    📍

                    {" "}

                    {
                      report.city ||
                      "Unknown"
                    }

                    {
                      report.state
                        ? `, ${report.state}`
                        : ""
                    }

                  </td>


                  <td>

                    <b>

                      {
                        score(
                          report.trust_score
                        )
                      }

                      %

                    </b>

                  </td>


                  <td>

                    {
                      score(
                        report.duplicate_score
                      )
                    }

                    %

                  </td>


                  <td>

                    <span

                      className={
                        statusClass(
                          report.verification_status
                        )
                      }

                    >

                      {
                        report.verification_status
                      }

                    </span>

                  </td>


                  <td>

                    {
                      report.source
                    }

                  </td>


                  <td>

                    <button

                      className="table-button"

                      onClick={() =>
                        setSelectedReport(
                          report
                        )
                      }

                    >

                      View

                    </button>

                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>



        {filteredReports.length === 0 && (

          <Empty

            text={
              "No reports match the selected filters."
            }

          />

        )}

      </div>


    </section>

  );




  // =====================================================
  // CITIZEN SUBMIT REPORT
  // =====================================================

  const SubmitReport = () => (

    <section>


      <Header

        eyebrow={
          "CITIZEN WEATHER INTELLIGENCE"
        }

        title={
          "Submit Weather Report"
        }

        description={
          "Describe what happened. ZYVORA automatically detects the event, location, duplicate risk and trust level."
        }

        action={false}

      />



      <div
        className="submit-grid"
      >


        <form

          className="panel form-panel"

          onSubmit={submitReport}

        >


          <h3>
            Citizen Weather Report
          </h3>


          <p>

            One description is enough.
            City and state are extracted
            automatically when possible.

          </p>



          <label>

            Weather Event Description *

          </label>



          <textarea

            value={description}

            onChange={(e) =>
              setDescription(
                e.target.value
              )
            }

            placeholder={
              "Example: Severe flooding reported in Madurai after continuous heavy rainfall. Several roads are waterlogged and traffic is affected."
            }

            rows="6"

          />



          <label>
            Report Source
          </label>



          <select

            value={source}

            onChange={(e) =>
              setSource(
                e.target.value
              )
            }

          >

            <option>
              Citizen
            </option>

            <option>
              News Website
            </option>

            <option>
              Public Dataset
            </option>

            <option>
              Government
            </option>

            <option>
              Sensor
            </option>

          </select>



          <div
            className="processing-list"
          >

            <b>
              🤖 Automatic AI Processing
            </b>


            <span>
              ✓ Weather Event Detection
            </span>

            <span>
              ✓ City & State Detection
            </span>

            <span>
              ✓ GPS Location Mapping
            </span>

            <span>
              ✓ Duplicate Detection
            </span>

            <span>
              ✓ Multi-Factor Trust Analysis
            </span>

            <span>
              ✓ AI Content Likelihood Analysis
            </span>

            <span>
              ✓ Verification Status
            </span>

          </div>



          <button

            type="submit"

            className="primary"

            disabled={
              loading ||
              description.trim().length < 8
            }

          >

            {loading

              ? "Analyzing Intelligence..."

              : "🚀 Submit & Analyze Report"

            }

          </button>


        </form>



        <AnalysisResult

          result={submitResult}

          title={
            "Report Processed Successfully"
          }

        />


      </div>


    </section>

  );




  // =====================================================
  // SOCIAL INTELLIGENCE
  // =====================================================

  const SocialIntelligence = () => (

    <section>


      <Header

        eyebrow={
          "SOCIAL SIGNAL INGESTION"
        }

        title={
          "Social Media Intelligence"
        }

        description={
          "Paste public weather-related social signals and let ZYVORA extract the event, location, duplicate risk and trust level."
        }

        action={false}

      />



      <div
        className="submit-grid"
      >


        <form

          className="panel form-panel"

          onSubmit={submitSocial}

        >


          <h3>
            Ingest Social Signal
          </h3>


          <p>

            This SIH demo ingestion layer
            processes public social media
            text through the same AI trust
            pipeline as citizen reports.

          </p>



          <label>
            Social Media Platform
          </label>



          <select

            value={platform}

            onChange={(e) =>
              setPlatform(
                e.target.value
              )
            }

          >

            <option>
              X / Twitter
            </option>

            <option>
              Instagram
            </option>

            <option>
              Facebook
            </option>

            <option>
              YouTube Community
            </option>

            <option>
              Other Social Media
            </option>

          </select>



          <label>
            Public Weather Post *
          </label>



          <textarea

            value={socialText}

            onChange={(e) =>
              setSocialText(
                e.target.value
              )
            }

            placeholder={
              "Example: Heavy rainfall in Madurai today. Several roads near Anna Nagar are flooded and traffic is heavily affected."
            }

            rows="6"

          />



          <div
            className="social-note"
          >

            📡 Social signals are treated
            as lower-reliability raw
            intelligence and are verified
            using location, event
            consistency and duplicate
            analysis.

          </div>



          <button

            type="submit"

            className="primary"

            disabled={
              loading ||
              socialText.trim().length < 8
            }

          >

            {loading

              ? "Processing Signal..."

              : "📡 Ingest & Analyze Social Signal"

            }

          </button>


        </form>



        <AnalysisResult

          result={socialResult}

          title={
            "Social Signal Processed Successfully"
          }

        />


      </div>



      <div
        className="panel"
      >

        <div
          className="panel-heading"
        >

          <div>

            <div
              className="eyebrow"
            >
              SOCIAL INTELLIGENCE FEED
            </div>


            <h3>
              Collected Social Signals
            </h3>

          </div>

        </div>



        {reports

          .filter(
            (report) =>
              report.source ===
              "Social Media"
          )

          .map(
            (report) => (

              <ReportRow

                key={report.id}

                report={report}

                onClick={() =>
                  setSelectedReport(
                    report
                  )
                }

              />

            )
          )

        }



        {!reports.some(
          (report) =>
            report.source ===
            "Social Media"
        ) && (

          <Empty

            text={
              "No social signals have been ingested yet."
            }

          />

        )}

      </div>


    </section>

  );




  // =====================================================
  // ADMIN PANEL
  // =====================================================

  const Admin = () => (

    <section>


      <Header

        eyebrow={
          "PLATFORM OPERATIONS"
        }

        title={
          "Admin Intelligence Panel"
        }

        description={
          "Monitor verification status, suspicious reports and duplicate activity."
        }

      />



      <div
        className="stats-grid"
      >

        <Stat

          icon="✓"

          label="Verified"

          value={
            dashboard.verified_reports || 0
          }

          text="High confidence"

        />


        <Stat

          icon="⚠"

          label="Under Review"

          value={
            dashboard.under_review_reports || 0
          }

          text="Needs validation"

        />


        <Stat

          icon="🚨"

          label="Suspicious"

          value={
            dashboard.suspicious_reports || 0
          }

          text="Manual attention"

        />


        <Stat

          icon="🔁"

          label="Duplicates"

          value={
            dashboard.duplicate_reports || 0
          }

          text="AI similarity detection"

        />

      </div>



      <div
        className="panel"
      >

        <div
          className="panel-heading"
        >

          <div>

            <div
              className="eyebrow"
            >
              VERIFICATION QUEUE
            </div>


            <h3>
              Recent Intelligence
            </h3>

          </div>

        </div>



        {adminLoading ? (

          <div className="admin-loading">
            Loading protected intelligence...
          </div>

        ) : adminReports.length > 0 ? (

          adminReports.map(
            (report) => (

            <div

              className="admin-row"

              key={report.id}

            >

              <div>

                <b>

                  {
                    eventInfo(
                      report.event_type
                    ).icon
                  }

                  {" "}

                  {report.event_type}

                </b>


                <span>

                  📍

                  {" "}

                  {
                    report.city ||
                    "Unknown"
                  }

                  {" · "}

                  {
                    report.source
                  }

                  {" · "}

                  {
                    score(
                      report.trust_score
                    )
                  }

                  % trust

                </span>

              </div>



              <div
                className="admin-actions"
              >

                <span

                  className={
                    statusClass(
                      report.verification_status
                    )
                  }

                >

                  {
                    report.verification_status
                  }

                </span>



                <button

                  className="table-button"

                  onClick={() =>
                    setSelectedReport(
                      report
                    )
                  }

                >

                  Inspect

                </button>

              </div>

            </div>

            )
          )

        ) : (

          <div className="admin-loading">
            No protected reports available.
          </div>

        )}


      </div>


      <div className="admin-footer-actions">
        <span>Authenticated as Administrator</span>

        <button
          className="admin-logout-button"
          onClick={handleAdminLogout}
        >
          🔒 Logout
        </button>
      </div>


    </section>

  );




  // =====================================================
  // ADMIN PAGE PROTECTION
  // =====================================================

  if (activePage === "Admin Panel" && !isAdmin) {
    return (
      <AdminLogin
        onLogin={() => {
          setIsAdmin(true);
          setAdminReports([]);
        }}
      />
    );
  }


  // =====================================================
  // PAGE ROUTING
  // =====================================================

  // IMPORTANT: These page renderers are declared inside App(), so rendering
  // them as <Component /> creates a new component identity on each state update.
  // Calling the renderer directly keeps the textarea DOM mounted while typing.
  let page;

  switch (activePage) {
    case "Dashboard":
      page = Dashboard();
      break;

    case "Live Weather Map":
      page = LiveMap();
      break;

    case "Live Weather News":
      page = LiveWeatherNews();
      break;

    case "Reports":
      page = Reports();
      break;

    case "Submit Report":
      page = SubmitReport();
      break;

    case "Social Intelligence":
      page = SocialIntelligence();
      break;

    case "Admin Panel":
      page = Admin();
      break;

    default:
      page = Dashboard();
  }




  // =====================================================
  // APP RETURN
  // =====================================================

  return (

    <div
      className="app"
    >

      <Sidebar />


      <main
        className={`main-content ${activePage === "Dashboard" ? "dashboard-page" : ""} active-page-${activePage.toLowerCase().replace(/\s+/g, "-")} mood-${weatherMood(
          liveWeather?.current_weather
            ?.weather_description
        )}`}
      >

        {page}

      </main>



      {selectedReport && (

        <ReportModal

          report={selectedReport}

          close={() =>
            setSelectedReport(null)
          }

          deleteReport={
            deleteReport
          }

          isAdmin={
            isAdmin
          }

        />

      )}

    </div>

  );

}




// =====================================================
// STAT COMPONENT
// =====================================================

function Stat({
  icon,
  label,
  value,
  text,
}) {

  return (

    <div
      className="stat-card"
    >

      <div
        className="stat-icon"
      >

        {icon}

      </div>


      <div>

        <span>
          {label}
        </span>


        <strong>
          {value}
        </strong>


        <small>
          {text}
        </small>

      </div>

    </div>

  );

}




// =====================================================
// MINI STAT
// =====================================================

function Mini({
  label,
  value,
  icon,
}) {

  return (

    <div
      className="mini"
    >

      <span>
        {icon}
      </span>


      <b>
        {value}
      </b>


      <small>
        {label}
      </small>

    </div>

  );

}




// =====================================================
// MAP SUMMARY
// =====================================================

function Summary({
  icon,
  label,
  value,
}) {

  return (

    <div
      className="summary"
    >

      <span>
        {icon}
      </span>


      <b>
        {value}
      </b>


      <small>
        {label}
      </small>

    </div>

  );

}




// =====================================================
// EMPTY COMPONENT
// =====================================================

function Empty({
  text,
}) {

  return (

    <div
      className="empty"
    >

      ◌

      {" "}

      {text}

    </div>

  );

}




// =====================================================
// REPORT ROW
// =====================================================

function ReportRow({
  report,
  onClick,
}) {

  return (

    <button

      className="report-row"

      onClick={onClick}

    >

      <span
        className="event-avatar"
      >

        {
          eventInfo(
            report.event_type
          ).icon
        }

      </span>



      <span
        className="report-copy"
      >

        <b>
          {report.event_type}
        </b>


        <small>
          {report.description}
        </small>

      </span>



      <span
        className="report-location"
      >

        📍

        {" "}

        {
          report.city ||
          "Unknown"
        }

      </span>



      <span

        className={
          statusClass(
            report.verification_status
          )
        }

      >

        {
          report.verification_status
        }

      </span>


    </button>

  );

}




// =====================================================
// WEATHER MAP
// =====================================================

function WeatherMap({
  reports,
  height,
}) {

  return (

    <div
      className="map-shell"
    >

      <MapContainer

        center={INDIA_CENTER}

        zoom={5}

        scrollWheelZoom

        style={{
          height,
          width: "100%",
        }}

      >


        <TileLayer

          attribution={
            "© OpenStreetMap contributors"
          }

          url={
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          }

        />


        <AutoCenter
          reports={reports}
        />



        {reports.map(
          (report) => {

            const info =
              eventInfo(
                report.event_type
              );


            return (

              <CircleMarker

                key={report.id}

                center={[

                  Number(
                    report.latitude
                  ),

                  Number(
                    report.longitude
                  ),

                ]}

                radius={18}

                pathOptions={{

                  color:
                    info.color,

                  fillColor:
                    info.color,

                  fillOpacity:
                    0.8,

                }}

              >

                <Popup>

                  <div
                    className="popup"
                  >

                    <b>

                      {info.icon}

                      {" "}

                      {report.event_type}

                    </b>


                    <p>
                      {report.description}
                    </p>


                    <p>

                      📍

                      {" "}

                      {report.city}

                      ,

                      {" "}

                      {report.state}

                    </p>


                    <p>

                      🛡 Trust:

                      {" "}

                      {
                        score(
                          report.trust_score
                        )
                      }

                      %

                    </p>


                    <p>

                      🔁 Duplicate:

                      {" "}

                      {
                        score(
                          report.duplicate_score
                        )
                      }

                      %

                    </p>

                  </div>

                </Popup>

              </CircleMarker>

            );

          }
        )}


      </MapContainer>

    </div>

  );

}




// =====================================================
// AI ANALYSIS RESULT
// =====================================================

function AnalysisResult({
  result,
  title,
}) {


  const report =
    result?.report;


  const analysis =
    report?.trust_analysis;


  return (

    <div
      className="panel result-panel"
    >


      {!result ? (

        <div
          className="result-empty"
        >

          <div>
            🤖
          </div>


          <h3>
            ZYVORA AI Ready
          </h3>


          <p>

            Submit intelligence to view
            event detection, geospatial
            analysis, trust factors and
            duplicate risk.

          </p>

        </div>

      ) : (

        <>


          <div
            className="success-title"
          >

            ✓

            {" "}

            {title}

          </div>



          <p
            className="muted"
          >

            ZYVORA AI has completed the
            weather intelligence analysis.

          </p>



          <div
            className="result-event"
          >

            <span>

              {
                eventInfo(
                  report.event_type
                ).icon
              }

            </span>


            <div>

              <h3>
                {report.event_type}
              </h3>


              <p>

                📍

                {" "}

                {
                  report.city ||
                  "Unknown"
                }

                ,

                {" "}

                {
                  report.state ||
                  ""
                }

              </p>


              <p>

                🗺 GPS:

                {" "}

                {
                  report.latitude ??
                  "N/A"
                }

                ,

                {" "}

                {
                  report.longitude ??
                  "N/A"
                }

              </p>

            </div>

          </div>



          <div
            className="trust-score"
          >

            <small>
              FINAL TRUST SCORE
            </small>


            <strong>

              {
                score(
                  report.trust_score
                )
              }

              %

            </strong>


            <span

              className={
                statusClass(
                  report.verification_status
                )
              }

            >

              {
                report.verification_status
              }

            </span>

          </div>



          <div
            className="factor-grid"
          >

            <Factor

              label="Source Reliability"

              value={
                analysis?.source_reliability
              }

              icon="👤"

            />


            <Factor

              label="Location Consistency"

              value={
                analysis?.location_consistency
              }

              icon="📍"

            />


            <Factor

              label="Report Completeness"

              value={
                analysis?.report_completeness
              }

              icon="📝"

            />


            <Factor

              label="Weather Consistency"

              value={
                analysis?.weather_consistency
              }

              icon="🌦️"

            />


            <Factor

              label="Event Confidence"

              value={
                analysis?.event_confidence
              }

              icon="🎯"

            />


            <Factor

              label="Duplicate Score"

              value={
                report.duplicate_score
              }

              icon="🔁"

            />

          </div>


          {/* =====================================================
              AI CONTENT ANALYSIS
          ===================================================== */}

          <div className="ai-content-analysis">

            <div className="ai-content-header">

              <div>

                <span className="ai-content-icon">🤖</span>

                <div>
                  <h4>AI Content Analysis</h4>
                  <p>Prototype linguistic likelihood analysis</p>
                </div>

              </div>

              <span className="ai-content-badge">SUPPORTING SIGNAL</span>

            </div>

            <div className="ai-content-metrics">

              <div className="ai-content-metric">
                <small>AI CONTENT LIKELIHOOD</small>
                <strong>
                  {score(analysis?.ai_content_likelihood)}%
                </strong>
              </div>

              <div className="ai-content-metric">
                <small>HUMAN-LIKE LIKELIHOOD</small>
                <strong>
                  {score(analysis?.human_like_likelihood)}%
                </strong>
              </div>

              <div className="ai-content-metric">
                <small>DETECTION CONFIDENCE</small>
                <strong>
                  {score(analysis?.detection_confidence)}%
                </strong>
              </div>

            </div>

            <div className="ai-content-bar">
              <div
                className="ai-content-bar-fill"
                style={{
                  width: `${Math.min(100, Math.max(0, Number(analysis?.ai_content_likelihood || 0)))}%`,
                }}
              />
            </div>

            <div className="ai-content-signals">

              <b>Detection signals</b>

              {(analysis?.ai_content_signals || []).map(
                (signal, index) => (
                  <span key={index}>
                    • {signal}
                  </span>
                )
              )}

              {(!analysis?.ai_content_signals ||
                analysis.ai_content_signals.length === 0) && (
                <span>• No strong style signals detected</span>
              )}

            </div>

            <p className="ai-content-disclaimer">
              This is a prototype heuristic estimate based on writing-style signals.
              It is not proof that the text was generated by AI.
            </p>

          </div>



          <div
            className="explanation"
          >

            <h4>

              🧠 Why did ZYVORA AI
              give this result?

            </h4>



            {
              analysis?.explanation?.map(
                (item, index) => (

                  <p
                    key={index}
                  >

                    •

                    {" "}

                    {item}

                  </p>

                )
              )
            }

          </div>


        </>

      )}

    </div>

  );

}




// =====================================================
// ANALYSIS FACTOR
// =====================================================

function Factor({
  icon,
  label,
  value,
}) {

  return (

    <div
      className="factor"
    >

      <span>
        {icon}
      </span>


      <small>
        {label}
      </small>


      <b>

        {
          score(value)
        }

        %

      </b>

    </div>

  );

}




// =====================================================
// REPORT MODAL
// =====================================================

function ReportModal({
  report,
  close,
  deleteReport,
  isAdmin,
}) {

  return (

    <div

      className="modal-backdrop"

      onMouseDown={close}

    >

      <div

        className="modal"

        onMouseDown={(e) =>
          e.stopPropagation()
        }

      >


        <div
          className="modal-header"
        >

          <div>

            <h3>

              {
                eventInfo(
                  report.event_type
                ).icon
              }

              {" "}

              {report.event_type}

            </h3>

          </div>


          <button

            className="close"

            onClick={close}

          >

            ×

          </button>

        </div>



        <p
          className="modal-description"
        >

          {report.description}

        </p>



        <div
          className="modal-grid"
        >

          <div>

            <small>
              Location
            </small>


            <b>

              📍

              {" "}

              {
                report.city ||
                "Unknown"
              }

              ,

              {" "}

              {
                report.state ||
                ""
              }

            </b>

          </div>



          <div>

            <small>
              Source
            </small>


            <b>
              {report.source}
            </b>

          </div>



          <div>

            <small>
              Trust Score
            </small>


            <b>

              {
                score(
                  report.trust_score
                )
              }

              %

            </b>

          </div>



          <div>

            <small>
              Duplicate Score
            </small>


            <b>

              {
                score(
                  report.duplicate_score
                )
              }

              %

            </b>

          </div>



          <div>

            <small>
              GPS
            </small>


            <b>

              {
                report.latitude ??
                "N/A"
              }

              ,

              {" "}

              {
                report.longitude ??
                "N/A"
              }

            </b>

          </div>



          <div>

            <small>
              Status
            </small>


            <span

              className={
                statusClass(
                  report.verification_status
                )
              }

            >

              {
                report.verification_status
              }

            </span>

          </div>

        </div>



        <div
          className="modal-buttons"
        >

          {isAdmin && (

            <button

              className="danger"

              onClick={() =>
                deleteReport(
                  report.id
                )
              }

            >

              Delete Report

            </button>

          )}

        </div>


      </div>

    </div>

  );

}


export default App;