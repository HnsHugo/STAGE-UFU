-- q02_highest_fee_rates
-- Goal: find Bitcoin transactions with the highest fee rates in September 2026
-- Result: ../results/q02_highest_fee_rates.csv

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
  AND virtual_size > 0
ORDER BY fee_rate_sat_vb DESC
LIMIT 20;