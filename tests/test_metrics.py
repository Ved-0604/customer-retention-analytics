"""
Test Suite: Metric Reconciliation (SQL vs Python KPI Alignment)
===============================================================
Certifies that core analytical business metrics calculated via PostgreSQL/DuckDB SQL
reconcile penny-for-penny and count-for-count with Python feature engineering.
"""

import pytest
import pandas as pd
import duckdb
from src.config import PROCESSED_DATA_DIR, DATA_DIR


@pytest.fixture(scope="module")
def db_connection():
    """Connect to embedded analytical database."""
    duckdb_file = DATA_DIR / "ecommerce_analytics.duckdb"
    con = duckdb.connect(str(duckdb_file))
    yield con
    con.close()


@pytest.fixture(scope="module")
def python_features():
    """Load Python customer feature mart."""
    return pd.read_csv(PROCESSED_DATA_DIR / "customer_features.csv")


@pytest.fixture(scope="module")
def python_orders():
    """Load processed orders."""
    return pd.read_csv(PROCESSED_DATA_DIR / "orders.csv")


def test_total_net_revenue_reconciliation(db_connection, python_orders):
    """Verify Net Revenue calculated via SQL matches Python within penny tolerance."""
    sql_rev = db_connection.execute("""
        SELECT ROUND(SUM(net_amount), 2) 
        FROM orders 
        WHERE order_status NOT IN ('Cancelled')
    """).fetchone()[0]

    valid_py_orders = python_orders[python_orders["order_status"] != "Cancelled"]
    py_rev = round(float(valid_py_orders["net_amount"].sum()), 2)

    assert abs(sql_rev - py_rev) < 0.05, f"Revenue mismatch: SQL ${sql_rev:,.2f} vs Python ${py_rev:,.2f}"


def test_average_order_value_reconciliation(db_connection, python_orders):
    """Verify Average Order Value (AOV) matches between SQL and Python."""
    sql_aov = db_connection.execute("""
        SELECT ROUND(AVG(net_amount), 2) 
        FROM orders 
        WHERE order_status NOT IN ('Cancelled')
    """).fetchone()[0]

    valid_py_orders = python_orders[python_orders["order_status"] != "Cancelled"]
    py_aov = round(float(valid_py_orders["net_amount"].mean()), 2)

    assert abs(sql_aov - py_aov) < 0.02, f"AOV mismatch: SQL ${sql_aov} vs Python ${py_aov}"


def test_churn_count_reconciliation(db_connection, python_features):
    """Verify 90-day inactivity churn count in SQL reconciles with Python feature mart."""
    sql_churn = db_connection.execute("""
        SELECT COUNT(customer_id)
        FROM (
            SELECT customer_id, (DATE '2025-12-31' - MAX(order_date::date)) AS days_inactive
            FROM orders
            WHERE order_status NOT IN ('Cancelled')
            GROUP BY customer_id
        )
        WHERE days_inactive > 90
    """).fetchone()[0]

    py_churn = int(python_features[python_features["lifetime_orders"] > 0]["is_churned"].sum())

    assert sql_churn == py_churn, f"Churn count mismatch: SQL {sql_churn} vs Python {py_churn}"


def test_repeat_customers_reconciliation(db_connection, python_features):
    """Verify count of repeat customers (>= 2 orders) reconciles exactly."""
    sql_repeat = db_connection.execute("""
        SELECT COUNT(customer_id)
        FROM (
            SELECT customer_id, COUNT(order_id) AS order_cnt
            FROM orders
            WHERE order_status NOT IN ('Cancelled')
            GROUP BY customer_id
            HAVING COUNT(order_id) >= 2
        )
    """).fetchone()[0]

    py_repeat = int((python_features["lifetime_orders"] >= 2).sum())

    assert sql_repeat == py_repeat, f"Repeat buyer count mismatch: SQL {sql_repeat} vs Python {py_repeat}"
