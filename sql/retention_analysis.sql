-- =====================================================================
-- SQL ANALYTICS: COHORT RETENTION & REPEAT PURCHASE BEHAVIOR
-- Monthly acquisition cohorts, retention heatmaps, and channel comparisons
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Monthly Cohort Retention Matrix (Month 0 through Month 12)
-- ---------------------------------------------------------------------
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', signup_date::timestamp) AS cohort_month
    FROM customers
),
order_activities AS (
    SELECT 
        o.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', o.order_date::timestamp) AS activity_month,
        (
            (EXTRACT(YEAR FROM o.order_date::timestamp) - EXTRACT(YEAR FROM c.cohort_month)) * 12 +
            (EXTRACT(MONTH FROM o.order_date::timestamp) - EXTRACT(MONTH FROM c.cohort_month))
        )::INT AS cohort_period
    FROM orders o
    JOIN customer_cohorts c ON o.customer_id = c.customer_id
    WHERE o.order_status NOT IN ('Cancelled')
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),
cohort_retention AS (
    SELECT 
        oa.cohort_month,
        cs.cohort_size,
        oa.cohort_period,
        COUNT(DISTINCT oa.customer_id) AS active_customers,
        ROUND((COUNT(DISTINCT oa.customer_id) * 100.0 / cs.cohort_size), 2) AS retention_rate_pct
    FROM order_activities oa
    JOIN cohort_sizes cs ON oa.cohort_month = cs.cohort_month
    GROUP BY oa.cohort_month, cs.cohort_size, oa.cohort_period
)
SELECT 
    cohort_month,
    cohort_size,
    MAX(CASE WHEN cohort_period = 0 THEN retention_rate_pct END) AS m0_retention_pct,
    MAX(CASE WHEN cohort_period = 1 THEN retention_rate_pct END) AS m1_retention_pct,
    MAX(CASE WHEN cohort_period = 2 THEN retention_rate_pct END) AS m2_retention_pct,
    MAX(CASE WHEN cohort_period = 3 THEN retention_rate_pct END) AS m3_retention_pct,
    MAX(CASE WHEN cohort_period = 6 THEN retention_rate_pct END) AS m6_retention_pct,
    MAX(CASE WHEN cohort_period = 12 THEN retention_rate_pct END) AS m12_retention_pct
FROM cohort_retention
GROUP BY cohort_month, cohort_size
ORDER BY cohort_month;

-- ---------------------------------------------------------------------
-- 2. Overall Customer Repeat Purchase Rate
-- ---------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        c.customer_id,
        COUNT(o.order_id) AS total_orders
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_id
)
SELECT 
    COUNT(*) AS total_customers,
    SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
    SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END) AS one_time_buyers,
    SUM(CASE WHEN total_orders = 0 THEN 1 ELSE 0 END) AS zero_order_signups,
    ROUND(
        (SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) AS repeat_purchase_rate_pct
FROM customer_order_counts;

-- ---------------------------------------------------------------------
-- 3. Retention & Repeat Rates by Acquisition Marketing Channel
-- ---------------------------------------------------------------------
WITH channel_customer_orders AS (
    SELECT 
        c.customer_id,
        mc.channel_name,
        mc.channel_type,
        mc.avg_cpa,
        COUNT(o.order_id) AS total_orders,
        COALESCE(SUM(o.net_amount), 0.0) AS total_customer_spend
    FROM customers c
    JOIN marketing_channels mc ON c.acquisition_channel_id = mc.channel_id
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_id, mc.channel_name, mc.channel_type, mc.avg_cpa
)
SELECT 
    channel_name,
    channel_type,
    avg_cpa,
    COUNT(customer_id) AS acquired_customers,
    SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND((SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id)), 2) AS repeat_rate_pct,
    ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
    ROUND(AVG(total_customer_spend), 2) AS avg_spend_per_customer,
    ROUND((AVG(total_customer_spend) - avg_cpa), 2) AS avg_net_customer_margin
FROM channel_customer_orders
GROUP BY channel_name, channel_type, avg_cpa
ORDER BY repeat_rate_pct DESC;
