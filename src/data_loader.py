"""
Data loader module for reading movie datasets into Apache Spark.
"""
import os
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

from src.config import MOVIES_METADATA_PATH, RATINGS_SMALL_PATH, CREDITS_PATH, KEYWORDS_PATH
from src.spark_session import get_spark_session


def verify_dataset_exists(file_path: Optional[Path] = None) -> Path:
    """Verify that the target dataset file exists and is not empty."""
    target = file_path or MOVIES_METADATA_PATH
    if not target.exists():
        raise FileNotFoundError(
            f"Dataset file not found at: {target}\n"
            f"Please ensure 'movies_metadata.csv' is placed inside the 'data/' directory."
        )
    if target.stat().st_size == 0:
        raise ValueError(f"Dataset file at {target} is empty (0 bytes).")
    return target


def load_raw_movies_data(spark, file_path: Optional[Path] = None):
    """Load raw movies_metadata.csv into a PySpark DataFrame.
    
    Uses multiLine=True and escape quotes to properly parse multi-line
    movie overviews and JSON strings without corruption.
    """
    target_path = verify_dataset_exists(file_path)

    raw_df = (
        spark.read
        .option("header", "true")
        .option("multiLine", "true")
        .option("escape", '"')
        .option("quote", '"')
        .option("mode", "PERMISSIVE")
        .csv(str(target_path))
    )

    # Register temporary SQL view
    raw_df.createOrReplaceTempView("movies_raw")
    return raw_df


def inspect_raw_dataset(raw_df) -> Dict[str, Any]:
    """Inspect raw PySpark DataFrame and return structural statistics."""
    total_rows = raw_df.count()
    columns = raw_df.columns
    schema_fields = [(field.name, str(field.dataType)) for field in raw_df.schema.fields]

    return {
        "file_name": "movies_metadata.csv",
        "total_rows": total_rows,
        "total_columns": len(columns),
        "columns": columns,
        "schema": schema_fields,
    }
