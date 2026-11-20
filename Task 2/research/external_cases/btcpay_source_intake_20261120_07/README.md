# BTCPay Server source intake, batch 7

The two pending leads from the [collector page](protocol.json) now have
complete public transaction tables. Each has one output to the collector in
the [BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).
The heights and hashes match the linked block pages.

| Payment | Block | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`31ded28c8a6d`](https://bitcoin.prod.gke.papers.tech/tx/31ded28c8a6ddf22d331d739359c2bb8706b38a2b4e7db28ae20fe036360ea21) | 974,164 | 3 | 44,456 | 38,781 | 5,675 |
| [`8d45f56cce1d`](https://bitcoin.prod.gke.papers.tech/tx/8d45f56cce1de942faba23adb1887bf6d96d4aa76b53a0c5e974e58ab40da7e5) | 974,163 | 1 | 44,873 | 44,573 | 300 |
| **Total** | | **4** | **89,329** | **83,354** | **5,975** |

Both sets of input values reconcile to the published totals and to collector
output plus fees. The [registry](source_registry.json.gz) adds four distinct
input-address hashes. There are zero exact address or reference-TXID matches
with the pinned Coldcard and CryptoBilis selections. Each transaction serves
as its own co-input group. Links between groups, merchant identity and
individual compromise remain unverified.

The cumulative registry covers **1,978 distinct addresses across 14 documented
payments**. Thirteen payments have reconciled input tables, and the partial
pilot retains its 11 visible addresses. This batch adds zero complete individual
histories. Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part7.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `aa801e94a095ba9d456c0201083073dc180fe3d7e60b6b357f306f7d790523ed`.
The [protocol](protocol.json) pins the earlier registries, lists all documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part7.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_07/protocol.json"
```
