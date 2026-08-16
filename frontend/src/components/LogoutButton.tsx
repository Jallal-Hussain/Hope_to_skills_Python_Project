import { useNavigate } from "react-router-dom";
import { BASE_URL } from "../api/var";

type LogoutButtonProps = {
  onLogout?: () => void; // Optional callback to notify parent components
};

export default function LogoutButton({ onLogout }: LogoutButtonProps) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await fetch(`${BASE_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // Ignore network error and continue with local UX cleanup.
    }

    window.dispatchEvent(new CustomEvent("authStateChanged"));

    if (onLogout) {
      onLogout();
    }

    navigate("/auth/login");
  };

  return (
    <button
      onClick={handleLogout}
      className="font-medium lg:font-lg hover:text-primary transition-colors px-2 md:px-4 py-1 cursor-pointer"
    >
      Logout
    </button>
  );
}
