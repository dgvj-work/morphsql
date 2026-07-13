-- Legacy customer lifetime value calculation
-- 4 CTEs, multiple joins, window functions

WITH customer_orders AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        order_amount - ZEROIFNULL(discount_amount) AS net_amount
    FROM staging.customer_transactions
    WHERE order_date >= CURRENT_DATE - 365
),
customer_refunds AS (
    SELECT
        customer_id,
        SUM(refund_amount) AS total_refunds
    FROM staging.refunds
    WHERE refund_date >= CURRENT_DATE - 365
    GROUP BY customer_id
),
customer_summary AS (
    SELECT
        co.customer_id,
        COUNT(DISTINCT co.order_id) AS order_count,
        SUM(co.net_amount) AS gross_spend,
        ZEROIFNULL(cr.total_refunds) AS total_refunds,
        SUM(co.net_amount) - ZEROIFNULL(cr.total_refunds) AS net_spend,
        MAX(co.order_date) AS last_order_date,
        MIN(co.order_date) AS first_order_date
    FROM customer_orders co
    LEFT JOIN customer_refunds cr
      ON co.customer_id = cr.customer_id
    GROUP BY co.customer_id, cr.total_refunds
),
customer_lifetime AS (
    SELECT
        cs.*,
        DATEDIFF('day', cs.first_order_date, cs.last_order_date) AS customer_lifespan_days,
        CASE
            WHEN cs.order_count >= 10 AND cs.net_spend > 1000 THEN 'PLATINUM'
            WHEN cs.order_count >= 5 AND cs.net_spend > 500 THEN 'GOLD'
            WHEN cs.order_count >= 2 THEN 'SILVER'
            ELSE 'BRONZE'
        END AS loyalty_tier
    FROM customer_summary cs
)
SELECT
    cl.customer_id,
    c.customer_name,
    cl.order_count,
    cl.gross_spend,
    cl.total_refunds,
    cl.net_spend AS customer_lifetime_value,
    cl.loyalty_tier,
    cl.last_order_date,
    cl.customer_lifespan_days
FROM customer_lifetime cl
JOIN staging.customers c
  ON cl.customer_id = c.customer_id
ORDER BY cl.net_spend DESC;
