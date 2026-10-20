"""
Page 3: Genre Analysis with exploded Spark relationships and multi-decade heatmaps.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyspark.sql import functions as F

st.set_page_config(page_title="Genre Analysis — CineScope", page_icon="🏷️", layout="wide")

from src.config import THEME
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import (
    apply_cinescope_theme,
    plot_genre_counts,
    plot_genre_heatmap,
    render_kpi_card_html,
)
from src.analytics import get_genre_metrics, get_genre_year_heatmap_data
from src.utils import format_currency, format_number, format_runtime

inject_custom_css()

try:
    resources = get_pipeline_resources()
    data_report = resources["data_report"]
    df_genres = resources["df_genres"]
    render_sidebar_status(data_report)
except Exception as e:
    st.error(f"Failed to load pipeline data: {str(e)}")
    st.stop()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 30px;">Genre Analytics & Market Dynamics</h1>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
        Exploded relational analysis normalized from nested JSON structures using PySpark SQL.
    </p>
</div>
""", unsafe_allow_html=True)

# Methodology Note Alert
st.markdown(f"""
<div style="
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid {THEME['accent_primary']};
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 20px;
    font-size: 13px;
    color: {THEME['text_primary']};
">
    💡 <strong>Methodology Note:</strong> Individual films frequently span multiple genres (e.g. <em>Toy Story</em> is Animation, Comedy, and Family). 
    In Apache Spark, each film is normalized using <code>F.explode(genres_list)</code>. Therefore, the sum of genre counts (<strong>{data_report['total_genre_exploded_records']:,} associations</strong>) 
    exceeds the unique catalog film count (<strong>{data_report['total_clean_records']:,} movies</strong>).
</div>
""", unsafe_allow_html=True)

# Controls
ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([1, 1, 1.5])
with ctrl_c1:
    min_films_threshold = st.slider("Min Movie Count per Genre", min_value=5, max_value=200, value=25, step=5)
with ctrl_c2:
    sort_genre_by = st.selectbox(
        "Sort Genre Table By",
        ["Movie Count", "Average Rating", "Total Revenue", "Average Revenue", "Average Budget", "Average Runtime"]
    )
with ctrl_c3:
    heatmap_years = st.slider("Heatmap Year Range", min_value=1960, max_value=2020, value=(1980, 2018))

# Compute Genre Metrics using Spark
genre_metrics_df = get_genre_metrics(df_genres, min_movies=min_films_threshold)

# Summary Cards
top_genre = genre_metrics_df.iloc[0] if not genre_metrics_df.empty else None
top_rated_genre = genre_metrics_df.sort_values("avg_rating", ascending=False).iloc[0] if not genre_metrics_df.empty else None
top_rev_genre = genre_metrics_df.sort_values("total_revenue", ascending=False).iloc[0] if not genre_metrics_df.empty else None
top_avg_rev_genre = genre_metrics_df.sort_values("avg_revenue", ascending=False).iloc[0] if not genre_metrics_df.empty else None

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(render_kpi_card_html("Top Volume Genre", top_genre["genre"] if top_genre is not None else "N/A", f"{format_number(top_genre['movie_count'])} titles" if top_genre is not None else "", "📊"), unsafe_allow_html=True)
with k2:
    st.markdown(render_kpi_card_html("Top Rated Genre", top_rated_genre["genre"] if top_rated_genre is not None else "N/A", f"{top_rated_genre['avg_rating']} avg rating" if top_rated_genre is not None else "", "⭐", "secondary"), unsafe_allow_html=True)
with k3:
    st.markdown(render_kpi_card_html("Top Grossing Genre", top_rev_genre["genre"] if top_rev_genre is not None else "N/A", f"{format_currency(top_rev_genre['total_revenue'])} total" if top_rev_genre is not None else "", "💰"), unsafe_allow_html=True)
with k4:
    st.markdown(render_kpi_card_html("Highest Avg Revenue", top_avg_rev_genre["genre"] if top_avg_rev_genre is not None else "N/A", f"{format_currency(top_avg_rev_genre['avg_revenue'])} / movie" if top_avg_rev_genre is not None else "", "🚀", "secondary"), unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Visualizations Row 1: Volume vs Average Rating
chart_c1, chart_c2 = st.columns(2)
with chart_c1:
    st.plotly_chart(plot_genre_counts(genre_metrics_df.head(15)), use_container_width=True)

with chart_c2:
    sorted_by_rating = genre_metrics_df.sort_values("avg_rating", ascending=True)
    fig_rating = go.Figure(go.Bar(
        x=sorted_by_rating["avg_rating"],
        y=sorted_by_rating["genre"],
        orientation="h",
        marker=dict(
            color=sorted_by_rating["avg_rating"],
            colorscale="Tealgrn",
            line=dict(color=THEME["border"], width=1)
        ),
        text=sorted_by_rating["avg_rating"].apply(lambda v: f"{v:.2f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Average Rating: %{x:.2f} / 10<extra></extra>"
    ))
    fig_rating.update_layout(title="Average Audience Rating by Genre", xaxis_title="Rating (0 - 10)", xaxis=dict(range=[0, 10]))
    st.plotly_chart(apply_cinescope_theme(fig_rating, height=500), use_container_width=True)

# Visualizations Row 2: Total Revenue vs Average Revenue
rev_c1, rev_c2 = st.columns(2)
with rev_c1:
    sorted_by_tot_rev = genre_metrics_df.sort_values("total_revenue", ascending=True)
    fig_tot_rev = go.Figure(go.Bar(
        x=sorted_by_tot_rev["total_revenue"],
        y=sorted_by_tot_rev["genre"],
        orientation="h",
        marker=dict(color="#8B5CF6", line=dict(color=THEME["border"], width=1)),
        text=sorted_by_tot_rev["total_revenue"].apply(lambda v: format_currency(v)),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Total Box Office: %{text}<extra></extra>"
    ))
    fig_tot_rev.update_layout(title="Total Worldwide Box Office by Genre", xaxis_title="Total Revenue ($ USD)")
    st.plotly_chart(apply_cinescope_theme(fig_tot_rev, height=480), use_container_width=True)

with rev_c2:
    sorted_by_avg_rev = genre_metrics_df.sort_values("avg_revenue", ascending=True)
    fig_avg_rev = go.Figure(go.Bar(
        x=sorted_by_avg_rev["avg_revenue"],
        y=sorted_by_avg_rev["genre"],
        orientation="h",
        marker=dict(color="#06B6D4", line=dict(color=THEME["border"], width=1)),
        text=sorted_by_avg_rev["avg_revenue"].apply(lambda v: format_currency(v)),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg Box Office: %{text}<extra></extra>"
    ))
    fig_avg_rev.update_layout(title="Average Worldwide Box Office per Film", xaxis_title="Average Revenue ($ USD)")
    st.plotly_chart(apply_cinescope_theme(fig_avg_rev, height=480), use_container_width=True)

# Heatmap: Genre production over decades
st.markdown("### 🔥 Genre Evolution & Production Intensity Across Decades")
heatmap_data = get_genre_year_heatmap_data(df_genres, min_year=heatmap_years[0], max_year=heatmap_years[1], top_n=15)
st.plotly_chart(plot_genre_heatmap(heatmap_data), use_container_width=True)

# Comprehensive Genre Ranking Table
st.markdown("### 📋 Genre Performance Benchmark Ranking")
metric_sort_col_map = {
    "Movie Count": "movie_count",
    "Average Rating": "avg_rating",
    "Total Revenue": "total_revenue",
    "Average Revenue": "avg_revenue",
    "Average Budget": "avg_budget",
    "Average Runtime": "avg_runtime",
}
sorted_table_df = genre_metrics_df.sort_values(metric_sort_col_map[sort_genre_by], ascending=False).copy()
sorted_table_df.columns = [
    "Genre", "Movie Count", "Avg Rating", "Total Box Office ($)", "Avg Revenue ($)", "Avg Budget ($)", "Avg Runtime (min)"
]

st.dataframe(
    sorted_table_df.style.format({
        "Movie Count": "{:,.0f}",
        "Avg Rating": "{:.2f}",
        "Total Box Office ($)": lambda x: format_currency(x),
        "Avg Revenue ($)": lambda x: format_currency(x),
        "Avg Budget ($)": lambda x: format_currency(x),
        "Avg Runtime (min)": lambda x: f"{x:.1f} m" if pd.notna(x) else "N/A"
    }),
    use_container_width=True
)
