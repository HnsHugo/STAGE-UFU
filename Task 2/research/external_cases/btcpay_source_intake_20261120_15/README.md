# BTCPay Server source intake, batch 15

Both pending references from the collector page have complete transaction
tables. The linked block pages confirm their heights and hashes at
[974,158](https://bitcoin.prod.gke.papers.tech/block/974158) and [974,157](https://bitcoin.prod.gke.papers.tech/block/974157).
Each payment has one output to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).

| Payment | Block | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`38347deb70e7`](https://bitcoin.prod.gke.papers.tech/tx/38347deb70e7a9f22206eb86c56adafee9d64a36d8209cf7301c38873713d2e5) | 974,158 | 4 | 72,926 | 71,426 | 1,500 |
| [`769e108188b1`](https://bitcoin.prod.gke.papers.tech/tx/769e108188b1c7f39720cab1c68ba3062491197834464ac0062a170b6acbeafb) | 974,157 | 1 | 5,000 | 4,756 | 244 |
| **Total** | | **5** | **77,926** | **76,182** | **1,744** |

The input rows reconcile to the displayed totals and to collector output
plus fees. The [registry](source_registry.json.gz) adds five distinct address
fingerprints grouped by payment. Exact address comparisons found zero matches
between the groups or with earlier BTCPay observations. The pinned Coldcard
and CryptoBilis selections have zero exact address or reference-TXID matches
with this batch. Links between groups, merchant identity and individual
compromise remain unverified.

The cumulative registry covers **2,474 distinct addresses across 30 documented
payments**. Twenty-nine have reconciled input tables. The partial pilot retains
its 11 visible addresses. This batch adds zero complete individual histories.
Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part15.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `aa2e97c78e963f3f3784c29563995589e02a21d43408f731a98adcde08c3ebe8`.
The [protocol](protocol.json) pins the earlier registries, lists the documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part15.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_15/protocol.json"
```
