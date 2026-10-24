SELECT state_holiday,
       COUNT(*) AS days,
       ROUND(AVG(sales)) AS avg_sales
FROM train_clean
GROUP BY state_holiday
ORDER BY avg_sales DESC;