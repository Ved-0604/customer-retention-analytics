"""
Customer Retention & Churn Analytics Platform - Database Loader
================================================================
Loads processed relational datasets into PostgreSQL (production target)
and an embedded analytical DuckDB instance (zero-dependency local execution).
Executes schema creation and initial data quality validation queries.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import duckdb
from sqlalchemy import create_engine, text

try:
    from src.config import (
        PROCESSED_DATA_DIR,
        SQL_DIR,
        DATA_DIR,
        db_config,
    )
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import (
        PROCESSED_DATA_DIR,
        SQL_DIR,
        DATA_DIR,
        db_config,
    )

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DUCKDB_PATH = DATA_DIR / "ecommerce_analytics.duckdb"


def load_to_duckdb(duckdb_path: Path = DUCKDB_PATH) -> duckdb.DuckDBPyConnection:
    """
    Creates an embedded DuckDB database loaded with all 6 relational tables.
    DuckDB supports full PostgreSQL analytical SQL syntax (CTEs, NTILE, Window Functions, DDL).
    """
    logger.info("Initializing embedded analytical database at %s...", duckdb_path)
    if duckdb_path.exists():
        try:
            duckdb_path.unlink()
        except Exception:
            pass
    con = duckdb.connect(str(duckdb_path))

    # Ingest processed CSVs directly with full type inference and native columnar performance
    tables = ["marketing_channels", "customers", "products", "orders", "order_items", "payments"]
    for tbl in tables:
        csv_file = PROCESSED_DATA_DIR / f"{tbl}.csv"
        con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{csv_file}', header=True)")
        cnt = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        logger.info("Loaded table '%s': %d records", tbl, cnt)

    return con


def load_to_postgres() -> bool:
    """Attempts to connect to PostgreSQL and load normalized tables if server is active."""
    try:
        engine = create_engine(db_config.connection_url, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to PostgreSQL at %s:%s/%s",
                    db_config.host, db_config.port, db_config.database)

        # Execute PostgreSQL schema
        schema_sql = (SQL_DIR / "schema.sql").read_text()
        with engine.connect() as conn:
            conn.execute(text(schema_sql))
            conn.commit()

        # Ingest CSVs using pandas to_sql
        tables = ["marketing_channels", "customers", "products", "orders", "order_items", "payments"]
        for tbl in tables:
            df = pd.read_csv(PROCESSED_DATA_DIR / f"{tbl}.csv")
            df.to_sql(tbl, engine, if_exists="append", index=False, chunksize=10000)
            logger.info("Ingested %s into PostgreSQL (%d rows)", tbl, len(df))

        return True
    except Exception as e:
        logger.warning("PostgreSQL server not currently active on %s:%s (%s). Using embedded analytical DuckDB instance.",
                       db_config.host, db_config.port, e)
        return False


def run_loader() -> None:
    """Run database loader pipeline."""
    # First load to DuckDB for instant zero-dependency SQL verification
    con = load_to_duckdb()
    
    # Run data quality checks in DuckDB
    logger.info("Executing SQL Data Quality Audits...")
    dq_result = con.execute("""
        SELECT 
            (SELECT COUNT(*) FROM customers) AS total_customers,
            (SELECT COUNT(*) FROM orders) AS total_orders,
            (SELECT COUNT(*) FROM order_items) AS total_items,
            (SELECT COUNT(*) FROM products) AS total_products,
            (SELECT COUNT(*) FROM payments) AS total_payments
    """).df()
    logger.info("Database verification metrics:\n%s", dq_result.to_string(index=False))

    # Next attempt PostgreSQL connection if configured
    load_to_postgres()
    con.close()


if __name__ == "__main__":
    run_loader()
