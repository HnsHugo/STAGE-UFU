# BTCPay Server source intake, batch 3

Two previously undocumented confirmed payments fall in blocks 974,152 through
974,216. Each public explorer table displays one output to the collector
published by BTCPay. The linked block headers match the transaction pages'
heights and block hashes. Every displayed input was captured and its value
reconciled against the listed input total, collector output and fee.
[Verified payment at 974,153](https://bitcoin.prod.gke.papers.tech/tx/1c4671ab2f4cfee8622291b3cf9357334c6da94c11436d52b94b586676abc45c) ·
[Verified payment at 974,154](https://bitcoin.prod.gke.papers.tech/tx/7840f3b186d7ae303565d2a423baab3e10ad916bd14389d9af95550990f80f10)

| Block | Inputs | Input total (sat) | Collector output (sat) | Fee (sat) |
| ---: | ---: | ---: | ---: | ---: |
| 974,153 | 1 | 12,598 | 12,476 | 122 |
| 974,154 | 7 | 430,569 | 429,569 | 1,000 |
| **Total** | **8** | **443,167** | **442,045** | **1,122** |

[The registry](source_registry.json.gz) records eight distinct input-address
hashes, all new. Exact checks found zero matches between the two groups or
against the prior BTCPay observations. The pinned Coldcard and CryptoBilis
selections (1,500 and 366 rows) also have zero exact input-address or
reference-TXID matches with this batch. Each transaction defines one observed
co-input group. Intergroup links, merchant identity and individual compromise
remain unverified.

The cumulative registry records **1,388 distinct addresses across seven
documented payments**. Six have reconciled displayed input tables. The
[partial pilot](../btcpay_hot_wallet_pilot_20261119/README.md) preserves its
11 individually visible addresses. This batch adds zero complete individual
histories. Any future reference history uses blocks strictly below its
reference height.

## Checkpoint and replay

The private evidence archive `BTCPay-source-evidence-20261119-part3.json.gz` was retrieved after
saving and matched byte for byte. Its SHA-256 is
`4919859ad0ab587defe00507641ab828a01d90231412095af3e9f0f273cb3485`.
[The protocol](protocol.json) lists all seven acquired reference TXIDs, pins the
prior registries and preserves two leads from the collector page. Screen each
lead by its own confirmed height and complete displayed table. This pass used
public archives because the published Coldcard lease remains marked running.

```bash
base="Task 2/research/external_cases"
python3 "$base/btcpay_source_intake_20261119_02/replay.py" \
  /path/to/BTCPay-source-evidence-20261119-part3.json.gz \
  --protocol "$base/btcpay_source_intake_20261119_03/protocol.json"
```
