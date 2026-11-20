# BTCPay Server source intake, batch 12

Both pending references from the collector page have complete transaction
tables and are confirmed in [block 974,161](https://bitcoin.prod.gke.papers.tech/block/974161). The linked
block page confirms the height and hash. Each transaction has a single output
to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).

| Payment | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: |
| [`67ca233b301e`](https://bitcoin.prod.gke.papers.tech/tx/67ca233b301e8acf13282e7c6509cd1cb8c4a532f39a20785b432667e9202606) | 1 | 1,194 | 1,072 | 122 |
| [`881b362d77d3`](https://bitcoin.prod.gke.papers.tech/tx/881b362d77d3bf815f0bec1a68f5ad07da3fbefe0163c77c51e2c37f01dc6aac) | 1 | 21,196 | 20,220 | 976 |
| **Total** | **2** | **22,390** | **21,292** | **1,098** |

The input values reconcile to the displayed totals and to the collector
outputs plus fees. The [registry](source_registry.json.gz) adds two distinct
address fingerprints, grouped by payment. There are no exact matches between
the groups, with earlier BTCPay observations, or with the pinned Coldcard and
CryptoBilis selections. This comparison uses address fingerprints and reference
TXIDs where available. Links between groups, merchant identity and individual
compromise remain unverified.

The cumulative registry covers **2,464 distinct addresses across 24 documented
payments**. Twenty-three have reconciled input tables. The partial pilot
retains its 11 visible addresses. This batch adds zero complete individual
histories. Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part12.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `4658557b1a1cf3dde4ec852eae8cc21ffe6c870211bb1dcc00c6d11d45f1bece`.
The [protocol](protocol.json) pins the earlier registries, lists all documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part12.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_12/protocol.json"
```
