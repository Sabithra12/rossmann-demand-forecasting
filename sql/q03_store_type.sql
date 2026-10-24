SELECT s.store_type,
       COUNT(DISTINCT t.store) AS stores,
       ROUND(AVG(t.sales)) AS avg_daily_sales,
       SUM(t.sales) AS total_sales
FROM train_clean t
JOIN store s ON t.store = s.store
GROUP BY s.store_type
ORDER BY avg_daily_sales DESC;