"""
Utility and helper functions for formatting, metrics conversion, and export.
"""
import io
import pandas as pd
import numpy as np


def format_currency(val, currency: str = "$") -> str:
    """Format large monetary values into readable units (K, M, B)."""
    if val is None or pd.isna(val) or val == 0:
        return f"{currency}0"
    
    val = float(val)
    if val >= 1_000_000_000:
        return f"{currency}{val / 1_000_000_000:.2f}B"
    elif val >= 1_000_000:
        return f"{currency}{val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"{currency}{val / 1_000:.1f}K"
    else:
        return f"{currency}{val:,.0f}"


def format_number(val) -> str:
    """Format integer/float counts with comma separators."""
    if val is None or pd.isna(val):
        return "0"
    try:
        return f"{int(round(float(val))):,}"
    except (ValueError, TypeError):
        return str(val)


def format_percentage(val) -> str:
    """Format ROI / growth values as signed percentage string."""
    if val is None or pd.isna(val):
        return "0.0%"
    try:
        val_f = float(val)
        sign = "+" if val_f > 0 else ""
        return f"{sign}{val_f:.1f}%"
    except (ValueError, TypeError):
        return "0.0%"


def format_runtime(minutes) -> str:
    """Convert minutes to human readable 'Xh Ym' format."""
    if minutes is None or pd.isna(minutes) or minutes <= 0:
        return "N/A"
    try:
        mins = int(round(float(minutes)))
        h = mins // 60
        m = mins % 60
        if h > 0 and m > 0:
            return f"{h}h {m}m"
        elif h > 0:
            return f"{h}h"
        else:
            return f"{m}m"
    except (ValueError, TypeError):
        return "N/A"


def format_rating(rating) -> str:
    """Format rating out of 10."""
    if rating is None or pd.isna(rating):
        return "N/A"
    try:
        return f"{float(rating):.1f} / 10"
    except (ValueError, TypeError):
        return "N/A"


def safe_divide(numerator, denominator, default=0.0):
    """Safely divide two numbers avoiding ZeroDivisionError or NaN."""
    try:
        if denominator is None or pd.isna(denominator) or denominator == 0:
            return default
        if numerator is None or pd.isna(numerator):
            return default
        return float(numerator) / float(denominator)
    except Exception:
        return default


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a pandas DataFrame to UTF-8 CSV bytes for download."""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8")
    return csv_buffer.getvalue().encode("utf-8")


def resolve_movie_poster_url(title: str, year: any = None, poster_path: str = None) -> str:
    """Resolve an accessible, high-resolution image URL for a movie poster.
    
    Checks TMDB CDN path first. If inaccessible (404/purged on TMDB),
    gracefully falls back to Wikipedia Page Summary API for official poster art.
    """
    import urllib.request
    import urllib.parse
    import json

    # 1. Check TMDB if path provided
    if poster_path and str(poster_path) != "nan" and str(poster_path).strip():
        tmdb_url = f"https://image.tmdb.org/t/p/w500{str(poster_path).strip()}"
        try:
            req = urllib.request.Request(tmdb_url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=1.2) as resp:
                if resp.status == 200:
                    return tmdb_url
        except Exception:
            pass

    # 2. Check Wikipedia Page Summary for official theatrical poster
    if title and str(title) != "nan":
        candidates = []
        if year and str(year) != "nan":
            try:
                clean_year = int(float(year))
                candidates.append(f"{title} ({clean_year} film)")
            except Exception:
                pass
        candidates.append(str(title).strip())

        for cand in candidates:
            try:
                wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(cand)}"
                req = urllib.request.Request(wiki_url, headers={"User-Agent": "CineScope/1.0 (contact: info@cinescope.org)"})
                with urllib.request.urlopen(req, timeout=1.2) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        thumb = data.get("thumbnail", {}).get("source")
                        if thumb:
                            return thumb
            except Exception:
                continue

    return ""

