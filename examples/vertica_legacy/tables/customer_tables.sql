-- Customer transactions staging table
CREATE TABLE staging.customer_transactions (
    customer_id         INT NOT NULL,
    order_id            INT NOT NULL,
    order_date          DATE NOT NULL,
    order_amount        DECIMAL(18,2),
    discount_amount     DECIMAL(18,2),
    payment_method      VARCHAR(50),
    created_at          TIMESTAMP DEFAULT SYSDATE
)
SEGMENTED BY HASH(customer_id) ALL NODES
ORDER BY customer_id, order_date;

-- Customers dimension
CREATE TABLE staging.customers (
    customer_id         INT NOT NULL PRIMARY KEY,
    customer_name       VARCHAR(200),
    email               VARCHAR(200),
    registration_date   DATE,
    country_code        VARCHAR(3),
    is_active           INT DEFAULT 1
)
SEGMENTED BY HASH(customer_id) ALL NODES;

-- Customer daily fact table
CREATE TABLE analytics.customer_daily (
    customer_id         INT NOT NULL,
    activity_date       DATE NOT NULL,
    order_count         INT,
    total_spend         DECIMAL(18,2),
    last_order_date     DATE,
    avg_order_value     DECIMAL(18,2),
    customer_segment    VARCHAR(20),
    activity_status     VARCHAR(20)
)
SEGMENTED BY HASH(customer_id) ALL NODES
ORDER BY activity_date, customer_id;
