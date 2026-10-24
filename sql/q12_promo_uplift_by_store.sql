WITH per_store AS (
    SELECT store,
           AVG(CASE WHEN promo = 1 THEN sales END) AS promo_avg,
           AVG(CASE WHEN promo = 0 THEN sales END) AS non_promo_avg
    FROM train_clean
    GROUP BY store
)
SELECT store,
       ROUND(promo_avg) AS promo_avg,
       ROUND(non_promo_avg) AS non_promo_avg,
       ROUND(100.0 * (promo_avg - non_promo_avg) / non_promo_avg, 1) AS uplift_pct
FROM per_store
WHERE non_promo_avg IS NOT NULL
ORDER BY uplift_pct DESC
LIMIT 10;