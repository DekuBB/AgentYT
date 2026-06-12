from __future__ import annotations

import re
from dataclasses import dataclass

import requests

from .config import Settings, require


@dataclass
class ScriptResult:
    topic: str
    title: str
    description: str
    tags: list[str]
    script: str
    pexels_query: str


def generate_script(item: dict, settings: Settings) -> ScriptResult:
    api_key = require(settings.gemini_api_key, "GEMINI_API_KEY")
    topic = item["topic"]
    duration = int(item.get("duration_seconds", 180))
    style = item.get("style", "angażujący, edukacyjny, prosty język")

    prompt = f"""
Napisz kompletny skrypt narracyjny po polsku do filmu YouTube.
Temat: {topic}
Styl: {style}
Dlugosc: około {duration} sekund czytania.

Zasady:
- zacznij od mocnego haczyka w pierwszym zdaniu,
- pisz naturalnym językiem do lektora,
- bez markdown, bez list punktowanych w skrypcie,
- bez obietnic medycznych/finansowych i bez clickbaitowego wprowadzania w błąd,
- fakty niepewne oznacz ostrożnie.

Na końcu dodaj metadane w osobnych liniach:
TYTUL: maksymalnie 90 znakow
OPIS: 1-2 zdania SEO
TAGI: 6-10 tagow oddzielonych przecinkami
PEXELS: 2-4 angielskie slowa do wyszukiwania stock footage
""".strip()

    url = "https://generativelanguage.googleapis.com/v1beta/models/" f"{settings.gemini_model}:generateContent"
    response = requests.post(
        url,
        headers={"X-goog-api-key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return parse_response(text, topic, item.get("pexels_query", topic))


def parse_response(text: str, fallback_topic: str, fallback_query: str) -> ScriptResult:
    title = fallback_topic[:90]
    description = fallback_topic
    tags = ["ciekawostki", "wiedza", "edukacja"]
    pexels_query = fallback_query
    script_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        upper = line.upper()
        if upper.startswith(("TYTUL:", "TYTUŁ:")):
            title = re.sub(r"^TYTU[LŁ]:", "", line, flags=re.I).strip()[:90]
        elif upper.startswith("OPIS:"):
            description = line.split(":", 1)[1].strip()
        elif upper.startswith("TAGI:"):
            tags = [tag.strip() for tag in line.split(":", 1)[1].split(",") if tag.strip()]
        elif upper.startswith("PEXELS:"):
            pexels_query = line.split(":", 1)[1].strip()
        elif line:
            script_lines.append(line)

    script = "\n".join(script_lines).strip()
    if not script:
        raise RuntimeError("Gemini zwrocil pusty skrypt")

    return ScriptResult(
        topic=fallback_topic,
        title=title,
        description=description,
        tags=tags[:10],
        script=script,
        pexels_query=pexels_query,
    )
