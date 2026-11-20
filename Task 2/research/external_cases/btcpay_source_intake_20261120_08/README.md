# BTCPay Server source intake, batch 8

The two pending references from the collector page have complete transaction
tables. Both payments are confirmed in [block 974,163](https://bitcoin.prod.gke.papers.tech/block/974163)
and each has one output to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).
The transaction pages agree with the linked block page on the height and hash.

| Payment | Block | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`1b01cb746115`](https://bitcoin.prod.gke.papers.tech/tx/1b01cb7461150f55d168230504316891ef934c6feb50f7c570e118608f4079d8) | 974,163 | 1 | 32,087 | 31,773 | 314 |
| [`8ef5681b8b7d`](https://bitcoin.prod.gke.papers.tech/tx/8ef5681b8b7d360135535d0589559508372751b340bf88c4e3311fa410068153) | 974,163 | 4 | 82,336 | 81,336 | 1,000 |
| **Total** | | **5** | **114,423** | **113,109** | **1,314** |

Both sets of inputs reconcile to the displayed totals and to collector output
plus fees. The [registry](source_registry.json.gz) adds five distinct input
address hashes. Exact address and reference-TXID checks against the pinned
Coldcard and CryptoBilis selections found zero matches. Each transaction
defines its own co-input group. Links between groups, merchant identity and
individual compromise remain unverified.

The cumulative registry covers **1,983 distinct addresses across 16 documented
payments**. Fifteen payments have reconciled input tables. The partial pilot
retains its 11 visible addresses. This batch adds zero complete individual
histories. Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part8.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `8f91353933b8150c0a72c8d2ce5ff539ba52fe4570985a259ae192be7bf53993`.
The [protocol](protocol.json) pins the earlier registries, lists all documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part8.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_08/protocol.json"
```
