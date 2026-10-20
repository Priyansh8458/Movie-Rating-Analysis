"""
Page 6: Trends Over Time — Longitudinal analysis of cinematic evolution across decades.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pyspark.sql import functions as F

st.set_page_config(page_title="Trends Over Time — CineScope", page_icon="📈", layout="wide")

from src.config import THEME
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import (
    apply_cinescope_theme,
    plot_movies_by_year,
    plot_dual_trends,
)
from src.analytics import get_yearly_trends
from src.utils import format_currency, format_number

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
    <h1 style="margin: 0; font-size: 30px;">Longitudinal Trends Over Time</h1>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
        Historical timeline tracking movie volume, budgets, revenues, and ratings across decades (1920 – 2020).
    </p>
</div>
""", unsafe_allow_html=True)

# Year Range and Metric Selectors
c_range, c_metric = st.columns([1.5, 1])
with c_range:
    selected_year_range = st.slider("Select Timeline Range", min_value=1920, max_value=2020, value=(1960, 2018))
with c_metric:
    metric_choice = st.selectbox(
        "Highlight Secondary Metric",
        ["Average Rating", "Total Box Office", "Average Revenue", "Average Budget"]
    )

# Compute Yearly Trends for the selected range with Spark
timeline_df = get_yearly_trends(df_clean, min_year=selected_year_range[0], max_year=selected_year_range[1])

if timeline_df.empty:
    st.warning("No data points available for the selected year range.")
    st.stop()

# Primary Chart: Movie Volume Over Time
st.markdown("### 🎬 Annual Feature Film Production Volume")
st.plotly_chart(plot_movies_by_year(timeline_df), use_container_width=True)

# Dual-Axis Trend: Volume vs Selected Metric
metric_column_map = {
    "Average Rating": ("avg_rating", "Average Rating (0-10)"),
    "Total Box Office": ("total_revenue", "Total Box Office ($ USD)"),
    "Average Revenue": ("avg_revenue", "Average Revenue ($ USD)"),
    "Average Budget": ("avg_budget", "Average Budget ($ USD)")
}
metric_col, metric_label = metric_column_map[metric_choice]

st.markdown(f"### ⚖️ Production Volume vs. {metric_choice}")
st.plotly_chart(
    plot_dual_trends(timeline_df, "movie_count", metric_col, "Movies Released", metric_label),
    use_container_width=True
)

# Financial Escalation: Budget vs Revenue Trends
st.markdown("### 💰 Budget & Revenue Evolution Over Time")
fig_fin = go.Figure()
fig_fin.add_trace(go.Scatter(
    x=timeline_df["release_year"],
    y=timeline_df["avg_revenue"],
    name="Avg Revenue per Film",
    line=dict(color=THEME["success"], width=2.5),
    hovertemplate="Year %{x}<br>Avg Rev: $%{y:,.0f}<extra></extra>"
))
fig_fin.add_trace(go.Scatter(
    x=timeline_df["release_year"],
    y=timeline_df["avg_budget"],
    name="Avg Budget per Film",
    line=dict(color=THEME["accent_primary"], width=2.5, dash="dash"),
    hovertemplate="Year %{x}<br>Avg Budget: $%{y:,.0f}<extra></extra>"
))
fig_fin.update_layout(
    title="Average Film Budget vs. Revenue by Release Year",
    xaxis_title="Release Year",
    yaxis_title="Amount ($ USD)"
)
st.plotly_chart(apply_cinescope_theme(fig_fin, height=450), use_container_width=True)

# Summary Table of Annual Metrics
st.markdown("### 📋 Annual Statistics Data Table")
display_timeline = timeline_df.copy()
display_timeline.columns = ["Release Year", "Movies Released", "Avg Rating", "Total Box Office", "Avg Revenue", "Avg Budget"]

st.dataframe(
    display_timeline.style.format({
        "Movies Released": "{:,.0f}",
        "Avg Rating": "{:.2f}",
        "Total Box Office": lambda x: format_currency(x),
        "Avg Revenue": lambda x: format_currency(x),
        "Avg Budget": lambda x: format_currency(x),
    }),
    use_container_width=True,
    height=350
)
