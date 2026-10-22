# Central experiment — Retrieve known collectors from complete Bitcoin blocks

## Question and answer

**Can simple, label-blind recipient rankings bring the known Coldcard and
CryptoBilis collectors near the top among all recipients in their incident blocks?**

Yes, in this retrospective experiment: counting **external funding transactions
with exactly one output** places the three supplied references at **ranks 1, 2
and 4**. Simple receipt counts and gross amounts do worse on the second case.
This is a concrete retrieval result, not a validated hardware-wallet classifier.

## Data and fixed procedure

The full population contains **30,938 transactions in six complete blocks**:
Coldcard heights 960188–960191, and CryptoBilis heights 970590–970591.
Six coinbase transactions are excluded from recipient features. All positive-value
outputs with a provider-decoded address are included, including change and
internal transfers. Zero-valued and address-less outputs are excluded.

The candidate populations are **6,426 recipient addresses** in the Coldcard
window and **13,264** in the CryptoBilis window. These are all eligible recipients,
not selected donation addresses or a balanced 100+100 sample.

Three baselines were fixed before computing the full-block rankings:

1. **Receipt count:** number of distinct transactions paying an address.
2. **External one-output count:** number of funding transactions with exactly one
   output, where all decoded input addresses differ from the recipient.
3. **Gross amount received:** total matching output values in integer satoshis.

Multiple outputs to one recipient in a transaction count once for receipt count;
their values all enter the amount. A self-payment cannot enter the second score.
Unknown input addresses do not establish external funding. One output does not
prove that all source-address UTXOs were drained. The address identifier and the
case reference are not ranking variables. No model is fitted or threshold tuned.

## Main results

Lower rank is better. All final reference ranks are untied.

| Case / supplied collector | Candidate recipients | Receipt count rank | External one-output rank | Gross received amount rank |
| --- | ---: | ---: | ---: | ---: |
| Coldcard `bc1qnk4…ecp0` | 6,426 | 9 | **1** | 3 |
| CryptoBilis `bc1qjq…49dl` | 13,264 | 11 | **2** | 19 |
| CryptoBilis `bc1qqn…jtm9` | 13,264 | 18 | **4** | 15 |

At the fixed top-10 review budget, the second score retrieves the supplied
Coldcard reference and both CryptoBilis references. Receipt count and amount
each retrieve the Coldcard reference and neither CryptoBilis reference.
This is **coverage of supplied references**, not recall over every theft in the
blocks or precision among the other candidates. The two CryptoBilis collectors
belong to one incident; the experiment has two incident groups, not three cases.

The second score is 500 for Coldcard and 76/46 for CryptoBilis. Other recipients
remain ahead of the CryptoBilis references: the strongest scores are 99 and 55.
They remain unreviewed leads, not classified criminals or confirmed false alarms.

## Confirmation-time progression

The code also ranks each case prefix after every selected block. No later
block or future spending is used in a prefix score.

- Coldcard is rank 1 on the second score after each of its four blocks, beginning
  with 63 receipts after block 960188.
- After block 970590, the CryptoBilis references are ranks 1 and 4 on that score.
  After block 970591, they are ranks 2 and 4.
- Other baselines can have ties: the first CryptoBilis reference is rank 4–5
  by receipt count after the first block. Best/worst tie intervals are retained;
  address sorting is not used to give a reference an optimistic rank.

## Integrity and interpretation

Every block's declared hash, height, time, main-chain flag and transaction count
are checked, along with declared input/output counts and contiguous output indices.
Transaction IDs must be unique within and across blocks; exactly
one first-position coinbase is required. Every positive receipt outpoint for the
three references agrees exactly with the already pinned Blockstream histories:
TXID, output index and value. The full-block data comes from Blockchain.com.
These are provider/record agreement checks, not cryptographic block-inclusion proof.

There are **194 shared recipient addresses** between the two candidate populations,
and no shared reference address or TXID. A future supervised split cannot assume
that all background entities are independent merely because the incidents differ.

The receipt-count leader in the second window is `bc1pfeessrawgf`. Its matching
script is `51024e73`, the P2A anchor template documented in the
[Bitcoin Core issue](https://github.com/bitcoin/bitcoin/issues/33265).
It is retained in the ranking population. A high count for a shared script
template must not automatically become a claim about a service or a key owner.

**Limits that determine the claim:** the block windows were located through
known incident receipts, and baseline ideas were informed by earlier case
descriptions. This is neither a blind blockchain-wide discovery experiment nor
an untouched external test. The reference set is incomplete. Hardware ownership,
victim identity and theft attribution are not established for all addresses.
No F1, false-positive rate, calibrated probability or general detection accuracy
can be inferred from these rankings.

## Reproduce the result

The committed evidence contains readable, anonymous cumulative score counts at
the supplied-reference and top-10 score values. No full address list is needed
to recalculate the reference ranks. Target scores are independently recomputed
from the pinned address histories, and score-count conservation is checked.
From `Task 2/research/external_cases`:

```bash
python rank_block_recipients.py reproduce central_results_20261020 central_protocol_20261020.json
python -m unittest discover -p 'test_*.py' -v
```

To independently repeat extraction from the six complete provider blocks:

```bash
python rank_block_recipients.py collect central_protocol_20261020.json /tmp/ufu-central-blocks
python rank_block_recipients.py analyze central_protocol_20261020.json \
  /tmp/ufu-central-blocks /tmp/ufu-central-new-results
```

The output directory must be new. Full per-recipient CSVs are generated locally
by `analyze` and excluded from Git. Raw JSON blocks total approximately 50 MB and
are also kept outside Git. Their hashes/URLs are recorded in
[the aggregate results](research/external_cases/central_results_20261020/summary.json).
Provider spent-status metadata may change on recollection; none enters the
features. Compare the canonical feature-cohort hashes and rankings, not mutable
raw-response bytes alone. The [protocol](research/external_cases/central_protocol_20261020.json)
records the selection, baselines, reference histories and tie policy.

Automatic upload review rejected opaque compressed cohorts and address-level
ranking details. These remain local. The committed alternatives are the smaller, readable
[score summary](research/external_cases/central_results_20261020/score_summary.json),
and aggregate results with reference IDs instead of addresses. Reference IDs 1,
2 and 3 correspond, in protocol order, to the Coldcard collector and the two
CryptoBilis collectors. Detailed CSVs and full rankings are retained locally
and reproducible through the public-block extraction command above.

Verification: **175 tests pass** across the six offline suites, including 14
new ranking/integrity tests. The supplied-reference ranks reproduce offline from
full-population cumulative counts and independently recomputed reference scores.
All 185 protected historical artifacts retain their hashes. See the
[actual verification log](verification/central_experiment_verified_20261020.json).

## What to tell Ivan

We ranked every eligible recipient in six complete incident blocks with three
simple scores. The external one-output count places the supplied Coldcard
collector first and the two CryptoBilis collectors second and fourth. It also
works on successive block prefixes. This supports a concrete collection-pattern
hypothesis worth testing beyond the selected incidents; it does not identify a
hardware brand or establish a general theft detector.

## Neighboring-block robustness check — 22 October 2026

The extension adds exactly one block immediately before and after each original
window: Coldcard 960187–960192 and CryptoBilis 970589–970592. The
[selection manifest](research/external_cases/neighbor_selection_20261022.json)
was saved before fetching or ranking those four additional blocks. Their hashes
were obtained from the previously saved boundary blocks. Predecessor links,
heights and the original integrity checks are verified. All three original
scores and the top-10 review budget are unchanged. This is a planned robustness
extension of known cases, not a preregistered independent test.

The enlarged population contains **53,526 transactions in ten blocks**:
22,588 additional transactions, with ten coinbases excluded from features.

| Reference | Expanded recipient population | Receipt count rank | External one-output rank | Gross amount rank |
| --- | ---: | ---: | ---: | ---: |
| Coldcard / reference 1 | 8,078 | 10 | **1** | 3 |
| CryptoBilis / reference 2 | 22,157 | 16 | **2** | 31 |
| CryptoBilis / reference 3 | 22,157 | 28–29 | **4** | 28 |

The external one-output ranks remain **1, 2 and 4**, with scores unchanged at
500, 76 and 46. No reference receives funds in its preceding block; each remains
unobserved rather than receiving an artificial zero-score rank. The successor
blocks add background recipients without adding reference receipts. Thus the
check tests dilution by nearby activity, not discovery of additional thefts.
Simple receipt-count ranks deteriorate, especially for the two CryptoBilis
references. The top-10 coverage comparison still favors the second baseline.

The expanded populations share 253 recipient addresses, no reference addresses
and no TXIDs. Shared recipients do not establish common ownership. There are
still only **two incident groups**. The small neighboring interval cannot
establish long-term stability, a false-positive rate or hardware attribution.
Full address tables and detailed rankings remain local; the published
[aggregate results](research/external_cases/neighbor_results_20261022/summary.json)
and [anonymous score counts](research/external_cases/neighbor_results_20261022/score_summary.json)
support the same offline reference-score/rank reproduction as the first run.
Raw-block URLs, hashes, byte counts and cohort hashes are recorded there.

From `Task 2/research/external_cases`:

```bash
python rank_block_recipients.py reproduce neighbor_results_20261022 neighbor_protocol_20261022.json
python -m unittest discover -p 'test_*.py' -v
# First obtain the original six blocks with the original collect command above.
# Choose new protocol/output paths; protocol must stay beside reference histories.
python extend_central_window.py neighbor_selection_20261022.json /tmp/ufu-central-blocks \
  neighbor_protocol_new.json /tmp/ufu-neighbor-new-results
```

The generated protocol records the selection-manifest and original-protocol
checksums. Histories and baseline definitions are reused without modification.
Four added tests cover fixed symmetric selection, skipped/duplicate neighbors,
incorrect chain links and offline expanded-rank reproduction. The external-case
suite passes **47 tests**; all six offline suites pass **179 tests** in total.
The full repository check is recorded in the
[extension verification log](verification/neighbor_experiment_20261022.json).

## Competing top-ranked patterns — 22 October 2026

A descriptive follow-up profiles **all top-10 ranks** on the expanded windows,
including any ties at the review boundary. There are ten selected recipients per
incident: three supplied references and **17 unattributed recipients** in total.
The baseline and candidate population remain unchanged. Candidate IDs are local
to a case and do not identify entities. Source addresses count decoded strings,
not victims, people, keys or hardware devices. No new labels or model are fitted.

| Case / profile | Fixed score | Receipt transactions | Distinct input addresses in qualifying transactions | Receipts with a self-input |
| --- | ---: | ---: | ---: | ---: |
| Coldcard reference 1 | 500 | 500 | 500 | 0 |
| Coldcard strongest competitor / candidate 2 | 71 | 81 | 68 | 10 |
| Coldcard candidate 3 | 45 | 45 | 45 | 0 |
| Coldcard candidate 4 | 19 | 21 | 1 | 1 |
| CryptoBilis strongest competitor / candidate 1 | 126 | 155 | 113 | 29 |
| CryptoBilis reference 2 | 76 | 76 | 76 | 0 |
| CryptoBilis candidate 3 | 55 | 56 | 55 | 1 |
| CryptoBilis reference 3 | 46 | 46 | 46 | 0 |

Nine unattributed recipients (five Coldcard, four CryptoBilis) have an external
one-output fraction of **100%**, as do the three references. The fraction alone
therefore does not separate the supplied references from other selected
candidates. These are **not confirmed false positives**: the other recipients
have no verified labels. Repeated transfers can also originate from the same
source address: Coldcard candidate 4 has 19 qualifying transactions but only
one distinct qualifying input address. Transaction counts cannot be reported
as victim counts. Forty-five receipts to Coldcard candidate 3 all have multiple
inputs, showing that the one-output rule does not require a single input.

The strongest CryptoBilis competitor spans all four blocks (9/64/58/24 receipts)
and has 29 self-input receipts excluded from its score. The two CryptoBilis
references have no receipts in the added neighboring blocks. This descriptive
timing difference is post-hoc; it is not a tuned filter or a validated classifier.

**Why receipt counts alone can mislead:** the Coldcard receipt-count leader has
6,142 receipts, all with its address also present in the input, and no one-output
receipts. Its collection score is zero. The CryptoBilis count leader has 1,818
receipts, 1,685 with a self-input, and no one-output receipts; its score is also
zero. Its matching output script is the P2A anchor template. These observations
explain some ranking differences without identifying the operators or alleging
illicit activity. They do not exclude other collection mechanisms.

The [anonymous profiles](research/external_cases/neighbor_results_20261022/competitor_profiles_20261022.json)
include all 20 selected candidates, receipt amounts in satoshis, per-block counts,
missing-input observations and exact rank intervals. The extractor checks the
saved protocol and raw-block SHA256 values, validates each block and recomputes
the recipient population and each selected baseline score. Future spending
metadata is not used. No full addresses or transaction identifiers are published
in the profile artifact.

From `Task 2/research/external_cases`, with the original matching block cache:

```bash
python profile_ranked_recipients.py neighbor_protocol_20261022.json \
  neighbor_results_20261022/summary.json /tmp/ufu-central-blocks /tmp/ufu-profiles-new.json
python -m unittest discover -p 'test_profile_ranked_recipients.py' -v
```

If a fresh provider response has different mutable raw bytes, regenerate the
expanded ranking and use its matching summary/cache instead of bypassing the
checksum check. Five new tests cover review-boundary ties, repeated outputs,
self/unknown inputs, repeated input addresses, protocol tampering and exclusion
of future spending metadata. All six offline suites pass **184 tests**; the
20 saved profiles reproduce exactly from the ten pinned cached blocks. See the
[profile verification log](verification/competitor_profiles_20261022.json).

## Next step within this experiment

Keep the three baselines unchanged. The candidate-profile review is complete;
no source labels support a precision/F1 claim for the other recipients. The next
scientific gain requires independent incident/role evidence or Ivan's code and
its dataset assumptions, followed by comparison against this saved baseline.
Avoid filtering the competing patterns merely to improve these known-case ranks.
