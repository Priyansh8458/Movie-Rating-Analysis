"""
Page 7: Data Quality & Spark Processing — Distributed pipeline audit and interactive Spark SQL.
Demonstrates PySpark pipeline stages, schema enforcement, missing value audits,
and live interactive Spark SQL analytical queries.
"""
import sys, importlib
if "src.ui_helpers" in sys.modules:
    importlib.reload(sys.modules["src.ui_helpers"])

import streamlit as st
import pandas as pd
import time
from pyspark.sql import functions as F

st.set_page_config(page_title="Data Quality & Spark — CineScope", page_icon="🔬", layout="wide")

from src.config import THEME, MOVIES_METADATA_PATH
from src.ui_helpers import inject_custom_css, render_sidebar_status, get_pipeline_resources
from src.visualizations import render_kpi_card_html
from src.analytics import execute_spark_sql
from src.utils import format_number, format_currency

inject_custom_css()

try:
    resources = get_pipeline_resources()
    data_report = resources["data_report"]
    df_clean = resources["df_clean"]
    spark = resources["spark"]
    render_sidebar_status(data_report)
except Exception as e:
    st.error(f"Failed to load pipeline data: {str(e)}")
    st.stop()

st.markdown("""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="
            background: linear-gradient(135deg, #10B981 0%, #06B6D4 100%);
            color: #0B1020;
            font-size: 11px;
            font-weight: 800;
            padding: 3px 10px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        ">
            Pipeline Validation & Schema Audit
        </span>
        <span style="color: #94A3B8; font-size: 13px;">Distributed Catalyst Processing</span>
    </div>
    <h1 style="margin: 4px 0 0 0; font-size: 30px;">Data Quality & Apache Spark Processing</h1>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
        Transparent data engineering pipeline detailing PySpark ingestion, schema validation, data cleaning operations, and live Spark SQL query execution.
    </p>
</div>
""", unsafe_allow_html=True)

# Lab Metrics Row
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(render_kpi_card_html("Raw Records", format_number(data_report["total_raw_records"]), "Input CSV rows", "📥"), unsafe_allow_html=True)
with m2:
    st.markdown(render_kpi_card_html("Cleaned Movies", format_number(data_report["total_clean_records"]), "Validated records", "✅", "secondary"), unsafe_allow_html=True)
with m3:
    st.markdown(render_kpi_card_html("Corrupt Rows", format_number(data_report["corrupted_records_excluded"]), "Shifted ID lines excluded", "⚠️"), unsafe_allow_html=True)
with m4:
    st.markdown(render_kpi_card_html("Duplicate IDs", format_number(data_report["duplicate_ids_count"]), "Duplicated movie IDs", "🔁", "secondary"), unsafe_allow_html=True)
with m5:
    st.markdown(render_kpi_card_html("Exploded Relations", format_number(data_report["total_genre_exploded_records"]), "Movie-Genre records", "🔗"), unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Main Content Tabs
tab_summary, tab_schema, tab_audit, tab_sql = st.tabs([
    "⚡ Spark Processing Summary",
    "📋 Spark Schema & Types",
    "🔍 Missing & Invalid Values Audit",
    "💻 Live Spark SQL Query Runner"
])

with tab_summary:
    st.markdown("### ⚙️ Apache Spark Execution Environment")
    env_c1, env_c2 = st.columns(2)
    with env_c1:
        st.markdown(f"""
        <div class="cinescope-card">
            <h4 style="margin: 0 0 10px 0; color: {THEME['accent_primary']};">Engine Specifications</h4>
            <table style="width: 100%; font-size: 13px; line-height: 2;">
                <tr><td style="color: {THEME['text_secondary']};">Spark Version:</td><td><strong>{spark.version}</strong></td></tr>
                <tr><td style="color: {THEME['text_secondary']};">Master URL:</td><td><code>{spark.sparkContext.master}</code> (Multi-core local)</td></tr>
                <tr><td style="color: {THEME['text_secondary']};">App Name:</td><td>{spark.sparkContext.appName}</td></tr>
                <tr><td style="color: {THEME['text_secondary']};">Default Shuffle Partitions:</td><td><code>8</code> (Optimized for interactive UI)</td></tr>
                <tr><td style="color: {THEME['text_secondary']};">Active Storage Level:</td><td><code>MEMORY_AND_DISK</code> (Persisted)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with env_c2:
        st.markdown(f"""
        <div class="cinescope-card">
            <h4 style="margin: 0 0 10px 0; color: {THEME['accent_secondary']};">Dataset Characteristics</h4>
            <table style="width: 100%; font-size: 13px; line-height: 2;">
                <tr><td style="color: {THEME['text_secondary']};">Source File:</td><td><code>{MOVIES_METADATA_PATH.name}</code></td></tr>
                <tr><td style="color: {THEME['text_secondary']};">File Size:</td><td>34.45 MB (Uncompressed CSV)</td></tr>
                <tr><td style="color: {THEME['text_secondary']};">Reader Options:</td><td><code>header=true, multiLine=true, escape="\""</code></td></tr>
                <tr><td style="color: {THEME['text_secondary']};">Registered Temp Views:</td><td><code>movies_clean</code>, <code>movies_genres</code>, <code>movies_financials</code></td></tr>
                <tr><td style="color: {THEME['text_secondary']};">Processing Paradigm:</td><td>Declarative PySpark DataFrame + Spark SQL</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🛠️ Spark Preprocessing & Transformation Pipeline")
    for idx, step in enumerate(data_report["spark_pipeline_steps"], start=1):
        st.markdown(f"""
        <div style="
            background: {THEME['bg_card']};
            border-left: 3px solid {THEME['accent_primary']};
            border-radius: 4px;
            padding: 8px 14px;
            margin-bottom: 8px;
            font-size: 13px;
        ">
            <strong>Stage {idx}:</strong> {step}
        </div>
        """, unsafe_allow_html=True)

with tab_schema:
    st.markdown("### 📑 PySpark Enforced Schema vs. Raw Source Fields")
    st.markdown("The schema below shows data types enforced during ingestion and cleaning:")
    
    schema_rows = []
    for field in df_clean.schema.fields:
        schema_rows.append({
            "Column Name": field.name,
            "Spark Data Type": str(field.dataType),
            "Nullable": str(field.nullable),
            "Description / Role": "Derived / Validated attribute" if field.name in ["profit", "roi", "release_year", "genres_list", "has_valid_financials"] else "Source attribute"
        })
    st.dataframe(pd.DataFrame(schema_rows), use_container_width=True, height=450)

with tab_audit:
    st.markdown("### 🔍 Missingness, Zero Values, and Anomaly Audit")
    st.markdown("In real-world data engineering, records are not silently dropped. Each field's quality characteristics are measured:")

    audit_metrics = [
        {"Category": "Missing / Unparseable Release Dates", "Count": data_report["missing_release_dates"], "Percentage": f"{(data_report['missing_release_dates'] / data_report['total_clean_records']) * 100:.2f}%", "Impact": "Excluded from timeline charts"},
        {"Category": "Unreported / Zero Budgets", "Count": data_report["missing_or_zero_budget"], "Percentage": f"{(data_report['missing_or_zero_budget'] / data_report['total_clean_records']) * 100:.2f}%", "Impact": "Preserved in catalog; excluded from ROI and budget averages"},
        {"Category": "Unreported / Zero Revenues", "Count": data_report["missing_or_zero_revenue"], "Percentage": f"{(data_report['missing_or_zero_revenue'] / data_report['total_clean_records']) * 100:.2f}%", "Impact": "Preserved in catalog; excluded from box office averages"},
        {"Category": "Missing / Zero Runtime", "Count": data_report["missing_or_zero_runtime"], "Percentage": f"{(data_report['missing_or_zero_runtime'] / data_report['total_clean_records']) * 100:.2f}%", "Impact": "Treated as N/A in runtime metrics"},
        {"Category": "Zero Audience Votes / Unrated", "Count": data_report["missing_or_zero_rating"], "Percentage": f"{(data_report['missing_or_zero_rating'] / data_report['total_clean_records']) * 100:.2f}%", "Impact": "Excluded when computing audience consensus"},
        {"Category": "Complete Commercial Records (Budget & Rev > 0)", "Count": data_report["records_with_both_budget_revenue"], "Percentage": f"{(data_report['records_with_both_budget_revenue'] / data_report['total_clean_records']) * 100:.2f}%", "Impact": "Used for Profit, ROI, and commercial break-even modeling"},
    ]
    st.dataframe(pd.DataFrame(audit_metrics), use_container_width=True)

with tab_sql:
    st.markdown("### 💻 Live Apache Spark SQL Query Runner")
    st.markdown(
        "Demonstrate genuine distributed query processing. Choose an example lab query or type a custom query against "
        "<code>movies_clean</code>, <code>movies_genres</code>, or <code>movies_financials</code>:"
    )

    preset_queries = {
        "Top 10 Movies by Revenue (SQL)": (
            "SELECT title_clean AS Title, release_year AS Year, genres_display AS Genres, revenue_num AS Revenue_USD "
            "FROM movies_clean "
            "WHERE revenue_num > 0 "
            "ORDER BY revenue_num DESC LIMIT 10"
        ),
        "Average Rating and Revenue by Genre (SQL)": (
            "SELECT genre, COUNT(*) AS movie_count, ROUND(AVG(vote_avg), 2) AS avg_rating, "
            "ROUND(AVG(revenue_num), 0) AS avg_revenue "
            "FROM movies_genres "
            "GROUP BY genre HAVING COUNT(*) >= 50 "
            "ORDER BY avg_rating DESC"
        ),
        "Annual Film Production and Box Office Totals (SQL)": (
            "SELECT release_year AS Year, COUNT(*) AS total_films, "
            "SUM(revenue_num) AS total_box_office, ROUND(AVG(vote_avg), 2) AS avg_rating "
            "FROM movies_clean "
            "WHERE release_year >= 2000 AND release_year <= 2017 "
            "GROUP BY release_year ORDER BY release_year DESC"
        ),
        "Most Profitable Films with Positive Budgets (SQL)": (
            "SELECT title_clean AS Title, budget_num AS Budget, revenue_num AS Revenue, "
            "profit AS Estimated_Profit, ROUND(roi, 1) AS ROI_Percent "
            "FROM movies_financials "
            "WHERE budget_num >= 5000000 "
            "ORDER BY profit DESC LIMIT 10"
        )
    }

    selected_preset = st.selectbox("Select Benchmark Analytical Query:", list(preset_queries.keys()))
    default_sql = preset_queries[selected_preset]

    query_input = st.text_area("SQL Query Editor (Spark SQL syntax):", default_sql, height=120)

    if st.button("🚀 Execute Spark SQL Query", use_container_width=True):
        try:
            start_time = time.time()
            result_df = execute_spark_sql(spark, query_input)
            exec_time = time.time() - start_time

            st.success(f"Query executed successfully via Spark SQL engine in **{exec_time:.3f} seconds** ({len(result_df)} rows returned).")
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"Spark SQL Execution Error:\n\n{str(e)}")
