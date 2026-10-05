# Activity in a fixed UTC window

Run from the repository root (Python 3.10+, standard library):

```bash
python "Task 2/part 1/collect_window.py" --input "Task 2/part 1/data/seed_addresses.csv" --output-dir "Task 2/part 1/results/window_experiment" --start 2026-09-01T00:00:00Z --end 2026-10-01T00:00:00Z --max-pages 1
```

These dates are an example, not a validated hot/cold comparison period. End must
be in the past. Start is inclusive; end is exclusive. Use a fresh output directory.
The collector uses the existing sequential, rate-limited history fetcher. It scans
at most max-pages (1..100), 25 transactions per page; it does not stop on an old
timestamp. This conservative first version requires count-consistent full history
before emitting complete-window metrics. Many busy addresses will remain unverified;
increasing the page cap may still be insufficient. It is not an efficient historical
window indexer. No automatic resume is implemented in this wrapper.

Each address JSON retains seed labels, source observation, selected transactions,
window boundaries and metrics. Input snapshot and manifest pin parameters. Errors
are saved per address and produce a failing exit status. Original response hashes
do not replace full raw transaction responses; see HISTORY.md.

Incomplete or unstable history yields metrics=null, not zero. A covered window
without transactions yields zero counts/flows and null median fees. Coverage is
a provider consistency check, not protection against reorgs or non-atomic requests.

Frequency divides by the entire fixed window, including inactive days. Fee median
uses only transactions spending funds from this address, and remains the fee rate
of the whole transaction. Fees on receive-only transactions are excluded. Address
flows include returns; they are not necessarily external payments. Across addresses,
deduplicate TXIDs when aggregating transaction counts or fees.

storage_prediction remains unknown. storage_label_window_validity remains
unverified: the program does not establish an operational interval for source
labels. It measures activity and does not infer cold storage, hardware or illicit
behaviour. See COMPARISON.md for the evidence and evaluation protocol.

Offline validation: python -m unittest discover -s "Task 2/part 1" -v.
This implementation has been tested offline; no new live window dataset is claimed.
