-- Refunds staging table (referenced by customer_lifetime_value query)
CREATE TABLE staging.refunds (
    refund_id           INT NOT NULL,
    customer_id         INT NOT NULL,
    order_id            INT,
    refund_amount       DECIMAL(18,2) NOT NULL,
    refund_date         DATE NOT NULL,
    reason_code         VARCHAR(50),
    created_at          TIMESTAMP DEFAULT SYSDATE
)
SEGMENTED BY HASH(customer_id) ALL NODES
ORDER BY refund_date, customer_id;
