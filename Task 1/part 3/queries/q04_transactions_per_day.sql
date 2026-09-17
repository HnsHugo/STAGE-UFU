-- q04_transactions_per_day
-- Goal: count Bitcoin transactions per day in September 2026
-- Result: ../results/q04_transactions_per_day.csv

SELECT
  DATE(block_timestamp) AS day,
  COUNT(*) AS transaction_count
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
GROUP BY day
ORDER BY day;