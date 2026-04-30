"""
Bean quality scoring heuristic.

Estimates a quality score on a 100-point scale (aligned with Coffee Review / SCA)
based on bean properties the user can read off a bag label.
"""

from typing import Optional


# Origin quality tiers based on Cup of Excellence averages
ORIGIN_SCORES = {
    "ethiopia": 18, "kenya": 17, "panama": 18, "colombia": 16,
    "guatemala": 16, "costa rica": 16, "rwanda": 15, "burundi": 15,
    "el salvador": 15, "honduras": 14, "peru": 14, "bolivia": 14,
    "tanzania": 14, "yemen": 17, "jamaica": 15, "gesha village": 19,
    "brazil": 13, "mexico": 13, "nicaragua": 13, "uganda": 12,
    "papua new guinea": 12, "india": 12, "myanmar": 12,
    "vietnam": 9, "indonesia": 11, "philippines": 10,
    "ecuador": 13, "cuba": 11, "dominican republic": 11,
    "haiti": 11, "puerto rico": 13, "china": 11,
    "laos": 10, "thailand": 11, "sri lanka": 10,
    "cameroon": 10, "congo (drc)": 11, "ivory coast": 9,
    "malawi": 12, "zambia": 12, "zimbabwe": 11,
    "madagascar": 11, "togo": 9, "mozambique": 10,
    "venezuela": 13, "taiwan": 11, "nepal": 11,
    "australia": 12, "hawaii (usa)": 15,
}

# Variety quality tiers
VARIETY_SCORES = {
    "gesha": 15, "geisha": 15, "pacamara": 14, "sl28": 14,
    "pink bourbon": 14, "sidra": 14, "wush wush": 13,
    "bourbon": 13, "typica": 13, "sl34": 13, "heirloom": 13,
    "ethiopian heirloom": 13, "maragogipe": 13, "mokka": 13,
    "yellow bourbon": 13, "red bourbon": 13, "laurina": 13,
    "caturra": 12, "villa sarchi": 12, "java": 12, "tabi": 12,
    "catuai": 11, "pacas": 11, "red catuai": 11, "yellow catuai": 11,
    "maracaturra": 12, "sarchimor": 10, "mundo novo": 11,
    "castillo": 10, "colombia": 10, "catimor": 9, "obata": 10,
    "icatu": 10, "ruiru 11": 9, "batian": 10, "kent": 11,
    "s795": 10, "tekisic": 11, "robusta": 6, "liberica": 8,
    "excelsa": 8,
    # Named origins get decent scores
    "yirgacheffe": 14, "sidamo": 13, "guji": 14, "huila": 13,
    "nariño": 13, "tolima": 12, "antigua": 13, "tarrazú": 13,
    "kona": 14, "jamaica blue mountain": 15, "mandheling": 11,
    "sulawesi toraja": 11, "kenya aa": 14, "kilimanjaro": 12,
    "nyeri": 13, "harrar": 12, "limu": 12,
}

# Processing method scores
PROCESS_SCORES = {
    "washed": 10,
    "natural": 11,
    "honey": 11,
    "anaerobic": 12,
    "wet_hulled": 8,
    "other": 9,
}

# Roast level scores (for espresso context)
ROAST_SCORES = {
    "light": 9,
    "medium": 10,
    "medium_dark": 8,
    "dark": 6,
}


def estimate_bean_score(
    origin_country: str = "",
    bean_variety: str = "",
    roast_level: str = "medium",
    process_method: str = "washed",
) -> dict:
    """
    Estimate a quality score (72-96 range) based on bean properties.

    Returns dict with score, label, and source note.
    """
    score = 0.0
    factors_known = 0

    # Origin (0-20)
    country_key = origin_country.strip().lower()
    origin_pts = ORIGIN_SCORES.get(country_key, 12)
    score += origin_pts
    if country_key in ORIGIN_SCORES:
        factors_known += 1

    # Variety (0-15)
    variety_key = bean_variety.strip().lower()
    variety_pts = VARIETY_SCORES.get(variety_key, 11)
    score += variety_pts
    if variety_key in VARIETY_SCORES:
        factors_known += 1

    # Processing (0-12)
    proc_pts = PROCESS_SCORES.get(process_method.lower(), 9)
    score += proc_pts
    factors_known += 1

    # Roast (0-10)
    roast_pts = ROAST_SCORES.get(roast_level.lower(), 8)
    score += roast_pts
    factors_known += 1

    # Fixed assumptions for unknown fields
    score += 10   # altitude (neutral)
    score += 4    # single origin bonus (moderate)
    score += 3    # specialty label (moderate)
    score += 4    # price signal (moderate)
    score += 3    # roaster reputation (moderate)

    # Normalize raw (41-95) → display (72-96)
    raw_min, raw_max = 41, 95
    display_min, display_max = 72, 96
    normalized = display_min + (score - raw_min) / (raw_max - raw_min) * (display_max - display_min)
    normalized = max(display_min, min(display_max, round(normalized, 1)))

    # Quality label
    if normalized >= 93:
        label = "Excellent"
    elif normalized >= 90:
        label = "Very Good"
    elif normalized >= 86:
        label = "Good"
    elif normalized >= 80:
        label = "Above Average"
    else:
        label = "Average"

    return {
        "score": normalized,
        "label": label,
        "source": "Est. quality on Coffee Review scale (coffeereview.com)",
    }
