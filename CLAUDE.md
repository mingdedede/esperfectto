# Esperfectto

An espresso dial-in assistant app built with Python and Kivy/KivyMD.

## Tech Stack

- **Language:** Python
- **Framework:** Kivy + KivyMD
- **Database:** SQLite (local)
- **Platform:** iOS / Android

## Project Structure

```
├── main.py           # Application entry point
├── app/
│   ├── screens/      # Kivy screen classes
│   ├── widgets/      # Custom Kivy widgets
│   └── utils/        # Knowledge engine, DB, helpers
├── assets/
│   ├── fonts/        # Custom fonts
│   └── images/       # Icons and images
├── kv/               # Kivy language (.kv) files
├── tasks/            # Todo and lessons tracking
├── tests/            # Test files
└── requirements.txt
```

## Running

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Code Style

- PEP 8 conventions
- Type hints where appropriate
- Modular widgets, business logic separate from UI
