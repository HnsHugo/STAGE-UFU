# BTCPay Server source intake, batch 13

Both pending references from the collector page have complete transaction
tables and are confirmed in [block 974,160](https://bitcoin.prod.gke.papers.tech/block/974160). The linked
block page confirms the height and hash. Each transaction has a single output
to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).

| Payment | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: |
| [`369a3e20248d`](https://bitcoin.prod.gke.papers.tech/tx/369a3e20248da148bc82896e79cb50bef67c824c6752d05fed3867b0cda1a79e) | 1 | 256,327 | 255,351 | 976 |
| [`c4e4dc1ac6fb`](https://bitcoin.prod.gke.papers.tech/tx/c4e4dc1ac6fb01b0224a8093882d55cc40d2ebe9fbfe7974a5dd49999d62b01b) | 1 | 75,163 | 74,163 | 1,000 |
| **Total** | **2** | **331,490** | **329,514** | **1,976** |

The input values reconcile to the displayed totals and to the collector
outputs plus fees. The [registry](source_registry.json.gz) adds two distinct
address fingerprints, grouped by payment. The two groups have zero exact
address matches with each other or earlier BTCPay observations. Exact address
and reference-TXID comparisons with the pinned Coldcard and CryptoBilis
selections found zero matches. Links between groups, merchant identity and
individual compromise remain unverified.

The cumulative registry covers **2,466 distinct addresses across 26 documented
payments**. Twenty-five have reconciled input tables. The partial pilot
retains its 11 visible addresses. This batch adds zero complete individual
histories. Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part13.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `354afd38d9348f9e1e426b012b8ec84d9e855b6513d53b8bd238348211c63fbc`.
The [protocol](protocol.json) pins the earlier registries, lists all documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part13.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_13/protocol.json"
```
