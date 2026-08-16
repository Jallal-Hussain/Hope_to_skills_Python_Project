import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import LogoutButton from "./LogoutButton";
import ThemeToggle from "./ThemeToggle";
import { BASE_URL } from "../api/var";

const Header = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuthState = async () => {
    try {
      const response = await fetch(`${BASE_URL}/auth/session`, {
        method: "GET",
        credentials: "include",
      });
      setIsAuthenticated(response.ok);
    } catch {
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    checkAuthState();

    const handleAuthChange = () => {
      checkAuthState();
    };

    window.addEventListener("authStateChanged", handleAuthChange);

    return () => {
      window.removeEventListener("authStateChanged", handleAuthChange);
    };
  }, []);

  return (
    <>
      {/* Enhanced Header */}
      <header className="sticky top-0 z-50 backdrop-blur-sm flex items-center justify-between px-4 py-2">
        <Link to="/" className="hover:opacity-90 transition-opacity">
          <img
            src="/avatar.png"
            alt="avatar"
            className="w-12 h-12 lg:w-16 lg:h-16 border-2 ml-5 lg:ml-10 border-secondary rounded-full object-cover"
          />
        </Link>
        <nav className="flex gap-1 md:gap-4 lg:gap-6 items-center">
          {!isAuthenticated && (
            <>
              <Link
                to="/auth/register"
                className="font-medium lg:font-lg hover:text-primary transition-colors px-2 md:px-4 py-1"
              >
                Register
              </Link>
              <Link
                to="/auth/login"
                className="font-medium lg:font-lg hover:text-primary transition-colors px-2 md:px-4 py-1"
              >
                Login
              </Link>
            </>
          )}
          {isAuthenticated && <LogoutButton onLogout={checkAuthState} />}
          <div className="ml-2">
            <ThemeToggle />
          </div>
        </nav>
      </header>
    </>
  );
};

export default Header;
