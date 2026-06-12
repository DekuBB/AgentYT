from __future__ import annotations

import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    client_file = Path("client_secret.json")
    if not client_file.exists():
        raise SystemExit("Umieść OAuth client JSON jako client_secret.json w katalogu projektu.")

    flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
    creds = flow.run_local_server(port=0)
    data = json.loads(client_file.read_text(encoding="utf-8"))
    installed = data.get("installed") or data.get("web") or {}

    print("\nDodaj te wartości do GitHub Secrets:\n")
    print(f"YOUTUBE_CLIENT_ID={installed.get('client_id')}")
    print(f"YOUTUBE_CLIENT_SECRET={installed.get('client_secret')}")
    print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
