-- =====================================================================
-- SQL ANALYTICS: CUSTOMER CHURN & HAZARD DRIVER ANALYSIS
-- Transparent 90-day inactivity churn model, behavioral segmentation, and driver analysis
--
-- METHODOLOGY & BUSINESS LIMITATIONS:
-- Definition: A customer is classified as 'Churned' if they have placed no valid orders
-- in the 90 days prior to the analysis snapshot date (2025-12-31 23:59:59).
--
-- Key Limitations to Defend in Interviews:
-- 1. Arbitrary Threshold: Annual or seasonal shoppers (e.g. buying gifts every Nov/Dec)
--    are falsely marked as churned during summer months.
-- 2. Right-Censoring: Customers acquired late in the observation window (e.g. Nov 2025)
--    cannot yet be fairly assessed under a 90-day window.
-- 3. Inactivity vs Defection: Inactivity does not guarantee customer intent to leave;
--    they may simply have longer inter-purchase replacement cycles.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Overall Churn Rate & Customer Inactivity Status
-- ---------------------------------------------------------------------
WITH customer_activity AS (
    SELECT 
        c.customer_id,
        c.signup_date,
        MAX(o.order_date::timestamp) AS last_order_date,
        (DATE '2025-12-31' - MAX(o.order_date::date)) AS days_since_last_order,
        COUNT(o.order_id) AS total_orders,
        COALESCE(SUM(o.net_amount), 0.0) AS total_spend
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_id, c.signup_date
)
SELECT 
    COUNT(*) AS total_customer_base,
    SUM(CASE WHEN days_since_last_order <= 90 THEN 1 ELSE 0 END) AS active_retained_customers,
    SUM(CASE WHEN days_since_last_order > 90 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        (SUM(CASE WHEN days_since_last_order > 90 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) AS overall_churn_rate_pct,
    ROUND(AVG(days_since_last_order), 1) AS avg_days_inactive
FROM customer_activity;

-- ---------------------------------------------------------------------
-- 2. Inactivity Distribution Bins
-- ---------------------------------------------------------------------
WITH customer_recency AS (
    SELECT 
        c.customer_id,
        (DATE '2025-12-31' - MAX(o.order_date::date)) AS days_inactive,
        COALESCE(SUM(o.net_amount), 0.0) AS total_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_id
)
SELECT 
    CASE 
        WHEN days_inactive <= 30 THEN '01. Active (0-30 days)'
        WHEN days_inactive BETWEEN 31 AND 60 THEN '02. Cooling Down (31-60 days)'
        WHEN days_inactive BETWEEN 61 AND 90 THEN '03. High Risk (61-90 days)'
        WHEN days_inactive BETWEEN 91 AND 180 THEN '04. Lapsed / Churned (91-180 days)'
        ELSE '05. Deeply Churned (180+ days)'
    END AS inactivity_tier,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_recency), 2) AS customer_pct,
    ROUND(SUM(total_spend), 2) AS total_revenue_at_stake
FROM customer_recency
GROUP BY 1
ORDER BY 1;

-- ---------------------------------------------------------------------
-- 3. Churn Rate by Discount Dependency (Bargain Hunters vs Full-Price)
-- ---------------------------------------------------------------------
WITH customer_discount_profile AS (
    SELECT 
        c.customer_id,
        (DATE '2025-12-31' - MAX(o.order_date::date)) AS days_inactive,
        COUNT(o.order_id) AS total_orders,
        SUM(o.discount_amount) / NULLIF(SUM(o.gross_amount), 0) AS avg_discount_rate
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_id
)
SELECT 
    CASE 
        WHEN avg_discount_rate = 0.00 THEN 'Zero Discount (Full Price)'
        WHEN avg_discount_rate < 0.10 THEN 'Low Discount (< 10%)'
        WHEN avg_discount_rate BETWEEN 0.10 AND 0.20 THEN 'Moderate Discount (10-20%)'
        ELSE 'High Discount (> 20% Bargain Hunter)'
    END AS discount_segment,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN days_inactive > 90 THEN 1 ELSE 0 END) AS churned_count,
    ROUND(
        (SUM(CASE WHEN days_inactive > 90 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) AS churn_rate_pct
FROM customer_discount_profile
GROUP BY 1
ORDER BY churn_rate_pct ASC;

-- ---------------------------------------------------------------------
-- 4. Churn Rate by Order Cancellation Experience
-- ---------------------------------------------------------------------
WITH customer_experience AS (
    SELECT 
        c.customer_id,
        (DATE '2025-12-31' - MAX(CASE WHEN o.order_status NOT IN ('Cancelled') THEN o.order_date::date END)) AS days_inactive,
        SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders_count
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
)
SELECT 
    CASE 
        WHEN cancelled_orders_count = 0 THEN '0 Cancellations (Smooth Experience)'
        WHEN cancelled_orders_count = 1 THEN '1 Cancellation (Friction Event)'
        ELSE '2+ Cancellations (Severe Friction)'
    END AS cancellation_experience,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN days_inactive > 90 THEN 1 ELSE 0 END) AS churned_count,
    ROUND(
        (SUM(CASE WHEN days_inactive > 90 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) AS churn_rate_pct
FROM customer_experience
GROUP BY 1
ORDER BY MIN(cancelled_orders_count);

-- ---------------------------------------------------------------------
-- 5. Churn Rate by Acquisition Marketing Channel
-- ---------------------------------------------------------------------
WITH channel_churn AS (
    SELECT 
        c.customer_id,
        mc.channel_name,
        (DATE '2025-12-31' - MAX(o.order_date::date)) AS days_inactive
    FROM customers c
    JOIN marketing_channels mc ON c.acquisition_channel_id = mc.channel_id
    JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_id, mc.channel_name
)
SELECT 
    channel_name,
    COUNT(customer_id) AS total_customers,
    SUM(CASE WHEN days_inactive > 90 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        (SUM(CASE WHEN days_inactive > 90 THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id)), 
        2
    ) AS channel_churn_rate_pct
FROM channel_churn
GROUP BY channel_name
ORDER BY channel_churn_rate_pct DESC;
