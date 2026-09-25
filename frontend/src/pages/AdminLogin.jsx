import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function AdminLogin({ onLogin }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("Admin@123");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!username.trim() || !password) {
      setError("Please enter your administrator username and password.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          password,
        }),
      });

      let data = {};
      try {
        data = await response.json();
      } catch {
        data = {};
      }

      if (!response.ok) {
        const detail =
          data?.detail ||
          data?.message ||
          "Invalid administrator credentials.";
        throw new Error(detail);
      }

      const token =
        data?.access_token ||
        data?.token ||
        data?.accessToken;

      if (!token) {
        throw new Error("Login succeeded, but no access token was returned by the server.");
      }

      localStorage.setItem("admin_token", token);
      localStorage.setItem("admin_role", data?.role || "admin");

      if (typeof onLogin === "function") {
        onLogin();
      }
    } catch (err) {
      console.error("Admin login error:", err);
      setError(
        err?.message ||
          "Unable to connect to the authentication server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="admin-login-page">
      <div className="admin-scene-globe" aria-hidden="true" />

      <div className="admin-scene-chip admin-scene-chip--left-top" aria-hidden="true">
        <span className="admin-scene-chip__icon">☁️</span>
        <div className="admin-scene-chip__text">
          <strong>Heavy Rain</strong>
          <small>Chennai</small>
        </div>
      </div>

      <div className="admin-scene-chip admin-scene-chip--left-bottom" aria-hidden="true">
        <span className="admin-scene-chip__icon">💨</span>
        <div className="admin-scene-chip__text">
          <strong>Strong Wind</strong>
          <small>Mumbai</small>
        </div>
      </div>

      <div className="admin-scene-chip admin-scene-chip--right-top" aria-hidden="true">
        <span className="admin-scene-chip__icon">⛈️</span>
        <div className="admin-scene-chip__text">
          <strong>Cyclone Alert</strong>
          <small>Bay of Bengal</small>
        </div>
      </div>

      <div className="admin-scene-chip admin-scene-chip--right-middle" aria-hidden="true">
        <span className="admin-scene-chip__icon">☁️</span>
        <div className="admin-scene-chip__text">
          <strong>Cloudy</strong>
          <small>Bengaluru</small>
        </div>
      </div>

      <div className="admin-scene-sidecopy" aria-hidden="true">
        <span>REAL-TIME</span>
        <span>WEATHER INTELLIGENCE</span>
        <span>FOR A SAFER TOMORROW</span>
        <i />
      </div>

      <section className="admin-login-card" aria-label="ZYVORA administrator login">
        <div className="admin-login-icon" aria-hidden="true">
          <svg viewBox="0 0 64 64" className="admin-weather-logo" aria-hidden="true">
            <circle cx="43" cy="20" r="11" fill="#FFD447" />
            <path
              d="M43 48H20.5C13.6 48 8 42.6 8 36s5.6-12 12.5-12c1.1 0 2.2.1 3.2.4C26 17.8 31.5 13.5 38 13.5c8.1 0 14.7 6.2 15.2 14.2C59.4 28.6 64 33.1 64 38.8 64 44 59.8 48 54.6 48H43Z"
              fill="#FFFFFF"
            />
          </svg>
        </div>

        <div className="admin-login-brand">ZYVORA</div>

        <h1>Admin Login</h1>
        <p>Weather Intelligence Administration</p>

        <form onSubmit={handleSubmit} noValidate>
          <div className="admin-input-group">
            <label htmlFor="admin-username">Username</label>
            <div className="admin-field-shell">
              <span className="admin-field-icon" aria-hidden="true">
                👤
              </span>
              <input
                id="admin-username"
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Enter admin username"
                autoComplete="username"
                autoFocus
                disabled={loading}
              />
            </div>
          </div>

          <div className="admin-input-group admin-password-group">
            <label htmlFor="admin-password">Password</label>
            <div className="admin-password-wrap admin-field-shell">
              <span className="admin-field-icon" aria-hidden="true">
                🔒
              </span>
              <input
                id="admin-password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter admin password"
                autoComplete="current-password"
                disabled={loading}
              />
              <button
                type="button"
                className="admin-password-toggle"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                disabled={loading}
              >
                {showPassword ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          {error && (
            <div className="admin-login-error" role="alert">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading}>
            <span>{loading ? "Signing In..." : "Sign In"}</span>
            {!loading && <span className="admin-sign-arrow">→</span>}
          </button>
        </form>

        <div className="admin-login-security">
          <span aria-hidden="true">🛡️</span>
          <span>Secure Access for Authorized Administrators</span>
        </div>
      </section>
    </main>
  );
}
