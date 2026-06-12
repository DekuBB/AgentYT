from __future__ import annotations

from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import Settings, require
from .script_generator import ScriptResult

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _credentials(settings: Settings) -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=require(settings.youtube_refresh_token, "YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=require(settings.youtube_client_id, "YOUTUBE_CLIENT_ID"),
        client_secret=require(settings.youtube_client_secret, "YOUTUBE_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def upload_video(video_path: Path, meta: ScriptResult, settings: Settings) -> str:
    youtube = build("youtube", "v3", credentials=_credentials(settings))
    body = {
        "snippet": {
            "title": meta.title[:100],
            "description": meta.description,
            "tags": meta.tags,
            "categoryId": "27",
            "defaultLanguage": settings.channel_lang,
        },
        "status": {
            "privacyStatus": settings.youtube_privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=-1)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]
