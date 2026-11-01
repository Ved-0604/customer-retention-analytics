"""
Customer Retention & Churn Analytics Platform - Statistical Analysis Engine
===========================================================================
Modular statistical and analytics functions:
1. RFM Quintile Scoring & Rule-Based Customer Segmentation
2. Cohort Retention Heatmap Matrix Construction
3. Churn Hazard & Logistic Regression Driver Modeling
4. Historical vs Estimated Customer Lifetime Value (CLV)
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

try:
    from src.config import PROCESSED_DATA_DIR, analytics_config
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import PROCESSED_DATA_DIR, analytics_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def calculate_rfm_segments(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies RFM quintile scoring (1-5) and assigns standard behavioral segments.
    """
    df = features_df[features_df["lifetime_orders"] > 0].copy()

    # Recency: lower days = higher score (5 is best)
    df["r_score"] = pd.qcut(df["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    # Frequency: higher orders = higher score (use rank for duplicates)
    df["f_score"] = pd.qcut(df["lifetime_orders"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    # Monetary: higher spend = higher score
    df["m_score"] = pd.qcut(df["lifetime_net_revenue"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    def assign_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 4 and f in [2, 3]:
            return "Potential Loyalists"
        elif r >= 4 and f == 1:
            return "New Customers"
        elif r == 1 and f >= 4 and m >= 4:
            return "Cannot Lose Them"
        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk"
        elif r <= 2 and f in [2, 3]:
            return "Hibernating"
        else:
            return "Lost Customers"

    df["customer_segment"] = df.apply(assign_segment, axis=1)
    logger.info("Assigned RFM segments across %d active customers.", len(df))
    return df


def compute_cohort_retention_matrix(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """Computes monthly acquisition cohort retention matrix from Month 0 to Month 12."""
    valid_orders = orders_df[orders_df["order_status"] != "Cancelled"].copy()
    valid_orders["order_date"] = pd.to_datetime(valid_orders["order_date"])
    valid_orders["order_month"] = valid_orders["order_date"].dt.to_period("M")

    cust = customers_df.copy()
    cust["signup_date"] = pd.to_datetime(cust["signup_date"])
    cust["cohort_month"] = cust["signup_date"].dt.to_period("M")

    merged = valid_orders.merge(cust[["customer_id", "cohort_month"]], on="customer_id")
    merged["cohort_period"] = (
        (merged["order_month"].dt.year - merged["cohort_month"].dt.year) * 12 +
        (merged["order_month"].dt.month - merged["cohort_month"].dt.month)
    )

    cohort_sizes = cust.groupby("cohort_month")["customer_id"].nunique()
    cohort_activity = merged.groupby(["cohort_month", "cohort_period"])["customer_id"].nunique().unstack()

    # Retention % matrix
    retention_matrix = cohort_activity.divide(cohort_sizes, axis=0) * 100
    retention_matrix.insert(0, "cohort_size", cohort_sizes)
    return retention_matrix.round(1)


def analyze_churn_drivers(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fits an interpretable Logistic Regression model to quantify odds ratios
    of key churn drivers (discount dependency, cancellation rate, AOV, channel).
    """
    df = features_df[features_df["lifetime_orders"] > 0].copy()

    feature_cols = [
        "discount_dependency_ratio",
        "cancellation_rate",
        "avg_order_value",
        "customer_tenure_days",
    ]

    X = df[feature_cols].fillna(0)
    y = df["is_churned"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(random_state=analytics_config.random_seed)
    model.fit(X_scaled, y)

    odds_ratios = np.exp(model.coef_[0])
    results = pd.DataFrame({
        "feature": feature_cols,
        "standardized_coefficient": model.coef_[0].round(4),
        "odds_ratio": odds_ratios.round(4),
        "direction": np.where(odds_ratios > 1, "Increases Churn Risk", "Decreases Churn Risk"),
    }).sort_values("odds_ratio", ascending=False)

    logger.info("Computed churn driver odds ratios:\n%s", results.to_string(index=False))
    return results


def estimate_clv_by_segment(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates historical realized gross profit vs estimated forward-looking CLV.
    """
    rfm_df = calculate_rfm_segments(features_df)
    
    summary = rfm_df.groupby("customer_segment").agg(
        customer_count=("customer_id", "count"),
        total_revenue=("lifetime_net_revenue", "sum"),
        avg_revenue_per_user=("lifetime_net_revenue", "mean"),
        avg_gross_profit=("lifetime_gross_profit", "mean"),
        avg_aov=("avg_order_value", "mean"),
        avg_orders=("lifetime_orders", "mean"),
        churn_rate=("is_churned", "mean"),
    ).reset_index()

    # Forward-Looking Estimated CLV Formula:
    # Lifespan = 1 / Churn Rate
    # Estimated CLV = AOV * Annual Orders * Lifespan * Margin Ratio
    summary["estimated_lifespan_years"] = (1.0 / summary["churn_rate"]).clip(upper=4.0, lower=0.5).round(2)
    summary["estimated_clv"] = (
        summary["avg_gross_profit"] * summary["estimated_lifespan_years"]
    ).round(2)

    summary["revenue_share_pct"] = (summary["total_revenue"] / summary["total_revenue"].sum() * 100).round(2)
    return summary.sort_values("total_revenue", ascending=False)


if __name__ == "__main__":
    feat = pd.read_csv(PROCESSED_DATA_DIR / "customer_features.csv")
    drivers = analyze_churn_drivers(feat)
    clv_seg = estimate_clv_by_segment(feat)
    print("\nCLV By Segment:\n", clv_seg[["customer_segment", "customer_count", "total_revenue", "estimated_clv"]])
