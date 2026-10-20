"""
Page 2: Movie Explorer with multi-dimensional filtering, detail card, and CSV export.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st
import pandas as pd
from pyspark.sql import functions as F

st.set_page_config(page_title="Movie Explorer — CineScope", page_icon="🔍", layout="wide")

from src.config import THEME, KNOWN_GENRES, PAGE_SIZE_OPTIONS
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import render_movie_detail_card
from src.utils import df_to_csv_bytes, format_currency, format_number, format_runtime, resolve_movie_poster_url

@st.cache_data(show_spinner=False, ttl=86400)
def get_cached_poster_url(title: str, year: any, poster_path: str = None) -> str:
    return resolve_movie_poster_url(title, year, poster_path)

inject_custom_css()

try:
    resources = get_pipeline_resources()
    data_report = resources["data_report"]
    df_clean = resources["df_clean"]
    render_sidebar_status(data_report)
except Exception as e:
    st.error(f"Failed to load pipeline data: {str(e)}")
    st.stop()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 30px;">Movie Explorer</h1>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
        Search and filter through the entire movie catalog using multi-dimensional parameters. Select a title to inspect deep metadata and poster assets.
    </p>
</div>
""", unsafe_allow_html=True)

# Filter Controls Card
with st.expander("🛠️ Search & Filter Controls", expanded=True):
    f_row1_1, f_row1_2, f_row1_3 = st.columns([2, 1.2, 1.2])
    with f_row1_1:
        search_query = st.text_input("🔍 Search Title / Keyword", "", placeholder="e.g. Toy Story, Avatar, Dark Knight...")
    with f_row1_2:
        selected_genre = st.selectbox("🏷️ Genre", ["All Genres"] + sorted(KNOWN_GENRES))
    with f_row1_3:
        language_options = ["All Languages", "en (English)", "fr (French)", "it (Italian)", "ja (Japanese)", "de (German)", "es (Spanish)", "ru (Russian)", "hi (Hindi)"]
        selected_lang_raw = st.selectbox("🌐 Language", language_options)
        selected_lang = selected_lang_raw.split()[0] if selected_lang_raw != "All Languages" else "All"

    f_row2_1, f_row2_2, f_row2_3 = st.columns(3)
    with f_row2_1:
        year_range = st.slider("📅 Release Year Range", min_value=1920, max_value=2020, value=(1970, 2020))
    with f_row2_2:
        rating_range = st.slider("⭐ Rating Range (0 - 10)", min_value=0.0, max_value=10.0, value=(0.0, 10.0), step=0.1)
    with f_row2_3:
        min_votes = st.number_input("🗳️ Minimum Vote Count", min_value=0, max_value=5000, value=10, step=25)

    f_row3_1, f_row3_2, f_row3_3 = st.columns(3)
    with f_row3_1:
        min_rev_mil = st.number_input("💰 Minimum Worldwide Revenue ($ Millions)", min_value=0, max_value=1000, value=0, step=10)
    with f_row3_2:
        sort_by = st.selectbox(
            "↕️ Sort Results By",
            [
                "Revenue (High to Low)",
                "Rating (High to Low)",
                "Popularity (High to Low)",
                "Vote Count (High to Low)",
                "Release Year (Newest)",
                "Release Year (Oldest)",
                "Budget (High to Low)",
                "Title (A-Z)"
            ]
        )
    with f_row3_3:
        page_size = st.selectbox("📄 Records to Display", PAGE_SIZE_OPTIONS, index=1)

# Apply PySpark DataFrame Filters
filtered_df = df_clean

if search_query.strip():
    q = search_query.strip().lower()
    filtered_df = filtered_df.filter(F.lower(F.col("title_clean")).contains(q))

if selected_genre != "All Genres":
    filtered_df = filtered_df.filter(F.array_contains(F.col("genres_list"), selected_genre))

if selected_lang != "All":
    filtered_df = filtered_df.filter(F.col("original_language") == selected_lang)

filtered_df = filtered_df.filter(
    F.col("release_year").isNotNull() &
    F.col("release_year").between(year_range[0], year_range[1]) &
    F.col("vote_avg").between(rating_range[0], rating_range[1]) &
    (F.col("vote_cnt") >= min_votes)
)

if min_rev_mil > 0:
    filtered_df = filtered_df.filter(F.col("revenue_num") >= (min_rev_mil * 1_000_000))

# Sorting mapping
sort_col_map = {
    "Revenue (High to Low)": ("revenue_num", False),
    "Rating (High to Low)": ("vote_avg", False),
    "Popularity (High to Low)": ("popularity_num", False),
    "Vote Count (High to Low)": ("vote_cnt", False),
    "Release Year (Newest)": ("release_year", False),
    "Release Year (Oldest)": ("release_year", True),
    "Budget (High to Low)": ("budget_num", False),
    "Title (A-Z)": ("title_clean", True),
}

metric_col, ascending = sort_col_map[sort_by]
sorted_df = filtered_df.orderBy(F.col(metric_col).asc() if ascending else F.col(metric_col).desc())

# Count matching records using Spark action
match_count = sorted_df.count()

# Display match status and download action
top_bar_col1, top_bar_col2 = st.columns([3, 1])
with top_bar_col1:
    st.markdown(f"#### 🎬 Found **{match_count:,}** movies matching your criteria")
with top_bar_col2:
    if match_count > 0:
        # Export up to 5,000 rows as CSV
        export_limit = min(match_count, 5000)
        export_pdf = sorted_df.limit(export_limit).toPandas()
        csv_data = df_to_csv_bytes(export_pdf)
        st.download_button(
            label=f"📥 Download Filtered CSV ({export_limit:,})",
            data=csv_data,
            file_name="cinescope_filtered_movies.csv",
            mime="text/csv",
            use_container_width=True
        )

# Results table
if match_count == 0:
    st.info("No movies matched your current filter criteria. Try adjusting the search term, sliders, or thresholds.")
else:
    # Limit for current table page view
    display_pdf = sorted_df.limit(page_size).toPandas()

    # Format dataframe for display
    table_view = display_pdf[[
        "title_clean", "release_year", "genres_display", "vote_avg", "vote_cnt",
        "revenue_num", "budget_num", "popularity_num", "runtime_num"
    ]].copy()

    table_view.columns = [
        "Title", "Year", "Genres", "Rating", "Votes", "Revenue ($)", "Budget ($)", "Popularity", "Runtime (m)"
    ]

    st.dataframe(
        table_view.style.format({
            "Rating": "{:.1f}",
            "Votes": "{:,.0f}",
            "Revenue ($)": lambda x: format_currency(x),
            "Budget ($)": lambda x: format_currency(x),
            "Popularity": "{:.1f}",
            "Runtime (m)": lambda x: f"{x:.0f}" if pd.notna(x) else "N/A"
        }),
        use_container_width=True,
        height=min(450, 40 + len(table_view) * 35)
    )

    # Detailed Movie Inspector
    st.markdown("### 📽️ Movie Detail Inspector")
    title_options = display_pdf["title_clean"].tolist()
    selected_title = st.selectbox("Select a movie from results to view full profile & poster:", title_options)

    if selected_title:
        selected_match = display_pdf[display_pdf["title_clean"] == selected_title]
        if not selected_match.empty:
            selected_row = selected_match.iloc[0].to_dict()
            selected_row["poster_url"] = get_cached_poster_url(
                selected_row.get("title_clean"),
                selected_row.get("release_year"),
                selected_row.get("poster_path")
            )
            detail_card_html = render_movie_detail_card(selected_row)
            if hasattr(st, "html"):
                st.html(detail_card_html)
            else:
                st.markdown(detail_card_html, unsafe_allow_html=True)


