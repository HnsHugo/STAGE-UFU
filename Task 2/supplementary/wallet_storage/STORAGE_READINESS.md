# Hot/cold dataset eligibility — 16 October 2026

**Status: supplementary pilot, currently paused.** The course requirement for a cold-address dataset/classifier remains partial. This unit checks previously collected observations without network collection, retraining or new attribution.

## Executed result

Two September collections are consolidated by address without summing their observations. Of eleven addresses, ten are research samples: five published cold, one hot and four unknown. Six research addresses have count-consistent complete windows: four cold and two unknown. The only hot address remains incomplete. **Zero addresses are eligible**, because none has explicit evidence that its storage label applies throughout September 2026.

A complete window with zero transactions retains zero. A truncated history retains an unavailable measurement. Unknown storage is not a negative class. `not_ready` is an input-eligibility result, not predictive performance.

## Rules and limitations

The script checks input hashes, address/evidence identity, equal window bounds and conflicts across collections. It selects a complete observation when available. It does not combine page counts or recompute historical features.

A future eligible label requires a reviewed `verified` status and explicit `storage_label_evidence` fields: `source_url`, `valid_from_utc`, `valid_until_utc_exclusive` and `published_at_utc`. The interval must cover the full window, with publication available no later than its end. `reviewed_at_utc` replaces none of those dates. The schema is prepared; no such evidence was added to the current dataset. Metadata checks do not authenticate their source or truth.

Even eligible rows would still require entity/incident group review and a separate train/validation/test protocol. Entity names are source attributions. Provider counters are not cryptographic proofs; address activity is not complete wallet activity. No hardware or illicitness label is inferred.

## Reproducibility discrepancy

The initial input CSV matches its manifest bytes exactly. The extended collection CSV does not match its original hash in the current Git bytes, but matches exactly after LF-to-CRLF reconstruction. The report separately records the actual byte hash and the reconstruction mode. Historical inputs were not modified. Any content difference beyond that precise newline conversion is rejected.

## Reproduce

From the repository root, choose a new output file:

```bash
python "Task 2/supplementary/wallet_storage/audit_storage_readiness.py" \
  "Task 2/supplementary/wallet_storage/results/window_september2026" \
  "Task 2/supplementary/wallet_storage/results/window_september2026_extended" \
  --output /path/to/new_storage_readiness.json
python -m unittest discover -s "Task 2/supplementary/wallet_storage" -p 'test*.py'
```

The executed result is `results/storage_readiness_20261016.json`. At that stage, 28 tests passed, including seven new checks on truncated zeros, unknown classes, API test addresses, temporal availability, missing evidence and newline hashes.

## Completed follow-up and current priority

The [Bitfinex chronology and Change snapshot profiles](TEMPORAL_LABELS_20261016.md) were subsequently completed; no September label eligibility was established. The previous proposal to keep searching for continuous hot/cold labels is paused. Follow the [main case-study path](../../README.md) and obtain the exact additional-case reference before extending the dataset.
