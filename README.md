# AutoKanał YouTube

MVP automatycznego kanału YouTube sterowanego przez:

- GitHub Actions jako scheduler i runner w chmurze,
- statyczny dashboard HTML w `dashboard/index.html`,
- Telegram bot do kolejkowania tematów i ręcznego uruchamiania,
- Python pipeline: Gemini -> Edge TTS -> Pexels -> MoviePy/FFmpeg -> YouTube API.

## Architektura

```text
dashboard/index.html -> data/queue.json
Telegram bot         -> data/queue.json
GitHub Actions cron  -> python -m src.pipeline --scheduled
Pipeline             -> Gemini -> TTS -> obrazy -> MP4 -> YouTube
```

Dashboard nie wymaga serwera. To panel pomocniczy do przygotowania kolejki i konfiguracji. Prawdziwe generowanie robi Python uruchamiany lokalnie albo w GitHub Actions.

## Szybki start lokalny

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Uzupełnij `.env`, potem zrób test bez publikacji:

```powershell
python -m src.pipeline --once --no-upload
```

## GitHub Actions

Workflow jest w `.github/workflows/publish.yml`.

Scheduler startuje co godzinę, a Python sprawdza, czy jest właściwe okno publikacji według `TIMEZONE=Europe/Warsaw` i `PUBLISH_TIME=16:00`. To omija problem statycznego UTC w cronach GitHub Actions podczas zmiany czasu lato/zima.

Dodaj w GitHub -> Settings -> Secrets and variables -> Actions:

Secrets:

- `GEMINI_API_KEY`
- `PEXELS_API_KEY`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`
- opcjonalnie `TELEGRAM_BOT_TOKEN`
- opcjonalnie `TELEGRAM_ALLOWED_CHAT_ID`

Variables:

- `PUBLISH_TIME` = `16:00`
- `PUBLISH_EVERY_DAYS` = `2`
- `TIMEZONE` = `Europe/Warsaw`
- `YOUTUBE_PRIVACY_STATUS` = `private` na start, później `public`
- opcjonalnie `GEMINI_MODEL` = `gemini-1.5-flash`

## YouTube OAuth refresh token

1. Wejdź w Google Cloud Console.
2. Włącz YouTube Data API v3.
3. Utwórz OAuth Client ID typu Desktop App.
4. Pobierz JSON i zapisz w katalogu projektu jako `client_secret.json`.
5. Uruchom:

```powershell
python scripts/create_youtube_token.py
```

Skrypt wypisze wartości do GitHub Secrets.

## Telegram bot

Lokalnie:

```powershell
python -m src.telegram_bot
```

Komendy:

- `/status` - stan publikacji i kolejki
- `/queue` - lista tematów
- `/add temat | pexels query` - dodaje temat do kolejki
- `/run` - uruchamia pipeline natychmiast

Uwaga: polling Telegram bota jako proces 24/7 nie jest dobrym zastosowaniem GitHub Actions. Do stałego bota użyj VPS, Render, Fly.io, Railway albo webhooka serverless. GitHub Actions zostaw jako scheduler publikacji.

## Dashboard

Otwórz plik:

```text
dashboard/index.html
```

Panel pozwala przygotować `queue.json` i `.env.example`. Po pobraniu `queue.json` wrzuć go do `data/queue.json` w repo.

## Bezpieczeństwo

- Nie commituj `.env`, `client_secret.json`, tokenów ani sekretów.
- Na początku publikuj jako `private`, dopiero po weryfikacji zmień na `public`.
- Sprawdzaj limity YouTube Data API i prawa do materiałów stockowych.
- Pexels/AI/TTS mogą mieć własne regulaminy komercyjnego użycia, więc zweryfikuj je przed monetyzacją.

## Możliwe rozszerzenia

- webhook Telegram zamiast pollingu,
- panel z GitHub API do odpalania `workflow_dispatch`,
- automatyczne miniatury,
- walidacja faktów przez drugi model,
- generowanie Shorts 9:16,
- baza Supabase zamiast JSON,
- separacja etapów pipeline na artefakty GitHub Actions.
