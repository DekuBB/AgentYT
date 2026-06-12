from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    pexels_api_key: str
    youtube_client_id: str
    youtube_client_secret: str
    youtube_refresh_token: str
    youtube_privacy_status: str
    telegram_bot_token: str
    telegram_allowed_chat_id: str
    publish_time: str
    publish_every_days: int
    timezone: str
    channel_lang: str


def load_settings() -> Settings:
    load_dotenv(ROOT / ".env")
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        pexels_api_key=os.getenv("PEXELS_API_KEY", ""),
        youtube_client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
        youtube_client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        youtube_refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN", ""),
        youtube_privacy_status=os.getenv("YOUTUBE_PRIVACY_STATUS", "private"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_allowed_chat_id=os.getenv("TELEGRAM_ALLOWED_CHAT_ID", ""),
        publish_time=os.getenv("PUBLISH_TIME", "16:00"),
        publish_every_days=int(os.getenv("PUBLISH_EVERY_DAYS", "2")),
        timezone=os.getenv("TIMEZONE", "Europe/Warsaw"),
        channel_lang=os.getenv("CHANNEL_LANG", "pl"),
    )


def require(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"Brak wymaganego sekretu/env: {name}")
    return value
