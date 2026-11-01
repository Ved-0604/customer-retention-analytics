# Customer Retention & Churn Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791.svg)](https://www.postgresql.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-FFF000.svg)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Executive_Dashboard-F2C811.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-green.svg)](https://pytest.org/)

An enterprise-grade, end-to-end e-commerce customer analytics platform engineered from scratch. Simulates real-world data engineering, relational database modeling in **PostgreSQL**, cohort retention and churn driver modeling in **Python**, validation with automated **pytest** suites, and executive reporting in **Power BI**.

---

## 🏗️ Architecture & Platform Overview

```
                               ┌──────────────────────────────────────────────┐
                               │           Raw Relational Data                │
                               │  15,000 Customers | 108,184 Transactions     │
                               │  174,298 Line Items | 12 Product Categories  │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │       Data Cleaning & Quality Pipeline       │
                               │ (src/data_cleaning.py, feature_eng.py)       │
                               │ Penny-exact balancing · Zero nulls & orphans │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │       PostgreSQL Analytical Warehouse        │
                               │   Normalized 3NF Tables, CHECK Constraints   │
                               │    B-Tree Indexes & Analytical SQL Views     │
                               └──────────────────────┬───────────────────────┘
                                                      │
                         ┌────────────────────────────┴───────────────────────────┐
                         ▼                                                        ▼
       ┌───────────────────────────────────┐                    ┌───────────────────────────────────┐
       │   Advanced SQL & Statistical ML   │                    │     Power BI Executive Dashboard  │
       │  - Monthly Cohort Heatmaps (M0-M12)│                   │  Page 1: Executive Overview       │
       │  - RFM Quintile Tiering (8 Tiers) │                    │  Page 2: Customer Retention       │
       │  - 90-Day Inactivity Churn Model  │                    │  Page 3: Churn Driver Analysis    │
       │  - Realized Margin vs Est. CLV    │                    │  Page 4: RFM Segmentation         │
       │  - Logistic Regression Odds Ratios│                    │  Page 5: Customer Lifetime Value  │
       └───────────────────────────────────┘                    └───────────────────────────────────┘
```

---

## 📊 Core Business & Platform Metrics

- **Total Net Revenue**: **\$21,787,238.47** (\$23.29M Gross GMV).
- **Average Order Value (AOV)**: **\$201.39** across 108,184 completed orders.
- **Customer Base**: **15,000 unique accounts** across 20 metropolitan areas.
- **Repeat Purchase Rate**: **54.8%** (8,217 repeat buyers).
- **90-Day Inactivity Churn Rate**: **58.1%** (8,722 churned accounts).
- **Top Segment Concentration (Pareto)**: The top **20% of customers (Champions & Loyalists) account for 74.0% of total platform revenue (\$16.13M)**.
- **Revenue at Immediate Risk**: **\$956.7K** across 980 high-spending customers currently in the "At Risk" and "Cannot Lose Them" dormancy zones.

---

## 📁 Repository Directory Structure

```
customer-retention-analytics/
│
├── data/
│   ├── raw/                               # Raw synthetic relational CSVs (108k+ orders)
│   ├── processed/                         # Cleaned, validated CSVs and customer_features.csv
│   └── ecommerce_analytics.duckdb         # Zero-dependency local OLAP SQL database
│
├── notebooks/
│   ├── 01_data_exploration.ipynb          # Exploratory Data Analysis & distributions
│   ├── 02_data_cleaning.ipynb             # Nulls, duplicates, and referential audits
│   ├── 03_rfm_analysis.ipynb              # Recency, Frequency, Monetary scoring
│   ├── 04_churn_analysis.ipynb            # Hazard rates & logistic regression drivers
│   └── 05_clv_analysis.ipynb              # Realized gross margin vs estimated CLV
│
├── sql/
│   ├── schema.sql                         # PostgreSQL 3NF DDL with PK, FK, and indexes
│   ├── data_quality.sql                   # Referential integrity and balance checks
│   ├── revenue_analysis.sql               # MoM growth, category performance, Pareto spend
│   ├── retention_analysis.sql             # Monthly cohort matrices (Month 0 to Month 12)
│   ├── churn_analysis.sql                 # Inactivity bins, cancellation impact, channel churn
│   ├── rfm_segmentation.sql               # NTILE(5) scoring and 8 behavioral tiers
│   └── clv_analysis.sql                   # Historical gross profit vs predictive CLV
│
├── powerbi/
│   ├── DAX_MEASURES.md                    # Star schema diagram & production DAX formulas
│   └── customer_retention_dashboard.pbix  # Power BI report template
│
├── reports/
│   ├── executive_recommendation_memo.md   # Formal briefing for Head of Growth / CMO
│   └── interactive_bi_platform.html       # Standalone 5-Page Interactive BI Dashboard
│
├── src/
│   ├── config.py                          # Global parameters, paths, and DB configs
│   ├── data_generation.py                 # Reproducible synthetic generator (Seed=42)
│   ├── data_cleaning.py                   # Type coercion, reconciliation, and audit logger
│   ├── db_loader.py                       # PostgreSQL and DuckDB ingestion pipeline
│   ├── feature_engineering.py             # Customer-level analytical feature store
│   ├── analysis.py                        # Statistical RFM, cohorts, and churn models
│   └── generate_notebooks.py              # Automated Jupyter notebook builder
│
├── tests/
│   ├── test_environment.py                # System runtime and dependency import checks
│   ├── test_data_generation.py            # Scale, date span, and FK integrity checks
│   ├── test_data_quality.py               # Financial ledger balancing and causality
│   └── test_metrics.py                    # SQL vs Python KPI reconciliation (100% parity)
│
├── .env.example                           # Configuration credentials template
├── .gitignore                             # Ignored artifacts, virtual environments, and DBs
├── requirements.txt                       # Pinned Python package manifest
└── README.md                              # Complete platform documentation
```

---

## 🔍 Technical Decisions & Interview Defense Guide

### 1. Why Define Churn as 90 Days of Continuous Inactivity?
- **Business Rationale**: In fast-moving e-commerce with a median repeat purchase interval of ~33 days, 90 days represents approximately $3\times$ the inter-purchase cycle.
- **Defending Limitations in Interviews**:
  - *Seasonal Buyers*: A customer who purchases holiday gifts every November will be erroneously flagged as churned in June.
  - *Right-Censoring*: Recently acquired users (e.g., acquired in late November) have not lived long enough to reach 90 days of observation.
  - *Dormancy vs. True Defection*: Inactivity signals disengagement, not necessarily that the customer deleted their account or switched to a competitor.

### 2. How Was Financial Ledger Consistency Guaranteed?
Rather than generating totals independently:
1. Every order's gross amount is strictly the sum of its associated `order_items`.
2. Net amount dynamically enforces business rules: $\text{Net} = \text{Gross} - \text{Discount} + \text{Shipping}$.
3. Payments reconcile penny-for-penny with order net amounts.
4. If any discrepancy exceeds \$0.01, automated pytest checks fail immediately.

### 3. Historical CLV vs. Estimated Forward-Looking CLV
- **Historical CLV**: The actual cumulative gross margin realized from past transactions minus acquisition CPA.
- **Estimated CLV**: A forward-looking projection based on customer unit economics:
  $$\text{Estimated CLV} = \text{AOV} \times \text{Annual Order Frequency} \times \text{Estimated Lifespan} \times \text{Gross Margin \%} - \text{CAC}$$
  where $\text{Estimated Lifespan} = \frac{1}{\text{Churn Rate}}$.

---

## 🚀 Reproduction & Execution Instructions

```bash
# 1. Activate Virtual Environment
cd customer-retention-analytics
source .venv/bin/activate

# 2. Run Test Suite (16 Automated Tests)
pytest tests/ -v

# 3. Regenerate Datasets (Optional)
python src/data_generation.py
python src/data_cleaning.py
python src/db_loader.py
python src/feature_engineering.py
```
