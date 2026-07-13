-- Customer metrics view built on daily aggregates
CREATE OR REPLACE VIEW analytics.v_customer_metrics AS
SELECT
    cd.customer_id,
    cd.activity_date,
    cd.order_count,
    cd.total_spend,
    cd.customer_segment,
    cd.activity_status,
    c.customer_name,
    c.registration_date,
    DATEDIFF('day', c.registration_date, cd.activity_date) AS customer_tenure_days,
    SUM(cd.total_spend) OVER (
        PARTITION BY cd.customer_id
        ORDER BY cd.activity_date
        ROWS UNBOUNDED PRECEDING
    ) AS lifetime_value,
    ROW_NUMBER() OVER (
        PARTITION BY cd.customer_id
        ORDER BY cd.activity_date DESC
    ) AS recency_rank
FROM analytics.customer_daily cd
JOIN staging.customers c
  ON cd.customer_id = c.customer_id
WHERE cd.activity_date >= CURRENT_DATE - 365;
