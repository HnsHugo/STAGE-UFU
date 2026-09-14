-- q03_fee_statistics
-- Goal: compute fee-rate statistics for Bitcoin transactions in September 2026
-- Result: ../results/q03_fee_statistics.csv

WITH tx AS (
  SELECT
    fee,
    virtual_size,
    SAFE_DIVIDE(fee, virtual_size) AS fee_rate_sat_vb
  FROM `bigquery-public-data.crypto_bitcoin.transactions`
  WHERE block_timestamp_month = DATE('2026-09-01')
    AND is_coinbase = FALSE
    AND virtual_size > 0
)

SELECT
  COUNT(*) AS transaction_count,

  AVG(fee_rate_sat_vb) AS avg_fee_rate_sat_vb,

  MIN(fee_rate_sat_vb) AS min_fee_rate_sat_vb,

  MAX(fee_rate_sat_vb) AS max_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(50)]
    AS median_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(90)]
    AS p90_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(95)]
    AS p95_fee_rate_sat_vb,

  APPROX_QUANTILES(fee_rate_sat_vb, 100)[OFFSET(99)]
    AS p99_fee_rate_sat_vb

FROM tx;