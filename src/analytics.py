"""
Analytical functions powered by Apache Spark (PySpark DataFrame API and Spark SQL).
Performs distributed aggregations, top-N rankings, financial breakdowns, and insight generation.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
from pyspark.sql import DataFrame, functions as F


def get_kpi_summary(df_clean: DataFrame) -> Dict[str, Any]:
    """Calculate high-level KPI metrics across the movie dataset using Spark aggregations."""
    # Compute in a single Spark aggregation action for maximum performance
    agg_row = df_clean.agg(
        F.count("*").alias("total_movies"),
        F.round(F.avg(F.when(F.col("vote_avg") > 0, F.col("vote_avg"))), 2).alias("avg_rating"),
        F.sum(F.when(F.col("revenue_num") > 0, F.col("revenue_num")).otherwise(0)).alias("total_revenue"),
        F.round(F.avg(F.when(F.col("revenue_num") > 0, F.col("revenue_num"))), 0).alias("avg_revenue"),
        F.round(F.avg(F.when(F.col("budget_num") > 0, F.col("budget_num"))), 0).alias("avg_budget"),
        F.round(F.avg(F.when(F.col("runtime_num") > 0, F.col("runtime_num"))), 1).alias("avg_runtime")
    ).collect()[0]

    return {
        "total_movies": agg_row["total_movies"] or 0,
        "avg_rating": agg_row["avg_rating"] or 0.0,
        "total_revenue": agg_row["total_revenue"] or 0.0,
        "avg_revenue": agg_row["avg_revenue"] or 0.0,
        "avg_budget": agg_row["avg_budget"] or 0.0,
        "avg_runtime": agg_row["avg_runtime"] or 0.0,
    }


def get_yearly_trends(df_clean: DataFrame, min_year: int = 1950, max_year: int = 2020) -> pd.DataFrame:
    """Compute movie release counts, average ratings, and revenues grouped by release year."""
    yearly_df = (
        df_clean
        .filter(F.col("release_year").isNotNull() & F.col("release_year").between(min_year, max_year))
        .groupBy("release_year")
        .agg(
            F.count("*").alias("movie_count"),
            F.round(F.avg(F.when(F.col("vote_avg") > 0, F.col("vote_avg"))), 2).alias("avg_rating"),
            F.sum(F.when(F.col("revenue_num") > 0, F.col("revenue_num")).otherwise(0)).alias("total_revenue"),
            F.round(F.avg(F.when(F.col("revenue_num") > 0, F.col("revenue_num"))), 0).alias("avg_revenue"),
            F.round(F.avg(F.when(F.col("budget_num") > 0, F.col("budget_num"))), 0).alias("avg_budget")
        )
        .orderBy("release_year")
    )
    return yearly_df.toPandas()


def get_genre_metrics(df_genres: DataFrame, min_movies: int = 10) -> pd.DataFrame:
    """Compute aggregate performance statistics per genre using the exploded genre DataFrame."""
    genre_df = (
        df_genres
        .groupBy("genre")
        .agg(
            F.count("*").alias("movie_count"),
            F.round(F.avg(F.when(F.col("vote_avg") > 0, F.col("vote_avg"))), 2).alias("avg_rating"),
            F.sum(F.when(F.col("revenue_num") > 0, F.col("revenue_num")).otherwise(0)).alias("total_revenue"),
            F.round(F.avg(F.when(F.col("revenue_num") > 0, F.col("revenue_num"))), 0).alias("avg_revenue"),
            F.round(F.avg(F.when(F.col("budget_num") > 0, F.col("budget_num"))), 0).alias("avg_budget"),
            F.round(F.avg(F.when(F.col("runtime_num") > 0, F.col("runtime_num"))), 1).alias("avg_runtime")
        )
        .filter(F.col("movie_count") >= min_movies)
        .orderBy(F.col("movie_count").desc())
    )
    return genre_df.toPandas()


def get_genre_year_heatmap_data(df_genres: DataFrame, min_year: int = 1980, max_year: int = 2018, top_n: int = 12) -> pd.DataFrame:
    """Generate pivot table of movie counts per genre over time for heatmaps."""
    # 1. Identify top N genres
    top_genres_rows = (
        df_genres
        .groupBy("genre")
        .count()
        .orderBy(F.col("count").desc())
        .limit(top_n)
        .select("genre")
        .collect()
    )
    top_genres = [r["genre"] for r in top_genres_rows]

    # 2. Filter and group by genre and release_year
    pivoted_spark = (
        df_genres
        .filter(
            F.col("genre").isin(top_genres) &
            F.col("release_year").isNotNull() &
            F.col("release_year").between(min_year, max_year)
        )
        .groupBy("genre", "release_year")
        .count()
        .orderBy("release_year", "genre")
    )
    pdf = pivoted_spark.toPandas()
    if pdf.empty:
        return pd.DataFrame()

    heatmap_table = pdf.pivot(index="genre", columns="release_year", values="count").fillna(0)
    return heatmap_table


def get_top_movies_by_metric(
    df_clean: DataFrame,
    metric_col: str = "revenue_num",
    n: int = 10,
    min_votes: int = 0,
    min_budget: float = 0.0,
    ascending: bool = False
) -> pd.DataFrame:
    """Retrieve top N movies ranked by a specific metric."""
    query = df_clean.filter(F.col(metric_col).isNotNull())
    if min_votes > 0:
        query = query.filter(F.col("vote_cnt") >= min_votes)
    if min_budget > 0:
        query = query.filter(F.col("budget_num") >= min_budget)

    ordered_query = query.orderBy(F.col(metric_col).asc() if ascending else F.col(metric_col).desc())
    
    top_df = ordered_query.select(
        "movie_id",
        "title_clean",
        "release_year",
        "genres_display",
        "budget_num",
        "revenue_num",
        "profit",
        "roi",
        "vote_avg",
        "vote_cnt",
        "popularity_num",
        "poster_path",
        "overview",
        "tagline"
    ).limit(n)
    return top_df.toPandas()


def get_financial_breakdown(df_clean: DataFrame, min_budget_for_roi: float = 1_000_000.0) -> Dict[str, Any]:
    """Calculate comprehensive financial analysis metrics and distributions."""
    valid_financials_df = df_clean.filter(F.col("has_valid_financials"))

    # Summary totals
    totals_row = valid_financials_df.agg(
        F.count("*").alias("count"),
        F.sum("budget_num").alias("total_budget"),
        F.sum("revenue_num").alias("total_revenue"),
        F.avg("budget_num").alias("avg_budget"),
        F.avg("revenue_num").alias("avg_revenue"),
        F.sum("profit").alias("total_profit"),
        F.avg("profit").alias("avg_profit")
    ).collect()[0]

    # Top 10 by Revenue
    top_revenue = get_top_movies_by_metric(df_clean, metric_col="revenue_num", n=10)

    # Top 10 by Profit
    top_profit = get_top_movies_by_metric(valid_financials_df, metric_col="profit", n=10)

    # Top 10 by ROI (with threshold to eliminate sub-$1M viral micro-budget outliers)
    top_roi = get_top_movies_by_metric(valid_financials_df, metric_col="roi", n=10, min_budget=min_budget_for_roi)

    # Box office hits vs Critical misses (High revenue top 10%, but rating < 6.0)
    rev_p90 = valid_financials_df.stat.approxQuantile("revenue_num", [0.90], 0.01)[0]
    box_office_misses = (
        valid_financials_df
        .filter((F.col("revenue_num") >= rev_p90) & (F.col("vote_avg") < 6.0) & (F.col("vote_cnt") >= 100))
        .orderBy(F.col("revenue_num").desc())
        .limit(10)
        .toPandas()
    )

    # Cult Classics / Underrated Gems (Rating >= 7.8, votes >= 300, but low revenue or loss)
    cult_classics = (
        valid_financials_df
        .filter((F.col("vote_avg") >= 7.8) & (F.col("vote_cnt") >= 300) & (F.col("revenue_num") < 50_000_000))
        .orderBy(F.col("vote_avg").desc())
        .limit(10)
        .toPandas()
    )

    # Sample for scatter plot (budget vs revenue) - limit to 3,000 for smooth browser rendering
    scatter_df = (
        valid_financials_df
        .select("title_clean", "release_year", "budget_num", "revenue_num", "profit", "roi", "vote_avg")
        .limit(3000)
        .toPandas()
    )

    return {
        "count": totals_row["count"] or 0,
        "total_budget": totals_row["total_budget"] or 0.0,
        "total_revenue": totals_row["total_revenue"] or 0.0,
        "avg_budget": totals_row["avg_budget"] or 0.0,
        "avg_revenue": totals_row["avg_revenue"] or 0.0,
        "total_profit": totals_row["total_profit"] or 0.0,
        "avg_profit": totals_row["avg_profit"] or 0.0,
        "top_revenue": top_revenue,
        "top_profit": top_profit,
        "top_roi": top_roi,
        "box_office_misses": box_office_misses,
        "cult_classics": cult_classics,
        "scatter_df": scatter_df,
    }


def get_ratings_popularity_analysis(df_clean: DataFrame, min_votes: int = 50) -> Dict[str, Any]:
    """Calculate distributions and rankings for ratings, votes, and popularity."""
    # Top rated with minimum vote filter
    top_rated = get_top_movies_by_metric(df_clean, metric_col="vote_avg", n=10, min_votes=min_votes)

    # Top popular
    top_popular = get_top_movies_by_metric(df_clean, metric_col="popularity_num", n=10)

    # Top by vote count
    top_votes = get_top_movies_by_metric(df_clean, metric_col="vote_cnt", n=10)

    # Rating distribution samples
    ratings_sample = (
        df_clean
        .filter(F.col("vote_avg") > 0)
        .select("vote_avg", "popularity_num", "vote_cnt", "title_clean")
        .limit(5000)
        .toPandas()
    )

    return {
        "top_rated": top_rated,
        "top_popular": top_popular,
        "top_votes": top_votes,
        "ratings_sample": ratings_sample,
    }


def generate_key_insights(df_clean: DataFrame, df_genres: DataFrame) -> List[Dict[str, str]]:
    """Dynamically derive analytical insights directly from computed Spark DataFrames."""
    insights = []

    try:
        # 1. Most common genre
        top_genre_row = df_genres.groupBy("genre").count().orderBy(F.col("count").desc()).first()
        if top_genre_row:
            insights.append({
                "title": "Most Prevalent Genre",
                "value": f"{top_genre_row['genre']} ({top_genre_row['count']:,} titles)",
                "desc": "Represents the largest production category across the cinematic catalog."
            })

        # 2. Peak release year
        peak_year_row = (
            df_clean
            .filter(F.col("release_year").isNotNull())
            .groupBy("release_year")
            .count()
            .orderBy(F.col("count").desc())
            .first()
        )
        if peak_year_row:
            insights.append({
                "title": "Peak Production Year",
                "value": f"{peak_year_row['release_year']} ({peak_year_row['count']:,} releases)",
                "desc": "Year with the highest volume of cataloged feature film releases."
            })

        # 3. Highest grossing movie
        top_grossing = (
            df_clean
            .filter(F.col("revenue_num") > 0)
            .orderBy(F.col("revenue_num").desc())
            .first()
        )
        if top_grossing:
            insights.append({
                "title": "Highest Grossing Movie",
                "value": f"{top_grossing['title_clean']} (${top_grossing['revenue_num'] / 1e9:.2f}B)",
                "desc": f"Released in {top_grossing['release_year'] or 'N/A'}, leading all-time worldwide revenue in this dataset."
            })

        # 4. Highest rated movie with min 500 votes
        top_rated_row = (
            df_clean
            .filter(F.col("vote_cnt") >= 500)
            .orderBy(F.col("vote_avg").desc(), F.col("vote_cnt").desc())
            .first()
        )
        if top_rated_row:
            insights.append({
                "title": "Top Audience Favorite",
                "value": f"{top_rated_row['title_clean']} ({top_rated_row['vote_avg']} / 10)",
                "desc": f"Rated by {top_rated_row['vote_cnt']:,} viewers (minimum 500 votes threshold)."
            })

        # 5. Highest rated genre with min 50 movies
        top_rated_genre = (
            df_genres
            .filter(F.col("vote_avg") > 0)
            .groupBy("genre")
            .agg(F.count("*").alias("count"), F.avg("vote_avg").alias("avg_score"))
            .filter(F.col("count") >= 50)
            .orderBy(F.col("avg_score").desc())
            .first()
        )
        if top_rated_genre:
            insights.append({
                "title": "Highest Critical Consensus Genre",
                "value": f"{top_rated_genre['genre']} ({top_rated_genre['avg_score']:.2f} avg)",
                "desc": f"Achieved the highest average rating among genres with at least 50 titles."
            })
    except Exception as e:
        insights.append({
            "title": "Data Note",
            "value": "Computed metrics ready",
            "desc": f"Generated from Apache Spark analysis: {str(e)}"
        })

    return insights


def execute_spark_sql(spark, query_str: str) -> pd.DataFrame:
    """Execute raw Spark SQL queries against registered temp views and return a pandas dataframe."""
    return spark.sql(query_str).toPandas()
