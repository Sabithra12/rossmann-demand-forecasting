SELECT DATE_TRUNC('month', date)::date AS month,
       SUM(sales) AS total_sales
FROM train_clean
GROUP BY 1
ORDER BY 1;