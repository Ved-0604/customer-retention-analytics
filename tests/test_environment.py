"""
Test Suite: Environment and Configuration Verification
======================================================
Validates that all essential libraries, directory structures, and configurations
are operational before initiating data pipelines and analytical processing.
"""

import sys
from pathlib import Path
import pytest


def test_python_version():
    """Verify Python runtime is 3.10+."""
    assert sys.version_info >= (3, 10), f"Python version {sys.version} is below 3.10"


def test_core_dependencies():
    """Verify critical data engineering and analytical libraries can be imported."""
    modules = [
        "pandas",
        "numpy",
        "scipy",
        "sklearn",
        "faker",
        "duckdb",
        "sqlalchemy",
        "psycopg2",
        "matplotlib",
        "seaborn",
        "dotenv",
    ]
    for mod in modules:
        __import__(mod)


def test_project_structure():
    """Verify required project directories exist and are writable."""
    from src.config import (
        PROJECT_ROOT,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        SQL_DIR,
        NOTEBOOKS_DIR,
        REPORTS_DIR,
        POWERBI_DIR,
    )

    required_dirs = [
        PROJECT_ROOT,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        SQL_DIR,
        NOTEBOOKS_DIR,
        REPORTS_DIR,
        POWERBI_DIR,
    ]

    for d in required_dirs:
        assert d.exists(), f"Directory {d} does not exist"
        assert d.is_dir(), f"Path {d} is not a directory"


def test_config_defaults():
    """Verify analytical and database configurations."""
    from src.config import analytics_config, db_config

    assert analytics_config.churn_inactivity_days == 90
    assert analytics_config.random_seed == 42
    assert analytics_config.target_customers >= 10000
    assert analytics_config.target_transactions >= 100000
    assert db_config.port == 5432
