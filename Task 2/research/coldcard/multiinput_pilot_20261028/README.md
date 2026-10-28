# Multi-input Coldcard source pilot — 28 October 2026

## Executed result

This extends the pre-payment source-address dataset to the group absent from the
first eight-source pilot. The **feature extractor is unchanged byte for byte**;
the new driver reuses its collection helper, prefix normalization and fourteen
feature definitions. Neither historical models nor saved results were replaced.

The protocol selected four sources by SHA256 ranking among the **81 candidate
addresses with multiple inputs in their unique collector payment**. The four
reference-payment input counts are 3, 2, 2 and 2. Selection preceded API requests;
there was no replacement or outcome-based sampling. Collection was bounded to
two workers, twelve pages per address and eight seconds per request.

All four histories are complete and consistent with stable provider counters.
They contain 4, 3, 3 and 3 confirmed transactions, including their reference
payments. All four feature vectors were computed using **only blocks strictly
before the reference-payment block**. No fitting, threshold selection or
train/test split was performed.

| Before-payment observation | Previous eight sources | Four multi-input sources |
| --- | ---: | ---: |
| Complete histories / selected | 8 / 8 | 4 / 4 |
| Earlier confirmed transactions per source | 1 | 2–3 |
| Earlier receipt outputs per source | 1 | 2–3 |
| Earlier spending transactions | 0 | 0 |
| Unspent address outputs at cutoff | 1 | 2–3 |
| Balance, BTC | 0.2145–1.34377744 | 0.39146846–10.00000624 |
| Blocks since last activity | 22,671–268,153 | 8,722–245,366 |
| Sources with historical spending-fee observations | 0 | 0 |

The twelve source addresses are distinct across the two pilots. The new pilot
has nine unique prior transaction IDs, with no shared prior transaction among
its sources or with the eight-source pilot. These checks do **not** establish
independent entities or incidents: all twelve remain in the same Coldcard case
group and all individual compromise/hardware labels remain unknown.

## Scientific interpretation and limits

The new sources accumulated multiple received outputs before the observed
payment, rather than having a single receipt like the first sample. This adds
history diversity but does not identify a hardware wallet or establish theft.
An address history is not the full wallet/entity history.

Four of the nine prior outputs are very small: **294, 294, 294 and 330 satoshis**.
They were retained. Such receipts affect transaction counts and last-activity
features even though a receipt alone does not establish who initiated it or why.
There is no verified explanation of these deposits, and no post-hoc dust filter
or extra classifier feature was introduced.

No source in either pilot spent previously, so the historical spending-fee
feature remains null for all twelve. Incoming fees and the later observed
collector-payment fees cannot replace this missing prior-spending information.
Current spent flags and reference-payment/future transactions are excluded.

The two small samples have different selection rules and must not be pooled to
estimate prevalence across all 500 sources. The 4/4 extraction success rate is
data coverage, not classification accuracy. There are no documented legitimate
controls, calibrated scores, hardware predictions or independent validation.
Stable counters and outpoint reconciliation are not cryptographic inclusion
proofs; historical API availability is not demonstrated by a current collection.

## Saved evidence and reproduction

- [Protocol](../multiinput_protocol_20261028.json): selection, pagination budget,
  pinned registry, frozen extractor and previous-cohort hashes.
- [Collection manifest](collection_manifest.json): eligible population (81),
  selection hash, per-source audits, retrieval dates and exact raw-file hashes.
- [Prior-block evidence](prefix_evidence.json): normalized prior transactions,
  values and hashed transaction/outpoint references.
- [Feature vectors](features.json): fourteen predictors separated from cutoff,
  group and unknown-label metadata.
- [Comparison summary](summary.json): real coverage and per-cohort ranges.
- `raw/` (local, ignored by Git): exact original provider snapshots. A new
  collection has different retrieval timestamps and possibly different contents.

The provider is `https://blockstream.info/api`. Source identities are
reconstructible from the pinned registry and deterministic selection; hashed
references do not guarantee anonymity. Full new address histories are not
republished as a bulk list of alleged victims.

From the repository root, the published evidence can be verified **offline**:

```bash
python "Task 2/research/coldcard/multiinput_pilot.py" verify \
  "Task 2/research/coldcard/multiinput_protocol_20261028.json" \
  "Task 2/research/coldcard/multiinput_pilot_20261028"
```

With the original raw snapshots, replace `verify` by `reproduce` to re-extract
and compare every analysis byte. To collect a new snapshot, choose a new output
directory and run `collect`, then `analyze`; existing directories/results are
refused. The first pilot's original `prepayment_pilot.py` commands still work.

```bash
python -m unittest discover -s "Task 2/research/coldcard" -p 'test*.py'
python "Task 2/check_repository.py"
```

Five added tests cover eligibility, deterministic selection, insufficient
populations, incomplete history, payment-anchor checks and reuse of the strict
cutoff. The [execution record](../../../verification/multiinput_pilot_20261028.json)
contains actual tests, raw/offline reproductions, cross-pilot overlap checks and
preservation of the first pilot.

## One next aligned unit

Move from pilots to a resumable collection over the 500 candidate sources,
reusing the twelve already collected histories and processing one short fixed
batch at a time. Retain coverage failures and strict cutoff/unknown-label rules;
do not start another unrelated benchmark or claim a hardware classifier.
