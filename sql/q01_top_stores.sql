SELECT t.store, s.store_type, s.assortment,
       SUM(t.sales) AS total_sales,
       ROUND(AVG(t.sales)) AS avg_daily_sales
FROM train_clean t
JOIN store s ON t.store = s.store
GROUP BY t.store, s.store_type, s.assortment
ORDER BY total_sales DESC
LIMIT 10;