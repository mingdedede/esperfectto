"""
Static reference data: bean varieties, roasters, countries, process methods.
Used for dropdowns, typo correction, and validation.
"""

import difflib
from typing import Optional

# ── Bean varieties / named beans, ordered popular → niche ──

BEAN_VARIETIES = [
    # Popular blends & styles
    "Espresso Blend",
    "House Blend",
    "Breakfast Blend",
    "Single Origin",
    "Decaf Blend",
    # Famous named origins
    "Yirgacheffe",
    "Sidamo",
    "Guji",
    "Huila",
    "Nariño",
    "Tolima",
    "Supremo",
    "Antigua",
    "Tarrazú",
    "Kona",
    "Jamaica Blue Mountain",
    "Mandheling",
    "Sumatra",
    "Sulawesi Toraja",
    "Kenya AA",
    "Kilimanjaro",
    "Rwanda",
    "Burundi",
    "Harrar",
    "Limu",
    "Nyeri",
    "Cerrado",
    "Santos",
    "Sul de Minas",
    "Huehuetenango",
    "Atitlan",
    "Lintong",
    "Gayo",
    "Marcala",
    "Jinotega",
    "Chirripó",
    "Da Lat",
    "Peaberry",
    # Classic cultivars
    "Bourbon",
    "Typica",
    "Caturra",
    "Catuai",
    "Gesha",
    "Geisha",
    "SL28",
    "SL34",
    "Pacamara",
    "Castillo",
    "Heirloom",
    "Mundo Novo",
    "Catimor",
    "Maragogipe",
    "Villa Sarchi",
    "Pacas",
    "Mokka",
    "Laurina",
    "Tabi",
    "Sidra",
    "Wush Wush",
    "Pink Bourbon",
    "Yellow Bourbon",
    "Red Bourbon",
    "Red Catuai",
    "Yellow Catuai",
    "Ethiopian Heirloom",
    "Java",
    "Obata",
    "Icatu",
    "Sarchimor",
    "Maracaturra",
    "Ruiru 11",
    "Batian",
    "Kent",
    "S795",
    "Tekisic",
    # Roast styles
    "French Roast",
    "Italian Roast",
    "Vienna Roast",
    "Mocha Java",
    # Species
    "Arabica",
    "Robusta",
    "Liberica",
    "Excelsa",
    # Catch-all
    "Other",
]

# ── Top roasters worldwide (~600, popular first) ──

TOP_ROASTERS = [
    "Starbucks", "Nespresso", "Lavazza", "Illy", "Peet's Coffee",
    "Blue Bottle Coffee", "Stumptown Coffee Roasters", "Intelligentsia Coffee",
    "Counter Culture Coffee", "La Colombe", "Dunkin'", "Tim Hortons",
    "Costa Coffee", "Julius Meinl", "Segafredo Zanetti", "Tchibo",
    "Death Wish Coffee", "Caribou Coffee", "The Coffee Bean & Tea Leaf",
    "Community Coffee", "Cafe Bustelo", "Green Mountain Coffee Roasters",
    "Seattle's Best Coffee", "Gloria Jean's Coffees", "Vittoria Coffee",
    "Kimbo", "Dallmayr", "Melitta",
    # Top specialty / third wave
    "Onyx Coffee Lab", "Verve Coffee Roasters", "Heart Coffee Roasters",
    "Ritual Coffee Roasters", "Four Barrel Coffee", "Sightglass Coffee",
    "Equator Coffees", "Ceremony Coffee Roasters", "George Howell Coffee",
    "Tandem Coffee Roasters", "Madcap Coffee", "Ruby Coffee Roasters",
    "PT's Coffee Roasting Co.", "Olympia Coffee Roasting", "Coava Coffee Roasters",
    "Proud Mary Coffee", "Tim Wendelboe", "The Barn", "Five Elephant",
    "Bonanza Coffee", "Square Mile Coffee Roasters", "Workshop Coffee",
    "Monmouth Coffee", "Allpress Espresso", "Has Bean Coffee",
    "Origin Coffee Roasting", "Koppi", "Drop Coffee", "Da Matteo",
    "Coffee Collective", "April Coffee Roasters", "Friedhats",
    "Manhattan Coffee Roasters", "Gardelli Specialty Coffees",
    "Passenger Coffee", "Sey Coffee", "Devocion",
    "Variety Coffee Roasters", "Parlor Coffee", "Joe Coffee Company",
    "Irving Farm Coffee Roasters", "Cafe Grumpy", "Toby's Estate Coffee",
    "Partners Coffee", "Black Fox Coffee",
    # US specialty continued
    "Sweet Bloom Coffee Roasters", "Huckleberry Roasters",
    "Boxcar Coffee Roasters", "Corvus Coffee Roasters",
    "Methodical Coffee", "Brandywine Coffee Roasters", "Klatch Coffee",
    "Bird Rock Coffee Roasters", "Mostra Coffee", "Temple Coffee Roasters",
    "Red Bay Coffee", "Highwire Coffee Roasters", "Chromatic Coffee",
    "Cat & Cloud Coffee", "Andytown Coffee Roasters", "Saint Frank Coffee",
    "Wrecking Ball Coffee Roasters", "Linea Caffe",
    "Camber Coffee", "Anchorhead Coffee", "Elm Coffee Roasters",
    "Victrola Coffee Roasters", "Slate Coffee Roasters",
    "Caffe Vita", "Nossa Familia Coffee", "Water Avenue Coffee",
    "Spyhouse Coffee Roasters", "Dogwood Coffee",
    "Metric Coffee", "Passion House Coffee Roasters", "Dark Matter Coffee",
    "Gaslight Coffee Roasters", "Halfwit Coffee Roasters",
    "Kickapoo Coffee", "JBC Coffee Roasters", "Wonderstate Coffee",
    "Colectivo Coffee", "Greater Goods Coffee", "Cuvee Coffee",
    "Merit Coffee", "Houndstooth Coffee", "Cultivar Coffee",
    "Methodical Coffee", "Revelator Coffee", "Deeper Roots Coffee",
    "Blueprint Coffee", "Messenger Coffee", "Oddly Correct",
    "Quills Coffee", "Barista Parlor",
    # Canada
    "Pilot Coffee Roasters", "Detour Coffee Roasters", "Monogram Coffee",
    "Phil & Sebastian Coffee Roasters", "Rosso Coffee Roasters",
    "Nemesis Coffee", "Matchstick Coffee Roasters",
    "49th Parallel Coffee Roasters", "Pallet Coffee Roasters",
    "Transcend Coffee", "Dispatch Coffee", "De Mello Coffee",
    # UK & Ireland
    "Union Hand-Roasted Coffee", "Dark Arts Coffee", "Assembly Coffee",
    "Climpson & Sons", "Caravan Coffee Roasters", "Ozone Coffee Roasters",
    "Notes Coffee", "Kiss the Hippo", "Redemption Roasters",
    "Round Hill Roastery", "Rave Coffee", "North Star Coffee Roasters",
    "Girls Who Grind Coffee", "Crankhouse Coffee", "Extract Coffee Roasters",
    "Clifton Coffee Roasters", "Colonna Coffee", "3fe Coffee",
    "Calendar Coffee", "Bailies Coffee Roasters",
    "Papercup Coffee", "Dear Green Coffee Roasters",
    "Fortitude Coffee", "Artisan Roast", "Pact Coffee",
    # Scandinavia & Nordic
    "Johan & Nyström", "Supreme Roastworks", "Solberg & Hansen",
    "Fuglen Coffee Roasters", "La Cabra", "Kaffa",
    # Germany, Austria & Switzerland
    "19grams", "Tres Cabezas", "Flying Roasters",
    "Public Coffee Roasters", "Elbgold", "Coffee Circle",
    "Röststätte Berlin", "Mame Coffee",
    # Netherlands & Belgium
    "Bocca Coffee", "White Label Coffee", "Lot Sixty One Coffee Roasters",
    "Caffenation",
    # France
    "Belleville Brulerie", "Coutume Cafe", "Terres de Cafe",
    "L'Arbre à Café",
    # Italy specialty
    "Ditta Artigianale", "Gardelli", "Caffè Vergnano", "Pellini",
    # Spain & Portugal
    "Right Side Coffee", "Nomad Coffee", "Satan's Coffee Corner",
    # Eastern Europe
    "Doubleshot", "Hard Beans", "HAYB", "Diamonds Roastery",
    # Middle East
    "% Arabica", "Brew92", "Kronotrop Coffee",
    # Australia & New Zealand
    "Market Lane Coffee", "Seven Seeds", "Padre Coffee", "St Ali",
    "Dukes Coffee Roasters", "Code Black Coffee", "Axil Coffee Roasters",
    "Industry Beans", "Five Senses Coffee", "Mecca Coffee", "Single O",
    "Sample Coffee", "Campos Coffee", "Ona Coffee",
    "Pablo & Rusty's", "Veneziano Coffee Roasters",
    "Coffee Supreme", "Havana Coffee Works", "Allpress Espresso",
    "L'affare Coffee",
    # Japan
    "Maruyama Coffee", "Glitch Coffee", "Onibus Coffee",
    "Koffee Mameya", "Kurasu", "Fuglen Tokyo",
    "Light Up Coffee", "Trunk Coffee",
    # South Korea
    "Fritz Coffee Company", "Felt Coffee", "Anthracite Coffee",
    "Coffee Libre",
    # China / HK / Taiwan
    "Manner Coffee", "Seesaw Coffee", "Simple Kaffa", "Fika Fika Cafe",
    "Elephant Grounds", "NOC Coffee Co.",
    # Southeast Asia
    "The Workshop Coffee", "Roots Coffee Roaster",
    "Common Man Coffee Roasters", "Nylon Coffee Roasters",
    "Papa Palheta", "Pacamara Coffee Roasters",
    # India
    "Blue Tokai Coffee Roasters", "Third Wave Coffee",
    "Sleepy Owl Coffee", "Araku Coffee",
    # Africa
    "Dormans Coffee", "Tomoca Coffee", "Truth Coffee Roasting",
    "Rosetta Roastery", "Father Coffee",
    # Latin America
    "Juan Valdez Cafe", "Devocion Colombia", "Pergamino Cafe",
    "Azahar Coffee", "Cafe Britt", "Coffee Lab Brazil",
    # DTC / Subscription
    "Trade Coffee", "Atlas Coffee Club", "MistoBox",
    "Driftaway Coffee", "Bean Box", "Yes Plz Coffee",
    # Other notable
    "Black Rifle Coffee Company", "Nguyen Coffee Supply",
    "Kicking Horse Coffee", "Bulletproof Coffee",
    "Bluestone Lane", "Blank Street Coffee", "Gregory's Coffee",
    "Alfred Coffee", "Go Get Em Tiger", "Dayglow Coffee",
    "Stereoscope Coffee", "Bar Nine", "Portola Coffee Roasters",
    "Copa Vida", "Reborn Coffee",
]

# ── Deduplicate roasters ──
_seen = set()
_deduped = []
for r in TOP_ROASTERS:
    key = r.lower().strip()
    if key not in _seen:
        _seen.add(key)
        _deduped.append(r)
TOP_ROASTERS = _deduped

# ── Coffee-producing countries by region ──

COFFEE_REGIONS = {
    "african": [
        "Burundi", "Cameroon", "Congo (DRC)", "Ethiopia", "Ivory Coast",
        "Kenya", "Madagascar", "Malawi", "Mozambique", "Rwanda",
        "Tanzania", "Togo", "Uganda", "Zambia", "Zimbabwe",
    ],
    "south_american": [
        "Bolivia", "Brazil", "Colombia", "Ecuador", "Peru", "Venezuela",
    ],
    "central_american": [
        "Costa Rica", "Cuba", "Dominican Republic", "El Salvador",
        "Guatemala", "Haiti", "Honduras", "Jamaica", "Mexico",
        "Nicaragua", "Panama", "Puerto Rico",
    ],
    "asian": [
        "China", "India", "Indonesia", "Laos", "Myanmar", "Nepal",
        "Papua New Guinea", "Philippines", "Sri Lanka", "Taiwan",
        "Thailand", "Vietnam", "Yemen",
    ],
    "blend": [],
    "other": [
        "Australia", "Hawaii (USA)", "Other",
    ],
}

# Flat list for country→region reverse lookup
COUNTRY_TO_REGION = {}
for region, countries in COFFEE_REGIONS.items():
    for country in countries:
        COUNTRY_TO_REGION[country.lower()] = region

# ── Process methods ──

PROCESS_METHODS = [
    ("washed", "Washed"),
    ("natural", "Natural"),
    ("honey", "Honey"),
    ("anaerobic", "Anaerobic"),
    ("wet_hulled", "Wet Hulled"),
    ("other", "Other"),
]


# ── Brand validation helpers ──

def find_brand_match(query: str, cutoff: float = 0.7) -> Optional[str]:
    """
    Check if a brand name matches or closely matches a known roaster.
    Returns the best match, or None if no close match found.
    """
    if not query or not query.strip():
        return None

    query_clean = query.strip()

    # Exact match (case-insensitive)
    for roaster in TOP_ROASTERS:
        if roaster.lower() == query_clean.lower():
            return roaster

    # Close match
    matches = difflib.get_close_matches(
        query_clean, TOP_ROASTERS, n=1, cutoff=cutoff
    )
    return matches[0] if matches else None


def is_known_brand(query: str) -> bool:
    """Check if brand exactly matches a known roaster (case-insensitive)."""
    if not query:
        return False
    query_lower = query.strip().lower()
    return any(r.lower() == query_lower for r in TOP_ROASTERS)


def suggest_brand(query: str) -> Optional[str]:
    """
    If query is close to but not exactly a known brand, return suggestion.
    Returns None if exact match or no close match.
    """
    if not query or not query.strip():
        return None
    if is_known_brand(query):
        return None  # Already exact match
    return find_brand_match(query, cutoff=0.6)


def get_countries_for_region(region: str) -> list:
    """Return list of countries for a given region key."""
    return COFFEE_REGIONS.get(region.lower(), [])
