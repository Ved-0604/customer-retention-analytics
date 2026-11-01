-- =====================================================================
-- DATA QUALITY AUDIT & REFERENTIAL INTEGRITY VERIFICATION (SQL)
-- Execute this suite to certify dataset integrity within the analytical warehouse
-- =====================================================================

-- 1. Entity Row Counts and Basic Footprint
SELECT 'marketing_channels' AS entity, COUNT(*) AS row_count FROM marketing_channels
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'payments', COUNT(*) FROM payments;

-- 2. Primary Key Uniqueness & Null Checks
SELECT 'customers' AS table_name, COUNT(*) - COUNT(DISTINCT customer_id) AS duplicate_pks, SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_pks FROM customers
UNION ALL
SELECT 'orders', COUNT(*) - COUNT(DISTINCT order_id), SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) - COUNT(DISTINCT order_item_id), SUM(CASE WHEN order_item_id IS NULL THEN 1 ELSE 0 END) FROM order_items
UNION ALL
SELECT 'products', COUNT(*) - COUNT(DISTINCT product_id), SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) FROM products
UNION ALL
SELECT 'payments', COUNT(*) - COUNT(DISTINCT payment_id), SUM(CASE WHEN payment_id IS NULL THEN 1 ELSE 0 END) FROM payments;

-- 3. Referential Integrity (Orphaned Foreign Keys Audit)
-- Expected Result: Zero rows for all checks
SELECT 
    'Orders without valid Customer' AS check_description,
    COUNT(*) AS orphaned_records
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT 
    'Order Items without valid Order' AS check_description,
    COUNT(*) AS orphaned_records
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL

UNION ALL

SELECT 
    'Order Items without valid Product' AS check_description,
    COUNT(*) AS orphaned_records
FROM order_items oi
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT 
    'Payments without valid Order' AS check_description,
    COUNT(*) AS orphaned_records
FROM payments p
LEFT JOIN orders o ON p.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 4. Financial Reconciliation Integrity Checks
-- Expected Result: Zero discrepancies
WITH order_item_aggregates AS (
    SELECT 
        order_id,
        ROUND(SUM(total_item_price)::numeric, 2) AS calculated_gross
    FROM order_items
    GROUP BY order_id
)
SELECT 
    'Gross Revenue Mismatch (Orders vs Order Items)' AS check_name,
    COUNT(*) AS discrepancy_count
FROM orders o
JOIN order_item_aggregates oia ON o.order_id = oia.order_id
WHERE ABS(o.gross_amount - oia.calculated_gross) > 0.02

UNION ALL

SELECT 
    'Net Revenue Mismatch (Gross - Discount + Shipping)' AS check_name,
    COUNT(*) AS discrepancy_count
FROM orders
WHERE ABS(net_amount - (gross_amount - discount_amount + shipping_fee)) > 0.02

UNION ALL

SELECT 
    'Payment Amount Mismatch (Payment vs Order Net)' AS check_name,
    COUNT(*) AS discrepancy_count
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE ABS(o.net_amount - p.amount) > 0.02;

-- 5. Temporal Causality Audit (Orders must NOT precede Customer Signup)
SELECT 
    COUNT(*) AS retroactive_orders_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date < (c.signup_date::timestamp - INTERVAL '1 hour');
