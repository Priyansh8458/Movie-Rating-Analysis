"""
Unit and integration tests for Spark preprocessing and transformation pipeline.
"""
import os
import tempfile
import pandas as pd
import pytest
from src.spark_session import get_spark_session
from src.preprocessing import extract_genre_names, clean_movies_dataframe


@pytest.fixture(scope="session")
def spark():
    """Session-scoped SparkSession fixture for testing."""
    return get_spark_session("CineScope-UnitTests")


@pytest.fixture
def sample_synthetic_raw_df(spark):
    """Small synthetic Spark DataFrame fixture loaded via CSV reader."""
    data = [
        # Normal record with valid financials
        {"id": "1", "title": "Toy Story", "budget": "30000000", "genres": "[{'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}]", "release_date": "1995-10-30", "revenue": "373554033", "runtime": "81.0", "vote_average": "7.7", "vote_count": "5415", "popularity": "21.9", "original_language": "en", "original_title": "Toy Story", "tagline": "tagline", "overview": "overview", "poster_path": "/poster.jpg"},
        # Zero budget, zero revenue
        {"id": "2", "title": "Jumanji 2", "budget": "0", "genres": "[{'id': 12, 'name': 'Adventure'}]", "release_date": "1996-12-15", "revenue": "0", "runtime": "104.0", "vote_average": "6.5", "vote_count": "100", "popularity": "15.0", "original_language": "en", "original_title": "Jumanji 2", "tagline": "", "overview": "", "poster_path": ""},
        # Unparseable date
        {"id": "3", "title": "Bad Date Movie", "budget": "1000000", "genres": "[{'id': 18, 'name': 'Drama'}]", "release_date": "invalid-date", "revenue": "2000000", "runtime": "90.0", "vote_average": "5.0", "vote_count": "20", "popularity": "5.0", "original_language": "en", "original_title": "Bad Date Movie", "tagline": "", "overview": "", "poster_path": ""},
        # Corrupt line (ID is a date string from shift)
        {"id": "1997-08-20", "title": "Corrupt Line", "budget": "0", "genres": "[]", "release_date": "1997-08-20", "revenue": "0", "runtime": "0", "vote_average": "0", "vote_count": "0", "popularity": "0", "original_language": "en", "original_title": "", "tagline": "", "overview": "", "poster_path": ""}
    ]
    pdf = pd.DataFrame(data)
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, newline="", encoding="utf-8") as f:
        pdf.to_csv(f, index=False)
        temp_path = f.name

    try:
        df = spark.read.option("header", "true").option("multiLine", "true").option("escape", '"').csv(temp_path)
        yield df
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_extract_genre_names():
    """Verify regex genre extraction parser."""
    raw = "[{'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]"
    result = extract_genre_names(raw)
    assert result == ["Animation", "Comedy", "Family"]

    empty_raw = "[]"
    assert extract_genre_names(empty_raw) == []
    assert extract_genre_names(None) == []


def test_corrupt_record_filtering(sample_synthetic_raw_df):
    """Verify that records with non-numeric IDs are excluded."""
    df_clean, df_genres, report = clean_movies_dataframe(sample_synthetic_raw_df)
    
    # 4 raw records, 1 corrupt -> 3 clean records
    assert report["total_raw_records"] == 4
    assert report["total_clean_records"] == 3
    assert report["corrupted_records_excluded"] == 1


def test_financial_profit_and_roi_calculation(sample_synthetic_raw_df):
    """Verify estimated profit and ROI calculation for positive and zero budgets."""
    df_clean, _, _ = clean_movies_dataframe(sample_synthetic_raw_df)
    
    # Toy Story: budget=30M, rev=373.554M -> profit=343.554M, ROI ~ 1145%
    toy_story = df_clean.filter("movie_id = 1").first()
    assert toy_story["budget_num"] == 30_000_000.0
    assert toy_story["revenue_num"] == 373_554_033.0
    assert toy_story["profit"] == 343_554_033.0
    assert round(toy_story["roi"], 2) == round(((373554033 - 30000000) / 30000000) * 100.0, 2)
    assert toy_story["has_valid_financials"] is True

    # Jumanji 2: budget=0, rev=0 -> profit and ROI must be NULL
    jumanji = df_clean.filter("movie_id = 2").first()
    assert jumanji["profit"] is None
    assert jumanji["roi"] is None
    assert jumanji["has_valid_financials"] is False


def test_date_parsing_and_year_extraction(sample_synthetic_raw_df):
    """Verify release_date parsing and release_year extraction."""
    df_clean, _, _ = clean_movies_dataframe(sample_synthetic_raw_df)

    toy_story = df_clean.filter("movie_id = 1").first()
    assert toy_story["release_year"] == 1995

    bad_date_movie = df_clean.filter("movie_id = 3").first()
    assert bad_date_movie["release_year"] is None


def test_genre_explosion_relation(sample_synthetic_raw_df):
    """Verify exploded genre relationships (movies with multiple genres produce multiple rows)."""
    _, df_genres, report = clean_movies_dataframe(sample_synthetic_raw_df)
    
    # Toy Story has 2 genres, Jumanji 2 has 1 genre, Bad Date has 1 genre -> total 4 exploded rows
    assert df_genres.count() == 4
    
    genres_for_toy_story = df_genres.filter("movie_id = 1").select("genre").collect()
    genre_names = [r["genre"] for r in genres_for_toy_story]
    assert "Animation" in genre_names
    assert "Comedy" in genre_names
