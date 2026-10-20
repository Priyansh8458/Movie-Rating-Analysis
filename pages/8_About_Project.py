"""
Page 8: About Project — Project documentation, architecture diagrams, and system specifications.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st

st.set_page_config(page_title="About Project — CineScope", page_icon="ℹ️", layout="wide")

from src.config import THEME, MOVIES_METADATA_PATH
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources

inject_custom_css()

try:
    resources = get_pipeline_resources()
    data_report = resources["data_report"]
    render_sidebar_status(data_report)
except Exception as e:
    st.error(f"Failed to load pipeline data: {str(e)}")
    st.stop()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 30px;">About CineScope Analytics</h1>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
        Enterprise Big Data Architecture — Comprehensive System Documentation & Distributed Engineering Specifications.
    </p>
</div>
""", unsafe_allow_html=True)

# Project Overview Card
st.markdown(f"""
<div class="cinescope-card">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; font-size: 13px;">
        <div>
            <div style="color: {THEME['text_muted']}; text-transform: uppercase; font-size: 11px; font-weight: 600;">Platform Title</div>
            <div style="color: {THEME['text_primary']}; font-weight: 700; font-size: 15px; margin-top: 2px;">CineScope — Movie Performance Analytics</div>
        </div>
        <div>
            <div style="color: {THEME['text_muted']}; text-transform: uppercase; font-size: 11px; font-weight: 600;">Architecture Pattern</div>
            <div style="color: {THEME['accent_secondary']}; font-weight: 600; font-size: 15px; margin-top: 2px;">Distributed PySpark & Streamlit Engine</div>
        </div>
        <div>
            <div style="color: {THEME['text_muted']}; text-transform: uppercase; font-size: 11px; font-weight: 600;">Data Processing Engine</div>
            <div style="color: {THEME['text_primary']}; font-weight: 600; font-size: 15px; margin-top: 2px;">Apache Spark (PySpark DataFrame API)</div>
        </div>
        <div>
            <div style="color: {THEME['text_muted']}; text-transform: uppercase; font-size: 11px; font-weight: 600;">Query Engine</div>
            <div style="color: {THEME['text_primary']}; font-weight: 600; font-size: 15px; margin-top: 2px;">PySpark SQL Temporary Views</div>
        </div>
        <div>
            <div style="color: {THEME['text_muted']}; text-transform: uppercase; font-size: 11px; font-weight: 600;">Frontend UI</div>
            <div style="color: {THEME['text_primary']}; font-weight: 600; font-size: 15px; margin-top: 2px;">Streamlit (Python 3.14)</div>
        </div>
        <div>
            <div style="color: {THEME['text_muted']}; text-transform: uppercase; font-size: 11px; font-weight: 600;">Interactive Visuals</div>
            <div style="color: {THEME['text_primary']}; font-weight: 600; font-size: 15px; margin-top: 2px;">Plotly Express & Graph Objects</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Architecture Diagram
st.markdown("### 🏛️ System Architecture & Dataflow Pipeline")
st.markdown(f"""
<div style="
    background: {THEME['bg_card']};
    border: 1px solid {THEME['border']};
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
">
    <div style="display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div style="background: {THEME['bg_card_secondary']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 14px; flex: 1; min-width: 180px; text-align: center;">
                <div style="font-size: 24px;">📁</div>
                <div style="font-weight: 700; color: {THEME['text_primary']}; margin-top: 4px;">Data Layer</div>
                <div style="font-size: 12px; color: {THEME['text_secondary']};"><code>movies_metadata.csv</code><br>45,466 Raw Records</div>
            </div>
            <div style="color: {THEME['accent_primary']}; font-size: 22px; font-weight: 700;">➔</div>
            <div style="background: {THEME['bg_card_secondary']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 14px; flex: 1.2; min-width: 220px; text-align: center;">
                <div style="font-size: 24px;">⚡</div>
                <div style="font-weight: 700; color: {THEME['accent_primary']}; margin-top: 4px;">Apache Spark Engine</div>
                <div style="font-size: 12px; color: {THEME['text_secondary']};">multiLine CSV Reader<br>Schema Casting & Regex UDFs<br>Exploded Relational Views</div>
            </div>
            <div style="color: {THEME['accent_secondary']}; font-size: 22px; font-weight: 700;">➔</div>
            <div style="background: {THEME['bg_card_secondary']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 14px; flex: 1.2; min-width: 220px; text-align: center;">
                <div style="font-size: 24px;">🧠</div>
                <div style="font-weight: 700; color: {THEME['accent_secondary']}; margin-top: 4px;">PySpark SQL & Aggregations</div>
                <div style="font-size: 12px; color: {THEME['text_secondary']};">In-Memory Cached DataFrames<br>Distributed Aggregations<br>SQL Analytical Queries</div>
            </div>
            <div style="color: {THEME['success']}; font-size: 22px; font-weight: 700;">➔</div>
            <div style="background: {THEME['bg_card_secondary']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 14px; flex: 1; min-width: 180px; text-align: center;">
                <div style="font-size: 24px;">🖥️</div>
                <div style="font-weight: 700; color: {THEME['success']}; margin-top: 4px;">Streamlit Frontend</div>
                <div style="font-size: 12px; color: {THEME['text_secondary']};">Multipage Dark Dashboard<br>Plotly Charts & Filters<br>Real TMDB Posters</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Analytical Features & Modules
st.markdown("### 🎯 Core Analytical Modules & Engineering Highlights")
f1, f2 = st.columns(2)

with f1:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 10px 0; color: {THEME['accent_primary']};">Big Data Engineering Features</h4>
        <ul style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.8; margin: 0; padding-left: 20px;">
            <li><strong>Distributed Processing:</strong> Uses PySpark DataFrames instead of loading 45K records into unmanaged memory.</li>
            <li><strong>Resilient Ingestion:</strong> Handles corrupted multi-line rows and escaped quotes using PySpark CSV reader options.</li>
            <li><strong>Data Normalization:</strong> Parses JSON string arrays into PySpark String Arrays and explodes them into individual genre observations.</li>
            <li><strong>Safe Metric Derivation:</strong> Mathematical models for Profit and ROI that strictly protect against division by zero and unreported budget distortion.</li>
            <li><strong>Interactive Spark SQL:</strong> Exposes live SQL execution against in-memory registered views.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div class="cinescope-card">
        <h4 style="margin: 0 0 10px 0; color: {THEME['accent_secondary']};">Business & Cinema Intelligence Insights</h4>
        <ul style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.8; margin: 0; padding-left: 20px;">
            <li><strong>Longitudinal Trends:</strong> Identifies the transition from classical studio releases to high-budget modern franchise cinema.</li>
            <li><strong>Commercial vs. Critical Gems:</strong> Highlights disconnects where blockbusters failed with critics or high-rated titles earned modest revenue.</li>
            <li><strong>Genre Dynamics:</strong> Compares genre production volume against average commercial revenue and critical consensus scores.</li>
            <li><strong>Asset Integration:</strong> Directly renders genuine movie posters via TMDB image CDN using real dataset paths with dynamic fallback.</li>
            <li><strong>Statistical Rigor:</strong> Integrates minimum vote thresholds to eliminate bias from single-vote 10/10 entries.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Limitations & Future Work
st.markdown("### ⚠️ Dataset Limitations & Practical Engineering Notes")
st.markdown(f"""
<div class="cinescope-card">
    <ol style="font-size: 13px; color: {THEME['text_secondary']}; line-height: 1.8; margin: 0; padding-left: 20px;">
        <li><strong>Unreported Financial Data:</strong> In Hollywood records, unrecorded budgets or revenues are frequently stored as 0. CineScope treats these as missing values rather than true $0 productions to avoid skewing averages.</li>
        <li><strong>Historical Inflation:</strong> Raw box office figures are nominal amounts from the release year. Adjusting for real-dollar inflation would further refine multi-decade revenue comparisons.</li>
        <li><strong>Cluster Scalability:</strong> Spark runs in high-throughput local master mode (<code>local[*]</code>), leveraging multi-core parallel worker threads. The exact same PySpark codebase seamlessly deploys to multi-node AWS EMR or Databricks clusters without code changes.</li>
    </ol>
</div>
""", unsafe_allow_html=True)
