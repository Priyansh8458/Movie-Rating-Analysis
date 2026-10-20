"""
SparkSession manager with automatic Java detection, local configuration,
and diagnostic environment validation.
"""
import os
import sys
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path

from src.config import SPARK_APP_NAME, SPARK_MASTER

_SPARK_SESSION = None


def configure_java_environment() -> Dict[str, Any]:
    """Detect and configure Java environment for Apache Spark.
    
    Prefers Java 8 / 11 / 17 installations if available to avoid Java 20+
    module reflection restrictions. Sets JAVA_HOME and PATH accordingly.
    """
    diagnostics = {
        "java_home": os.environ.get("JAVA_HOME"),
        "java_path": None,
        "java_version": None,
        "is_configured": False,
        "warning": None,
    }

    # Common Java installation paths on Windows
    candidate_paths = [
        r"C:\Program Files\Java\jre1.8.0_202",
        r"C:\Program Files\Java\jdk1.8.0_202",
        r"C:\Program Files\Java\jdk-17",
        r"C:\Program Files\Java\jdk-11",
        os.environ.get("JAVA_HOME", ""),
    ]

    selected_java_home = None
    for path in candidate_paths:
        if path and os.path.exists(path):
            java_bin = os.path.join(path, "bin", "java.exe" if os.name == "nt" else "java")
            if os.path.exists(java_bin):
                selected_java_home = path
                break

    if selected_java_home:
        os.environ["JAVA_HOME"] = selected_java_home
        java_bin_dir = os.path.join(selected_java_home, "bin")
        current_path = os.environ.get("PATH", "")
        if java_bin_dir not in current_path:
            os.environ["PATH"] = java_bin_dir + os.pathsep + current_path
        diagnostics["java_home"] = selected_java_home

    # Detect current active java command
    try:
        proc = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        version_output = proc.stderr or proc.stdout
        diagnostics["java_version"] = version_output.splitlines()[0] if version_output else "Unknown"
        diagnostics["is_configured"] = True
    except Exception as e:
        diagnostics["warning"] = f"Java not executable: {str(e)}"
        diagnostics["is_configured"] = False

    # Configure Python executable for PySpark workers
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    return diagnostics


def get_spark_session(app_name: str = SPARK_APP_NAME) -> Any:
    """Create or retrieve a cached local SparkSession.
    
    Configured for responsive local interactive analytics:
    - Master: local[*]
    - Driver memory: 2g
    - Shuffle partitions: 8 (optimized for local dataframes)
    - JVM module opens for Java 11/17/21+ compatibility
    """
    global _SPARK_SESSION

    if _SPARK_SESSION is not None:
        try:
            # Check if active
            if not _SPARK_SESSION.sparkContext._jsc.sc().isStopped():
                return _SPARK_SESSION
        except Exception:
            _SPARK_SESSION = None

    # Configure environment
    java_diag = configure_java_environment()
    if not java_diag["is_configured"]:
        raise RuntimeError(
            "Java is not available or could not be executed. Apache Spark requires Java 8, 11, or 17.\n"
            f"Details: {java_diag.get('warning', 'Unknown error')}"
        )

    try:
        from pyspark.sql import SparkSession
    except ImportError as e:
        raise ImportError(
            f"PySpark is not installed or import failed: {str(e)}. "
            "Please ensure 'pyspark' is installed via pip."
        )

    # Conditional JVM options: Java 8 does not recognize --add-opens (introduced in Java 9+)
    java_ver_str = str(java_diag.get("java_version", ""))
    is_java_8 = "1.8" in java_ver_str or "version \"1.8" in java_ver_str

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(SPARK_MASTER)
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.ui.enabled", "false")
    )

    if not is_java_8:
        # Standard Java JVM module opens to avoid reflective access warnings on Java 9/11/17+
        jvm_options = (
            "--add-opens=java.base/java.lang=ALL-UNNAMED "
            "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
            "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
            "--add-opens=java.base/java.io=ALL-UNNAMED "
            "--add-opens=java.base/java.net=ALL-UNNAMED "
            "--add-opens=java.base/java.nio=ALL-UNNAMED "
            "--add-opens=java.base/java.util=ALL-UNNAMED "
            "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED "
            "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED "
            "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED "
            "--add-opens=java.base/sun.nio.cs=ALL-UNNAMED "
            "--add-opens=java.base/sun.security.action=ALL-UNNAMED "
            "--add-opens=java.base/sun.util.calendar=ALL-UNNAMED "
            "--add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED"
        )
        builder = builder.config("spark.driver.extraJavaOptions", jvm_options).config("spark.executor.extraJavaOptions", jvm_options)

    try:
        _SPARK_SESSION = builder.getOrCreate()
        # Set log level to WARN to suppress verbose INFO logs in Streamlit
        _SPARK_SESSION.sparkContext.setLogLevel("WARN")
        return _SPARK_SESSION
    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Apache Spark session: {str(e)}\n"
            f"JAVA_HOME is set to: {os.environ.get('JAVA_HOME')}\n"
            f"Python executable is: {sys.executable}"
        )


def stop_spark_session():
    """Safely stop the active SparkSession."""
    global _SPARK_SESSION
    if _SPARK_SESSION is not None:
        try:
            _SPARK_SESSION.stop()
        except Exception:
            pass
        finally:
            _SPARK_SESSION = None
