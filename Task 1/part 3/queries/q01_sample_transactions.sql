-- Query: q01_sample_transactions
-- Goal: Retrieve 10 sample Bitcoin transactions from September 2026
-- Result: results/q01_sample_transactions.csv

SELECT
  `hash` AS txid,
  block_timestamp,
  block_number,
  input_count,
  output_count,
  input_value,
  output_value,
  fee,
  size,
  virtual_size,
  is_coinbase
FROM `bigquery-public-data.crypto_bitcoin.transactions`
WHERE block_timestamp_month = DATE('2026-09-01')
LIMIT 10;