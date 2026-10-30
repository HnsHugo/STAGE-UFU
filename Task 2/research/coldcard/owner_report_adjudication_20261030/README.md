# First-person owner-report adjudication — 30 October 2026

## Executed unit

Follow public owner/report-based leads from the external reconstructions and
map exact source/payment identifiers to the fixed 500-address cohort. The
observation unit is a source address, with distinct targets for reported loss,
declared hardware association, independently verified compromise/seed origin
and signing-device use. This is a lead-driven review, not a random sample or
exhaustive victim search. No training, controls or new feature extraction occurred.

## Result

One first-person account maps exactly to **`cohort_0002`**. Its original
[loss report](https://www.reddit.com/r/Bitcoin/comments/1vatgl4/full_panic_one_of_my_wallets_was_drained/)
links the [payment explicitly](https://www.reddit.com/r/Bitcoin/comments/1vatgl4/comment/p0peuvv/).
The same author's [follow-up timeline](https://www.reddit.com/r/Bitcoin/comments/1vb6teq/wallet_drained_timeline/)
publishes the source address and describes a Mk3 setup followed by a Mk4
restoration. These are one report, not independent confirmations.

The independently saved chain data matches both identifiers. The reference
payment is confirmed in block **960189**, at **2026-07-30 01:37:21 UTC**.
It consumes **five inputs totaling 78,962,661 satoshis** from that source and
all five UTXOs known at the prior-block cutoff. These observations do not prove
that every address in the author's wallet was emptied or who authorized signing.

| Evidence layer | Current result |
| --- | --- |
| Exact source address and payment match | Observed for `cohort_0002` |
| First-person loss declaration | Recorded as `reported_loss_label = 1` |
| Declared hardware association | Recorded as Coldcard; Mk3/Mk4 claims remain declarative |
| Owner identity / proof of control | Not independently verified |
| Seed-origin, firmware cause and theft-signing device | Not independently verified |
| Other 499 cohort records | Unchanged; no label propagation |
| Model fitting | None |

See the [per-report decision](adjudication.json), [review protocol](protocol.json)
and [verification journal](../../../verification/source_owner_reports_20261030.json).
Original feature/label snapshots and the 500-source corroboration layer remain
unchanged. This is a new **owner-reported evidence tier**, not a verified-label
training dataset. It supplies one individually traceable example beyond a
chain-pattern attribution; it does not label the full cohort.

## Dates and unresolved points

The readable pages expose relative posting times. Direct JSON access was
unavailable, so absolute publication and original label-availability timestamps
remain unknown. The project observed the evidence on 30 October; transaction
time must not be substituted for report publication time.

The dedicated timeline is more specific than earlier comments about restoration
timing; the discrepancy is retained in the decision. Setup age is not the
first-funding age of one address, and restoring an existing seed does not identify
the signer of a later theft transaction. A statement about a suspected failure
point is not a firmware diagnosis. No device firmware version or forensic
control proof was established here.

## Other leads reviewed

- Alvaro P.'s source registry provided the public discussion followed above.
- SomaxBT mentions an owner-confirmed wave-4 account without an exact report URL
  in the reviewed README; that statement cannot be assigned to our July 30 cohort.
- Coldcard Watch describes report verification, but the reviewed public GitHub
  issues API returned zero entries and no individually adjudicated report feed.
  Its heuristic/common-input assertions are not adopted as ownership proof.
- Coldcard Entropy retrieval failed; no historical-report CSV was ingested.
- The referenced KLoaec/Rob Hamilton X pages were inaccessible; no labels are
  inferred from them. Private victim correspondence is not a public dataset.

## Verification and reproduction

Eight new tests reject receiver/source confusion, wrong transactions, third-party
summaries, unsupported hardware inference, duplicate-account counting, and
corrupted payment anchors/amounts and redacted-input tampering. All **42 source-path tests** pass. Exact
reproduction also verifies the frozen cohort/checkpoint hashes and preserves
unknown independently verified labels.

Focused readable-page extracts stay in the ignored local working directory;
their hashes are recorded. The [redacted curated facts](redacted_assertions.json)
are public: exact address/payment identifiers can be restored in memory from
the pinned cohort by both hashes, and the resulting canonical snapshot must
match its original SHA256. The decision reproduces without the private working
cache; the source assertions themselves still require human review of the
permalinks. Current live pages need not reproduce historical extracted bytes or
relative timestamps.

```bash
python "Task 2/research/coldcard/adjudicate_owner_reports.py" verify \
  "Task 2/research/coldcard/owner_report_adjudication_20261030/protocol.json" \
  "."
```

## Next aligned unit

Find further attributable public reports with explicit source/payment identifiers
and record their declared device history and availability dates. Keep authors,
addresses, wallets and incident groups distinct. A future study of reported
case association needs a separately stated target and suitable controls; this
single account cannot validate a general theft or hardware-wallet classifier.
