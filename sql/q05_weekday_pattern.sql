SELECT day_of_week,
       COUNT(*) AS days,
       ROUND(AVG(sales)) AS avg_sales
FROM train_clean
GROUP BY day_of_week
ORDER BY day_of_week;