"""
CineScope — Movie Performance Analytics
Main Application Entry Point.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st

# Configure page layout and metadata
st.set_page_config(
    page_title="CineScope — Movie Performance Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import THEME, MOVIES_METADATA_PATH
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import render_kpi_card_html
from src.utils import format_currency, format_number, format_runtime

# Apply custom dark cinematic theme
inject_custom_css()

# Error handling wrapper around Spark initialization
try:
    resources = get_pipeline_resources()
    data_report = resources["data_report"]
    kpis = resources["kpis"]
    render_sidebar_status(data_report)
except Exception as e:
    st.error(f"### ⚠️ Initialization Notice\n\n{str(e)}")
    st.info(
        "**Troubleshooting Checklist:**\n"
        "1. Ensure Java (JRE 8, 11, or 17) is installed and accessible.\n"
        "2. Ensure `data/movies_metadata.csv` exists and is not corrupted.\n"
        "3. Ensure `pyspark` and required libraries are installed."
    )
    st.stop()

# Main Hero Header
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(21, 28, 47, 0.95) 0%, rgba(11, 16, 32, 0.95) 100%);
    border: 1px solid {THEME['border']};
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
">
    <div style="position: absolute; right: -20px; top: -20px; font-size: 150px; opacity: 0.04; pointer-events: none;">
        🎬
    </div>
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap;">
        <span style="
            background: linear-gradient(135deg, {THEME['accent_primary']} 0%, #6366F1 100%);
            color: white;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.4);
        ">
            Enterprise Analytics Platform
        </span>
        <span style="
            background: rgba(6, 182, 212, 0.12);
            border: 1px solid rgba(6, 182, 212, 0.35);
            color: {THEME['accent_secondary']};
            font-size: 11px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
        ">
            ⚡ Apache Spark 3.5.5 Catalyst Engine
        </span>
        <span style="
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: {THEME['success']};
            font-size: 11px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
        ">
            🟢 45,463 Cleaned Records
        </span>
    </div>
    <h1 style="margin: 0 0 10px 0; font-size: 38px; font-weight: 800; letter-spacing: -0.02em;">
        CineScope — Movie Performance Analytics
    </h1>
    <p style="margin: 0; color: {THEME['text_secondary']}; font-size: 15px; max-width: 880px; line-height: 1.6;">
        A high-performance cinematic intelligence platform analyzing <strong>{data_report['total_clean_records']:,} feature films</strong> across decades. 
        Engineered with distributed PySpark DataFrames, native Catalyst SQL transformations, and real-time interactive analytical visualizations.
    </p>
</div>
""", unsafe_allow_html=True)

# Top KPI Metric Cards Preview
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(render_kpi_card_html("Total Movies", format_number(kpis["total_movies"]), "Cataloged titles", "🎬"), unsafe_allow_html=True)
with col2:
    st.markdown(render_kpi_card_html("Avg Rating", f"{kpis['avg_rating']} / 10", "Across rated films", "⭐", "secondary"), unsafe_allow_html=True)
with col3:
    st.markdown(render_kpi_card_html("Total Revenue", format_currency(kpis["total_revenue"]), "Reported box office", "💰"), unsafe_allow_html=True)
with col4:
    st.markdown(render_kpi_card_html("Avg Revenue", format_currency(kpis["avg_revenue"]), "Per commercial release", "📈", "secondary"), unsafe_allow_html=True)
with col5:
    st.markdown(render_kpi_card_html("Avg Budget", format_currency(kpis["avg_budget"]), "Production expenditure", "💼"), unsafe_allow_html=True)
with col6:
    st.markdown(render_kpi_card_html("Avg Runtime", format_runtime(kpis["avg_runtime"]), "Standard feature length", "⏱️", "secondary"), unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Navigation Hub Cards
st.markdown("### 🧭 Explore Analytical Modules")
st.markdown("Select any module from the sidebar navigation or explore the modules below:")

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

with row1_col1:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_primary']};">1. Overview</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            Executive summary with multi-decade release timelines, genre distributions, box office leaders, and dynamic key insights.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_secondary']}; font-weight: 600;">👉 Navigate to 1_Overview in sidebar</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_primary']};">2. Movie Explorer</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            Multi-attribute search engine with real-time filtering by genre, release year, ratings, vote thresholds, posters, and CSV export.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_secondary']}; font-weight: 600;">👉 Navigate to 2_Movie_Explorer</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col3:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_primary']};">3. Genre Analysis</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            Normalized PySpark exploded genre relations, revenue comparisons, runtime averages, and decade production heatmaps.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_secondary']}; font-weight: 600;">👉 Navigate to 3_Genre_Analysis</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col4:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_primary']};">4. Revenue & Budget</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            Financial performance models, estimated profit, ROI rankings, scatter distributions, and box office hits vs. critical misses.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_secondary']}; font-weight: 600;">👉 Navigate to 4_Revenue_Budget</div>
    </div>
    """, unsafe_allow_html=True)

row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

with row2_col1:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_secondary']};">5. Ratings & Popularity</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            Audience sentiment analysis, vote count thresholds to eliminate skew, popularity correlation, and top-rated leaderboards.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_primary']}; font-weight: 600;">👉 Navigate to 5_Ratings_Popularity</div>
    </div>
    """, unsafe_allow_html=True)

with row2_col2:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_secondary']};">6. Trends Over Time</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            Longitudinal timeline charts tracking production volume, average ratings, and historical budget and revenue expansions.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_primary']}; font-weight: 600;">👉 Navigate to 6_Trends_Over_Time</div>
    </div>
    """, unsafe_allow_html=True)

with row2_col3:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_secondary']};">7. Data Quality & Spark</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            Data engineering core: Spark schema verification, missing value audits, pipeline stages, and interactive Spark SQL query runner.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_primary']}; font-weight: 600;">👉 Navigate to 7_Data_Quality</div>
    </div>
    """, unsafe_allow_html=True)

with row2_col4:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 6px 0; color: {THEME['accent_secondary']};">8. About Project</h4>
        <p style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.5; margin: 0 0 12px 0;">
            System architecture diagram, technology stack documentation, performance benchmarks, and dataset engineering methodology.
        </p>
        <div style="font-size: 12px; color: {THEME['accent_primary']}; font-weight: 600;">👉 Navigate to 8_About_Project</div>
    </div>
    """, unsafe_allow_html=True)
