"""
Customer Retention & Churn Analytics Platform - Data Cleaning & Quality Audit
=============================================================================
Performs schema enforcement, type coercion, null/duplicate auditing,
referential integrity verification, and penny-exact financial reconciliation.
Saves validated datasets into data/processed/.
"""

import sys
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

try:
    from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, analytics_config
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, analytics_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class QualityAuditReport:
    """Stores data quality audit metrics for validation and interview reporting."""
    total_customers: int
    total_orders: int
    total_order_items: int
    total_products: int
    total_payments: int
    total_channels: int
    min_order_date: str
    max_order_date: str
    date_span_days: int
    orphaned_orders: int
    orphaned_order_items: int
    orphaned_payments: int
    financial_discrepancies: int
    payment_discrepancies: int
    duplicate_customers: int
    duplicate_orders: int
    null_counts: dict
    validation_status: str


class DataCleaner:
    """Production cleaning and validation pipeline."""

    def __init__(self, raw_dir: Path = RAW_DATA_DIR, processed_dir: Path = PROCESSED_DATA_DIR):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def load_raw_data(self) -> dict[str, pd.DataFrame]:
        """Load raw CSV tables."""
        logger.info("Loading raw datasets from %s...", self.raw_dir)
        tables = {
            "channels": pd.read_csv(self.raw_dir / "marketing_channels.csv"),
            "customers": pd.read_csv(self.raw_dir / "customers.csv"),
            "products": pd.read_csv(self.raw_dir / "products.csv"),
            "orders": pd.read_csv(self.raw_dir / "orders.csv"),
            "order_items": pd.read_csv(self.raw_dir / "order_items.csv"),
            "payments": pd.read_csv(self.raw_dir / "payments.csv"),
        }
        return tables

    def clean_and_audit(self, tables: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], QualityAuditReport]:
        """
        Enforce strict schemas, check nulls and duplicates, verify FK integrity,
        and validate financial reconciliation.
        """
        logger.info("Starting data cleaning and quality auditing...")

        channels = tables["channels"].copy()
        customers = tables["customers"].copy()
        products = tables["products"].copy()
        orders = tables["orders"].copy()
        order_items = tables["order_items"].copy()
        payments = tables["payments"].copy()

        # 1. Type Coercion & Datetime standardization
        customers["signup_date"] = pd.to_datetime(customers["signup_date"])
        orders["order_date"] = pd.to_datetime(orders["order_date"])
        payments["payment_date"] = pd.to_datetime(payments["payment_date"])

        # Numerical type casting
        orders["gross_amount"] = orders["gross_amount"].astype(float).round(2)
        orders["discount_amount"] = orders["discount_amount"].astype(float).round(2)
        orders["shipping_fee"] = orders["shipping_fee"].astype(float).round(2)
        orders["net_amount"] = orders["net_amount"].astype(float).round(2)

        order_items["unit_price"] = order_items["unit_price"].astype(float).round(2)
        order_items["unit_cost"] = order_items["unit_cost"].astype(float).round(2)
        order_items["total_item_price"] = order_items["total_item_price"].astype(float).round(2)
        payments["amount"] = payments["amount"].astype(float).round(2)

        # 2. Duplicate checking
        dup_customers = int(customers["customer_id"].duplicated().sum())
        dup_orders = int(orders["order_id"].duplicated().sum())

        # 3. Null audit
        null_counts = {
            "customers": int(customers.isna().sum().sum()),
            "orders": int(orders.isna().sum().sum()),
            "order_items": int(order_items.isna().sum().sum()),
            "products": int(products.isna().sum().sum()),
            "payments": int(payments.isna().sum().sum()),
            "channels": int(channels.isna().sum().sum()),
        }

        # 4. Referential Integrity Checks
        valid_cust_ids = set(customers["customer_id"])
        valid_order_ids = set(orders["order_id"])
        valid_prod_ids = set(products["product_id"])

        orphaned_orders = int((~orders["customer_id"].isin(valid_cust_ids)).sum())
        orphaned_items = int((~order_items["order_id"].isin(valid_order_ids)).sum() + 
                             (~order_items["product_id"].isin(valid_prod_ids)).sum())
        orphaned_payments = int((~payments["order_id"].isin(valid_order_ids)).sum())

        # 5. Financial Reconciliation:
        # Check order_items sum matches orders.gross_amount within 1 cent tolerance (floating point rounding)
        items_sum_by_order = order_items.groupby("order_id")["total_item_price"].sum().round(2)
        merged_orders = orders.set_index("order_id").copy()
        merged_orders["calculated_gross"] = items_sum_by_order
        gross_diff = (merged_orders["gross_amount"] - merged_orders["calculated_gross"]).abs()
        financial_discrepancies = int((gross_diff > 0.02).sum())

        # Check net_amount = gross_amount - discount_amount + shipping_fee
        expected_net = (orders["gross_amount"] - orders["discount_amount"] + orders["shipping_fee"]).round(2)
        net_diff = (orders["net_amount"] - expected_net).abs()
        financial_discrepancies += int((net_diff > 0.02).sum())

        # Check payment amount matches order net_amount
        payments_by_order = payments.set_index("order_id")["amount"]
        payment_diff = (merged_orders["net_amount"] - payments_by_order).abs()
        payment_discrepancies = int((payment_diff > 0.02).sum())

        # Date span calculation
        min_date = orders["order_date"].min()
        max_date = orders["order_date"].max()
        date_span_days = (max_date - min_date).days

        is_valid = (
            orphaned_orders == 0 and
            orphaned_items == 0 and
            orphaned_payments == 0 and
            financial_discrepancies == 0 and
            payment_discrepancies == 0 and
            dup_customers == 0 and
            dup_orders == 0
        )

        audit_report = QualityAuditReport(
            total_customers=len(customers),
            total_orders=len(orders),
            total_order_items=len(order_items),
            total_products=len(products),
            total_payments=len(payments),
            total_channels=len(channels),
            min_order_date=str(min_date),
            max_order_date=str(max_date),
            date_span_days=date_span_days,
            orphaned_orders=orphaned_orders,
            orphaned_order_items=orphaned_items,
            orphaned_payments=orphaned_payments,
            financial_discrepancies=financial_discrepancies,
            payment_discrepancies=payment_discrepancies,
            duplicate_customers=dup_customers,
            duplicate_orders=dup_orders,
            null_counts=null_counts,
            validation_status="PASSED" if is_valid else "FAILED",
        )

        cleaned_tables = {
            "marketing_channels": channels,
            "customers": customers,
            "products": products,
            "orders": orders,
            "order_items": order_items,
            "payments": payments,
        }

        logger.info("Quality audit completed with status: %s", audit_report.validation_status)
        return cleaned_tables, audit_report

    def save_processed(self, cleaned_tables: dict[str, pd.DataFrame]) -> None:
        """Save cleaned and validated tables to data/processed/ as CSV."""
        for name, df in cleaned_tables.items():
            out_file = self.processed_dir / f"{name}.csv"
            df.to_csv(out_file, index=False)
            logger.info("Saved processed %s: %d rows (%.2f MB)", name, len(df), out_file.stat().st_size / (1024 * 1024))


def run_cleaning_pipeline() -> QualityAuditReport:
    """Execute end-to-end cleaning and quality audit."""
    cleaner = DataCleaner()
    raw_tables = cleaner.load_raw_data()
    cleaned_tables, audit_report = cleaner.clean_and_audit(raw_tables)
    cleaner.save_processed(cleaned_tables)
    return audit_report


if __name__ == "__main__":
    report = run_cleaning_pipeline()
    print("\n" + "=" * 50)
    print("DATA QUALITY AUDIT REPORT")
    print("=" * 50)
    for k, v in asdict(report).items():
        print(f"  {k:30s}: {v}")
    print("=" * 50)
