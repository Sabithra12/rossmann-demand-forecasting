SELECT CASE
           WHEN s.competition_distance IS NULL THEN 'Unknown'
           WHEN s.competition_distance < 1000 THEN 'Under 1 km'
           WHEN s.competition_distance < 5000 THEN '1 to 5 km'
           ELSE 'Over 5 km'
       END AS competition_band,
       COUNT(DISTINCT t.store) AS stores,
       ROUND(AVG(t.sales)) AS avg_daily_sales
FROM train_clean t
JOIN store s ON t.store = s.store
GROUP BY 1
ORDER BY avg_daily_sales DESC;