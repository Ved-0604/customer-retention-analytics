"""
Customer Retention & Churn Analytics Platform - Global Configuration
=====================================================================
Centralized configuration management for database connections, file paths,
random seeds, and analytical constants.
"""

from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
POWERBI_DIR = PROJECT_ROOT / "powerbi"

# Load environment variables from .env file if it exists
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv(PROJECT_ROOT / ".env.example")


@dataclass(frozen=True)
class DatabaseConfig:
    """PostgreSQL Database Configuration."""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "ecommerce_analytics")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")

    @property
    def connection_url(self) -> str:
        """SQLAlchemy connection URL."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass(frozen=True)
class AnalyticsConfig:
    """Business and Analytical Definitions."""
    churn_inactivity_days: int = int(os.getenv("CHURN_INACTIVITY_DAYS", "90"))
    random_seed: int = int(os.getenv("RANDOM_SEED", "42"))
    
    # Dataset Target Scale
    target_customers: int = 15000
    target_transactions: int = 135000
    target_categories: int = 12
    
    # Date Range (2 full years of analytical history)
    start_date: str = os.getenv("ANALYSIS_START_DATE", "2024-01-01")
    end_date: str = os.getenv("ANALYSIS_END_DATE", "2025-12-31")


# Global instances for modular imports
db_config = DatabaseConfig()
analytics_config = AnalyticsConfig()
