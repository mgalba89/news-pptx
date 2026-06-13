# News to PowerPoint

Flask web app that collects news from URLs and Instagram screenshots, summarizes with Google Gemini AI, stores in SQLite, and generates .pptx presentations on demand.

Runs on Raspberry Pi 4 at `http://192.168.100.2:5001`.

## Tech Stack

- **Web framework**: Flask
- **Scraping**: requests, BeautifulSoup4
- **AI**: google-genai — Gemini 2.5 Flash (`gemini-2.5-flash`)
- **Database**: SQLite (`news.db`)
- **PowerPoint**: python-pptx
- **Env vars**: python-dotenv

## Project Structure

```
app.py            # Flask routes (/, /add_url, /add_image, /generate, /clear)
db.py             # SQLite helpers
scraper.py        # URL → text via requests + BeautifulSoup
ai.py             # Gemini API: summarize text, summarize image, structure slides
pptx_builder.py   # python-pptx deck builder
templates/
  index.html      # Single-page UI (drag & drop, paste, file picker)
.env              # GOOGLE_API_KEY (never commit)
news.db           # SQLite DB (auto-created, never commit)
uploads/          # Uploaded images (never commit)
news-pptx.service # systemd service file
```

## Environment

```
GOOGLE_API_KEY=AIza...
```

Get key at aistudio.google.com → Get API key → Create API key.

## Running

```bash
source venv/bin/activate
flask run --host=0.0.0.0 --port=5001
```

## systemd Service

The app auto-starts on boot via systemd.

```bash
sudo systemctl status news-pptx    # check status
sudo systemctl restart news-pptx   # restart after code changes
sudo journalctl -u news-pptx -f    # live logs
```

## Image Upload

The UI supports three ways to add images:
- Drag & drop onto the drop zone
- Ctrl+V / Cmd+V to paste from clipboard
- Click "browse" to use file picker

## Notes

- Port 5001 (5000 is taken by another gunicorn app)
- `news.db` and `uploads/` are gitignored — never commit them
- AI client is lazily initialized on first request
