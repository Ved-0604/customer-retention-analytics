"""
Test Suite: Data Generation Scale and Referential Integrity
============================================================
Validates that generated relational datasets comply with enterprise scale requirements:
- Customers >= 10,000
- Transactions / Orders >= 100,000
- Product Categories >= 10
- Longitudinal Date Span >= 2 years (720+ days)
- 100% Primary Key Uniqueness & Foreign Key Referential Integrity
"""

import pytest
import pandas as pd
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR


@pytest.fixture(scope="module")
def datasets():
    """Load raw datasets for testing."""
    return {
        "channels": pd.read_csv(RAW_DATA_DIR / "marketing_channels.csv"),
        "customers": pd.read_csv(RAW_DATA_DIR / "customers.csv"),
        "products": pd.read_csv(RAW_DATA_DIR / "products.csv"),
        "orders": pd.read_csv(RAW_DATA_DIR / "orders.csv"),
        "order_items": pd.read_csv(RAW_DATA_DIR / "order_items.csv"),
        "payments": pd.read_csv(RAW_DATA_DIR / "payments.csv"),
    }


def test_scale_requirements(datasets):
    """Verify data meets or exceeds all project volume standards."""
    assert len(datasets["customers"]) >= 10000, f"Expected >= 10,000 customers, got {len(datasets['customers'])}"
    assert len(datasets["orders"]) >= 100000, f"Expected >= 100,000 orders, got {len(datasets['orders'])}"
    assert datasets["products"]["category"].nunique() >= 10, "Expected >= 10 product categories"


def test_longitudinal_date_span(datasets):
    """Verify order history spans at least 2 full calendar years."""
    orders = datasets["orders"]
    order_dates = pd.to_datetime(orders["order_date"])
    min_date = order_dates.min()
    max_date = order_dates.max()
    span_days = (max_date - min_date).days

    assert span_days >= 720, f"Expected >= 720 days (2 years), got {span_days} days ({min_date} to {max_date})"


def test_primary_key_uniqueness(datasets):
    """Verify all entity primary keys are 100% unique and non-null."""
    pk_map = {
        "channels": "channel_id",
        "customers": "customer_id",
        "products": "product_id",
        "orders": "order_id",
        "order_items": "order_item_id",
        "payments": "payment_id",
    }

    for table_name, pk_col in pk_map.items():
        df = datasets[table_name]
        assert df[pk_col].is_unique, f"Duplicate primary keys found in {table_name}.{pk_col}"
        assert df[pk_col].notna().all(), f"Null primary keys found in {table_name}.{pk_col}"


def test_referential_integrity(datasets):
    """Verify all foreign key relationships are valid with zero orphaned records."""
    customers = datasets["customers"]
    orders = datasets["orders"]
    order_items = datasets["order_items"]
    products = datasets["products"]
    payments = datasets["payments"]
    channels = datasets["channels"]

    # Customer -> Acquisition Channel
    valid_channel_ids = set(channels["channel_id"])
    assert customers["acquisition_channel_id"].isin(valid_channel_ids).all(), "Invalid acquisition_channel_id in customers"

    # Order -> Customer
    valid_cust_ids = set(customers["customer_id"])
    assert orders["customer_id"].isin(valid_cust_ids).all(), "Orphaned orders referencing non-existent customer_id"

    # Order Item -> Order
    valid_order_ids = set(orders["order_id"])
    assert order_items["order_id"].isin(valid_order_ids).all(), "Orphaned order_items referencing non-existent order_id"

    # Order Item -> Product
    valid_prod_ids = set(products["product_id"])
    assert order_items["product_id"].isin(valid_prod_ids).all(), "Orphaned order_items referencing non-existent product_id"

    # Payment -> Order
    assert payments["order_id"].isin(valid_order_ids).all(), "Orphaned payments referencing non-existent order_id"
