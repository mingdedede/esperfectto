"""
Knowledge engine for espresso dial-in recommendations.

Maps bean properties (roast, origin, process) to optimal La Specialista Arte settings.
Learns from user feedback history to refine recommendations over time.
"""

from typing import Optional
from app.utils.database import get_similar_sessions


# === Base Recommendation Matrix ===
# Key: (roast_level, origin, process_method)
# Value: (grind, dose_grams, dose_dial, temp_celsius)

BASE_SETTINGS = {
    # Light roasts — finer grind, higher temp
    ("light", "african", "washed"):    (2, 18.0, 25, 96),
    ("light", "african", "natural"):   (3, 18.0, 25, 96),
    ("light", "african", "honey"):     (2, 18.0, 25, 96),
    ("light", "south_american", "washed"):  (2, 18.0, 25, 96),
    ("light", "south_american", "natural"): (3, 18.0, 25, 96),
    ("light", "south_american", "honey"):   (3, 18.0, 25, 96),
    ("light", "asian", "washed"):      (2, 18.5, 26, 96),
    ("light", "asian", "natural"):     (3, 18.5, 26, 96),
    ("light", "asian", "honey"):       (3, 18.5, 26, 96),
    ("light", "central_american", "washed"):  (2, 18.0, 25, 96),
    ("light", "central_american", "natural"): (3, 18.0, 25, 96),
    ("light", "central_american", "honey"):   (2, 18.0, 25, 96),
    ("light", "central_american", "anaerobic"): (2, 18.0, 25, 96),
    ("light", "central_american", "wet_hulled"): (3, 18.0, 25, 96),
    ("light", "blend", "washed"):      (2, 18.0, 25, 96),
    ("light", "blend", "natural"):     (3, 18.0, 25, 96),
    ("light", "blend", "honey"):       (3, 18.0, 25, 96),
    # Anaerobic — fermentation intensifies flavors, treat like natural but slightly finer
    ("light", "african", "anaerobic"):    (2, 18.0, 25, 96),
    ("light", "south_american", "anaerobic"): (2, 18.0, 25, 96),
    ("light", "asian", "anaerobic"):      (2, 18.5, 26, 96),
    ("light", "blend", "anaerobic"):      (2, 18.0, 25, 96),
    # Wet hulled — earthy Indonesian method, needs finer grind for light roasts
    ("light", "african", "wet_hulled"):    (2, 18.0, 25, 96),
    ("light", "south_american", "wet_hulled"): (2, 18.0, 25, 96),
    ("light", "asian", "wet_hulled"):      (3, 18.5, 26, 96),
    ("light", "blend", "wet_hulled"):      (3, 18.0, 25, 96),

    # Medium roasts — balanced
    ("medium", "african", "washed"):    (4, 18.0, 25, 94),
    ("medium", "african", "natural"):   (4, 18.0, 25, 94),
    ("medium", "african", "honey"):     (4, 18.0, 25, 94),
    ("medium", "south_american", "washed"):  (4, 18.0, 25, 94),
    ("medium", "south_american", "natural"): (5, 18.0, 25, 94),
    ("medium", "south_american", "honey"):   (4, 18.0, 25, 94),
    ("medium", "asian", "washed"):      (4, 18.0, 25, 94),
    ("medium", "asian", "natural"):     (5, 18.0, 25, 94),
    ("medium", "asian", "honey"):       (4, 18.0, 25, 94),
    ("medium", "central_american", "washed"):  (4, 18.0, 25, 94),
    ("medium", "central_american", "natural"): (4, 18.0, 25, 94),
    ("medium", "central_american", "honey"):   (4, 18.0, 25, 94),
    ("medium", "central_american", "anaerobic"): (3, 18.0, 25, 94),
    ("medium", "central_american", "wet_hulled"): (4, 18.0, 25, 94),
    ("medium", "blend", "washed"):      (4, 18.0, 25, 94),
    ("medium", "blend", "natural"):     (5, 18.0, 25, 94),
    ("medium", "blend", "honey"):       (4, 18.0, 25, 94),
    ("medium", "african", "anaerobic"):    (3, 18.0, 25, 94),
    ("medium", "south_american", "anaerobic"): (4, 18.0, 25, 94),
    ("medium", "asian", "anaerobic"):      (4, 18.0, 25, 94),
    ("medium", "blend", "anaerobic"):      (4, 18.0, 25, 94),
    ("medium", "african", "wet_hulled"):    (4, 18.0, 25, 94),
    ("medium", "south_american", "wet_hulled"): (4, 18.0, 25, 94),
    ("medium", "asian", "wet_hulled"):      (5, 18.0, 25, 94),
    ("medium", "blend", "wet_hulled"):      (4, 18.0, 25, 94),

    # Medium-dark — transition zone
    ("medium_dark", "african", "washed"):    (5, 18.0, 25, 94),
    ("medium_dark", "african", "natural"):   (5, 18.0, 25, 92),
    ("medium_dark", "african", "honey"):     (5, 18.0, 25, 94),
    ("medium_dark", "south_american", "washed"):  (5, 18.0, 25, 94),
    ("medium_dark", "south_american", "natural"): (5, 18.0, 25, 92),
    ("medium_dark", "south_american", "honey"):   (5, 18.0, 25, 94),
    ("medium_dark", "asian", "washed"):      (5, 17.5, 24, 92),
    ("medium_dark", "asian", "natural"):     (6, 17.5, 24, 92),
    ("medium_dark", "asian", "honey"):       (5, 17.5, 24, 92),
    ("medium_dark", "central_american", "washed"):  (5, 18.0, 25, 94),
    ("medium_dark", "central_american", "natural"): (5, 18.0, 25, 92),
    ("medium_dark", "central_american", "honey"):   (5, 18.0, 25, 94),
    ("medium_dark", "central_american", "anaerobic"): (4, 18.0, 25, 94),
    ("medium_dark", "central_american", "wet_hulled"): (5, 18.0, 25, 92),
    ("medium_dark", "blend", "washed"):      (5, 18.0, 25, 94),
    ("medium_dark", "blend", "natural"):     (5, 18.0, 25, 92),
    ("medium_dark", "blend", "honey"):       (5, 18.0, 25, 94),
    ("medium_dark", "african", "anaerobic"):    (4, 18.0, 25, 94),
    ("medium_dark", "south_american", "anaerobic"): (5, 18.0, 25, 94),
    ("medium_dark", "asian", "anaerobic"):      (5, 17.5, 24, 92),
    ("medium_dark", "blend", "anaerobic"):      (5, 18.0, 25, 94),
    ("medium_dark", "african", "wet_hulled"):    (5, 18.0, 25, 94),
    ("medium_dark", "south_american", "wet_hulled"): (5, 18.0, 25, 92),
    ("medium_dark", "asian", "wet_hulled"):      (6, 17.5, 24, 92),
    ("medium_dark", "blend", "wet_hulled"):      (5, 18.0, 25, 92),

    # Dark roasts — coarser grind, lower temp
    ("dark", "african", "washed"):     (6, 17.5, 24, 92),
    ("dark", "african", "natural"):    (6, 17.5, 24, 92),
    ("dark", "african", "honey"):      (6, 17.5, 24, 92),
    ("dark", "south_american", "washed"):  (5, 18.0, 25, 92),
    ("dark", "south_american", "natural"): (6, 18.0, 25, 92),
    ("dark", "south_american", "honey"):   (6, 18.0, 25, 92),
    ("dark", "asian", "washed"):       (6, 17.0, 23, 92),
    ("dark", "asian", "natural"):      (7, 17.0, 23, 92),
    ("dark", "asian", "honey"):        (6, 17.0, 23, 92),
    ("dark", "central_american", "washed"):  (5, 18.0, 25, 92),
    ("dark", "central_american", "natural"): (6, 18.0, 25, 92),
    ("dark", "central_american", "honey"):   (6, 18.0, 25, 92),
    ("dark", "central_american", "anaerobic"): (5, 18.0, 25, 92),
    ("dark", "central_american", "wet_hulled"): (6, 18.0, 25, 92),
    ("dark", "blend", "washed"):       (5, 18.0, 25, 92),
    ("dark", "blend", "natural"):      (6, 18.0, 25, 92),
    ("dark", "blend", "honey"):        (6, 18.0, 25, 92),
    ("dark", "african", "anaerobic"):     (5, 17.5, 24, 92),
    ("dark", "south_american", "anaerobic"): (5, 18.0, 25, 92),
    ("dark", "asian", "anaerobic"):       (6, 17.0, 23, 92),
    ("dark", "blend", "anaerobic"):       (5, 18.0, 25, 92),
    ("dark", "african", "wet_hulled"):     (6, 17.5, 24, 92),
    ("dark", "south_american", "wet_hulled"): (6, 18.0, 25, 92),
    ("dark", "asian", "wet_hulled"):       (7, 17.0, 23, 92),
    ("dark", "blend", "wet_hulled"):       (6, 18.0, 25, 92),
}

# Fallback if exact combo not found
DEFAULT_SETTINGS = {
    "light":       (2, 18.0, 25, 96),
    "medium":      (4, 18.0, 25, 94),
    "medium_dark": (5, 18.0, 25, 94),
    "dark":        (6, 17.5, 24, 92),
}

# === Explanation Templates ===

ORIGIN_TRAITS = {
    "african": "bright acidity and complex floral/fruity notes",
    "south_american": "smooth, balanced body with chocolate and nut tones",
    "central_american": "clean sweetness with balanced acidity and citrus notes",
    "asian": "heavy body with earthy, spicy depth",
    "blend": "a balanced flavor profile from multiple origins",
    "other": "a unique regional character",
}

ROAST_TRAITS = {
    "light": "dense and delicate — needs finer grinding and higher heat to fully develop flavor",
    "medium": "balanced density — standard extraction parameters bring out the best character",
    "medium_dark": "developed sugars with lower acidity — moderate grind prevents over-extraction",
    "dark": "highly soluble and fragile — coarser grind and lower temp avoid bitter harshness",
}

PROCESS_TRAITS = {
    "washed": "clean profile that highlights origin clarity",
    "natural": "fruit-forward sweetness that can over-extract quickly",
    "honey": "syrupy body with balanced sweetness",
    "anaerobic": "intensified fermentation flavors with boosted complexity",
    "wet_hulled": "earthy, full-bodied Indonesian character",
    "other": "standard processing characteristics",
}


def get_recommendation(
    roast_level: str,
    origin: str,
    process_method: str,
    bean_name: str = "",
    brand: str = "",
) -> dict:
    """
    Returns a recommendation dict with settings and explanation.
    Checks historical feedback first, falls back to base matrix.
    """
    # Normalize inputs
    roast = roast_level.lower().strip()
    orig = origin.lower().strip().replace(" ", "_")
    proc = process_method.lower().strip()

    # Try learning from history first
    learned = _get_learned_adjustment(roast, orig, proc)

    # Get base settings
    key = (roast, orig, proc)
    if key in BASE_SETTINGS:
        grind, dose_g, dose_dial, temp = BASE_SETTINGS[key]
    elif roast in DEFAULT_SETTINGS:
        grind, dose_g, dose_dial, temp = DEFAULT_SETTINGS[roast]
    else:
        grind, dose_g, dose_dial, temp = DEFAULT_SETTINGS["medium"]

    confidence = "low"

    # Apply learned adjustments if available
    if learned:
        grind = learned["grind"]
        dose_g = learned["dose_grams"]
        dose_dial = learned["dose_dial"]
        temp = learned["temp"]
        confidence = learned["confidence"]

    # Clamp to machine limits
    grind = max(1, min(8, round(grind)))
    dose_g = max(14.0, min(21.0, round(dose_g, 1)))
    dose_dial = max(10, min(40, round(dose_dial)))
    temp = _nearest_temp(temp)

    # Generate explanation
    explanation = _build_explanation(bean_name, brand, roast, orig, proc, grind, temp)

    return {
        "grind": grind,
        "dose_grams": dose_g,
        "dose_dial": dose_dial,
        "temp": temp,
        "explanation": explanation,
        "confidence": confidence,
    }


def _nearest_temp(temp: float) -> int:
    """Snap to nearest available temperature (92, 94, 96)."""
    options = [92, 94, 96]
    return min(options, key=lambda t: abs(t - temp))


def _get_learned_adjustment(roast: str, origin: str, process: str) -> Optional[dict]:
    """
    Check feedback history for similar beans.
    If 3+ sessions exist with ratings, compute weighted average of
    settings from the top-rated sessions.
    """
    sessions = get_similar_sessions(roast, origin, process)

    if len(sessions) < 3:
        return None

    # Weight: higher-rated and more recent sessions count more
    scored = []
    for i, s in enumerate(sessions):
        overall = s.get("rating_overall", 3) or 3
        # Use actual settings if user adjusted, otherwise use recommended
        grind = s.get("actual_grind") or s["rec_grind"]
        dose_g = s.get("actual_dose_grams") or s["rec_dose_grams"]
        dose_dial = s.get("actual_dose_dial") or s["rec_dose_dial"]
        temp = s.get("actual_temp") or s["rec_temp"]

        recency_weight = 1.0 / (i + 1)  # Most recent = highest weight
        quality_weight = overall / 5.0
        weight = recency_weight * quality_weight

        scored.append({
            "grind": grind,
            "dose_grams": dose_g,
            "dose_dial": dose_dial,
            "temp": temp,
            "weight": weight,
        })

    total_weight = sum(s["weight"] for s in scored)
    if total_weight == 0:
        return None

    avg_grind = sum(s["grind"] * s["weight"] for s in scored) / total_weight
    avg_dose = sum(s["dose_grams"] * s["weight"] for s in scored) / total_weight
    avg_dial = sum(s["dose_dial"] * s["weight"] for s in scored) / total_weight
    avg_temp = sum(s["temp"] * s["weight"] for s in scored) / total_weight

    # Confidence based on data volume and rating consistency
    avg_rating = sum((s.get("rating_overall", 3) or 3) for s in sessions) / len(sessions)
    if len(sessions) >= 10 and avg_rating >= 4:
        confidence = "high"
    elif len(sessions) >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "grind": avg_grind,
        "dose_grams": avg_dose,
        "dose_dial": avg_dial,
        "temp": avg_temp,
        "confidence": confidence,
    }


def _build_explanation(
    bean_name: str, brand: str, roast: str, origin: str, process: str,
    grind: int, temp: int,
) -> str:
    """Build a 1-sentence explanation for why these settings work."""
    bean_label = f"{brand} {bean_name}".strip() if brand else bean_name

    origin_note = ORIGIN_TRAITS.get(origin, "a balanced flavor profile")
    roast_note = ROAST_TRAITS.get(roast, "standard extraction works well")
    process_note = PROCESS_TRAITS.get(process, "standard processing")

    roast_display = roast.replace("_", "-")

    return (
        f"{bean_label} is a {roast_display} roast with {origin_note} and "
        f"{process_note} — grind {grind} at {temp}°C ensures even extraction "
        f"without pulling bitter or sour."
    )


def calculate_xp(overall_rating: int) -> int:
    """XP earned based on overall rating of the shot."""
    xp_map = {1: 10, 2: 15, 3: 25, 4: 40, 5: 60}
    return xp_map.get(overall_rating, 25)


def get_barista_rank(total_xp: int) -> str:
    """Return barista rank title based on total XP."""
    ranks = [
        (0, "Rookie Barista"),
        (100, "Bean Explorer"),
        (300, "Grind Apprentice"),
        (600, "Shot Specialist"),
        (1000, "Extraction Artist"),
        (1500, "Dial-In Master"),
        (2500, "Espresso Sage"),
        (4000, "Crema Legend"),
    ]
    title = ranks[0][1]
    for threshold, rank in ranks:
        if total_xp >= threshold:
            title = rank
    return title


def get_next_rank_info(total_xp: int) -> dict:
    """Return info about the next rank."""
    ranks = [
        (0, "Rookie Barista"),
        (100, "Bean Explorer"),
        (300, "Grind Apprentice"),
        (600, "Shot Specialist"),
        (1000, "Extraction Artist"),
        (1500, "Dial-In Master"),
        (2500, "Espresso Sage"),
        (4000, "Crema Legend"),
    ]
    for i, (threshold, name) in enumerate(ranks):
        if total_xp < threshold:
            prev_threshold = ranks[i - 1][0] if i > 0 else 0
            return {
                "next_rank": name,
                "xp_needed": threshold - total_xp,
                "progress": (total_xp - prev_threshold) / (threshold - prev_threshold),
            }
    return {"next_rank": "MAX", "xp_needed": 0, "progress": 1.0}
