SELECT s.store_type,
       ROUND(AVG(t.customers)) AS avg_customers,
       ROUND(SUM(t.sales)::numeric / SUM(t.customers), 2) AS sales_per_customer
FROM train_clean t
JOIN store s ON t.store = s.store
GROUP BY s.store_type
ORDER BY sales_per_customer DESC;