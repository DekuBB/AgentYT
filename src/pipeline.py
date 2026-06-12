from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .config import OUTPUT_DIR, load_settings
from .media_provider import download_pexels_images
from .script_generator import generate_script
from .storage import get_queue, get_state, get_topics, mark_published, save_queue, save_state
from .tts_generator import text_to_speech
from .video_creator import create_video
from .youtube_uploader import upload_video

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("yt-auto")


def due_now() -> bool:
    settings = load_settings()
    now = datetime.now(ZoneInfo(settings.timezone))
    publish_hour, publish_minute = [int(part) for part in settings.publish_time.split(":")]
    if now.hour != publish_hour or now.minute > 20:
        log.info("Poza oknem publikacji: teraz %s, cel %s", now.strftime("%H:%M"), settings.publish_time)
        return False

    state = get_state()
    last = state.get("last_publish_date")
    if not last:
        return True
    last_date = datetime.fromisoformat(last).date()
    return now.date() >= last_date + timedelta(days=settings.publish_every_days)


def pick_next_item() -> dict:
    queue = get_queue()
    if queue:
        item = queue.pop(0)
        save_queue(queue)
        return item

    topics = get_topics()
    if not topics:
        raise RuntimeError("Brak tematow w data/topics.json i brak kolejki")

    state = get_state()
    index = int(state.get("topic_index", 0))
    item = topics[index % len(topics)]
    state["topic_index"] = index + 1
    save_state(state)
    return item


def run_once(upload: bool = True) -> str:
    settings = load_settings()
    item = pick_next_item()
    run_dir = OUTPUT_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    log.info("Start pipeline: %s", item["topic"])

    meta = generate_script(item, settings)
    audio_path = text_to_speech(meta.script, run_dir / "voice.mp3")
    images = download_pexels_images(meta.pexels_query, settings, run_dir / "images")
    video_path = create_video(audio_path, images, meta.title, run_dir / "video.mp4")

    if not upload:
        log.info("Tryb bez uploadu. Wideo: %s", video_path)
        return str(video_path)

    video_id = upload_video(video_path, meta, settings)
    mark_published({"topic": meta.topic, "title": meta.title}, video_id)
    log.info("Opublikowano: https://youtu.be/%s", video_id)
    return video_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Uruchom pipeline natychmiast")
    parser.add_argument("--scheduled", action="store_true", help="Uruchom tylko gdy harmonogram jest due")
    parser.add_argument("--no-upload", action="store_true", help="Wygeneruj MP4 bez publikacji")
    args = parser.parse_args()

    if args.scheduled and not due_now():
        return 0
    if not args.once and not args.scheduled:
        parser.print_help()
        return 2

    run_once(upload=not args.no_upload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
