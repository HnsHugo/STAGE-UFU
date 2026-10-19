# BTCPay evidence and documented comparison pilot — 14 October 2026

## Address-level evidence

[BTCPay's official incident response](https://blog.btcpayserver.org/btcpay-server-security-incident-response-and-next-steps/) confirms stolen funds through compromised LND credentials. It does not identify either collector, so it corroborates the incident mechanism rather than exact-address attribution.

[An operator's first-person account](https://cafe.tollbooth-dpyc.com/blogs/our-value/anatomy-of-a-lightning-theft-no-balances-lost) identifies collector A (19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH) and transaction 10f219c427635e50dc374af6aa601e6f412ac0dccc7c545932afba5f818808f0. Its four inputs total 578705 sats; one output pays A 576777 sats; the fee is 1928 sats. These facts reconcile exactly with our saved provider observations. The operator claims theft and publishes node-log excerpts; we have not authenticated private logs or reproduced the exploit. This strengthens A's evidence to direct operator testimony plus reconciled transaction facts, not a legal finding or independently verified attacker identity. The article discusses competing vulnerability explanations; use the official advisory for mechanism claims.

Collector B (17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF) remains [research-attributed](https://github.com/somaxbt/btcpay-lnd-drain-2026-08/tree/2f62ebd642966f14ec0d49e743e70a1b5a716e4f). No separate first-person testimony naming B was found in this search. The saved histories reproduce a 15258-sat dependency from output 1 of 7029f7ff0bdd859e075287d9b7fb61ba38ed63d7ba19dedae6c73047554998c0 (a transaction paying B) into 054f3a8e1bb6856017db024eb675091f458d9ecc82bfb45bcffa19013a631a80 (paying A). This links transactions; it does not alone prove common ownership of both destination keys. Keep both in one conservative case group. The report's August unspent status is dated: our October 13 provider counters show both collectors' received outputs spent. Current balance must not replace historical cutoff features.

Neither address receives an automatic verified-theft training label. Different evidence confidence is retained, while historical attribution availability remains unknown.

## Official donation comparison group

| Organization | Bitcoin address | Official source | Current confirmed provider TX count |
|---|---|---|---:|
| Internet Archive | 1Archive1n2C579dMsAu3iC6tWzuQJz8dN | https://archive.org/donate/cryptocurrency | 7029 |
| Electronic Frontier Foundation | 3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so | https://www.eff.org/pages/other-ways-give-and-donor-support | 191 |
| Free Software Foundation | 1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN | https://www.fsf.org/about/ways-to-donate | 2593 |

All three exact addresses appear in fetched official HTML and are absent from both full Real-CATS files. Source-page and provider-response hashes are recorded with observation time. The three organizations are separate comparison groups; no ownership expansion is inferred. Selection precedes model scoring.

This establishes documented donation purpose, not legitimacy of every incoming fund or absence of compromise. These remain comparison candidates under a disclosed purpose-based policy, not certified benign labels. Three public reused donation addresses form a convenience stress-test group and differ from ordinary exchange recipients in the benchmark. Current page publication does not establish the historical date an address was first attributed. Tor's official cryptocurrency page was also examined, but its address was not exposed in the retrieved text; it was not added based on a third-party list.

Only provider counters were fetched for the controls. Full histories and equivalent model features are not yet collected. Archive and FSF require hundreds of history pages, so a small-page collector would be incomplete. EFF is the practical first full-history collection candidate (about eight pages); expand the organization sample and fix the observation/label policy before performance claims. No model fitting, score-based filtering, or final-test predictions occurred.

## Reproduction and validation

```bash
python review_external_evidence.py pilot_histories_20261013 /path/to/Real-CATS new_evidence_review.json
python -m unittest discover -p 'test*.py'
```

The script requires a new output path, records failed fetches, checks official-page address presence, audits raw-file address overlap, and asserts the operator transaction's exact structure and amounts. Six existing theft-case tests pass. Live counters/pages can change; saved histories and their hashes anchor the transaction reconciliation. Provider consistency does not constitute cryptographic inclusion proof. The original candidate registries are retained unchanged; donation_comparison_selection_20261014.json is a separate evidence-preserving selection.
