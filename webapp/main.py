"""
Esperfectto — FastAPI webapp.

Reuses the existing engine/scoring/bean_data/database modules from app/utils
unchanged. The HTML/CSS layer replaces the Kivy UI, but the business logic
is identical to the desktop app.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Make the project root importable so we can reuse app/utils/*
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.utils import database  # noqa: E402
from app.utils.bean_data import (  # noqa: E402
    BEAN_VARIETIES,
    COFFEE_REGIONS,
    is_known_brand,
    suggest_brand,
    get_countries_for_region,
)
from app.utils.engine import (  # noqa: E402
    calculate_xp,
    get_barista_rank,
    get_next_rank_info,
    get_recommendation,
)
from app.utils.scoring import estimate_bean_score  # noqa: E402

# === App setup ===
app = FastAPI(title="Esperfectto", description="Espresso dial-in assistant")

WEBAPP_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=WEBAPP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=WEBAPP_DIR / "templates")

# === Constants for the form ===
ROAST_LEVELS = [
    ("light", "Light"),
    ("medium", "Medium"),
    ("medium_dark", "Medium-Dark"),
    ("dark", "Dark"),
]

REGIONS = [
    ("african", "African"),
    ("south_american", "S. American"),
    ("central_american", "C. American"),
    ("asian", "Asian"),
    ("blend", "Blend"),
    ("other", "Other"),
]

PROCESSES = [
    ("washed", "Washed"),
    ("natural", "Natural"),
    ("honey", "Honey"),
    ("anaerobic", "Anaerobic"),
    ("wet_hulled", "Wet Hulled"),
    ("other", "Other"),
]


@app.on_event("startup")
def _init_db_on_startup():
    database.init_db()


# === Routes ===

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    stats = database.get_user_stats()
    rank = get_barista_rank(stats["total_xp"])
    next_rank = get_next_rank_info(stats["total_xp"])
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "stats": stats,
            "rank": rank,
            "next_rank": next_rank,
            "progress_pct": int(next_rank["progress"] * 100),
        },
    )


@app.get("/input", response_class=HTMLResponse)
def input_form(request: Request, error: str = "", origin: str = "south_american"):
    countries = get_countries_for_region(origin)
    return templates.TemplateResponse(
        request,
        "input.html",
        {
            "error": error,
            "varieties": BEAN_VARIETIES,
            "roast_levels": ROAST_LEVELS,
            "regions": REGIONS,
            "processes": PROCESSES,
            "countries": countries,
            "selected_origin": origin,
        },
    )


@app.post("/check-brand", response_class=HTMLResponse)
def check_brand(request: Request, brand: str = Form("")):
    """HTMX endpoint — returns a tiny snippet with suggestion or 'new brand' confirm."""
    brand = brand.strip()
    if not brand:
        return HTMLResponse("")
    if is_known_brand(brand):
        return HTMLResponse(
            f'<div class="brand-status ok">✓ {brand} recognized</div>'
        )
    suggestion = suggest_brand(brand)
    if suggestion:
        return HTMLResponse(
            f'<div class="brand-status suggest">Did you mean '
            f'<button type="button" class="link" '
            f'onclick="document.getElementById(\'brand\').value=\'{suggestion}\';this.parentElement.outerHTML=\'\'">'
            f'{suggestion}</button>?</div>'
        )
    return HTMLResponse(
        '<div class="brand-status new">New brand — that\'s fine, just submit</div>'
    )


@app.post("/recommend")
def recommend(
    bean_name: str = Form(...),
    brand: str = Form(...),
    roast_level: str = Form("medium"),
    origin: str = Form("south_american"),
    country: str = Form(""),
    process_method: str = Form("washed"),
):
    bean_name = bean_name.strip()
    brand = brand.strip()

    # Validation
    if not bean_name or bean_name == "Select bean...":
        return RedirectResponse(url="/input?error=Select+a+bean+variety", status_code=303)
    if not brand:
        return RedirectResponse(url="/input?error=Enter+a+brand", status_code=303)
    if origin != "blend" and not country:
        return RedirectResponse(
            url=f"/input?error=Select+a+country&origin={origin}", status_code=303
        )

    rec = get_recommendation(
        roast_level=roast_level,
        origin=origin,
        process_method=process_method,
        bean_name=bean_name,
        brand=brand,
    )
    bean_score = estimate_bean_score(
        origin_country=country,
        bean_variety=bean_name,
        roast_level=roast_level,
        process_method=process_method,
    )
    session_id = database.save_session(
        bean_name=bean_name,
        brand=brand,
        roast_level=roast_level,
        origin=origin,
        process_method=process_method,
        rec_grind=rec["grind"],
        rec_dose_grams=rec["dose_grams"],
        rec_dose_dial=rec["dose_dial"],
        rec_temp=rec["temp"],
        rec_explanation=rec["explanation"],
    )
    return RedirectResponse(
        url=f"/results/{session_id}?score={bean_score['score']}"
        f"&label={bean_score['label']}",
        status_code=303,
    )


@app.get("/results/{session_id}", response_class=HTMLResponse)
def results(
    request: Request,
    session_id: int,
    score: float = 0.0,
    label: str = "",
):
    sessions = database.get_all_sessions(limit=200)
    session = next((s for s in sessions if s["id"] == session_id), None)
    if not session:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "session": session,
            "bean_label": f"{session['brand']} {session['bean_name']}".strip(),
            "score": score,
            "score_label": label,
        },
    )


@app.get("/feedback/{session_id}", response_class=HTMLResponse)
def feedback_form(request: Request, session_id: int):
    sessions = database.get_all_sessions(limit=200)
    session = next((s for s in sessions if s["id"] == session_id), None)
    if not session:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request,
        "feedback.html",
        {
            "session": session,
            "bean_label": f"{session['brand']} {session['bean_name']}".strip(),
        },
    )


@app.post("/feedback/{session_id}")
def submit_feedback(
    session_id: int,
    sweetness: int = Form(3),
    acidity: int = Form(3),
    bitterness: int = Form(3),
    body: int = Form(3),
    overall: int = Form(3),
    notes: str = Form(""),
):
    database.save_feedback(
        session_id=session_id,
        sweetness=sweetness,
        acidity=acidity,
        bitterness=bitterness,
        body=body,
        overall=overall,
        notes=notes,
    )
    xp = calculate_xp(overall)
    database.update_stats_after_session(xp)
    return RedirectResponse(url=f"/?xp_earned={xp}", status_code=303)


@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    sessions = database.get_all_sessions(limit=100)
    favorite = database.get_favorite_bean()
    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "sessions": sessions,
            "favorite": favorite,
        },
    )


# Health check for Render
@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("webapp.main:app", host="0.0.0.0", port=port, reload=False)
