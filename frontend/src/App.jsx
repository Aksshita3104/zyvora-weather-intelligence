import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const INDIA_CENTER = [22.5937, 78.9629];

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

    if (reports.length > 0) {

      const latest = reports[0];

      map.flyTo(
        [
          Number(latest.latitude),
          Number(latest.longitude),
        ],
        reports.length === 1 ? 7 : 5,
        {
          duration: 1,
        }
      );

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




// =====================================================
// MAIN APP
// =====================================================

function App() {


  // =====================================================
  // APP STATE
  // =====================================================

  const [activePage, setActivePage] =
    useState("Dashboard");


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
  // FILTER STATE
  // =====================================================

  const [filters, setFilters] =
    useState({

      event: "All Events",

      location: "",

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
            mappedReports.length
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
            mappedReports
          }

          height={620}

        />


        {mappedReports.length === 0 && (

          <Empty

            text={
              "Reports need a recognized location before they can appear on the map."
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



        {reports.map(
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
        )}


      </div>


    </section>

  );




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
        className="main-content"
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

          openMap={() => {

            setSelectedReport(null);

            setActivePage(
              "Live Weather Map"
            );

          }}

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

                radius={11}

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
  openMap,
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

            <div
              className="eyebrow"
            >

              WEATHER INTELLIGENCE REPORT

            </div>


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

          <button

            className="secondary"

            onClick={openMap}

          >

            🗺 View Map

          </button>



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

        </div>


      </div>

    </div>

  );

}


export default App;