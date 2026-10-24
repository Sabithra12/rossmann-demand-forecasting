SELECT promo, COUNT(*) AS days, ROUND(AVG(sales)) AS avg_sales
FROM train_clean
GROUP BY promo;