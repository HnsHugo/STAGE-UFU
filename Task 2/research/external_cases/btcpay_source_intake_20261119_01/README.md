# BTCPay Server source intake — first batch

This intake extends the [BTCPay source pilot](../btcpay_hot_wallet_pilot_20261119/README.md)
for a later external test of the pooled Coldcard and CryptoBilis model. It
records Bitcoin addresses observed funding two single-output payments to the
destination in the BTCPay advisory. They are graph candidates for source-cohort
membership. Merchant ownership and individual compromise remain unresolved.
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/)

| Reference block | Input rows | Distinct addresses | Collector output | Fee (sat) |
| ---: | ---: | ---: | ---: | ---: |
| 974,172 | 1,316 | 1,282 | 0.79509561 BTC | 90,461 |
| 974,178 | 69 | 69 | 0.07781110 BTC | 9,492 |
| **Total** | **1,385** | **1,351** | **0.87290671 BTC** | **99,953** |

The two published input tables were transcribed in full. Each table's values
sum to the reported inputs, and the input total equals the collector output
plus the fee. Both references are within the height window in the
[protocol](protocol.json). Full transaction IDs and block hashes are included
with each reference.
[Block 974,172 transaction](https://bitcoin.prod.gke.papers.tech/tx/22f6b68ef2c2d889230795634fd90ca0185a4344eca7e18a4e5d5bfd4300b017) ·
[Block 974,178 transaction](https://bitcoin.prod.gke.papers.tech/tx/00454b5f90c5e4e0dedc38a5f7242b6f8914d63a7123a55eb09a6f9c701d5203)

The two payments have zero matching input addresses, so the observed source
graph has two components in this batch. All 1,351 address digests are distinct
from the 11 individually observed pilot addresses. The development check
found zero exact address or reference-transaction matches against the 1,500
Coldcard and 366 CryptoBilis selections. These checks use exact identities.
Funding links between groups and the remaining inputs of the original pilot
transaction require full transaction evidence.

## Acquisition and replay

The intake used publicly displayed explorer records. It made **zero direct
requests to the collection APIs**. The published collection lease remains
marked running for Coldcard unit 53. Testing 263 distinct observable lock files found
them free at inspection time. The published lease remains the authority for
direct collection.

The evidence archive `BTCPay-source-evidence-20261119-part1.json.gz` was
reopened and matched byte for byte. Its SHA-256 digest is
`fa786906349b6595d73ba0203a86daae239342fa940e5cc9c753b34dabb8a60e`.
The [hashed registry](source_registry.json.gz) contains the aggregate audit and
the identifiers needed to check overlaps in later batches.

```bash
scope="Task 2/research/external_cases/btcpay_source_intake_20261119_01"
python3 "$scope/audit.py" /path/to/BTCPay-source-evidence-20261119-part1.json.gz
```

The collector census, funding outpoint verification, independent-group audit,
matched controls, and pre-reference feature histories are still pending. Model
evaluation remains gated on those inputs.
