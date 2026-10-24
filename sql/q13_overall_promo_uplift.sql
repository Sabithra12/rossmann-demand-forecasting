WITH per_store AS (
    SELECT store,
           AVG(CASE WHEN promo = 1 THEN sales END) AS promo_avg,
           AVG(CASE WHEN promo = 0 THEN sales END) AS non_promo_avg
    FROM train_clean
    GROUP BY store
)
SELECT COUNT(*) AS stores,
       ROUND(AVG(uplift)::numeric, 1) AS avg_uplift_pct,
       ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY uplift))::numeric, 1) AS median_uplift_pct
FROM (
    SELECT store, 100.0 * (promo_avg - non_promo_avg) / non_promo_avg AS uplift
    FROM per_store
    WHERE non_promo_avg IS NOT NULL
) u;