"""
Configuration settings and constants for CineScope.
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
SPARK_APP_NAME = "CineScope - Movie Performance Analytics"
SPARK_MASTER = "local[*]"

# Image & Poster CDN
TMDB_POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Styling / Theme Tokens
THEME = {
    "bg_main": "#0B1020",
    "bg_card": "#151C2F",
    "bg_card_secondary": "#1E293B",
    "border": "#2E3A52",
    "accent_primary": "#8B5CF6",     # Electric Violet
    "accent_secondary": "#06B6D4",   # Cyan
    "accent_hover": "#7C3AED",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "success": "#10B981",            # Emerald
    "warning": "#F59E0B",            # Amber
    "danger": "#F43F5E",             # Rose
    "chart_palette": [
        "#8B5CF6", "#06B6D4", "#3B82F6", "#10B981",
        "#F59E0B", "#EC4899", "#6366F1", "#14B8A6",
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
