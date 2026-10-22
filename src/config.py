"""
Configuration settings and constants for CinePulse.
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

MOVIES_METADATA_PATH = DATA_DIR / "movies_metadata.csv"
RATINGS_SMALL_PATH = DATA_DIR / "ratings_small.csv"
CREDITS_PATH = DATA_DIR / "credits.csv"
KEYWORDS_PATH = DATA_DIR / "keywords.csv"

# Spark Application Details
SPARK_APP_NAME = "CinePulse - Movie Performance Analytics"
SPARK_MASTER = "local[*]"

# Image & Poster CDN
TMDB_POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Styling / Theme Tokens
THEME = {
    "bg_main": "#0A0D14",
    "bg_card": "#131926",
    "bg_card_secondary": "#1E2638",
    "border": "#273248",
    "accent_primary": "#F59E0B",     # Cinema Amber Gold
    "accent_secondary": "#06B6D4",   # Cyber Cyan
    "accent_hover": "#D97706",       # Deep Amber
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "success": "#10B981",            # Emerald
    "warning": "#F59E0B",            # Amber
    "danger": "#F43F5E",             # Rose Red
    "chart_palette": [
        "#F59E0B", "#06B6D4", "#3B82F6", "#10B981",
        "#EC4899", "#8B5CF6", "#F97316", "#14B8A6",
        "#F43F5E", "#84CC16", "#A855F7", "#0EA5E9"
    ]
}

# Analytics Thresholds & Defaults
DEFAULT_MIN_VOTES = 50
DEFAULT_MIN_BUDGET_ROI = 1000000  # $1M threshold for ROI to avoid micro-budget distortion
DEFAULT_CURRENCY = "$"
PAGE_SIZE_OPTIONS = [10, 25, 50, 100]

# Known Genres
KNOWN_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime",
    "Documentary", "Drama", "Family", "Fantasy", "Foreign",
    "History", "Horror", "Music", "Mystery", "Romance",
    "Science Fiction", "TV Movie", "Thriller", "War", "Western"
]
