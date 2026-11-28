# Bitfinex 2016 source-membership evaluation

The outcome is documented source-cohort membership at the address's reference payment. Witnesses are comparison observations from the same incident. Features use confirmed transactions strictly before the reference block. See the [frozen evaluation protocol](PROTOCOL.md) and [method inventory](methods.csv).

| Incident | Sources | Witnesses | Linked groups |
| --- | ---: | ---: | ---: |
| Coldcard | 500 | 963 | 1 |
| CryptoBilis | 122 | 207 | 1 |
| BTCPay | 16 | 32 | 8 |
| Bitfinex | 706 | 1412 | 2 |

These are the eligible populations before excluding links to the specific training set. The overlap audit retained eight historical addresses with an unavailable replay as identity records outside model fitting and scoring.

## Phase 1 · External Bitfinex evaluation

All seven transfers use training references after Bitfinex and are retrospective. The table gives the most sources retrieved among configurations within the realized false-alert budget, using fewer false alerts and then AP to break ties. These summaries describe the results. They did not drive model or threshold selection.

| Training | Test population | Sources / witnesses | Groups | Most sources retrieved within 5% realized | Inactivity TP / FP |
| --- | --- | ---: | ---: | --- | ---: |
| Coldcard | Pilot-unseen | 7 / 14 | 1 | Unavailable | — |
| Coldcard | All eligible | 7 / 14 | 1 | Unavailable | — |
| CryptoBilis | Pilot-unseen | 7 / 14 | 1 | Unavailable | — |
| CryptoBilis | All eligible | 7 / 14 | 1 | Unavailable | — |
| BTCPay | Pilot-unseen | 7 / 14 | 1 | `inactivity` · 0 TP / 0 FP (0.0%) | 0 / 0 |
| BTCPay | All eligible | 7 / 14 | 1 | `inactivity` · 0 TP / 0 FP (0.0%) | 0 / 0 |
| Coldcard + CryptoBilis | Pilot-unseen | 7 / 14 | 1 | Unavailable | — |
| Coldcard + CryptoBilis | All eligible | 7 / 14 | 1 | Unavailable | — |
| Coldcard + BTCPay | Pilot-unseen | 7 / 14 | 1 | `logit_inactivity_balance` · 4 TP / 0 FP (0.0%) | 2 / 0 |
| Coldcard + BTCPay | All eligible | 7 / 14 | 1 | `logit_inactivity_balance` · 4 TP / 0 FP (0.0%) | 2 / 0 |
| CryptoBilis + BTCPay | Pilot-unseen | 7 / 14 | 1 | `rbf_svm` · 5 TP / 0 FP (0.0%) | 2 / 0 |
| CryptoBilis + BTCPay | All eligible | 7 / 14 | 1 | `rbf_svm` · 5 TP / 0 FP (0.0%) | 2 / 0 |
| Coldcard + CryptoBilis + BTCPay | Pilot-unseen | 7 / 14 | 1 | `random_forest` · 6 TP / 0 FP (0.0%) | 2 / 0 |
| Coldcard + CryptoBilis + BTCPay | All eligible | 7 / 14 | 1 | `random_forest` · 6 TP / 0 FP (0.0%) | 2 / 0 |

Among 128 scorable budget-calibrated method and training-set results on the all-eligible test, 59 exceeded 5% realized false alerts. The full table includes weak and unavailable results, the two test populations, and applicable historical operating points. [Phase 1 results](phase1.csv)

The two Bitfinex populations coincide after the external overlap quarantine across all seven training sets. They contain seven sources and fourteen witnesses in one connected group. A single false alert would represent 7.1% of witnesses. The results give one group-level observation of transfer.

## Phase 2 · Exploratory four-incident benchmark

The matrix covers all 225 ordered train and test pairs. Its seven legacy-to-Bitfinex pairs overlap Phase 1. The reuse flag identifies predictions reused with identical training observations, grouping and test population. The all-eligible sensitivity defines the matching Phase 1 population.

| Pair type | Cells accounted for | Cells with a scorable budget result | Scorable budget method rows / total |
| --- | ---: | ---: | ---: |
| Disjoint | 50 | 8 | 256 / 1600 |
| Diagonal | 15 | 8 | 256 / 480 |
| Overlap | 160 | 52 | 1664 / 5120 |

Classification counts, recall, precision, AP, realized false-alert rate and group counts are reported per test incident and in a pooled view. Of the 2176 complete pooled budget results, 2048 use training references after a tested reference. AP for pooled mixed fits describes a pooled ranking across fold-specific and external scores, whose scales can differ. The repeated populations and nested cross-validation make this an exploratory benchmark.

[Disjoint pairs](matrix-disjoint.csv) · [Diagonals](matrix-diagonal.csv) · [Other overlaps](matrix-overlap.csv)

| Reason a pooled budget result is unavailable | Method rows |
| --- | ---: |
| `partial_incident_coverage:coldcard` | 768 |
| `partial_incident_coverage:cryptobilis` | 768 |
| `partial_incident_coverage:coldcard\|cryptobilis` | 608 |
| `empty_after_eligibility_or_quarantine` | 448 |
| `no_valid_grouped_calibration` | 448 |
| `partial_incident_coverage:coldcard\|bitfinex` | 352 |
| `partial_incident_coverage:cryptobilis\|bitfinex` | 352 |
| `partial_incident_coverage:coldcard\|cryptobilis\|bitfinex` | 352 |
| `no_valid_grouped_outer_split` | 128 |
| `partial_incident_coverage:bitfinex` | 128 |
| `partial_incident_coverage:coldcard\|btcpay` | 96 |
| `partial_incident_coverage:cryptobilis\|btcpay` | 96 |
| `partial_incident_coverage:btcpay\|bitfinex` | 96 |
| `partial_incident_coverage:coldcard\|cryptobilis\|btcpay` | 96 |
| `partial_incident_coverage:coldcard\|btcpay\|bitfinex` | 96 |
| `partial_incident_coverage:cryptobilis\|btcpay\|bitfinex` | 96 |
| `partial_incident_coverage:coldcard\|cryptobilis\|btcpay\|bitfinex` | 96 |

A blank metric indicates that its denominator, two-class ranking, or full population coverage is unavailable. Incident-level predictions from evaluable portions of mixed tests retain their own aggregate results.

## Dependency audit

| Incident combination in cross-incident components | Components |
| --- | ---: |
| Bitfinex + BTCPay + Coldcard + CryptoBilis | 1 |

The identities of observations with incomplete histories still contributed known dependencies. The protocol audits exact feature matches separately because identical aggregates can arise from distinct histories. Physical dependencies control the splits. The two independent component calculations agreed, and confusion counts and AP were checked by independent calculations.

## Candidate decision

The candidate remains supported by the existing registry comparison. Phase 1 is retrospective, and Phase 2 reuses previously studied incidents in its exploratory design. This experiment supplies no new qualifying chronological test on an intact incident. [Current candidate and decision history](../../CURRENT.md)
