"""
Page 4: Revenue & Budget Analysis — Financial modeling, profit, and ROI distributions.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyspark.sql import functions as F

st.set_page_config(page_title="Revenue & Budget — CineScope", page_icon="💰", layout="wide")

from src.config import THEME, DEFAULT_MIN_BUDGET_ROI
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import (
    apply_cinescope_theme,
    render_kpi_card_html,
    plot_top_movies_bar,
    plot_budget_vs_revenue,
)
from src.analytics import get_financial_breakdown
from src.utils import format_currency, format_number, format_percentage, format_rating

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
    <h1 style="margin: 0; font-size: 30px;">Revenue & Budget Analytics</h1>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
        Empirical financial modeling evaluating production expenditures, gross box office receipts, estimated profit, and Return on Investment (ROI).
    </p>
</div>
""", unsafe_allow_html=True)

# ROI Outlier Control Slider
col_ctrl1, col_ctrl2 = st.columns([2, 1])
with col_ctrl1:
    min_budget_roi = st.slider(
        "Threshold: Minimum Budget for ROI Leaderboard ($ Millions)",
        min_value=0.1,
        max_value=20.0,
        value=1.0,
        step=0.5,
        help="Micro-budget films (e.g. $10,000 budget making $1M) create astronomical ROI percentages that distort commercial comparisons. Setting a minimum budget filters realistic studio releases."
    )
with col_ctrl2:
    st.info(f"Filtering movies with budget ≥ **${min_budget_roi:.1f}M** for ROI rankings.")

# Compute financial models with Spark
financials = get_financial_breakdown(df_clean, min_budget_for_roi=min_budget_roi * 1_000_000)

# Financial KPI Cards
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(render_kpi_card_html("Commercial Films", format_number(financials["count"]), "Both budget & rev > 0", "🎬"), unsafe_allow_html=True)
with k2:
    st.markdown(render_kpi_card_html("Total Box Office", format_currency(financials["total_revenue"]), "Aggregated revenue", "💰", "secondary"), unsafe_allow_html=True)
with k3:
    st.markdown(render_kpi_card_html("Total Production", format_currency(financials["total_budget"]), "Aggregated budget", "💼"), unsafe_allow_html=True)
with k4:
    st.markdown(render_kpi_card_html("Total Est. Profit", format_currency(financials["total_profit"]), "Revenue minus budget", "📈", "secondary"), unsafe_allow_html=True)
with k5:
    st.markdown(render_kpi_card_html("Avg Box Office", format_currency(financials["avg_revenue"]), "Per commercial title", "💵"), unsafe_allow_html=True)
with k6:
    st.markdown(render_kpi_card_html("Avg Budget", format_currency(financials["avg_budget"]), "Per commercial title", "📊", "secondary"), unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Scatter plot: Budget vs Revenue
st.markdown("### 📈 Production Budget vs. Worldwide Gross Box Office")
st.plotly_chart(plot_budget_vs_revenue(financials["scatter_df"]), use_container_width=True)

# Visualizations Row: Top Revenue vs Top Profit
col_rev, col_prof = st.columns(2)
with col_rev:
    st.plotly_chart(
        plot_top_movies_bar(financials["top_revenue"], "revenue_num", "Top 10 Highest Grossing Movies", "Revenue ($ USD)"),
        use_container_width=True
    )
with col_prof:
    st.plotly_chart(
        plot_top_movies_bar(financials["top_profit"], "profit", "Top 10 Most Profitable Movies (Est.)", "Profit ($ USD)"),
        use_container_width=True
    )

# Top ROI Leaderboard
st.markdown("### 🚀 Top 10 Return on Investment (ROI) Champions")
st.markdown(f"*Computed as: <code>(Revenue - Budget) / Budget × 100</code> for films with budget ≥ ${min_budget_roi:.1f}M*")

top_roi_df = financials["top_roi"].copy()
if not top_roi_df.empty:
    fig_roi = go.Figure(go.Bar(
        x=top_roi_df["roi"],
        y=top_roi_df["title_clean"],
        orientation="h",
        text=top_roi_df["roi"].apply(lambda v: format_percentage(v)),
        textposition="outside",
        marker=dict(
            color=top_roi_df["roi"],
            colorscale="Plasma",
            line=dict(color=THEME["border"], width=1)
        ),
        hovertemplate="<b>%{y}</b><br>ROI: %{text}<extra></extra>"
    ))
    fig_roi.update_layout(title="Top ROI Champions", xaxis_title="ROI Percentage (%)")
    st.plotly_chart(apply_cinescope_theme(fig_roi, height=450), use_container_width=True)

# Section: Critical Disconnects
st.markdown("### 🎭 Critical & Commercial Disconnects")
tab1, tab2 = st.tabs(["💥 Box Office Hits, Critical Misses", "💎 Cult Classics & Underrated Gems"])

with tab1:
    st.markdown("Movies in the **top 10% of revenue** that scored **below 6.0 / 10** from audiences (Commercial juggernauts panned by critics/viewers):")
    hits_misses = financials["box_office_misses"]
    if not hits_misses.empty:
        display_hm = hits_misses[["title_clean", "release_year", "revenue_num", "budget_num", "vote_avg", "vote_cnt"]].copy()
        display_hm.columns = ["Title", "Year", "Revenue", "Budget", "Audience Rating", "Votes"]
        st.dataframe(
            display_hm.style.format({
                "Revenue": lambda x: format_currency(x),
                "Budget": lambda x: format_currency(x),
                "Audience Rating": "{:.1f} / 10",
                "Votes": "{:,.0f}"
            }),
            use_container_width=True
        )
    else:
        st.info("No records match this criteria.")

with tab2:
    st.markdown("Movies scoring **7.8+ rating** with substantial vote count (**≥300 votes**) but modest box office revenue (**< $50M**):")
    cult = financials["cult_classics"]
    if not cult.empty:
        display_cult = cult[["title_clean", "release_year", "vote_avg", "vote_cnt", "revenue_num", "budget_num"]].copy()
        display_cult.columns = ["Title", "Year", "Audience Rating", "Votes", "Revenue", "Budget"]
        st.dataframe(
            display_cult.style.format({
                "Audience Rating": "{:.1f} / 10",
                "Votes": "{:,.0f}",
                "Revenue": lambda x: format_currency(x),
                "Budget": lambda x: format_currency(x)
            }),
            use_container_width=True
        )
    else:
        st.info("No records match this criteria.")
