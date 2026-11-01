# Power BI Dimensional Model & DAX Measures Reference
## Customer Retention & Churn Analytics Platform

This document outlines the dimensional model star schema, relationship cardinalities, and production DAX measures required to build the 5-page interactive Power BI dashboard.

---

## 🏛️ Dimensional Model Star Schema

```
                           ┌────────────────────────┐
                           │      Dim_Date          │
                           │ Date, Month, Year, Qtr │
                           └───────────┬────────────┘
                                       │ 1:Many
                                       ▼
┌────────────────────────┐ 1:M ┌────────────────────────┐ M:1 ┌────────────────────────┐
│     Dim_Customers      ├────►│      Fact_Orders       │◄────┤  Dim_MarketingChannels │
│ customer_id, age, city │     │ order_id, order_date,  │     │ channel_id, channel_name│
└───────────┬────────────┘     │ gross, net, status     │     └────────────────────────┘
            │ 1:1              └───────────┬────────────┘
            ▼                              │ 1:Many
┌────────────────────────┐                 ▼
│    Dim_RFMSegments     │     ┌────────────────────────┐ M:1 ┌────────────────────────┐
│ segment, r_score, etc. │     │    Fact_OrderItems     ├────►│      Dim_Products      │
└────────────────────────┘     │ item_id, qty, price    │     │ product_id, category   │
                               └────────────────────────┘     └────────────────────────┘
```

---

## 📐 Core DAX Measures

### 1. Revenue & Order Volume
```dax
Total Gross Revenue = 
SUM(Fact_Orders[gross_amount])

Total Net Revenue = 
CALCULATE(
    SUM(Fact_Orders[net_amount]),
    Fact_Orders[order_status] <> "Cancelled"
)

Total Completed Orders = 
CALCULATE(
    COUNTROWS(Fact_Orders),
    Fact_Orders[order_status] <> "Cancelled"
)

Average Order Value (AOV) = 
DIVIDE([Total Net Revenue], [Total Completed Orders], 0)
```

### 2. Customer Activity & Retention
```dax
Total Customers = 
DISTINCTCOUNT(Dim_Customers[customer_id])

Monthly Active Customers (MAC) = 
CALCULATE(
    DISTINCTCOUNT(Fact_Orders[customer_id]),
    Fact_Orders[order_status] <> "Cancelled"
)

Repeat Customers = 
CALCULATE(
    DISTINCTCOUNT(Fact_Orders[customer_id]),
    FILTER(
        VALUES(Dim_Customers[customer_id]),
        CALCULATE(COUNTROWS(Fact_Orders), Fact_Orders[order_status] <> "Cancelled") >= 2
    )
)

Repeat Purchase Rate % = 
DIVIDE([Repeat Customers], [Total Customers], 0) * 100
```

### 3. Inactivity & Churn Metrics
```dax
Customer Inactivity Days = 
VAR SnapshotDate = DATE(2025, 12, 31)
VAR LastOrderDate = MAX(Fact_Orders[order_date])
RETURN
DATEDIFF(LastOrderDate, SnapshotDate, DAY)

Churned Customers = 
CALCULATE(
    COUNTROWS(Dim_Customers),
    FILTER(
        Dim_Customers,
        [Customer Inactivity Days] > 90
    )
)

Churn Rate % = 
DIVIDE([Churned Customers], [Total Customers], 0) * 100
```

### 4. Customer Lifetime Value (CLV)
```dax
Historical Gross Profit = 
SUMX(
    Fact_OrderItems,
    (Fact_OrderItems[unit_price] - Fact_OrderItems[unit_cost]) * Fact_OrderItems[quantity]
)

Historical CLV = 
DIVIDE([Historical Gross Profit], [Total Customers], 0)

Estimated Lifespan (Years) = 
VAR CalculatedChurn = [Churn Rate %] / 100
RETURN
IF(CalculatedChurn = 0, 4.0, MIN(4.0, MAX(0.5, 1 / CalculatedChurn)))

Estimated CLV = 
VAR AnnualOrders = DIVIDE([Total Completed Orders], [Total Customers] * 2, 0)
VAR MarginRatio = DIVIDE([Historical Gross Profit], [Total Net Revenue], 0)
RETURN
[Average Order Value (AOV)] * AnnualOrders * [Estimated Lifespan (Years)] * MarginRatio
```
