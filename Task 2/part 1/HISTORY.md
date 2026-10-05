# Bounded confirmed history

## Run from the repository root

```bash
python "Task 2/part 1/collect_history.py" --input "Task 2/part 1/data/seed_addresses.csv" --output-dir "Task 2/part 1/results/my_history" --max-pages 1
python -m unittest discover -s "Task 2/part 1" -v
```

Python 3.10+, standard library only. One page contains at most 25 confirmed
transactions per address. Increase --max-pages with a new directory (maximum 100).
The input and run parameters are pinned by the manifest. Resume the same run to
reuse saved address observations and retry address failures. Partial-address
fetches are discarded and retried from scratch. Run one process per directory.
Calls are sequential with a one-second pause between requests and bounded retries.

## Outputs

- address_summary.csv: all input labels and sources, provider transaction counts,
  confirmed balance from the pre-history stats call, observed count and date range,
  sample received/spent totals, coverage and error.
- transactions.csv: one row per address/transaction. A transaction involving two
  seed addresses appears twice; never sum its fee twice for transaction-level work.
- One address JSON: before/after statistics, normalized transaction observations,
  request URLs, retrieval dates and SHA-256 hashes of original response bytes.
- input.csv and manifest.json: input snapshot, parameters and per-address outcomes.

JSON retains selected observations, not full raw transaction responses. Hashes
identify retrieved response bytes but do not permit reconstructing them. Full
inputs/outputs, scripts and outpoints must be acquired by TXID for future graph,
UTXO holding-time or CPFP analysis. Never claim those are available in this output.

## Coverage

| Value | Meaning |
| --- | --- |
| partial | Observed count is below stable provider chain count |
| count_matches_stable_stats | Counts match and before/after chain_stats agree |
| stats_changed | Provider chain_stats changed during this address collection |
| inconsistent_count | Observed count exceeds stable provider chain count |

Count agreement is a consistency check, not proof of an atomic snapshot or
protection against reorgs. Requests span time and may use separately updated API
caches. stop_reason distinguishes page_limit from endpoint_exhausted. Error rows
retain input labels but have blank measurements. Unknown labels stay unknown.

## Measurement definitions

All monetary amounts are integer satoshis. confirmed_balance_sat_before excludes
unconfirmed transactions and belongs to the address, not its whole wallet/cluster.
Address received/spent amounts sum matching vout values and matching vin.prevout
values respectively. Net is received minus spent: it includes returns/change to
the same address and is not automatically an external payment.

vsize_vb = ceil(weight/4). fee_rate_sat_vb = whole-transaction fee / vsize.
Block times are UTC confirmation timestamps, not mempool broadcast times.
Coinbase spending inputs are absent. Mempool transactions are excluded.

oldest/newest_observed describe the sample, not lifetime first/last activity.
No frequency, lifetime inactivity, UTXO holding time, CPFP flag, high-fee threshold
or illicit score is inferred. Historical storage evidence may not cover these
recent transactions; check each evidence date before comparing cold/hot behaviour.

## Source

https://github.com/Blockstream/esplora/blob/master/API.md
Endpoints used: GET /address/:address and GET /address/:address/txs/chain,
with last_seen_txid for subsequent pages. Provider: https://blockstream.info/api.
The initial committed history_20261005 run uses max-pages=1.
