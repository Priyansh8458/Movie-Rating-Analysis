"""
Unit tests for Spark analytics calculations, financial models, and aggregations.
"""
import os
import tempfile
import pandas as pd
import pytest
from src.spark_session import get_spark_session
from src.preprocessing import clean_movies_dataframe
from src.analytics import (
    get_kpi_summary,
    get_genre_metrics,
    get_top_movies_by_metric,
    get_financial_breakdown,
    generate_key_insights,
)


@pytest.fixture(scope="session")
def spark():
    """Session-scoped SparkSession fixture for testing."""
    return get_spark_session("CineScope-AnalyticsTests")


@pytest.fixture
def analytics_test_data(spark):
    """Synthetic dataset loaded via Spark CSV reader."""
    data = [
        {"id": "1", "title": "Blockbuster A", "budget": "100000000", "genres": "[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}]", "release_date": "2015-05-01", "revenue": "500000000", "runtime": "120.0", "vote_average": "7.5", "vote_count": "1000", "popularity": "50.0", "original_language": "en", "original_title": "Blockbuster A", "tagline": "Tag 1", "overview": "Overview 1", "poster_path": "/p1.jpg"},
        {"id": "2", "title": "Blockbuster B", "budget": "150000000", "genres": "[{'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}]", "release_date": "2015-07-15", "revenue": "600000000", "runtime": "140.0", "vote_average": "8.0", "vote_count": "2000", "popularity": "75.0", "original_language": "en", "original_title": "Blockbuster B", "tagline": "Tag 2", "overview": "Overview 2", "poster_path": "/p2.jpg"},
        {"id": "3", "title": "Indie Gem", "budget": "5000000", "genres": "[{'id': 18, 'name': 'Drama'}]", "release_date": "2016-10-10", "revenue": "30000000", "runtime": "95.0", "vote_average": "8.5", "vote_count": "500", "popularity": "20.0", "original_language": "en", "original_title": "Indie Gem", "tagline": "Tag 3", "overview": "Overview 3", "poster_path": "/p3.jpg"},
        {"id": "4", "title": "Flop Feature", "budget": "50000000", "genres": "[{'id': 35, 'name': 'Comedy'}]", "release_date": "2017-03-20", "revenue": "10000000", "runtime": "90.0", "vote_average": "4.0", "vote_count": "200", "popularity": "10.0", "original_language": "en", "original_title": "Flop Feature", "tagline": "Tag 4", "overview": "Overview 4", "poster_path": "/p4.jpg"},
        {"id": "5", "title": "Unreported Title", "budget": "0", "genres": "[{'id': 99, 'name': 'Documentary'}]", "release_date": "2018-01-01", "revenue": "0", "runtime": "80.0", "vote_average": "6.5", "vote_count": "50", "popularity": "5.0", "original_language": "en", "original_title": "Unreported Title", "tagline": "Tag 5", "overview": "Overview 5", "poster_path": "/p5.jpg"},
    ]
    pdf = pd.DataFrame(data)
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, newline="", encoding="utf-8") as f:
        pdf.to_csv(f, index=False)
        temp_path = f.name

    try:
        raw_df = spark.read.option("header", "true").option("multiLine", "true").option("escape", '"').csv(temp_path)
        df_clean, df_genres, report = clean_movies_dataframe(raw_df)
        yield df_clean, df_genres
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_kpi_summary_calculation(analytics_test_data):
    """Verify high-level KPI aggregation logic."""
    df_clean, _ = analytics_test_data
    kpis = get_kpi_summary(df_clean)

    assert kpis["total_movies"] == 5
    # Total revenue = 500M + 600M + 30M + 10M + 0 = 1,140,000,000
    assert kpis["total_revenue"] == 1_140_000_000.0
    # Average revenue across positive revenues (4 films) = 1,140,000,000 / 4 = 285,000,000
    assert kpis["avg_revenue"] == 285_000_000.0
    # Average budget across positive budgets (4 films) = (100M + 150M + 5M + 50M) / 4 = 76,250,000
    assert kpis["avg_budget"] == 76_250_000.0


def test_top_movies_ranking(analytics_test_data):
    """Verify top N movie ranking by revenue and ratings."""
    df_clean, _ = analytics_test_data
    
    top_rev = get_top_movies_by_metric(df_clean, metric_col="revenue_num", n=2)
    assert len(top_rev) == 2
    assert top_rev.iloc[0]["title_clean"] == "Blockbuster B"
    assert top_rev.iloc[0]["revenue_num"] == 600_000_000.0
    assert top_rev.iloc[1]["title_clean"] == "Blockbuster A"

    top_rated = get_top_movies_by_metric(df_clean, metric_col="vote_avg", n=1, min_votes=300)
    assert top_rated.iloc[0]["title_clean"] == "Indie Gem"
    assert top_rated.iloc[0]["vote_avg"] == 8.5


def test_genre_metrics_aggregation(analytics_test_data):
    """Verify genre-level grouping and metrics."""
    _, df_genres = analytics_test_data
    genre_metrics = get_genre_metrics(df_genres, min_movies=1)

    # Action appears twice (Blockbuster A and B)
    action_row = genre_metrics[genre_metrics["genre"] == "Action"].iloc[0]
    assert action_row["movie_count"] == 2
    assert action_row["total_revenue"] == 1_100_000_000.0
    assert action_row["avg_revenue"] == 550_000_000.0


def test_financial_breakdown_models(analytics_test_data):
    """Verify profit and ROI modeling on commercial films."""
    df_clean, _ = analytics_test_data
    financials = get_financial_breakdown(df_clean, min_budget_for_roi=1_000_000)

    # 4 commercial films with both budget and rev > 0
    assert financials["count"] == 4
    # Blockbuster B: profit = 600M - 150M = 450M
    assert financials["top_profit"].iloc[0]["title_clean"] == "Blockbuster B"
    assert financials["top_profit"].iloc[0]["profit"] == 450_000_000.0

    # Indie Gem: budget = 5M, revenue = 30M -> ROI = (25M / 5M) * 100 = 500%
    # Blockbuster B: budget = 150M, rev = 600M -> ROI = (450M / 150M) * 100 = 300%
    top_roi = financials["top_roi"]
    assert top_roi.iloc[0]["title_clean"] == "Indie Gem"
    assert top_roi.iloc[0]["roi"] == 500.0


def test_dynamic_key_insights_generation(analytics_test_data):
    """Verify that key insights are derived programmatically."""
    df_clean, df_genres = analytics_test_data
    insights = generate_key_insights(df_clean, df_genres)

    assert len(insights) > 0
    titles = [i["title"] for i in insights]
    assert "Highest Grossing Movie" in titles
    assert "Peak Production Year" in titles
