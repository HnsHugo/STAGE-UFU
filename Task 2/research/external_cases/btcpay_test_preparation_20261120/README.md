# BTCPay Server external test preparation

BTCPay is held out from the frozen Coldcard and CryptoBilis models. The unit is
an address at a documented reference payment. The target is observed membership
in the source cohort. Merchant identity, individual compromise and the signing
device remain unverified.

All 15 saved intake archives reproduce their published registries. The private
catalogue contains **2,463 address/reference pairs from 29 reconciled payments**.
Each pair retains the address, reference transaction, reference block height
and hash, input count, and aggregate satoshi value for anchor verification.
Observed co-input groups use the reference transaction fingerprint. The 11
witnesses of the partly visible pilot remain represented by their saved hashes,
bringing the observed registry to 2,474 distinct addresses. Comparisons with
the pinned development selections found no exact address or reference-transaction
overlap. Funding and intergroup links still require history-level checks.

The protocol freezes **one candidate per covered reference block**, 16 in all,
using only salted fingerprints. This bounds the first coverage study before
any scores or history availability are known. It calls for two comparison
addresses per block, selected independently from complete same-block input
censuses after excluding known linked sources. The [preparation report](preparation.json)
provides reproducible aggregate counts and the private catalogue SHA-256.
The private save was reopened and matched byte for byte.

## Reconstruct the reference catalogue

Put the 15 verified intake archive files in one private directory, then run
from the repository root. The output path must be outside the repository.

```sh
scope="Task 2/research/external_cases/btcpay_test_preparation_20261120"
python3 "$scope/prepare.py" /private/intake-archives /private/BTCPay-test-catalogue-20261120.json.gz
```

## Audit a saved prior history

The offline verifier accepts a privately saved, fingerprinted capture from an
authorized collection. The capture JSON has `address`, `reference` (the
confirmed Esplora transaction), `reference_after` (the reread status),
`parent_statuses` (keyed by funding TXID), and ordered `pages`. Each page
stores `after_txid` and its decoded `transactions` list. The first native
cursor is the frozen reference TXID. Supply the capture fingerprint from its
verified evidence manifest. An unexhausted tail yields no features. A complete
tail requires stable reference confirmation, funding closure, and an empty
terminal page. The 14 features use only confirmed transactions in blocks
**strictly below** the reference height and must match the independent recount.

```sh
python3 "$scope/verify_prefix.py" CATALOGUE CATALOGUE_SHA256 SOURCE_ID CAPTURE CAPTURE_SHA256 /private/result.json.gz
```

Use the existing [same-block census validation](../../coldcard/source_comparison_design.py)
before selecting the pilot comparisons. Verify their references and prior
prefixes to the same standard. Keep shared funding and co-input links together
when checking overlap against development. Report coverage by block and group
before scoring with the pinned development models.

The required BTCPay history and census archives are still missing. The published
global lease still records Coldcard unit 53 as running. Preparation made no
direct collection requests and produced zero BTCPay feature vectors and zero
model evaluations. The offline verification tests used a repository test fixture.
