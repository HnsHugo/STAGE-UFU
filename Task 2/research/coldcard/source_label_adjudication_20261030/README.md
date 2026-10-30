# Exact-identifier source-label adjudication — 30 October 2026

## Executed unit

Five source addresses were fixed before public retrieval: `cohort_0001` through
`cohort_0005`, the first five records in the existing frozen SHA256 cohort order.
Each was searched by its quoted exact address and reference-payment TXID,
for ten planned queries. The unit is a source address. Compromise, hardware seed
origin and signing-device use at the event are separate targets. The 500-row
feature checkpoint and its strict prior-block cutoffs were not changed; no
training, negative control or evaluation split was introduced.

See the [prespecified protocol](protocol.json), [per-source decisions](adjudication.json)
and [verification](../../../verification/source_label_adjudication_20261030.json).

## Result and evidential limits

| Scope | Result |
| --- | ---: |
| Fixed sources individually searched | 5 |
| Exact-identifier queries executed | 10 |
| Sources with identifiers appearing in explorer search results | 5 |
| Qualifying individual compromise assertions found | 0 |
| Qualifying individual hardware assertions found | 0 |
| Labels promoted / supervised-eligible additions | 0 |
| Other cohort sources not individually searched | 495 |

The relevant results were transaction/block explorer records. Generic lookup
pages without an exact identifier were discarded. Mempool pages returned no
readable lines on opening, so their search snippets are recorded as discovery
evidence only. The readable BTC Fees block page supplies ledger observations.
These sources do not independently establish unauthorized taking, seed origin
or signing-device identity. We found no qualifying individual assertion within
this bounded retrieval; we do not claim none exists elsewhere.

All three target labels remain **unknown** for all five reviewed sources.
Their on-chain input relationship remains observed. Unknown is not a negative
class. This pilot is not a population-wide label audit, a victim count or an
accuracy measurement. The feature-complete cohort remains 500 addresses with
zero adjudicated individual labels and no documented target-matched controls.

## What evidence would change a decision

A usable compromise assertion must identify the exact address, transaction or
outpoint, state its role in unauthorized taking, and have an attributable source,
event period, publication date and label-availability date. Device evidence must
separately tie that wallet to seed generation or the relevant signing event.
An explorer link, aggregate incident total, address type or absence of a report
does not supply those assertions. The minimum fields and distinct target
definitions are in the [evidence review](../source_label_review_20261029.json).

Queries and full retrieval responses are retained in the ignored local working
directory. Published records contain cohort identifiers, hashes, evidence URLs,
review scope and decisions, avoiding a new bulk list of alleged victims.
The query hashes and fixed selection can be checked against the pinned cohort
plan. Search results are time-dependent; replay is not guaranteed to return the
same snippets. Saved retrieval hashes document this review, rather than making
the search engine an immutable dataset.

## Next aligned unit

Prioritize a public owner/researcher incident report that publishes an exact
source/payment identifier and explicit role, then map it to the registry and
adjudicate its date, independence and device claim. The focused case-reference
review and these ten searches have not supplied such evidence. Do not extend
blind explorer searches or recast graph candidates as verified victims simply
to obtain training labels. If the intended experiment uses a proxy relationship
instead, define that different target and its controls/split explicitly before
fitting; it cannot demonstrate hardware-wallet or theft identification.
