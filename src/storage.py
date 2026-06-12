from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .config import DATA_DIR


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    tmp.replace(path)


def get_queue() -> list[dict[str, Any]]:
    return read_json(DATA_DIR / "queue.json", [])


def save_queue(queue: list[dict[str, Any]]) -> None:
    write_json(DATA_DIR / "queue.json", queue)


def get_topics() -> list[dict[str, Any]]:
    return read_json(DATA_DIR / "topics.json", [])


def save_topics(topics: list[dict[str, Any]]) -> None:
    write_json(DATA_DIR / "topics.json", topics)


def get_state() -> dict[str, Any]:
    return read_json(
        DATA_DIR / "state.json",
        {"published": [], "last_publish_date": None, "topic_index": 0},
    )


def save_state(state: dict[str, Any]) -> None:
    write_json(DATA_DIR / "state.json", state)


def mark_published(item: dict[str, Any], video_id: str) -> None:
    state = get_state()
    state.setdefault("published", []).append(
        {
            "date": date.today().isoformat(),
            "topic": item["topic"],
            "title": item.get("title"),
            "video_id": video_id,
            "url": f"https://youtu.be/{video_id}",
        }
    )
    state["last_publish_date"] = date.today().isoformat()
    save_state(state)
