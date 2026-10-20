"""
UI helper functions for Streamlit application styling, persistent sidebar,
and cached data pipeline access.
"""
import streamlit as st
from typing import Tuple, Dict, Any

from src.config import THEME, MOVIES_METADATA_PATH
from src.spark_session import get_spark_session
from src.data_loader import load_raw_movies_data
from src.preprocessing import clean_movies_dataframe
from src.analytics import get_kpi_summary, get_yearly_trends, get_genre_metrics, generate_key_insights


def inject_custom_css():
    """Inject polished CineScope dark cinematic CSS styles into Streamlit."""
    st.markdown(f"""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {THEME['text_primary']};
    }}

    .stApp {{
        background-color: {THEME['bg_main']};
    }}

    /* Main Container Padding */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
    }}

    /* Headers */
    h1, h2, h3, h4 {{
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: {THEME['text_primary']};
    }}

    h1 {{
        font-size: 2.2rem;
        background: linear-gradient(120deg, #FFFFFF 0%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }}

    /* Sidebar Styling & Compact Header */
    section[data-testid="stSidebar"] {{
        background-color: {THEME['bg_card']} !important;
        border-right: 1px solid {THEME['border']} !important;
    }}

    /* Eliminate empty top gap in sidebar */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
        padding-top: 0.5rem !important;
        display: flex !important;
        flex-direction: column !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
        padding-top: 0.25rem !important;
        padding-bottom: 0 !important;
        min-height: unset !important;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }}

    /* Shift Brand Header to top above navigation */
    #cinescope-sidebar-brand {{
        order: -10 !important;
        width: 100% !important;
        margin-top: 0 !important;
        padding-top: 0.25rem !important;
    }}

    /* Sidebar Page Navigation Menu */
    [data-testid="stSidebarNav"] {{
        order: -5 !important;
        padding-top: 0.6rem !important;
        padding-bottom: 0.8rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        margin-bottom: 0.75rem !important;
    }}

    /* Style entrypoint link if rendered as 'app' */
    [data-testid="stSidebarNav"] li:first-child a span {{
        font-weight: 600;
    }}

    /* Status card below navigation */
    .cinescope-status-box {{
        order: 5 !important;
    }}

    /* Card Containers */
    .cinescope-card {{
        background: linear-gradient(145deg, {THEME['bg_card']} 0%, #111728 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.35rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.25rem;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s ease, border-color 0.25s ease;
    }}

    .cinescope-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(139, 92, 246, 0.45);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
    }}

    /* Dataframe Container */
    div[data-testid="stDataFrame"] {{
        border: 1px solid {THEME['border']};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* Custom Streamlit Metric Overrides */
    div[data-testid="stMetricValue"] {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {THEME['text_primary']};
    }}

    div[data-testid="stMetricLabel"] {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {THEME['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Streamlit Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {THEME['accent_primary']} 0%, #6366F1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, {THEME['accent_hover']} 0%, #4F46E5 100%);
        box-shadow: 0 6px 18px rgba(139, 92, 246, 0.5);
        transform: translateY(-1px);
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {THEME['bg_card']};
        padding: 6px;
        border-radius: 10px;
        border: 1px solid {THEME['border']};
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px;
        color: {THEME['text_secondary']};
        font-weight: 500;
        padding: 8px 16px;
    }}

    .stTabs [aria-selected="true"] {{
        background: {THEME['bg_card_secondary']} !important;
        color: {THEME['accent_secondary']} !important;
        font-weight: 600;
    }}

    /* Scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {THEME['bg_main']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {THEME['border']};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {THEME['accent_primary']};
    }}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_status(data_report: Dict[str, Any]):
    """Render consistent branding at the top of the sidebar, followed by navigation and Spark engine status."""
    with st.sidebar:
        # Brand Title Header — Shifted to the VERY TOP of the sidebar
        st.markdown(f"""
        <div id="cinescope-sidebar-brand" style="text-align: center; padding-bottom: 14px; margin-bottom: 12px; border-bottom: 1px solid {THEME['border']};">
            <div style="font-size: 34px; margin-bottom: 4px; filter: drop-shadow(0 4px 12px rgba(139, 92, 246, 0.45));">🎬</div>
            <div style="font-size: 24px; font-weight: 800; font-family: 'Outfit', sans-serif; letter-spacing: -0.02em; background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2;">
                CineScope
            </div>
            <div style="font-size: 11px; font-weight: 700; color: {THEME['accent_secondary']}; text-transform: uppercase; letter-spacing: 0.14em; margin-top: 3px;">
                Movie Performance Analytics
            </div>
            <div style="font-size: 10px; color: {THEME['text_muted']}; margin-top: 4px; font-weight: 500; letter-spacing: 0.04em;">
                Enterprise Big Data Intelligence
            </div>
        </div>

        <script>
            (function() {{
                function moveBrandToTop() {{
                    var brand = document.getElementById('cinescope-sidebar-brand');
                    var nav = document.querySelector('[data-testid="stSidebarNav"]');
                    if (brand && nav && brand.nextElementSibling !== nav) {{
                        nav.parentNode.insertBefore(brand, nav);
                    }}
                }}
                moveBrandToTop();
                setTimeout(moveBrandToTop, 50);
                setTimeout(moveBrandToTop, 200);
            }})();
        </script>
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1' height='1'/>"
             style="display:none;"
             onload="
                var brand = document.getElementById('cinescope-sidebar-brand');
                var nav = document.querySelector('[data-testid=\\'stSidebarNav\\']');
                if (brand && nav && brand.nextElementSibling !== nav) {{
                    nav.parentNode.insertBefore(brand, nav);
                }}
             "
             onerror="
                var brand = document.getElementById('cinescope-sidebar-brand');
                var nav = document.querySelector('[data-testid=\\'stSidebarNav\\']');
                if (brand && nav && brand.nextElementSibling !== nav) {{
                    nav.parentNode.insertBefore(brand, nav);
                }}
             "
        />
        """, unsafe_allow_html=True)

        # Status Badge Container
        total_clean = data_report.get("total_clean_records", 0)
        file_name = MOVIES_METADATA_PATH.name

        st.markdown(f"""
        <div class="cinescope-status-box" style="
            background: linear-gradient(145deg, {THEME['bg_card_secondary']} 0%, #151D2F 100%);
            border: 1px solid {THEME['border']};
            border-radius: 10px;
            padding: 13px;
            margin-bottom: 15px;
            font-size: 12px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px;">
                <span style="color: {THEME['text_secondary']};">Engine:</span>
                <span style="color: {THEME['accent_secondary']}; font-weight: 600;">⚡ Apache Spark 3.5</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px;">
                <span style="color: {THEME['text_secondary']};">Architecture:</span>
                <span style="color: {THEME['text_primary']};">Local Master [*]</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px;">
                <span style="color: {THEME['text_secondary']};">Dataset:</span>
                <span style="color: {THEME['text_primary']}; font-family: monospace;">{file_name}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: {THEME['text_secondary']};">Status:</span>
                <span style="color: {THEME['success']}; font-weight: 600;">🟢 {total_clean:,} Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Reload & Recache Data", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

        st.markdown(f"""
        <div style="margin-top: 20px; padding-top: 10px; border-top: 1px solid {THEME['border']}; font-size: 11px; color: {THEME['text_muted']}; text-align: center;">
            CineScope v1.2.0 • Apache Spark & Streamlit
        </div>
        """, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_pipeline_resources():
    """Singleton cached pipeline resource for the entire application.
    
    Initializes SparkSession once, loads movies_metadata.csv, executes the
    preprocessing pipeline, caches DataFrames in Spark memory, and computes
    core analytics dataframes.
    """
    spark = get_spark_session()
    raw_df = load_raw_movies_data(spark)
    df_clean, df_genres, data_report = clean_movies_dataframe(raw_df)

    # Persist cleaned DataFrames in Spark memory for high query performance
    df_clean.persist()
    df_genres.persist()

    # Pre-calculate baseline summaries for instantaneous page loads
    kpis = get_kpi_summary(df_clean)
    yearly_df = get_yearly_trends(df_clean, min_year=1960, max_year=2020)
    genre_df = get_genre_metrics(df_genres, min_movies=10)
    insights = generate_key_insights(df_clean, df_genres)

    return {
        "spark": spark,
        "df_clean": df_clean,
        "df_genres": df_genres,
        "data_report": data_report,
        "kpis": kpis,
        "yearly_df": yearly_df,
        "genre_df": genre_df,
        "insights": insights,
    }
