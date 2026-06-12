from __future__ import annotations

import asyncio
from functools import wraps

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from .config import load_settings, require
from .pipeline import run_once
from .storage import get_queue, get_state, save_queue


settings = load_settings()


def restricted(fn):
    @wraps(fn)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        allowed = require(settings.telegram_allowed_chat_id, "TELEGRAM_ALLOWED_CHAT_ID")
        chat_id = str(update.effective_chat.id)
        if chat_id != allowed:
            await update.message.reply_text("Brak dostępu.")
            return
        return await fn(update, context)

    return wrapper


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "AutoKanał YT\n"
        "/status - stan\n"
        "/queue - kolejka\n"
        "/add temat | pexels query - dodaj film\n"
        "/run - wygeneruj i opublikuj teraz"
    )


@restricted
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = get_state()
    queue = get_queue()
    await update.message.reply_text(
        f"Opublikowane: {len(state.get('published', []))}\n"
        f"W kolejce: {len(queue)}\n"
        f"Ostatnia publikacja: {state.get('last_publish_date') or '-'}"
    )


@restricted
async def queue_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queue = get_queue()
    if not queue:
        await update.message.reply_text("Kolejka jest pusta.")
        return
    text = "\n".join(f"{i + 1}. {item['topic']}" for i, item in enumerate(queue[:20]))
    await update.message.reply_text(text)


@restricted
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args).strip()
    if not raw:
        await update.message.reply_text("Użycie: /add temat | pexels query")
        return
    topic, _, query = raw.partition("|")
    queue = get_queue()
    queue.append(
        {
            "topic": topic.strip(),
            "pexels_query": (query or topic).strip(),
            "style": "angażujący i konkretny",
            "duration_seconds": 180,
        }
    )
    save_queue(queue)
    await update.message.reply_text(f"Dodano do kolejki: {topic.strip()}")


@restricted
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Startuję pipeline. To może potrwać kilka minut.")
    try:
        result = await asyncio.to_thread(run_once, True)
        await update.message.reply_text(f"Gotowe: https://youtu.be/{result}")
    except Exception as exc:
        await update.message.reply_text(f"Błąd pipeline: {exc}")


def main() -> None:
    token = require(settings.telegram_bot_token, "TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("queue", queue_cmd))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("run", run))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
