import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []))
DATABASE_URL = os.getenv("DATABASE_URL", "")  # PostgreSQL di Railway
SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///gaynonimous.db")  # Local fallback
USE_POSTGRES = bool(DATABASE_URL)
MEDIA_APPROVAL_TIMEOUT = int(os.getenv("MEDIA_APPROVAL_TIMEOUT", "60"))  # detik
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
