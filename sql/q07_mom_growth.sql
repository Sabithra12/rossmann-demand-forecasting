WITH monthly AS (
    SELECT DATE_TRUNC('month', date)::date AS month,
           SUM(sales) AS total_sales
    FROM train_clean
    GROUP BY 1
)
SELECT month,
       total_sales,
       LAG(total_sales) OVER (ORDER BY month) AS prev_month,
       ROUND(100.0 * (total_sales - LAG(total_sales) OVER (ORDER BY month))
             / LAG(total_sales) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;