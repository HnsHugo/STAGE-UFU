# Part 1 — Address-to-cluster observations

## Objective

Given a public Bitcoin address, record the cluster ID and optional service name
reported by WalletExplorer, alongside the original response and provenance.
This is an observation from a third-party heuristic, not ground-truth ownership.

## Run

Python 3.10+; the script uses only the standard library. From the repo root:

```bash
python "Task 2/part 1/lookup_address.py" 16SbwNa22nBwhLtg6HzWVYFQiUxtNzAUpt --output "Task 2/part 1/results/new_snapshot.json"
python -m unittest discover -s "Task 2/part 1" -v
```

The example address is taken from the official API documentation. It is an API
smoke test, not a representative dataset and not an independently verified label.
Read `results/api_example_snapshot.json` for the actual dated response.
The CLI refuses to overwrite an existing observation. New requests create new
snapshots; network/API errors return a nonzero exit code and do not create data.
HTTP 429 and selected transient failures receive bounded exponential retries.

## Output

| Field | Meaning |
| --- | --- |
| address | Queried public mainnet address |
| wallet_id | WalletExplorer cluster identifier, or null |
| service_label | Provider's name, or null; no illicit classification |
| lookup_status | found or not_found; errors are not converted to not_found |
| retrieved_at_utc | Retrieval time, not transaction/block time |
| updated_to_block | Provider's reported indexed height, when present |
| source_url | Exact request for provenance |
| raw_response | Unmodified parsed provider response |

## Interpretation and limitations

WalletExplorer describes merging addresses that are co-spent as transaction inputs,
including transitive merging. This assumes shared control; collaborative transactions
can violate that assumption. Missing or unnamed results are not proof of legitimate
activity, and cluster IDs are provider-specific observations that may change.

According to the official FAQ, service names have rarely been updated since 2016.
Only confirmed transactions appear, with a delay. This source cannot supply live
mempool history for establishing parent-unconfirmed-at-child-broadcast CPFP evidence.
Neither a cluster ID nor a service name establishes Ledger/Trezor hardware usage,
cold storage or illicit activity.

The first version deliberately fetches one lookup, not all cluster addresses.
The input table is now defined in `data/seed_addresses.csv`; see `data/README.md`
for column definitions and evidence rules. It currently contains one API smoke-test
address. CSV ingestion and validation are implemented. Next: collect
bounded address samples and preserve pagination/provenance before adding features. No completeness claim
should be made about a cluster from a partial address page.

## Sources checked on 2026-10-05

- API and response contract: https://www.walletexplorer.com/api
- Clustering, labels and refresh limitations: https://www.walletexplorer.com/info

## Collect the input table

From the repo root:

```bash
python "Task 2/part 1/collect_addresses.py" --input "Task 2/part 1/data/seed_addresses.csv" --output-dir "Task 2/part 1/results/my_collection" --validate-only
python "Task 2/part 1/collect_addresses.py" --input "Task 2/part 1/data/seed_addresses.csv" --output-dir "Task 2/part 1/results/my_collection"
```

Validation checks all 14 columns, enums, UTC review dates, required source URLs,
duplicate addresses and basic address shape before any network request. It does
not validate Bitcoin address checksums or verify the truth of a cited claim.

Each run directory contains a copy of the input CSV, one dated JSON observation
per successfully queried address, and a manifest with found/not_found/error counts.
The manifest identifies the input by SHA-256. Reusing a run directory with changed
input is rejected: use a new directory when changing the table or refreshing data.
Run only one collector per output directory.

Rerunning the same input/output reuses consistent saved responses, including
not_found, and retries failed lookups. Therefore cached not_found results are not
fresh lookups. A new directory is required for a refresh. Requests are sequential,
with at least one second delay after a lookup and the existing bounded retries.
Partial failures produce exit code 1. A negative lookup remains separate from a
network/API error. Ctrl+C can interrupt a run; rerun to recover completed snapshots.
Filesystem errors stop the run rather than being disguised as API failures.

The committed `results/seed_collection_20261005/` is a real one-address smoke test.
It does not establish clustering accuracy, storage classification or illicit links.

## Combined results table

Open `results.csv` inside a collection directory to see the input evidence and
WalletExplorer observations side by side. The original 14 columns are preserved;
8 columns are appended: lookup_status, wallet_id, service_label, updated_to_block,
retrieved_at_utc, source_url, cached and error.

Input unknown values remain unknown. Empty provider fields mean unavailable data,
not a negative storage/hardware/illicit classification. Entity_name is the input
attribution; service_label is the provider response. Neither overwrites the other.

The CSV is updated atomically after each processed address and contains the processed
portion of the input during an interrupted run. Rows with API errors retain all input
fields, have blank provider fields and include an error message. On resume the table
is rebuilt from validated cached observations and retried errors.

Example: `results/seed_collection_20261005/results.csv`.
