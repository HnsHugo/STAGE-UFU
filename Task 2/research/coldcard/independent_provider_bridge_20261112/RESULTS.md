# Verified independent-provider bridge — 12 November 2026

The explicit request to find another acquisition method is implemented and verified
with the public Mempool API. The original Blockstream scope remains closed; its
local cooldown is unchanged. Mempool has its own public limits. No paid service,
account, IP, proxy, TLS or automatic provider change was used.

## Observed results

| Measure | Verified result |
|---|---:|
| Fresh Mempool responses | 25 HTTP200, zero failure |
| Saved Blockstream response bodies verified | 36 |
| Overlapping transaction cores verified | 7 |
| Additional source-transaction observations | 419 |
| Newly complete fourteen-feature prefixes | 1 |
| All preceding vectors preserved | 1,401 |
| Coldcard prefix vectors now available | 1,402 / 1,500 |
| CryptoBilis prefix vectors, unchanged | 329 / 366 |
| Information gaps retained across both cohorts | 135 |
| Focused software checks | 13 passing |
| Fits / new model scores | 0 / 0 |

comparison_0351 retains 844 distinct transactions: 425 old observations plus
419 new ones, six verified overlaps, and seventeen native Mempool pages. It
remains bounded with null features. comparison_0358 retains all 379 previous
transactions, verifies one overlap and two native pages, and now meets the
original completeness and funding-closure requirements. Its new vector was
recounted independently. Observations are source-transaction pairs, not globally
unique transactions.

## Acquisition correction and scientific scope

The first preserved probe exposed intra-block ordering differences between
indexers. The corrected bridge rewinds above the partial boundary block and
compares immutable transaction fields at every overlap. Only native Mempool
cursors drive fresh pagination. The checked union contains each transaction
once; unknown transactions in previously complete newer blocks are rejected.
A native empty terminal page, matching before/after reference block and original
UTXO funding closure are mandatory before producing a complete vector.

The unit is the frozen source/reference pair and the target remains the
operational incident-membership proxy. Fourteen predictors use transactions at
heights strictly below the reference block. Unknown theft and hardware-wallet
labels stay unknown; comparison addresses are not proven legitimate. All old
identities, cutoffs, full-current statuses and models/scores are unchanged. No
training, scoring, split or threshold change occurred. Recheck overlap before
any future updated-snapshot model work.

Both audits pass. All 131 private evidence files are verified and saved. The
archive includes actual native cursors and the verified 82-source identity
registry. Public files contain hashes and pseudonymous IDs, not raw identities.

## Retained continuation

This scope is closed and cannot restart. The lease is idle, locks are free and
automation is disabled. A distinct bounded native-Mempool scope may collect the
eighteen remaining original pending sources, using their existing identities
and cutoff. Preserve comparison_0351's actual native cursor: the last element of
the sorted union is not a safe cross-provider pagination cursor. All three
576-page histories, prior queues and 42 untouched sources remain retained.
Keep one worker, five-second request spacing and first-failure stop. Do not
probe the closed Blockstream route before its unchanged due time.
