-- =====================================================================
-- E-COMMERCE CUSTOMER RETENTION & CHURN ANALYTICS PLATFORM
-- Relational Database Schema (PostgreSQL 14+)
-- Normalized 3NF Architecture with Constraints, Indexes, and Integrity Checks
-- =====================================================================

-- Clean existing objects
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS marketing_channels CASCADE;

-- ---------------------------------------------------------------------
-- 1. MARKETING CHANNELS (Dimension)
-- ---------------------------------------------------------------------
CREATE TABLE marketing_channels (
    channel_id INT PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL UNIQUE,
    channel_type VARCHAR(50) NOT NULL,
    avg_cpa NUMERIC(10, 2) NOT NULL CHECK (avg_cpa >= 0.00)
);

COMMENT ON TABLE marketing_channels IS 'Acquisition marketing channels with benchmark Cost Per Acquisition (CPA)';

-- ---------------------------------------------------------------------
-- 2. CUSTOMERS (Dimension)
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    gender VARCHAR(20) NOT NULL,
    age INT NOT NULL CHECK (age BETWEEN 18 AND 100),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL DEFAULT 'United States',
    signup_date DATE NOT NULL,
    acquisition_channel_id INT NOT NULL,
    CONSTRAINT fk_customers_channel FOREIGN KEY (acquisition_channel_id)
        REFERENCES marketing_channels (channel_id) ON DELETE RESTRICT
);

COMMENT ON TABLE customers IS 'Customer demographic profiles, cohort signup dates, and acquisition channels';

-- ---------------------------------------------------------------------
-- 3. PRODUCTS (Dimension)
-- ---------------------------------------------------------------------
CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    base_price NUMERIC(10, 2) NOT NULL CHECK (base_price > 0.00),
    cogs NUMERIC(10, 2) NOT NULL CHECK (cogs > 0.00),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_products_positive_margin CHECK (base_price >= cogs)
);

COMMENT ON TABLE products IS 'Product catalog spanning 12 distinct categories with COGS and unit economics';

-- ---------------------------------------------------------------------
-- 4. ORDERS (Fact)
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    order_date TIMESTAMP NOT NULL,
    order_status VARCHAR(50) NOT NULL CHECK (order_status IN ('Delivered', 'Completed', 'Cancelled', 'Returned', 'Refunded')),
    gross_amount NUMERIC(10, 2) NOT NULL CHECK (gross_amount >= 0.00),
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0.00),
    shipping_fee NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (shipping_fee >= 0.00),
    net_amount NUMERIC(10, 2) NOT NULL CHECK (net_amount >= 0.00),
    acquisition_channel_id INT NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_channel FOREIGN KEY (acquisition_channel_id)
        REFERENCES marketing_channels (channel_id) ON DELETE RESTRICT
);

COMMENT ON TABLE orders IS 'Longitudinal transaction headers with order status, dates, and financial totals';

-- ---------------------------------------------------------------------
-- 5. ORDER ITEMS (Fact Line Items)
-- ---------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0.00),
    unit_cost NUMERIC(10, 2) NOT NULL CHECK (unit_cost > 0.00),
    total_item_price NUMERIC(10, 2) NOT NULL CHECK (total_item_price > 0.00),
    CONSTRAINT fk_items_order FOREIGN KEY (order_id)
        REFERENCES orders (order_id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product FOREIGN KEY (product_id)
        REFERENCES products (product_id) ON DELETE RESTRICT
);

COMMENT ON TABLE order_items IS 'Granular basket line items detailing unit selling prices, quantities, and COGS';

-- ---------------------------------------------------------------------
-- 6. PAYMENTS (Fact / Ledger)
-- ---------------------------------------------------------------------
CREATE TABLE payments (
    payment_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL CHECK (payment_status IN ('Success', 'Failed', 'Refunded')),
    payment_date TIMESTAMP NOT NULL,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0.00),
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id)
        REFERENCES orders (order_id) ON DELETE CASCADE
);

COMMENT ON TABLE payments IS 'Multi-tender payment transactions reconciled with order net amounts';

-- =====================================================================
-- PERFORMANCE OPTIMIZATION INDEXES
-- =====================================================================
-- Index foreign keys for performant joins
CREATE INDEX idx_customers_channel ON customers (acquisition_channel_id);
CREATE INDEX idx_customers_signup ON customers (signup_date);

CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_date ON orders (order_date);
CREATE INDEX idx_orders_status ON orders (order_status);
CREATE INDEX idx_orders_channel ON orders (acquisition_channel_id);

CREATE INDEX idx_items_order ON order_items (order_id);
CREATE INDEX idx_items_product ON order_items (product_id);

CREATE INDEX idx_payments_order ON payments (order_id);
CREATE INDEX idx_payments_status ON payments (payment_status);
CREATE INDEX idx_products_category ON products (category);
