"""
Page 1: Movie Performance Overview Dashboard.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st

st.set_page_config(page_title="Overview — CineScope", page_icon="📊", layout="wide")

from src.config import THEME
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import (
    render_kpi_card_html,
    plot_movies_by_year,
    plot_genre_counts,
    plot_top_movies_bar,
    plot_ratings_histogram,
    plot_budget_vs_revenue,
)
from src.utils import format_currency, format_number, format_runtime
from src.analytics import get_top_movies_by_metric

inject_custom_css()

try:
    resources = get_pipeline_resources()
    data_report = resources["data_report"]
    kpis = resources["kpis"]
    yearly_df = resources["yearly_df"]
    genre_df = resources["genre_df"]
    insights = resources["insights"]
    df_clean = resources["df_clean"]
    render_sidebar_status(data_report)
except Exception as e:
    st.error(f"Failed to load pipeline data: {str(e)}")
    st.stop()

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 30px;">Movie Performance Overview</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
                Comprehensive analytics engine powered by Apache Spark, analyzing release patterns, box office performance, and audience reception.
            </p>
        </div>
        <div style="
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #10B981;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            color: #10B981;
            margin-top: 8px;
        ">
            ● Dataset Processed & Cached
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI Cards
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(render_kpi_card_html("Total Movies", format_number(kpis["total_movies"]), "Cleaned catalog titles", "🎬"), unsafe_allow_html=True)
with k2:
    st.markdown(render_kpi_card_html("Average Rating", f"{kpis['avg_rating']} / 10", "Audience consensus", "⭐", "secondary"), unsafe_allow_html=True)
with k3:
    st.markdown(render_kpi_card_html("Total Revenue", format_currency(kpis["total_revenue"]), "Worldwide box office", "💰"), unsafe_allow_html=True)
with k4:
    st.markdown(render_kpi_card_html("Average Revenue", format_currency(kpis["avg_revenue"]), "Per reporting title", "📈", "secondary"), unsafe_allow_html=True)
with k5:
    st.markdown(render_kpi_card_html("Average Budget", format_currency(kpis["avg_budget"]), "Production cost", "💼"), unsafe_allow_html=True)
with k6:
    st.markdown(render_kpi_card_html("Average Runtime", format_runtime(kpis["avg_runtime"]), "Minutes per feature", "⏱️", "secondary"), unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Dynamically Generated Key Insights
st.markdown("### 💡 Key Insights (Derived with Apache Spark)")
insight_cols = st.columns(len(insights))
for idx, col in enumerate(insight_cols):
    item = insights[idx]
    with col:
        st.markdown(f"""
        <div style="
            background: {THEME['bg_card']};
            border: 1px solid {THEME['border']};
            border-left: 3px solid {THEME['accent_primary'] if idx % 2 == 0 else THEME['accent_secondary']};
            border-radius: 10px;
            padding: 14px;
            height: 100%;
        ">
            <div style="font-size: 11px; text-transform: uppercase; color: {THEME['text_muted']}; font-weight: 600; letter-spacing: 0.05em;">
                {item['title']}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: {THEME['text_primary']}; margin: 4px 0;">
                {item['value']}
            </div>
            <div style="font-size: 12px; color: {THEME['text_secondary']}; line-height: 1.4;">
                {item['desc']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Visualizations Grid - Row 1: Releases over time & Genre Counts
c1, c2 = st.columns([1.1, 0.9])
with c1:
    st.plotly_chart(plot_movies_by_year(yearly_df), use_container_width=True)
with c2:
    st.plotly_chart(plot_genre_counts(genre_df.head(15)), use_container_width=True)

# Visualizations Grid - Row 2: Top Revenue & Rating Distribution & Budget vs Revenue
r2_c1, r2_c2 = st.columns([1, 1])
with r2_c1:
    top_revenue_df = get_top_movies_by_metric(df_clean, metric_col="revenue_num", n=10)
    st.plotly_chart(plot_top_movies_bar(top_revenue_df, "revenue_num", "Top 10 Movies by Worldwide Revenue", "Revenue ($ USD)"), use_container_width=True)

with r2_c2:
    ratings_sample_df = df_clean.filter("vote_avg > 0").select("vote_avg").limit(5000).toPandas()
    st.plotly_chart(plot_ratings_histogram(ratings_sample_df), use_container_width=True)

# Row 3: Budget vs Revenue
st.markdown("### 💵 Financial Performance: Budget vs. Revenue")
financial_sample_df = df_clean.filter("has_valid_financials").select(
    "title_clean", "release_year", "budget_num", "revenue_num", "profit", "roi", "vote_avg"
).limit(2500).toPandas()

st.plotly_chart(plot_budget_vs_revenue(financial_sample_df), use_container_width=True)
