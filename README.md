# Esperfectto ☕

A dial-in assistant for the De'Longhi La Specialista Arte espresso machine. Skip the 30–40 minute micro-adjustment phase when trying new beans — get a recommended grind, dose, dose dial, and brew temperature based on bean characteristics, then refine with feedback over time.

Game-like UX: dark theme, XP system, barista ranks, daily streaks. The engine learns from your ratings, so the more shots you log, the better the recommendations get for similar beans.

## Features

- **Bean Intel input** — searchable variety dropdown (84 beans, popular → niche), brand text input with typo correction against 270+ top roasters, region/country/process selectors
- **Knowledge engine** — 128 base recipes across roast × origin × process; refines via weighted average of your top-rated past shots
- **Bean quality score** — heuristic estimate on the Coffee Review 100-point scale based on origin, variety, process, and roast
- **Feedback loop** — rate sweetness, acidity, bitterness, body, overall; engine learns
- **Progress tracking** — XP, 8 barista ranks (Rookie Barista → Crema Legend), daily streaks, history of every pull, favorite bean

## Tech Stack

- **Python 3.10+**
- **Kivy 2.3.1** + KivyMD (cross-platform UI)
- **SQLite** with WAL mode (local persistence)

## Project Structure

```
esperfectto/
├── main.py                # Entry point
├── app/
│   ├── screens/           # Home, Input, Results, Feedback, History
│   ├── widgets/           # Custom widgets (RatingRow)
│   └── utils/
│       ├── engine.py      # Recommendation + learning engine
│       ├── scoring.py     # Bean quality estimator
│       ├── bean_data.py   # Varieties, roasters, regions
│       └── database.py    # SQLite layer
├── kv/esperfectto.kv      # All UI layouts
├── assets/                # Images, fonts
├── requirements.txt
└── buildozer.spec         # Mobile build config
```

## Running locally

```bash
git clone https://github.com/<your-username>/esperfectto.git
cd esperfectto

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python main.py
```

A 390×844 desktop window opens (phone aspect). Walk through Bean Intel → Suggested Pull → Feedback to log your first shot.

## Mobile builds

```bash
# Android (requires buildozer)
pip install buildozer cython
buildozer android debug

# iOS (requires macOS + Xcode)
buildozer ios debug
```

## Development notes

- All business logic lives in `app/utils/`. The Kivy screens and KV file are a pure UI layer over those modules — they're framework-agnostic and reusable for a web port.
- `esperfectto.db` is created on first launch; it's gitignored so each user has their own history.
- The recommendation engine (`get_recommendation`) checks `get_similar_sessions` before falling back to the base matrix; once you have 3+ rated shots for a (roast, origin, process) combo, the engine starts learning.

## License

MIT
