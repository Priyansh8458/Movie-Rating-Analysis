"""
Visualization module providing Plotly charts and custom HTML components
styled for CineScope's dark cinematic theme.
"""
from typing import Dict, Any, Optional
import textwrap
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import THEME
from src.utils import (
    format_currency,
    format_number,
    format_runtime,
    format_percentage,
    format_rating,
    resolve_movie_poster_url
)


def apply_cinescope_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    """Apply CineScope dark cinematic palette, fonts, and clean grids to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=THEME["bg_card"],
        plot_bgcolor=THEME["bg_card"],
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color=THEME["text_primary"], size=12),
        title=dict(font=dict(size=16, color=THEME["text_primary"]), x=0.02, y=0.96),
        margin=dict(l=40, r=30, t=50, b=40),
        height=height,
        colorway=THEME["chart_palette"],
        hoverlabel=dict(
            bgcolor=THEME["bg_main"],
            bordercolor=THEME["accent_primary"],
            font=dict(color=THEME["text_primary"], size=12)
        ),
        xaxis=dict(
            gridcolor=THEME["bg_card_secondary"],
            linecolor=THEME["border"],
            zerolinecolor=THEME["border"],
            tickfont=dict(color=THEME["text_secondary"]),
            title_font=dict(color=THEME["text_secondary"], size=12)
        ),
        yaxis=dict(
            gridcolor=THEME["bg_card_secondary"],
            linecolor=THEME["border"],
            zerolinecolor=THEME["border"],
            tickfont=dict(color=THEME["text_secondary"]),
            title_font=dict(color=THEME["text_secondary"], size=12)
        )
    )
    return fig


def render_kpi_card_html(title: str, value: str, subtitle: str = "", icon: str = "🎬", accent: str = "primary") -> str:
    """Generate high-aesthetic HTML card for KPI overview metrics."""
    accent_color = THEME["accent_primary"] if accent == "primary" else THEME["accent_secondary"]
    html_card = f"""<div style="background: linear-gradient(135deg, {THEME['bg_card']} 0%, {THEME['bg_card_secondary']} 100%); border: 1px solid {THEME['border']}; border-top: 3px solid {accent_color}; border-radius: 12px; padding: 20px 18px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35); margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<span style="font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: {THEME['text_secondary']};">{title}</span>
<span style="font-size: 20px; opacity: 0.85;">{icon}</span>
</div>
<div style="font-size: 28px; font-weight: 700; color: {THEME['text_primary']}; letter-spacing: -0.02em; margin-bottom: 4px;">{value}</div>
<div style="font-size: 12px; color: {THEME['text_muted']};">{subtitle}</div>
</div>"""
    return html_card


def plot_movies_by_year(yearly_df: pd.DataFrame) -> go.Figure:
    """Interactive line and area chart of movie counts over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly_df["release_year"],
        y=yearly_df["movie_count"],
        mode="lines+markers",
        name="Releases",
        line=dict(color=THEME["accent_primary"], width=3, shape="spline"),
        marker=dict(size=5, color=THEME["accent_secondary"]),
        fill="tozeroy",
        fillcolor="rgba(139, 92, 246, 0.15)",
        hovertemplate="<b>Year %{x}</b><br>Total Movies: %{y:,}<extra></extra>"
    ))
    fig.update_layout(
        title="Movies Released by Year",
        xaxis_title="Release Year",
        yaxis_title="Number of Movies",
    )
    return apply_cinescope_theme(fig)


def plot_genre_counts(genre_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart for movie count by genre."""
    sorted_df = genre_df.sort_values("movie_count", ascending=True)
    fig = go.Figure(go.Bar(
        x=sorted_df["movie_count"],
        y=sorted_df["genre"],
        orientation="h",
        marker=dict(
            color=sorted_df["movie_count"],
            colorscale=[[0, "#3B82F6"], [0.5, "#8B5CF6"], [1, "#06B6D4"]],
            line=dict(color=THEME["border"], width=1)
        ),
        hovertemplate="<b>%{y}</b><br>Movies: %{x:,}<extra></extra>"
    ))
    fig.update_layout(
        title="Movie Count by Genre",
        xaxis_title="Total Movies",
        yaxis_title="",
        yaxis=dict(dtick=1)
    )
    return apply_cinescope_theme(fig, height=500)


def plot_top_movies_bar(df: pd.DataFrame, metric_col: str, title: str, x_label: str, is_currency: bool = True) -> go.Figure:
    """Horizontal bar chart displaying top movies for a metric."""
    if df.empty:
        return apply_cinescope_theme(go.Figure().update_layout(title=title))

    sorted_df = df.sort_values(metric_col, ascending=True)
    
    # Text formatting
    if is_currency:
        text_vals = sorted_df[metric_col].apply(lambda v: format_currency(v))
    else:
        text_vals = sorted_df[metric_col].apply(lambda v: f"{v:,.1f}" if isinstance(v, (int, float)) else str(v))

    fig = go.Figure(go.Bar(
        x=sorted_df[metric_col],
        y=sorted_df["title_clean"],
        orientation="h",
        text=text_vals,
        textposition="outside",
        textfont=dict(color=THEME["text_primary"], size=11),
        marker=dict(
            color=sorted_df[metric_col],
            colorscale=[[0, "#4F46E5"], [1, "#06B6D4"]],
            line=dict(color=THEME["border"], width=1)
        ),
        hovertemplate="<b>%{y}</b><br>" + x_label + ": %{text}<extra></extra>"
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title="",
    )
    return apply_cinescope_theme(fig, height=450)


def plot_ratings_histogram(ratings_df: pd.DataFrame) -> go.Figure:
    """Distribution histogram of movie ratings."""
    fig = px.histogram(
        ratings_df,
        x="vote_avg",
        nbins=25,
        title="Audience Rating Distribution",
        labels={"vote_avg": "Vote Average (0 - 10)"},
        color_discrete_sequence=[THEME["accent_primary"]],
    )
    avg_score = ratings_df["vote_avg"].mean()
    fig.add_vline(
        x=avg_score,
        line_dash="dash",
        line_color=THEME["accent_secondary"],
        annotation_text=f"Mean: {avg_score:.2f}",
        annotation_position="top right"
    )
    fig.update_layout(yaxis_title="Frequency of Movies")
    return apply_cinescope_theme(fig)


def plot_budget_vs_revenue(scatter_df: pd.DataFrame) -> go.Figure:
    """Scatter plot illustrating financial correlation between budget and revenue."""
    fig = px.scatter(
        scatter_df,
        x="budget_num",
        y="revenue_num",
        color="vote_avg",
        color_continuous_scale="Viridis",
        hover_name="title_clean",
        hover_data={"release_year": True, "budget_num": ":$,.0f", "revenue_num": ":$,.0f", "vote_avg": ":.1f"},
        title="Budget vs. Worldwide Revenue",
        labels={
            "budget_num": "Budget ($ USD)",
            "revenue_num": "Worldwide Revenue ($ USD)",
            "vote_avg": "Rating"
        }
    )
    # Add breakeven reference line (x = y)
    max_val = min(scatter_df["budget_num"].max(), scatter_df["revenue_num"].max())
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode="lines",
        line=dict(color=THEME["danger"], dash="dot", width=1.5),
        name="Break-even (1:1)"
    ))
    return apply_cinescope_theme(fig, height=480)


def plot_genre_heatmap(heatmap_df: pd.DataFrame) -> go.Figure:
    """Density heatmap of genre production across release years."""
    if heatmap_df.empty:
        return apply_cinescope_theme(go.Figure().update_layout(title="Genre Evolution Over Time"))

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=heatmap_df.index,
        colorscale=[[0, "#0B1020"], [0.2, "#1E1B4B"], [0.6, "#6366F1"], [1, "#06B6D4"]],
        colorbar=dict(title=dict(text="Movies", side="top", font=dict(color=THEME["text_primary"]))),
        hoverongaps=False,
        hovertemplate="Genre: <b>%{y}</b><br>Year: <b>%{x}</b><br>Movies: <b>%{z:,}</b><extra></extra>"
    ))
    fig.update_layout(
        title="Genre Production Heatmap Across Decades",
        xaxis_title="Release Year",
        yaxis_title="",
    )
    return apply_cinescope_theme(fig, height=520)


def plot_dual_trends(yearly_df: pd.DataFrame, y1_col: str, y2_col: str, y1_name: str, y2_name: str) -> go.Figure:
    """Dual-axis interactive trend line chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly_df["release_year"],
        y=yearly_df[y1_col],
        name=y1_name,
        line=dict(color=THEME["accent_primary"], width=2.5),
        yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=yearly_df["release_year"],
        y=yearly_df[y2_col],
        name=y2_name,
        line=dict(color=THEME["accent_secondary"], width=2.5, dash="dash"),
        yaxis="y2"
    ))
    fig.update_layout(
        title=f"{y1_name} vs. {y2_name} Over Time",
        xaxis=dict(title="Release Year"),
        yaxis=dict(
            title=y1_name,
            title_font=dict(color=THEME["accent_primary"]),
            gridcolor=THEME["bg_card_secondary"]
        ),
        yaxis2=dict(
            title=y2_name,
            title_font=dict(color=THEME["accent_secondary"]),
            overlaying="y",
            side="right",
            showgrid=False,
            gridcolor="rgba(0,0,0,0)"
        ),
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(21, 28, 47, 0.8)")
    )
    return apply_cinescope_theme(fig)


def render_movie_detail_card(movie: Dict[str, Any]) -> str:
    """Generate high-fidelity HTML card showcasing detailed movie attributes."""
    title_clean = movie.get("title_clean", "Unknown Title")
    release_year = movie.get("release_year", "N/A")
    poster_path = movie.get("poster_path")

    # Use pre-resolved poster URL if present, or resolve dynamically
    poster_url = movie.get("poster_url")
    if not poster_url:
        poster_url = resolve_movie_poster_url(title_clean, release_year, poster_path)

    if poster_url:
        poster_html = f'<div style="flex-shrink: 0; width: 150px; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.5); background: #0F172A; border: 1px solid {THEME["border"]};"><img src="{poster_url}" alt="{title_clean}" style="width: 100%; height: auto; min-height: 215px; display: block; object-fit: cover;" /></div>'
    else:
        # High-aesthetic dark cinematic card placeholder when no poster image exists
        poster_html = f"""<div style="flex-shrink: 0; width: 150px; min-height: 220px; border-radius: 8px; overflow: hidden; background: linear-gradient(145deg, #1E1B4B 0%, #0F172A 100%); border: 1px solid {THEME['border']}; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.5); text-align: center;">
<div style="font-size: 38px; margin-bottom: 8px;">🎬</div>
<div style="font-size: 13px; font-weight: 700; color: {THEME['text_primary']}; line-height: 1.3; max-height: 48px; overflow: hidden;">{title_clean}</div>
<div style="font-size: 11px; color: {THEME['accent_primary']}; font-weight: 600; margin-top: 6px;">{release_year}</div>
</div>"""

    tagline = movie.get("tagline")
    tagline_html = f'<p style="font-style: italic; color: {THEME["accent_secondary"]}; font-size: 13px; margin: 4px 0 10px 0;">"{tagline}"</p>' if tagline and str(tagline) != "nan" else ""

    overview = movie.get("overview")
    overview_text = str(overview) if overview and str(overview) != "nan" else "No synopsis recorded."

    card_html = f"""<div style="background: {THEME['bg_card']}; border: 1px solid {THEME['border']}; border-radius: 12px; padding: 20px; margin: 15px 0; display: flex; gap: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.4);">
{poster_html}
<div style="flex-grow: 1;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
<div>
<h3 style="margin: 0; font-size: 22px; font-weight: 700; color: {THEME['text_primary']};">{movie.get('title_clean', 'Unknown Title')} <span style="font-size: 16px; font-weight: 400; color: {THEME['text_secondary']};">({movie.get('release_year', 'N/A')})</span></h3>
{tagline_html}
</div>
<div style="background: rgba(139, 92, 246, 0.2); border: 1px solid {THEME['accent_primary']}; border-radius: 20px; padding: 4px 12px; font-weight: 700; color: {THEME['text_primary']}; font-size: 14px;">
⭐ {format_rating(movie.get('vote_avg'))} <span style="font-size: 11px; font-weight: 400; color: {THEME['text_secondary']};">({format_number(movie.get('vote_cnt'))} votes)</span>
</div>
</div>
<div style="margin: 10px 0; display: flex; flex-wrap: wrap; gap: 8px;">
<span style="background: {THEME['bg_card_secondary']}; border: 1px solid {THEME['border']}; border-radius: 6px; padding: 3px 10px; font-size: 12px; color: {THEME['accent_secondary']};">🏷️ {movie.get('genres_display', 'Uncategorized')}</span>
<span style="background: {THEME['bg_card_secondary']}; border: 1px solid {THEME['border']}; border-radius: 6px; padding: 3px 10px; font-size: 12px; color: {THEME['text_secondary']};">⏱️ {format_runtime(movie.get('runtime_num'))}</span>
<span style="background: {THEME['bg_card_secondary']}; border: 1px solid {THEME['border']}; border-radius: 6px; padding: 3px 10px; font-size: 12px; color: {THEME['text_secondary']};">🔥 Popularity: {float(movie.get('popularity_num', 0) or 0):.1f}</span>
</div>
<p style="color: {THEME['text_secondary']}; font-size: 13px; line-height: 1.6; margin: 12px 0;">{overview_text}</p>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 15px; padding-top: 15px; border-top: 1px solid {THEME['border']};">
<div><div style="font-size: 11px; color: {THEME['text_muted']}; text-transform: uppercase;">Budget</div><div style="font-size: 15px; font-weight: 600; color: {THEME['text_primary']};">{format_currency(movie.get('budget_num'))}</div></div>
<div><div style="font-size: 11px; color: {THEME['text_muted']}; text-transform: uppercase;">Revenue</div><div style="font-size: 15px; font-weight: 600; color: {THEME['success']};">{format_currency(movie.get('revenue_num'))}</div></div>
<div><div style="font-size: 11px; color: {THEME['text_muted']}; text-transform: uppercase;">Est. Profit</div><div style="font-size: 15px; font-weight: 600; color: {THEME['accent_secondary']};">{format_currency(movie.get('profit'))}</div></div>
<div><div style="font-size: 11px; color: {THEME['text_muted']}; text-transform: uppercase;">Est. ROI</div><div style="font-size: 15px; font-weight: 600; color: {THEME['accent_primary']};">{format_percentage(movie.get('roi'))}</div></div>
</div>
</div>
</div>"""
    return card_html
