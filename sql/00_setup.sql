-- Rossmann project: database setup (PostgreSQL)
-- 1) Create a database named "rossmann", then run the two CREATE TABLE statements.
-- 2) Import Kaggle's train.csv into "train" and store.csv into "store"
--    (pgAdmin: right-click table > Import/Export Data, format csv, header ON, delimiter ,).
-- 3) Run the train_clean statement at the end.

DROP TABLE IF EXISTS train_clean;
DROP TABLE IF EXISTS train;
DROP TABLE IF EXISTS store;

CREATE TABLE train (
    store INT,
    day_of_week INT,
    date DATE,
    sales INT,
    customers INT,
    open INT,
    promo INT,
    state_holiday TEXT,
    school_holiday INT
);

CREATE TABLE store (
    store INT PRIMARY KEY,
    store_type TEXT,
    assortment TEXT,
    competition_distance FLOAT,
    competition_open_since_month INT,
    competition_open_since_year INT,
    promo2 INT,
    promo2_since_week INT,
    promo2_since_year INT,
    promo_interval TEXT
);

-- Run AFTER importing the CSV files.
-- Keeps only open store-days with sales (expected: 844,338 rows).
CREATE TABLE train_clean AS
SELECT * FROM train
WHERE open = 1 AND sales > 0;
