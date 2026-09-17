-- q05_daily_transaction_statistics
-- Goal: compute daily Bitcoin transaction statistics for September 2026
-- Result: ../results/q05_daily_transaction_statistics.csv

SELECT
  DATE(block_timestamp) AS day,
  COUNT(*) AS transaction_count,
  AVG(input_value) AS avg_input_value_sats,
  AVG(output_value) AS avg_output_value_sats,
  AVG(fee) AS avg_fee_sats,
  AVG(SAFE_DIVIDE(fee, virtual_size)) AS avg_fee_rate_sat_vb
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
  AND is_coinbase = FALSE
  AND virtual_size > 0
GROUP BY day
ORDER BY day;