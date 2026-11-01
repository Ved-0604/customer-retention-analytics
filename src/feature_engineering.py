"""
Customer Retention & Churn Analytics Platform - Feature Engineering Pipeline
=============================================================================
Transforms relational transaction tables into a customer-level analytical
feature mart for RFM segmentation, churn hazard modeling, and CLV analysis.
Outputs to data/processed/customer_features.csv.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

try:
    from src.config import PROCESSED_DATA_DIR, analytics_config
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import PROCESSED_DATA_DIR, analytics_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_customer_feature_mart() -> pd.DataFrame:
    """Aggregates multi-table relational records into customer-level analytical features."""
    logger.info("Loading relational tables for feature engineering...")
    customers = pd.read_csv(PROCESSED_DATA_DIR / "customers.csv")
    orders = pd.read_csv(PROCESSED_DATA_DIR / "orders.csv")
    order_items = pd.read_csv(PROCESSED_DATA_DIR / "order_items.csv")
    products = pd.read_csv(PROCESSED_DATA_DIR / "products.csv")
    channels = pd.read_csv(PROCESSED_DATA_DIR / "marketing_channels.csv")

    snapshot_dt = pd.to_datetime(f"{analytics_config.end_date} 23:59:59")
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])

    logger.info("Calculating order and revenue features per customer...")

    # Filter out cancelled orders for revenue & frequency metrics
    valid_orders = orders[orders["order_status"] != "Cancelled"].copy()

    # Aggregate orders per customer
    order_agg = valid_orders.groupby("customer_id").agg(
        lifetime_orders=("order_id", "count"),
        lifetime_net_revenue=("net_amount", "sum"),
        lifetime_gross_amount=("gross_amount", "sum"),
        lifetime_discount_amount=("discount_amount", "sum"),
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
        avg_order_value=("net_amount", "mean"),
    ).reset_index()

    # Cancellation statistics across all attempted orders
    cancel_agg = orders.groupby("customer_id").agg(
        total_attempted_orders=("order_id", "count"),
        cancelled_orders=("order_status", lambda s: (s == "Cancelled").sum()),
    ).reset_index()
    cancel_agg["cancellation_rate"] = (
        cancel_agg["cancelled_orders"] / cancel_agg["total_attempted_orders"]
    ).round(4)

    # Product category preference per customer
    item_prod = order_items.merge(products[["product_id", "category"]], on="product_id")
    item_order = item_prod.merge(orders[["order_id", "customer_id", "order_status"]], on="order_id")
    valid_items = item_order[item_order["order_status"] != "Cancelled"]

    # Gross margin calculation
    item_margins = valid_items.copy()
    item_margins["margin_dollars"] = (item_margins["unit_price"] - item_margins["unit_cost"]) * item_margins["quantity"]
    margin_agg = item_margins.groupby("customer_id")["margin_dollars"].sum().reset_index(name="lifetime_gross_profit")

    # Primary category (mode category)
    cat_counts = valid_items.groupby(["customer_id", "category"]).size().reset_index(name="cnt")
    top_cat = cat_counts.sort_values(["customer_id", "cnt"], ascending=[True, False]).drop_duplicates("customer_id")
    top_cat = top_cat[["customer_id", "category"]].rename(columns={"category": "favorite_category"})

    # Assemble Customer Feature Mart
    mart = customers.merge(channels[["channel_id", "channel_name", "avg_cpa"]],
                           left_on="acquisition_channel_id", right_on="channel_id", how="left")
    mart = mart.merge(order_agg, on="customer_id", how="left")
    mart = mart.merge(cancel_agg[["customer_id", "cancellation_rate", "cancelled_orders"]], on="customer_id", how="left")
    mart = mart.merge(margin_agg, on="customer_id", how="left")
    mart = mart.merge(top_cat, on="customer_id", how="left")

    # Impute signups with zero valid orders
    mart["lifetime_orders"] = mart["lifetime_orders"].fillna(0).astype(int)
    mart["lifetime_net_revenue"] = mart["lifetime_net_revenue"].fillna(0.0).round(2)
    mart["lifetime_gross_profit"] = mart["lifetime_gross_profit"].fillna(0.0).round(2)
    mart["avg_order_value"] = mart["avg_order_value"].fillna(0.0).round(2)
    mart["cancellation_rate"] = mart["cancellation_rate"].fillna(0.0)
    mart["favorite_category"] = mart["favorite_category"].fillna("None")

    # Discount dependency ratio
    mart["discount_dependency_ratio"] = np.where(
        mart["lifetime_gross_amount"] > 0,
        (mart["lifetime_discount_amount"] / mart["lifetime_gross_amount"]).round(4),
        0.0
    )

    # Recency & Tenure Calculations
    mart["recency_days"] = np.where(
        mart["last_order_date"].notna(),
        (snapshot_dt - mart["last_order_date"]).dt.days,
        (snapshot_dt - mart["signup_date"]).dt.days
    )
    mart["customer_tenure_days"] = (snapshot_dt - mart["signup_date"]).dt.days

    # 90-Day Inactivity Churn Indicator
    mart["is_churned"] = (mart["recency_days"] > analytics_config.churn_inactivity_days).astype(int)

    # Output feature store
    out_file = PROCESSED_DATA_DIR / "customer_features.csv"
    mart.to_csv(out_file, index=False)
    logger.info("Saved customer feature mart to %s: %d rows (%.2f MB)",
                out_file, len(mart), out_file.stat().st_size / (1024 * 1024))

    return mart


if __name__ == "__main__":
    df = build_customer_feature_mart()
    print("Feature Mart Shape:", df.shape)
    print("Churn Rate: %.2f%%" % (df["is_churned"].mean() * 100))
