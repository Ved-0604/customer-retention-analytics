-- =====================================================================
-- SQL ANALYTICS: REVENUE, GROWTH & PRODUCT CATEGORY PERFORMANCE
-- Comprehensive analytical queries using CTEs, window functions, and aggregations
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Monthly Active Customers (MAC) & Month-over-Month (MoM) Growth
-- ---------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', order_date::timestamp) AS order_month,
        COUNT(DISTINCT customer_id) AS monthly_active_customers,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(net_amount), 2) AS total_net_revenue,
        ROUND(AVG(net_amount), 2) AS average_order_value
    FROM orders
    WHERE order_status NOT IN ('Cancelled')
    GROUP BY DATE_TRUNC('month', order_date::timestamp)
),
mom_growth AS (
    SELECT 
        order_month,
        monthly_active_customers,
        total_orders,
        total_net_revenue,
        average_order_value,
        LAG(total_net_revenue, 1) OVER (ORDER BY order_month) AS prev_month_revenue,
        LAG(monthly_active_customers, 1) OVER (ORDER BY order_month) AS prev_month_mac
    FROM monthly_metrics
)
SELECT 
    order_month,
    monthly_active_customers,
    total_orders,
    total_net_revenue,
    average_order_value,
    ROUND(
        ((total_net_revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0)) * 100.0, 
        2
    ) AS mom_revenue_growth_pct,
    ROUND(
        ((monthly_active_customers - prev_month_mac) * 100.0 / NULLIF(prev_month_mac, 0)), 
        2
    ) AS mom_active_customers_growth_pct
FROM mom_growth
ORDER BY order_month;

-- ---------------------------------------------------------------------
-- 2. Category Performance & Gross Margin Analysis
-- ---------------------------------------------------------------------
WITH item_margins AS (
    SELECT 
        oi.order_id,
        p.category,
        p.product_id,
        oi.quantity,
        oi.unit_price,
        oi.unit_cost,
        oi.total_item_price,
        ROUND((oi.unit_price - oi.unit_cost) * oi.quantity, 2) AS gross_margin_dollar
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status NOT IN ('Cancelled')
)
SELECT 
    category,
    COUNT(DISTINCT order_id) AS orders_count,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(total_item_price), 2) AS total_gross_revenue,
    ROUND(SUM(gross_margin_dollar), 2) AS total_gross_profit,
    ROUND((SUM(gross_margin_dollar) / NULLIF(SUM(total_item_price), 0)) * 100.0, 2) AS gross_margin_pct,
    ROUND(AVG(unit_price), 2) AS avg_selling_price
FROM item_margins
GROUP BY category
ORDER BY total_gross_revenue DESC;

-- ---------------------------------------------------------------------
-- 3. Customer Revenue Concentration (Pareto 80/20 Cumulative Distribution)
-- ---------------------------------------------------------------------
WITH customer_spend AS (
    SELECT 
        customer_id,
        ROUND(SUM(net_amount), 2) AS total_customer_spend,
        COUNT(order_id) AS lifetime_orders
    FROM orders
    WHERE order_status NOT IN ('Cancelled')
    GROUP BY customer_id
),
ranked_customers AS (
    SELECT 
        customer_id,
        total_customer_spend,
        lifetime_orders,
        ROW_NUMBER() OVER (ORDER BY total_customer_spend DESC) AS spend_rank,
        COUNT(*) OVER () AS total_customers_count,
        SUM(total_customer_spend) OVER (ORDER BY total_customer_spend DESC) AS cumulative_spend,
        SUM(total_customer_spend) OVER () AS total_revenue
    FROM customer_spend
)
SELECT 
    customer_id,
    total_customer_spend,
    lifetime_orders,
    spend_rank,
    ROUND((spend_rank * 100.0 / total_customers_count), 2) AS customer_percentile,
    ROUND((cumulative_spend * 100.0 / total_revenue), 2) AS cumulative_revenue_share_pct
FROM ranked_customers
ORDER BY spend_rank;

-- ---------------------------------------------------------------------
-- 4. Customer Purchase Frequency Distribution
-- ---------------------------------------------------------------------
WITH customer_order_frequencies AS (
    SELECT 
        customer_id,
        COUNT(order_id) AS order_frequency
    FROM orders
    WHERE order_status NOT IN ('Cancelled')
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN order_frequency = 1 THEN '1 Order (One-Time)'
        WHEN order_frequency BETWEEN 2 AND 3 THEN '2-3 Orders (Low Repeat)'
        WHEN order_frequency BETWEEN 4 AND 7 THEN '4-7 Orders (Medium Repeat)'
        WHEN order_frequency BETWEEN 8 AND 14 THEN '8-14 Orders (High Repeat)'
        ELSE '15+ Orders (VIP Power Buyer)'
    END AS frequency_tier,
    COUNT(customer_id) AS customer_count,
    ROUND(COUNT(customer_id) * 100.0 / (SELECT COUNT(DISTINCT customer_id) FROM customer_order_frequencies), 2) AS customer_pct
FROM customer_order_frequencies
GROUP BY 1
ORDER BY MIN(order_frequency);
