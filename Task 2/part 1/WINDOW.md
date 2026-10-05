# Activity in a fixed UTC window

Run from the repository root (Python 3.10+, standard library):

```bash
python "Task 2/part 1/collect_window.py" --input "Task 2/part 1/data/seed_addresses.csv" --output-dir "Task 2/part 1/results/window_experiment" --start 2026-09-01T00:00:00Z --end 2026-10-01T00:00:00Z --max-pages 1
```

These dates are an example, not a validated hot/cold comparison period. End must
be in the past. Start is inclusive; end is exclusive. Use a fresh output directory for a new experiment.
The collector uses the existing sequential, rate-limited history fetcher. It scans
at most max-pages (1..100), 25 transactions per page; it does not stop on an old
timestamp. This conservative first version requires count-consistent full history
before emitting complete-window metrics. Many busy addresses will remain unverified;
increasing the page cap may still be insufficient. It is not an efficient historical
window indexer. This version checkpoints pages and supports resume; see below.

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

## Resume and extend

Repeat the same command and output directory to reuse downloaded pages after an
interruption. Increase --max-pages (up to 100) in that directory to extend history.
The limit is the total pages scanned per address, including cached pages, not the
number of new pages per run. For example, changing 1 to 10 allows up to nine new
pages for an address that already has one full page.

Input and UTC boundaries are pinned by a version-2 manifest. Old version-1 pilot
directories remain immutable: use a new directory for this collector version.
Run only one process per directory. Address results are replaced by the latest
attempt; errors have no metrics. Page checkpoints survive errors.

Each address.pages.json retains raw transaction page responses and their original
request evidence. Checkpoint files supplement the normalized history; this wrapper
now retains raw pages, unlike the original bounded-history collector. Resuming
reuses their original timestamps; it does not pretend pages were fetched again.

Live chain_stats are checked before and after every address scan against the saved
anchor. If they change, the address attempt fails and asks for a new directory,
preventing silent mixing of an older prefix with changed address activity.
This may often happen for busy addresses, and equal statistics still cannot
exclude every reorg. The feature improves retry cost; it does not yet provide
efficient block-based coverage of a fixed window. Full-history count consistency
is still required for complete metrics. Requests for cached pages retain the
one-second pacing of the shared fetcher.
