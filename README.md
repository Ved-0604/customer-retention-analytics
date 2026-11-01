# Customer Retention & Churn Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Executive_Dashboard-F2C811.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-green.svg)](https://pytest.org/)

An enterprise-grade, end-to-end e-commerce customer analytics platform engineered to diagnose customer retention, identify churn drivers, calculate Customer Lifetime Value (CLV), execute RFM segmentation, and deliver actionable executive retention strategies.

Built to simulate real-world analytics engineering workflows at scale: relational database modeling in **PostgreSQL**, statistical and cohort analytics in **Python**, validation with automated **pytest** suites, and executive reporting in **Power BI**.

---

## 🏗️ Architecture & Tech Stack

```
                              ┌──────────────────────────────────────────────┐
                              │            Raw Relational Data               │
                              │ 10,000+ Customers | 100,000+ Transactions    │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                                     ▼
                              ┌──────────────────────────────────────────────┐
                              │     Python ETL & Feature Engineering         │
                              │ (src/data_cleaning.py, feature_eng.py)       │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                                     ▼
                              ┌──────────────────────────────────────────────┐
                              │        PostgreSQL Analytical Warehouse       │
                              │  Normalized Tables, Constraints, Indexes     │
                              │     Analytical Views (RFM, Cohorts, CLV)     │
                              └──────────────────────┬───────────────────────┘
                                                     │
                         ┌───────────────────────────┴───────────────────────────┐
                         ▼                                                       ▼
       ┌───────────────────────────────────┐                   ┌───────────────────────────────────┐
       │   Advanced SQL & Python Analytics │                   │     Power BI Executive Dashboard  │
       │  - Monthly Cohort Heatmaps        │                   │  Page 1: Executive Overview       │
       │  - Recency-Frequency-Monetary     │                   │  Page 2: Customer Retention       │
       │  - 90-Day Inactivity Churn Model  │                   │  Page 3: Churn Driver Analysis    │
       │  - Historical vs Estimated CLV    │                   │  Page 4: RFM Segmentation         │
       └───────────────────────────────────┘                   │  Page 5: Customer Lifetime Value  │
                                                               └───────────────────────────────────┘
```

- **Database**: PostgreSQL (Relational schema, 3NF, indexed foreign keys, analytical views).
- **Analytics Engineering / Data Processing**: Python 3.13 (`pandas`, `numpy`, `scipy`, `scikit-learn`, `sqlalchemy`, `duckdb`).
- **Testing & Quality Assurance**: `pytest` test suites validating data integrity, no future leakage, and SQL-Python metric alignment.
- **Business Intelligence**: Power BI (5-page interactive dashboard with DAX measures and dimensional model).
- **Business Strategy**: Actionable Executive Recommendation Memo addressed to Head of Growth / CMO.

---

## 📁 Repository Structure

```
customer-retention-analytics/
│
├── data/
│   ├── raw/                           # Raw synthetic relational CSVs (100k+ transactions)
│   └── processed/                     # Cleaned, validated, and enriched analytical datasets
│
├── notebooks/
│   ├── 01_data_exploration.ipynb      # Initial EDA, missingness, distributions
│   ├── 02_data_cleaning.ipynb         # Data auditing, type casting, deduplication
│   ├── 03_rfm_analysis.ipynb          # RFM scoring, quantile segmentation, revenue impact
│   ├── 04_churn_analysis.ipynb        # Inactivity churn modeling, hazard & driver analysis
│   └── 05_clv_analysis.ipynb          # Historical CLV vs Estimated Predictive CLV
│
├── sql/
│   ├── schema.sql                     # PostgreSQL DDL with PK, FK, constraints, indexes
│   ├── data_quality.sql               # Data sanity audits and referential integrity tests
│   ├── revenue_analysis.sql           # MoM growth, category performance, AOV
│   ├── retention_analysis.sql         # Monthly acquisition cohort retention matrices
│   ├── churn_analysis.sql             # 90-day churn rates, tenure, cancellation analysis
│   ├── rfm_segmentation.sql           # NTILE window functions and customer tiering
│   └── clv_analysis.sql               # Cumulative margin and customer lifetime value
│
├── powerbi/
│   └── customer_retention_dashboard.pbix  # Interactive Power BI report & DAX specifications
│
├── reports/
│   └── executive_recommendation_memo.md   # Executive briefing for VP of Growth / CMO
│
├── src/
│   ├── config.py                      # Global paths, constants, and database configurations
│   ├── data_generation.py             # Reproducible synthetic data generator (seed=42)
│   ├── data_cleaning.py               # Production cleaning and validation pipelines
│   ├── feature_engineering.py         # Customer-level feature aggregation and metrics
│   └── analysis.py                    # Modular statistical functions for cohorts & RFM
│
├── tests/
│   ├── test_environment.py            # Environment, package, and config tests
│   ├── test_data_generation.py        # Entity volume and referential integrity tests
│   ├── test_data_quality.py           # Anomaly, missing value, and constraint checks
│   └── test_metrics.py                # Reconciliation between SQL and Python KPIs
│
├── .env.example                       # Environment template for DB credentials
├── .gitignore                         # Standard git ignore rules
├── requirements.txt                   # Pinned dependency manifest
└── README.md                          # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ (or Docker / DuckDB for local verification)
- Git

### 2. Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd customer-retention-analytics

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 3. Verify Installation
```bash
pytest tests/test_environment.py
```
