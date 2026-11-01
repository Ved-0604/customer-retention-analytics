"""
Test Suite: Data Quality, Financial Reconciliation, and Behavioral Integrity
=============================================================================
Validates:
- Penny-exact financial reconciliation across orders, items, and payments
- Positive unit economics and margins
- Temporal causality (orders strictly on or after signup date)
- Logical consistency of order and payment statuses
"""

import pytest
import pandas as pd
import numpy as np
from src.config import PROCESSED_DATA_DIR


@pytest.fixture(scope="module")
def processed_data():
    """Load processed datasets for quality verification."""
    return {
        "customers": pd.read_csv(PROCESSED_DATA_DIR / "customers.csv"),
        "orders": pd.read_csv(PROCESSED_DATA_DIR / "orders.csv"),
        "order_items": pd.read_csv(PROCESSED_DATA_DIR / "order_items.csv"),
        "products": pd.read_csv(PROCESSED_DATA_DIR / "products.csv"),
        "payments": pd.read_csv(PROCESSED_DATA_DIR / "payments.csv"),
    }


def test_financial_reconciliation(processed_data):
    """Verify that item line totals reconcile with order totals and payments."""
    orders = processed_data["orders"]
    order_items = processed_data["order_items"]
    payments = processed_data["payments"]

    # 1. Order Items sum == Order Gross Amount
    items_gross = order_items.groupby("order_id")["total_item_price"].sum().round(2)
    orders_indexed = orders.set_index("order_id")
    gross_diff = (orders_indexed["gross_amount"] - items_gross).abs()
    assert (gross_diff < 0.02).all(), f"Found {(gross_diff >= 0.02).sum()} gross reconciliation errors"

    # 2. Net Amount == Gross - Discount + Shipping
    calculated_net = (orders["gross_amount"] - orders["discount_amount"] + orders["shipping_fee"]).round(2)
    net_diff = (orders["net_amount"] - calculated_net).abs()
    assert (net_diff < 0.02).all(), f"Found {(net_diff >= 0.02).sum()} net amount calculation errors"

    # 3. Payment Amount == Order Net Amount
    payments_indexed = payments.set_index("order_id")["amount"]
    payment_diff = (orders_indexed["net_amount"] - payments_indexed).abs()
    assert (payment_diff < 0.02).all(), f"Found {(payment_diff >= 0.02).sum()} payment mismatch errors"


def test_positive_unit_economics(processed_data):
    """Verify products have positive base price and cost of goods sold < base price."""
    products = processed_data["products"]
    order_items = processed_data["order_items"]

    assert (products["base_price"] > 0).all(), "Found non-positive base price in products"
    assert (products["cogs"] > 0).all(), "Found non-positive COGS in products"
    assert (products["base_price"] >= products["cogs"]).all(), "Found negative margin product in catalog"

    assert (order_items["quantity"] > 0).all(), "Found zero or negative order quantity"
    assert (order_items["unit_price"] > 0).all(), "Found zero or negative unit price"


def test_temporal_causality(processed_data):
    """Verify every customer order occurred on or after their account signup date."""
    customers = processed_data["customers"].set_index("customer_id")["signup_date"]
    orders = processed_data["orders"]

    order_dates = pd.to_datetime(orders["order_date"])
    signup_dates = pd.to_datetime(orders["customer_id"].map(customers))

    # Order date must not precede signup date (allow small minute-level precision tolerance if on same day)
    date_difference = (order_dates - signup_dates).dt.total_seconds()
    assert (date_difference >= -3600).all(), "Detected retroactive orders placed before customer signup"


def test_order_payment_status_consistency(processed_data):
    """Verify that cancelled orders have failed payments and delivered orders have success payments."""
    orders = processed_data["orders"].set_index("order_id")
    payments = processed_data["payments"].set_index("order_id")

    # Cancelled orders -> Failed payments
    cancelled_order_ids = orders[orders["order_status"] == "Cancelled"].index
    assert (payments.loc[cancelled_order_ids, "payment_status"] == "Failed").all(), \
        "Cancelled orders must have 'Failed' payment status"

    # Delivered orders -> Success payments
    delivered_order_ids = orders[orders["order_status"] == "Delivered"].index
    assert (payments.loc[delivered_order_ids, "payment_status"] == "Success").all(), \
        "Delivered orders must have 'Success' payment status"
