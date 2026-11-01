"""
Generates the 5 project Jupyter Notebooks matching professional portfolio standards.
"""

import json
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.13"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }


def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }


def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }


# Notebook 1: Data Exploration
nb1_cells = [
    md_cell("# 01. Exploratory Data Analysis (EDA)\n## E-Commerce Customer Retention & Churn Analytics\nThis notebook performs initial exploratory data analysis on the raw relational e-commerce tables: customers, orders, order items, products, payments, and marketing channels."),
    code_cell("import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom pathlib import Path\n\nsns.set_theme(style='whitegrid')\nRAW_DIR = Path('../data/raw')\n\ncustomers = pd.read_csv(RAW_DIR / 'customers.csv')\norders = pd.read_csv(RAW_DIR / 'orders.csv')\nproducts = pd.read_csv(RAW_DIR / 'products.csv')\nprint(f'Customers: {len(customers):,}')\nprint(f'Orders: {len(orders):,}')\nprint(f'Products: {len(products):,}')"),
    md_cell("### Customer Age & Demographic Distribution"),
    code_cell("plt.figure(figsize=(10, 4))\nsns.histplot(customers['age'], bins=25, kde=True, color='royalblue')\nplt.title('Customer Age Distribution (Mean ~ 35 Years)')\nplt.xlabel('Age')\nplt.ylabel('Count')\nplt.show()"),
    md_cell("### Order Value Distributions and Outliers"),
    code_cell("plt.figure(figsize=(10, 4))\nsns.boxplot(x=orders['net_amount'], color='mediumaquamarine')\nplt.title('Order Net Amount Boxplot (Distribution & Outliers)')\nplt.xlabel('Net Amount ($)')\nplt.show()")
]

# Notebook 2: Data Cleaning
nb2_cells = [
    md_cell("# 02. Data Cleaning & Referential Integrity Auditing\nValidates types, verifies nulls and duplicates, audits foreign key relationships, and certifies financial ledger balancing."),
    code_cell("import pandas as pd\nfrom pathlib import Path\n\nRAW_DIR = Path('../data/raw')\nPROCESSED_DIR = Path('../data/processed')\n\nfrom src.data_cleaning import DataCleaner\ncleaner = DataCleaner(raw_dir=RAW_DIR, processed_dir=PROCESSED_DIR)\nraw_tables = cleaner.load_raw_data()\ncleaned_tables, audit_report = cleaner.clean_and_audit(raw_tables)\ncleaner.save_processed(cleaned_tables)\nprint('Audit Status:', audit_report.validation_status)"),
    code_cell("for table_name, df in cleaned_tables.items():\n    print(f'{table_name:20s}: {len(df):,} rows | 0 Nulls: {df.isna().sum().sum() == 0}')")
]

# Notebook 3: RFM Analysis
nb3_cells = [
    md_cell("# 03. RFM Customer Segmentation\nComputes Recency, Frequency, and Monetary Value, applies quintile scoring (1-5), and assigns 8 distinct behavioral tiers."),
    code_cell("import pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom src.analysis import calculate_rfm_segments\n\nfeatures = pd.read_csv('../data/processed/customer_features.csv')\nrfm_df = calculate_rfm_segments(features)\n\nseg_summary = rfm_df.groupby('customer_segment').agg(\n    customers=('customer_id', 'count'),\n    total_revenue=('lifetime_net_revenue', 'sum'),\n    avg_spend=('lifetime_net_revenue', 'mean'),\n    avg_orders=('lifetime_orders', 'mean'),\n    avg_recency=('recency_days', 'mean')\n).reset_index().sort_values('total_revenue', ascending=False)\nseg_summary"),
    code_cell("plt.figure(figsize=(12, 5))\nsns.barplot(data=seg_summary, x='customer_segment', y='total_revenue', palette='Blues_r')\nplt.title('Total Revenue by RFM Customer Segment')\nplt.xticks(rotation=30)\nplt.ylabel('Total Net Revenue ($)')\nplt.show()")
]

# Notebook 4: Churn Analysis
nb4_cells = [
    md_cell("# 04. Customer Churn & Inactivity Driver Analysis\nDefines 90-day inactivity churn, evaluates churn hazard across discount dependency, cancellations, channels, and fits an interpretable driver model."),
    code_cell("import pandas as pd\nimport seaborn as sns\nimport matplotlib.pyplot as plt\nfrom src.analysis import analyze_churn_drivers\n\nfeatures = pd.read_csv('../data/processed/customer_features.csv')\ndrivers = analyze_churn_drivers(features)\nprint(drivers)"),
    code_cell("plt.figure(figsize=(10, 4))\nsns.barplot(data=drivers, x='odds_ratio', y='feature', palette='mako')\nplt.axvline(1.0, color='red', linestyle='--', label='Neutral Hazard (OR=1.0)')\nplt.title('Churn Driver Odds Ratios (Logistic Regression)')\nplt.xlabel('Odds Ratio (Values > 1 increase churn hazard)')\nplt.legend()\nplt.show()")
]

# Notebook 5: CLV Analysis
nb5_cells = [
    md_cell("# 05. Customer Lifetime Value (Historical vs Estimated CLV)\nEvaluates realized gross profit versus forward-looking estimated CLV and calculates LTV/CAC across acquisition channels."),
    code_cell("import pandas as pd\nfrom src.analysis import estimate_clv_by_segment\n\nfeatures = pd.read_csv('../data/processed/customer_features.csv')\nclv_summary = estimate_clv_by_segment(features)\nclv_summary[['customer_segment', 'customer_count', 'total_revenue', 'avg_gross_profit', 'estimated_clv', 'revenue_share_pct']]")
]

notebooks = {
    "01_data_exploration.ipynb": nb1_cells,
    "02_data_cleaning.ipynb": nb2_cells,
    "03_rfm_analysis.ipynb": nb3_cells,
    "04_churn_analysis.ipynb": nb4_cells,
    "05_clv_analysis.ipynb": nb5_cells,
}

for filename, cells in notebooks.items():
    nb_content = make_notebook(cells)
    with open(NOTEBOOKS_DIR / filename, "w") as f:
        json.dump(nb_content, f, indent=2)
    print(f"Generated {filename}")
