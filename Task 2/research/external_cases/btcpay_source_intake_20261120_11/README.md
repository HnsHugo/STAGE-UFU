# BTCPay Server source intake, batch 11

The two queued references from page 33 of the collector address have complete
transaction tables. Both are confirmed in [block 974,163](https://bitcoin.prod.gke.papers.tech/block/974163).
The transaction views agree with the linked block page on height and hash.
Each payment has one output to the collector named in the
[BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).

| Payment | Input rows | Distinct addresses | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`496cd168bda5`](https://bitcoin.prod.gke.papers.tech/tx/496cd168bda5bd189b1dadcd3d9502ac63caf91bfcea1cf8847fd545cd18e7ca) | 9 | 9 | 333,727 | 329,727 | 4,000 |
| [`f31e3ec60050`](https://bitcoin.prod.gke.papers.tech/tx/f31e3ec60050ff702b5a82c23278e27699a15854569e35d88e062951ca354223) | 3 | 2 | 68,023 | 66,523 | 1,500 |
| **Total** | **12** | **11** | **401,750** | **396,250** | **5,500** |

Each set of inputs reconciles to the displayed total and to collector output
plus fees. The [registry](source_registry.json.gz) adds 11 distinct input-address
fingerprints across two observed co-input groups. One address recurs within the
second payment. There are zero exact address matches between the two groups
or with earlier observations. Exact address and reference-TXID comparisons
with the pinned Coldcard and CryptoBilis selections found zero matches.
Links between groups, merchant identity and individual compromise remain
unverified.

The cumulative registry covers **2,462 distinct addresses across 22 documented
payments**. Twenty-one have reconciled input tables. The partial pilot retains
its 11 visible addresses. This batch adds zero complete individual histories.
Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part11.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `e9915f8b16a15a1c3cd74a4b446e501b14e1d2f60e67317f577eaf14e863b59d`.
The [protocol](protocol.json) pins the earlier registries, lists all documented
TXIDs and records two pending leads from the same collector page.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part11.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_11/protocol.json"
```
