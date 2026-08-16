import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import api from "../api/axios";
import { BASE_URL } from "../api/var";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const location = useLocation();

  const expired = new URLSearchParams(location.search).get("expired");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.post(`${BASE_URL}/auth/login`, {
        username,
        password,
      });

      window.dispatchEvent(new CustomEvent("authStateChanged"));

      navigate("/admin/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full absolute top-1/4 flex justify-center items-center p-4">
      <div className="w-full max-w-sm text-background bg-foreground dark:text-foreground dark:bg-background rounded-xl shadow-lg shadow-primary/30 p-8">
        <h2 className="text-2xl font-medium mb-6 text-center">Login</h2>
        {expired && (
          <div className="text-red-500 dark:text-red-700 text-sm text-center mb-4">
            Session expired, please log in again.
          </div>
        )}
        <form onSubmit={handleLogin} className="flex flex-col gap-5">
          <div>
            <input
              className="w-full p-3 rounded-lg border border-foreground bg-background text-foreground placeholder:text-muted-secondary/70 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              type="text"
              id="username"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <input
              className="w-full p-3 rounded-lg border border-foreground bg-background text-foreground placeholder:text-muted-secondary/70 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              type="password"
              id="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            className="w-full bg-primary hover:bg-primary/90 text-white rounded-lg py-3 px-4 font-medium cursor-pointer transition-colors disabled:bg-secondary/40"
            type="submit"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
          {error && (
            <div className="text-red-500 dark:text-red-700 text-sm text-center mt-2">
              {error}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
