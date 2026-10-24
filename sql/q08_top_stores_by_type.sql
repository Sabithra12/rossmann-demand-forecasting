WITH store_sales AS (
    SELECT t.store, s.store_type, SUM(t.sales) AS total_sales
    FROM train_clean t
    JOIN store s ON t.store = s.store
    GROUP BY t.store, s.store_type
)
SELECT store_type, store, total_sales, rank_in_type
FROM (
    SELECT *, RANK() OVER (PARTITION BY store_type ORDER BY total_sales DESC) AS rank_in_type
    FROM store_sales
) r
WHERE rank_in_type <= 3
ORDER BY store_type, rank_in_type;