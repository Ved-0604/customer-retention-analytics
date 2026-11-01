-- =====================================================================
-- SQL ANALYTICS: CUSTOMER LIFETIME VALUE (HISTORICAL VS ESTIMATED CLV)
-- Customer unit economics, gross margins, and predictive CLV formulations
--
-- METHODOLOGICAL CLARIFICATION:
-- 1. Historical CLV: Actual realized net revenue and gross profit generated to date.
-- 2. Estimated CLV: Forward-looking theoretical value derived from AOV, annual purchase
--    frequency, gross margin %, and expected retention lifespan (1 / Churn Rate).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Customer-Level Historical CLV (Actual Realized Margin)
-- ---------------------------------------------------------------------
WITH customer_order_economics AS (
    SELECT 
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.net_amount) AS total_net_revenue,
        SUM(oi.unit_cost * oi.quantity) AS total_cogs,
        MIN(o.order_date::date) AS first_order_date,
        MAX(o.order_date::date) AS last_order_date
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('Cancelled')
    GROUP BY o.customer_id
),
customer_clv_summary AS (
    SELECT 
        c.customer_id,
        mc.channel_name,
        mc.avg_cpa,
        coe.total_orders,
        coe.total_net_revenue,
        coe.total_cogs,
        ROUND((coe.total_net_revenue - coe.total_cogs), 2) AS historical_gross_profit,
        ROUND((coe.total_net_revenue - coe.total_cogs - mc.avg_cpa), 2) AS net_historical_clv,
        ROUND(coe.total_net_revenue / NULLIF(coe.total_orders, 0), 2) AS customer_aov,
        GREATEST(1, (coe.last_order_date - coe.first_order_date)) AS active_tenure_days
    FROM customers c
    JOIN customer_order_economics coe ON c.customer_id = coe.customer_id
    JOIN marketing_channels mc ON c.acquisition_channel_id = mc.channel_id
)
SELECT 
    customer_id,
    channel_name,
    total_orders,
    ROUND(total_net_revenue, 2) AS historical_net_revenue,
    historical_gross_profit,
    avg_cpa AS acquisition_cost,
    net_historical_clv,
    customer_aov,
    ROUND((historical_gross_profit / NULLIF(total_net_revenue, 0)) * 100.0, 2) AS gross_margin_pct
FROM customer_clv_summary
ORDER BY net_historical_clv DESC;

-- ---------------------------------------------------------------------
-- 2. Estimated Forward-Looking CLV by Acquisition Channel
-- Formula: Estimated CLV = (AOV * Annual Purchase Frequency * Lifespan * Gross Margin %) - CPA
-- ---------------------------------------------------------------------
WITH channel_cohort_stats AS (
    SELECT 
        mc.channel_name,
        mc.avg_cpa,
        COUNT(DISTINCT c.customer_id) AS total_acquired,
        COUNT(o.order_id) AS total_orders,
        SUM(o.net_amount) AS total_revenue,
        SUM((oi.unit_price - oi.unit_cost) * oi.quantity) AS total_margin_dollars,
        -- Churn rate: Inactivity > 90 days as of 2025-12-31
        SUM(CASE WHEN (DATE '2025-12-31' - o_max.max_date) > 90 THEN 1 ELSE 0 END) AS churned_count
    FROM customers c
    JOIN marketing_channels mc ON c.acquisition_channel_id = mc.channel_id
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN (
        SELECT customer_id, MAX(order_date::date) AS max_date 
        FROM orders 
        WHERE order_status NOT IN ('Cancelled') 
        GROUP BY customer_id
    ) o_max ON c.customer_id = o_max.customer_id
    GROUP BY mc.channel_name, mc.avg_cpa
),
channel_clv_model AS (
    SELECT 
        channel_name,
        avg_cpa,
        total_acquired,
        ROUND((total_revenue / NULLIF(total_orders, 0)), 2) AS aov,
        -- Annual purchase frequency (over 2-year observation window)
        ROUND((total_orders / NULLIF(total_acquired, 0) / 2.0), 2) AS annual_frequency,
        ROUND((total_margin_dollars / NULLIF(total_revenue, 0)), 3) AS gross_margin_ratio,
        ROUND((churned_count * 1.0 / NULLIF(total_acquired, 0)), 3) AS churn_rate,
        -- Estimated lifespan in years = 1 / Churn Rate (bounded realistically)
        ROUND(LEAST(4.0, GREATEST(0.5, 1.0 / NULLIF((churned_count * 1.0 / NULLIF(total_acquired, 0)), 0))), 2) AS estimated_lifespan_years
    FROM channel_cohort_stats
)
SELECT 
    channel_name,
    avg_cpa AS acquisition_cost,
    aov,
    annual_frequency,
    ROUND(gross_margin_ratio * 100, 1) AS gross_margin_pct,
    ROUND(churn_rate * 100, 1) AS churn_rate_pct,
    estimated_lifespan_years,
    -- Estimated CLV Calculation
    ROUND((aov * annual_frequency * estimated_lifespan_years * gross_margin_ratio), 2) AS gross_estimated_clv,
    ROUND((aov * annual_frequency * estimated_lifespan_years * gross_margin_ratio - avg_cpa), 2) AS net_estimated_clv,
    -- ROI (CLV to CAC Ratio)
    ROUND(
        (aov * annual_frequency * estimated_lifespan_years * gross_margin_ratio) / NULLIF(avg_cpa, 0), 
        2
    ) AS ltv_to_cac_ratio
FROM channel_clv_model
ORDER BY net_estimated_clv DESC;
