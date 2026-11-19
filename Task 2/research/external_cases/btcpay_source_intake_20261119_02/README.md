# BTCPay Server source intake — second batch

The first manual run of the BTCPay automation collected two complete displayed
Bitcoin input tables inside the [existing height window](protocol.json). Both
payments have a single output to the collector named in the BTCPay advisory.
Individual compromise and common merchant ownership remain undetermined.
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/)

| Reference block | Input rows | Distinct input addresses | Collector output (sat) | Fee (sat) |
| ---: | ---: | ---: | ---: | ---: |
| 974,155 | 12 | 12 | 298,555 | 9,000 |
| 974,166 | 6 | 6 | 88,444 | 924 |
| **Total** | **18** | **18** | **386,999** | **9,924** |

The captured rows reconcile with the displayed input totals. Both payments
balance exactly in satoshis. The block hashes and reference transactions are in
the protocol. The prior registry contained none of the 18 input addresses.
Exact identity checks also found zero address or reference-transaction matches
in the pinned Coldcard and CryptoBilis selections.
[Block 974,155 payment](https://bitcoin.prod.gke.papers.tech/tx/6d61beff902953ea50a60edc49f2441d6dc47b75a5f35c0d93bfe6e6b0f59413) ·
[Block 974,166 payment](https://bitcoin.prod.gke.papers.tech/tx/4260975a3e18198f030191f4138e5969746804a52119c6dec282d0ab1b81dcd5)

The cumulative observed registry now counts 1,380 distinct addresses across
five documented payments, including the 11 individually visible witnesses
from the [partial pilot](../btcpay_hot_wallet_pilot_20261119/README.md).
Independence of merchant groups, funding outpoints, complete individual
histories and comparison sources still require additional evidence.

## Checkpoint and replay

The raw observation backup `BTCPay-source-evidence-20261119-part2.json.gz`
was reopened and matched byte for byte. Its SHA-256 digest is
`42d17ffbc4910c8db0f9a05f5c54048cfd0a1511f9b0a6f8a04d57622a3c229a`.
The [published registry](source_registry.json.gz) retains only address hashes
and aggregate values. All data in this batch came from displayed public
records. The published Coldcard lease remains marked running.

```bash
scope="Task 2/research/external_cases/btcpay_source_intake_20261119_02"
python3 "$scope/replay.py" /path/to/BTCPay-source-evidence-20261119-part2.json.gz
```

The protocol records three screened transactions below the accepted window and
one pending public lead. Pagination on the linked collector page is a discovery
hint. Each candidate requires its own confirmed reference-height and complete
displayed-input check.
