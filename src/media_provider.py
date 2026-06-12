from __future__ import annotations

from pathlib import Path

import requests

from .config import Settings, require


def download_pexels_images(query: str, settings: Settings, output_dir: Path, count: int = 8) -> list[Path]:
    api_key = require(settings.pexels_api_key, "PEXELS_API_KEY")
    output_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": api_key},
        params={"query": query, "per_page": count, "orientation": "landscape"},
        timeout=45,
    )
    response.raise_for_status()
    photos = response.json().get("photos", [])
    if not photos:
        raise RuntimeError(f"Pexels nie zwrocil zdjec dla query: {query}")

    paths: list[Path] = []
    for index, photo in enumerate(photos[:count], start=1):
        url = photo["src"].get("large2x") or photo["src"]["large"]
        img = requests.get(url, timeout=45)
        img.raise_for_status()
        path = output_dir / f"pexels_{index}.jpg"
        path.write_bytes(img.content)
        paths.append(path)
    return paths
