-- =====================================================================
-- SQL ANALYTICS: RFM (RECENCY, FREQUENCY, MONETARY) SEGMENTATION
-- Industry-standard behavioral tiering using NTILE window functions
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Base Customer RFM Metrics & Quintile Scoring (1 to 5)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_customer_rfm_scores AS
WITH customer_rfm_raw AS (
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.signup_date,
        mc.channel_name AS acquisition_channel,
        (DATE '2025-12-31' - MAX(o.order_date::date)) AS recency_days,
        COUNT(o.order_id) AS frequency,
        ROUND(SUM(o.net_amount), 2) AS monetary_value,
        ROUND(AVG(o.net_amount), 2) AS avg_order_value
    FROM customers c
    JOIN marketing_channels mc ON c.acquisition_channel_id = mc.channel_id
    JOIN orders o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('Cancelled')
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.signup_date, mc.channel_name
),
rfm_quantiles AS (
    SELECT 
        customer_id,
        first_name,
        last_name,
        email,
        signup_date,
        acquisition_channel,
        recency_days,
        frequency,
        monetary_value,
        avg_order_value,
        -- R_Score: 5 = Most Recent (lowest days), 1 = Least Recent (highest days)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- F_Score: 5 = Highest Frequency, 1 = Lowest
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        -- M_Score: 5 = Highest Monetary Spend, 1 = Lowest
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM customer_rfm_raw
)
SELECT 
    customer_id,
    first_name,
    last_name,
    email,
    signup_date,
    acquisition_channel,
    recency_days,
    frequency,
    monetary_value,
    avg_order_value,
    r_score,
    f_score,
    m_score,
    -- Segmentation Logic
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalists'
        WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'
        WHEN r_score = 1 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose Them'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score BETWEEN 2 AND 3 THEN 'Hibernating'
        ELSE 'Lost Customers'
    END AS customer_segment
FROM rfm_quantiles;

-- ---------------------------------------------------------------------
-- 2. Segment Revenue Contribution & Distribution
-- ---------------------------------------------------------------------
SELECT 
    customer_segment,
    COUNT(customer_id) AS total_customers,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER (), 2) AS customer_share_pct,
    ROUND(SUM(monetary_value), 2) AS total_segment_revenue,
    ROUND(SUM(monetary_value) * 100.0 / SUM(SUM(monetary_value)) OVER (), 2) AS revenue_share_pct,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_lifetime_orders,
    ROUND(AVG(monetary_value), 2) AS avg_customer_spend,
    ROUND(AVG(avg_order_value), 2) AS avg_basket_size
FROM v_customer_rfm_scores
GROUP BY customer_segment
ORDER BY total_segment_revenue DESC;

-- ---------------------------------------------------------------------
-- 3. High-Priority "At Risk" & "Cannot Lose Them" Action List
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    first_name || ' ' || last_name AS customer_name,
    email,
    customer_segment,
    recency_days,
    frequency,
    monetary_value,
    acquisition_channel
FROM v_customer_rfm_scores
WHERE customer_segment IN ('Cannot Lose Them', 'At Risk')
ORDER BY monetary_value DESC
LIMIT 50;
