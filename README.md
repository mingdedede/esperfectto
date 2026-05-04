# Esperfectto ☕

A dial-in assistant for the De'Longhi La Specialista Arte espresso machine. Skip the 30–40 minute micro-adjustment phase when trying new beans — get a recommended grind, dose, dose dial, and brew temperature based on bean characteristics, then refine with feedback over time.

Game-like UX: dark theme, XP system, barista ranks, daily streaks. The engine learns from your ratings, so the more shots you log, the better the recommendations get for similar beans.

**Two ways to run it:**
- **Desktop / mobile** — Kivy app (`python main.py`)
- **Webapp** — FastAPI + HTML, free deploy on Render (`uvicorn webapp.main:app`)

Both share the same engine, scoring, bean data, and SQLite database modules.

## Features

- **Bean Intel input** — searchable variety dropdown (84 beans, popular → niche), brand text input with typo correction against 270+ top roasters, region/country/process selectors
- **Knowledge engine** — 128 base recipes across roast × origin × process; refines via weighted average of your top-rated past shots
- **Bean quality score** — heuristic estimate on the Coffee Review 100-point scale based on origin, variety, process, and roast
- **Feedback loop** — rate sweetness, acidity, bitterness, body, overall; engine learns
- **Progress tracking** — XP, 8 barista ranks (Rookie Barista → Crema Legend), daily streaks, history of every pull, favorite bean

## Project Structure

```
esperfectto/
├── main.py                   # Kivy desktop entry point
├── webapp/                   # FastAPI webapp
│   ├── main.py               # Routes
│   ├── templates/            # Jinja2 (home, input, results, feedback, history)
│   └── static/style.css      # Dark/gold theme
├── app/                      # Shared business logic
│   ├── screens/              # Kivy screens
│   ├── widgets/              # Custom Kivy widgets
│   └── utils/
│       ├── engine.py         # Recommendation + learning engine
│       ├── scoring.py        # Bean quality estimator
│       ├── bean_data.py      # Varieties, roasters, regions
│       └── database.py       # SQLite layer
├── kv/esperfectto.kv         # Kivy UI layout
├── requirements.txt          # Webapp deps (Render uses this)
├── requirements-desktop.txt  # Kivy deps
├── render.yaml               # Render blueprint
└── Procfile                  # Heroku-compatible
```

## Run the webapp locally

```bash
git clone https://github.com/mingdedede/esperfectto.git
cd esperfectto

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

uvicorn webapp.main:app --reload
# open http://127.0.0.1:8000
```

## Deploy the webapp free on Render

1. Push the repo to GitHub (already done if you're reading this).
2. Sign in to https://render.com (free with GitHub).
3. **New → Blueprint** → connect this repo. Render reads `render.yaml` and wires everything up.
   *Or:* **New → Web Service** → connect repo → Render auto-detects from `Procfile` and `requirements.txt`.
4. Click **Deploy**. First build takes ~2 minutes. You'll get a public URL like `https://esperfectto.onrender.com`.

> Free tier note: the service sleeps after 15 minutes idle and takes ~30s to wake on the next request. Fine for sharing; upgrade to Starter ($7/mo) for always-on.

## Run the desktop / mobile app

```bash
pip install -r requirements-desktop.txt
python main.py
```

A 390×844 desktop window opens (phone aspect). For Android/iOS:

```bash
pip install buildozer cython
buildozer android debug   # or:  buildozer ios debug
```

## Development notes

- All business logic lives in `app/utils/`. The Kivy and FastAPI layers are pure UI over those modules.
- `esperfectto.db` is created on first launch; gitignored so each deploy / clone has its own history.
- Webapp uses [HTMX](https://htmx.org) for the brand-typo-check live feedback (one tag, no JS bundle).
- The recommendation engine (`get_recommendation`) checks `get_similar_sessions` before falling back to the base matrix; once you have 3+ rated shots for a (roast, origin, process) combo, the engine starts learning.

## License

MIT
