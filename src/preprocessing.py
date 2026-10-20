"""
Preprocessing and data transformation pipeline using Apache Spark (PySpark).
Performs safe casting, date extraction, genre explosion, financial metric derivation,
and data quality auditing.
"""
from typing import Dict, Any, Tuple
import re

from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    IntegerType,
    StringType,
    ArrayType,
    DateType,
)


def extract_genre_names(genres_str: str):
    """Pure Python parser helper for extracting genre names from JSON-like strings."""
    if not genres_str:
        return []
    matches = re.findall(r"'name':\s*['\"]([^'\"]+)['\"]", str(genres_str))
    return [m.strip() for m in matches if m.strip()]


def clean_movies_dataframe(raw_df: DataFrame) -> Tuple[DataFrame, DataFrame, Dict[str, Any]]:
    """Execute complete Spark cleaning pipeline on raw movie dataset.
    
    Returns:
        df_clean: Main cleaned Spark DataFrame (one row per movie)
        df_genres_exploded: Exploded DataFrame (one row per movie-genre)
        data_quality_report: Comprehensive metrics on missingness, duplicates, and casts
    """
    total_raw = raw_df.count()

    # Step 1: Identify and separate corrupt records (where id is non-numeric or missing)
    # The Kaggle dataset has 3 known corrupt lines where overview newlines shifted columns
    valid_id_condition = F.col("id").rlike("^[0-9]+$")
    df_valid = raw_df.filter(valid_id_condition)
    corrupted_count = total_raw - df_valid.count()

    # Step 2: Safe casting of numeric columns
    # Non-parseable strings become NULL
    df_transformed = (
        df_valid
        .withColumn("movie_id", F.col("id").cast(LongType()))
        .withColumn("title_clean", F.coalesce(F.trim(F.col("title")), F.col("original_title")))
        .withColumn("budget_num", F.col("budget").cast(DoubleType()))
        .withColumn("revenue_num", F.col("revenue").cast(DoubleType()))
        .withColumn("vote_avg", F.col("vote_average").cast(DoubleType()))
        .withColumn("vote_cnt", F.col("vote_count").cast(LongType()))
        .withColumn("popularity_num", F.col("popularity").cast(DoubleType()))
        .withColumn("runtime_num", F.col("runtime").cast(DoubleType()))
    )

    # Step 3: Date parsing and year extraction
    # Standard format in movies_metadata is yyyy-MM-dd
    df_with_dates = (
        df_transformed
        .withColumn("release_date_parsed", F.to_date(F.col("release_date"), "yyyy-MM-dd"))
        .withColumn("release_year", F.year(F.col("release_date_parsed")))
    )

    # Step 4: Parse genres array natively in Spark SQL (no Python UDF overhead)
    # Converts single-quote JSON strings to standard JSON and parses into struct array
    df_with_genres = (
        df_with_dates
        .withColumn("_json_std", F.regexp_replace(F.col("genres"), "'", '"'))
        .withColumn("_genres_struct", F.from_json(F.col("_json_std"), "array<struct<id:int,name:string>>"))
        .withColumn("genres_list", F.coalesce(F.col("_genres_struct.name"), F.array()))
        .drop("_json_std", "_genres_struct")
        .withColumn(
            "genres_display",
            F.when(F.size(F.col("genres_list")) > 0, F.concat_ws(", ", F.col("genres_list"))).otherwise("Uncategorized")
        )
    )

    # Step 5: Derive financial metrics (profit & ROI)
    # Profit & ROI are only valid if both revenue > 0 and budget > 0
    valid_financials_cond = (F.col("budget_num") > 0) & (F.col("revenue_num") > 0)

    df_clean = (
        df_with_genres
        .withColumn(
            "profit",
            F.when(valid_financials_cond, F.col("revenue_num") - F.col("budget_num")).otherwise(None)
        )
        .withColumn(
            "roi",
            F.when(valid_financials_cond, ((F.col("revenue_num") - F.col("budget_num")) / F.col("budget_num")) * 100.0).otherwise(None)
        )
        .withColumn("has_valid_financials", valid_financials_cond)
    )

    # Step 6: Create exploded DataFrame for genre-level analytics
    df_genres_exploded = (
        df_clean
        .withColumn("genre", F.explode(F.col("genres_list")))
        .filter(F.col("genre") != "")
    )

    # Step 7: Calculate Data Quality Report using Spark aggregations
    # Missingness, zeroes, duplicates
    total_clean = df_clean.count()
    
    # Missing counts
    missing_release_date = df_clean.filter(F.col("release_date_parsed").isNull()).count()
    missing_runtime = df_clean.filter(F.col("runtime_num").isNull() | (F.col("runtime_num") <= 0)).count()
    missing_rating = df_clean.filter(F.col("vote_avg").isNull() | (F.col("vote_avg") <= 0)).count()
    
    # Financial data availability
    zero_budget = df_clean.filter(F.col("budget_num").isNull() | (F.col("budget_num") <= 0)).count()
    zero_revenue = df_clean.filter(F.col("revenue_num").isNull() | (F.col("revenue_num") <= 0)).count()
    valid_financials_count = df_clean.filter(F.col("has_valid_financials")).count()

    # Duplicates check
    dup_ids_count = df_clean.groupBy("movie_id").count().filter("count > 1").count()

    data_quality_report = {
        "total_raw_records": total_raw,
        "total_clean_records": total_clean,
        "corrupted_records_excluded": corrupted_count,
        "duplicate_ids_count": dup_ids_count,
        "missing_release_dates": missing_release_date,
        "missing_or_zero_runtime": missing_runtime,
        "missing_or_zero_rating": missing_rating,
        "missing_or_zero_budget": zero_budget,
        "missing_or_zero_revenue": zero_revenue,
        "records_with_both_budget_revenue": valid_financials_count,
        "total_genre_exploded_records": df_genres_exploded.count(),
        "spark_pipeline_steps": [
            "Loaded raw CSV with multiLine and quote escaping",
            "Identified and filtered non-numeric corrupted movie IDs",
            "Safely cast budget, revenue, popularity, rating, and runtime to Double/Long",
            "Parsed ISO release_date into Spark DateType and extracted release_year",
            "Parsed JSON genre structures into normalized string arrays via regex UDF",
            "Computed estimated profit (revenue - budget) and ROI (%) for positive budgets",
            "Created exploded movie-genre relation for genre analytics",
            "Registered Spark SQL temporary views (movies_clean, movies_genres, movies_financials)"
        ]
    }

    # Register Spark SQL views for analytical queries
    df_clean.createOrReplaceTempView("movies_clean")
    df_genres_exploded.createOrReplaceTempView("movies_genres")
    df_clean.filter(F.col("has_valid_financials")).createOrReplaceTempView("movies_financials")

    return df_clean, df_genres_exploded, data_quality_report
