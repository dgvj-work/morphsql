-- Vertica legacy customer metrics stored procedure
-- Migration candidate: SP_BUILD_CUSTOMER_DAILY

CREATE OR REPLACE PROCEDURE SP_BUILD_CUSTOMER_DAILY(load_date DATE)
AS $$
BEGIN
    -- Stage customer transactions
    CREATE LOCAL TEMP TABLE tmp_customer_txns ON COMMIT PRESERVE ROWS AS
    SELECT
        customer_id,
        order_id,
        order_date,
        order_amount,
        ZEROIFNULL(discount_amount) AS discount_amount,
        order_amount - ZEROIFNULL(discount_amount) AS net_amount
    FROM staging.customer_transactions
    WHERE order_date = load_date;

    -- Build daily customer aggregates
    CREATE LOCAL TEMP TABLE tmp_customer_daily ON COMMIT PRESERVE ROWS AS
    SELECT
        customer_id,
        load_date AS activity_date,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(net_amount) AS total_spend,
        MAX(order_date) AS last_order_date,
        AVG(net_amount) AS avg_order_value
    FROM tmp_customer_txns
    GROUP BY customer_id, load_date;

    -- Classify customer segments
    DELETE FROM analytics.customer_daily WHERE activity_date = load_date;

    INSERT INTO analytics.customer_daily
    SELECT
        customer_id,
        activity_date,
        order_count,
        total_spend,
        last_order_date,
        avg_order_value,
        CASE
            WHEN order_count >= 5
             AND last_order_date >= load_date - 90
             AND total_spend > 500
            THEN 'HIGH_VALUE'
            WHEN order_count >= 2
             AND total_spend > 100
            THEN 'MEDIUM_VALUE'
            ELSE 'STANDARD'
        END AS customer_segment,
        CASE
            WHEN order_count = 1 THEN 'NEW'
            WHEN last_order_date >= load_date - 30 THEN 'ACTIVE'
            ELSE 'DORMANT'
        END AS activity_status
    FROM tmp_customer_daily;

    COMMIT;
END;
$$;
