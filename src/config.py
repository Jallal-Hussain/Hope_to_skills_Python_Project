import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_list(value: str | None, default: List[str]) -> List[str]:
    if value is None or not value.strip():
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
DEBUG = _as_bool(os.getenv("DEBUG"), default=False)
FRONTEND_ORIGINS = _normalize_list(
    os.getenv("FRONTEND_ORIGINS"),
    ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:4173", "http://127.0.0.1:4173"],
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is required. Set it in your environment or .env before starting the application."
    )

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is required. Set it in your environment or .env before starting the application."
    )

DATABASE_URL = os.getenv("MYSQL_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    if APP_ENV == "production":
        raise RuntimeError(
            "MYSQL_DATABASE_URL or DATABASE_URL is required in production. Configure a secure database URL before startup."
        )
    DATABASE_URL = "sqlite:///./app.db"

if DATABASE_URL.startswith("mysql") and APP_ENV == "production" and "ssl" not in DATABASE_URL.lower():
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{separator}ssl_disabled=false"

if DATABASE_URL.startswith("postgres") and APP_ENV == "production" and "sslmode" not in DATABASE_URL.lower():
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))
