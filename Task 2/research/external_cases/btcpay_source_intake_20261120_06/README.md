# BTCPay Server source intake, batch 6

Two indexed public transaction tables on Trezor Bitcoin Explorer provided
complete evidence. Each payment has a single output to the collector named in
the [BTCPay advisory](https://blog.btcpayserver.org/btcpay-server-security-incident-2-4-1-and-earlier/).
Each transaction's block height and hash matched its linked block page.

| Payment | Block | Input rows | Input total (sat) | Collector output (sat) | Fee (sat) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [`bc995303ba75`](https://bitcoin.prod.gke.papers.tech/tx/bc995303ba75e5a2bed09a172357c00c732134e0516ec25f600e730695d28c15) | 974,175 | 9 | 3,580,519 | 3,578,521 | 1,998 |
| [`6b2a8b718b28`](https://bitcoin.prod.gke.papers.tech/tx/6b2a8b718b28a2b205e975385c7908b93e3416808c357e8d9fae933133e9e0b4) | 974,196 | 6 | 355,969 | 354,589 | 1,380 |

Both displayed input tables reconcile to the listed totals and to the
collector output plus fees. Each payment defines one observed co-input group.
The [registry](source_registry.json.gz) adds 15 distinct input-address hashes.
Exact address and reference-TXID checks against the pinned Coldcard and
CryptoBilis selections found zero matches. Merchant identity, compromise and
links between groups remain unverified.

The cumulative registry covers **1,974 distinct addresses across 12 documented
payments**. Eleven have reconciled input tables. The partial pilot retains
its 11 visible addresses. This batch adds zero complete individual histories.
Future histories use blocks strictly below the reference height.

## Checkpoint and replay

The private archive `BTCPay-source-evidence-20261120-part6.json.gz` was reopened and matched byte for byte.
Its SHA-256 is `bc8f444a4b30ab679d6c7417eb72a1890a9de1f6f0bf2d8a5c5ed7b0385f0ea9`.
The [protocol](protocol.json) pins the prior registries and lists all documented
TXIDs. The two previously recorded candidates from the collector page remain
pending because their transaction pages were unavailable during screening.

The published Coldcard lease remains marked running. This batch used public
archive views and zero direct collection API requests.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261120-part6.json.gz \
  --protocol "$base/btcpay_source_intake_20261120_06/protocol.json"
```
