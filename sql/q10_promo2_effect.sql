SELECT s.promo2,
       COUNT(DISTINCT t.store) AS stores,
       ROUND(AVG(t.sales)) AS avg_daily_sales
FROM train_clean t
JOIN store s ON t.store = s.store
GROUP BY s.promo2
ORDER BY s.promo2;