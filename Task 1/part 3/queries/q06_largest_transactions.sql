-- q06_largest_transactions
-- Goal: find the largest Bitcoin transactions by input value in September 2026
-- Result: ../results/q06_largest_transactions.csv

SELECT
  `hash` AS txid,
  block_timestamp,
  block_number,
  input_count,
  output_count,
  input_value,
  output_value,
  fee,
  virtual_size,
  SAFE_DIVIDE(fee, virtual_size) AS fee_rate_sat_vb
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
  AND is_coinbase = FALSE
ORDER BY input_value DESC
LIMIT 20;