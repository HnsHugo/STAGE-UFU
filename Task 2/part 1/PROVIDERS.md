# Targeted provider feasibility — 2026-10-05

Goal: avoid scanning the entire high-activity Bitfinex address history merely to
measure a historical month.

## Documented capability and observed result

Official BlockCypher documentation:
https://www.blockcypher.com/dev/bitcoin/#address-endpoint
https://github.com/blockcypher/docs/blob/master/source/includes/_address.md

The address endpoint documents exclusive before/after block-height filters,
TXRefs pagination and a limit of up to 2000 references. References are inputs
and outputs, not unique transactions: deduplication by TXID is essential.

Two small real read-only requests used before=960100, with and without
after=960000, limit=10, confirmations=1. Both returned HTTP 200 and 12 references
at heights 969962..969971, all outside the requested bounds. The response byte
hashes were identical. See [report.json](results/provider_probe_20261005/report.json)
and the raw responses beside it.

These are observed failures on this execution path, not proof that the public API
always behaves this way. We have not isolated whether the provider, a cache or
the access path ignored parameters. HTTP success is not filter validation.
No September statistics or storage predictions were generated from this data.

## Reproduce

Run from repository root:
```bash
python "Task 2/part 1/probe_blockcypher.py" --output-dir "Task 2/part 1/results/my_provider_probe"
python -m unittest discover -s "Task 2/part 1" -v
```

The probe makes two requests, retains exact bytes and SHA-256 provenance, and
reports strict bound violations. Empty results are inconclusive. A response
without counterexamples is not proof of completeness or correct pagination.
This is a diagnostic probe, not a production collector. Output directory must
be new. No account, key, paid plan or transaction broadcast was used.

## Acceptance before integration

Verify that the parameters actually change results, all references respect bounds,
and consecutive pages share no dropped boundary-block references. Cross-check
TXIDs against the existing provider for an address whose history is known.
Require explicit coverage/completeness checks; do not infer them from a short page.

Heights are not dates. A validated block-height slice must remain a block-height
slice until its relationship to the UTC interval is established. Individual block
timestamps can be nonmonotone. Filtering references by date after an approximate
height mapping does not by itself prove all relevant blocks were included.

Next technical decision: investigate a second indexed provider and its access
requirements, or define a block-height experiment separately. Existing confirmed
history/window collection remains the validated implementation; targeted
high-activity monthly collection is unresolved.
