"""
Page 5: Ratings & Popularity — Audience sentiment, vote thresholds, and engagement correlations.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyspark.sql import functions as F

st.set_page_config(page_title="Ratings & Popularity — CineScope", page_icon="⭐", layout="wide")

from src.config import THEME, DEFAULT_MIN_VOTES
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import (
    apply_cinescope_theme,
    render_kpi_card_html,
    plot_ratings_histogram,
    plot_top_movies_bar,
)
from src.analytics import get_ratings_popularity_analysis
from src.utils import format_number, format_rating

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
    <h1 style="margin: 0; font-size: 30px;">Ratings & Popularity Analytics</h1>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
        Audience reception and popularity metrics powered by Spark aggregations.
    </p>
</div>
""", unsafe_allow_html=True)

# Minimum vote count control
col_ctrl1, col_ctrl2 = st.columns([2, 1])
with col_ctrl1:
    min_vote_threshold = st.slider(
        "🗳️ Minimum Vote Count Threshold for Highest-Rated Rankings",
        min_value=10,
        max_value=2000,
        value=150,
        step=25,
        help="Films with only 1 or 2 votes often have 10/10 scores, introducing severe statistical bias. A minimum vote threshold ensures critical credibility."
    )
with col_ctrl2:
    st.info(f"Filtering movies with **≥ {min_vote_threshold} votes** to rank audience favorites.")

# Compute ratings & popularity analytics with Spark
rp_data = get_ratings_popularity_analysis(df_clean, min_votes=min_vote_threshold)
sample_df = rp_data["ratings_sample"]

# Visualizations Row 1: Rating Distribution & Top Rated
r1_c1, r1_c2 = st.columns(2)
with r1_c1:
    st.plotly_chart(plot_ratings_histogram(sample_df), use_container_width=True)

with r1_c2:
    st.plotly_chart(
        plot_top_movies_bar(rp_data["top_rated"], "vote_avg", f"Top 10 Highest-Rated Movies (≥ {min_vote_threshold} votes)", "Average Rating", is_currency=False),
        use_container_width=True
    )

# Visualizations Row 2: Top Popular Movies & Most Voted Movies
r2_c1, r2_c2 = st.columns(2)
with r2_c1:
    st.plotly_chart(
        plot_top_movies_bar(rp_data["top_popular"], "popularity_num", "Top 10 Most Popular Movies (TMDB Index)", "Popularity Metric", is_currency=False),
        use_container_width=True
    )

with r2_c2:
    st.plotly_chart(
        plot_top_movies_bar(rp_data["top_votes"], "vote_cnt", "Top 10 Most Voted Movies", "Total Votes Count", is_currency=False),
        use_container_width=True
    )

# Correlations Section: Ratings vs Popularity & Ratings vs Votes
st.markdown("### 🔬 Correlation & Audience Engagement Dynamics")
corr_tab1, corr_tab2 = st.tabs(["🔥 Rating vs. Popularity Index", "🗳️ Rating vs. Total Vote Count"])

with corr_tab1:
    fig_pop = px.scatter(
        sample_df,
        x="vote_avg",
        y="popularity_num",
        hover_name="title_clean",
        title="Audience Rating vs. TMDB Popularity Index",
        labels={"vote_avg": "Average Rating (0 - 10)", "popularity_num": "Popularity Index"},
        color_discrete_sequence=[THEME["accent_secondary"]]
    )
    st.plotly_chart(apply_cinescope_theme(fig_pop, height=450), use_container_width=True)

with corr_tab2:
    fig_votes = px.scatter(
        sample_df,
        x="vote_avg",
        y="vote_cnt",
        hover_name="title_clean",
        title="Audience Rating vs. Number of Ratings Submitted",
        labels={"vote_avg": "Average Rating (0 - 10)", "vote_cnt": "Total Vote Count"},
        color_discrete_sequence=[THEME["accent_primary"]]
    )
    st.plotly_chart(apply_cinescope_theme(fig_votes, height=450), use_container_width=True)
