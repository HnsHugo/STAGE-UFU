# Professor-supplied incident references — 19 October 2026

## What is now established for the project

Hugo supplied the Coldcard/Overleaf references and an explicit CryptoBilis
reference in the conversation. **CryptoBilis is the intended second incident.**
This resolves case selection, not the exact prediction target, address-to-device
ground truth, incident membership of every transaction, or the missing professor
code. The two Bitcoin recipients previously collected remain source-attributed
candidates; their address-specific evidence still comes from Bitquery.

The earlier registries and numerical reports retain their original wording,
identifiers, hashes and provisional flags. Those flags describe the evidence
available when they were created. This review adds the case-selection update
without silently relabeling the historical data.

## Source map

| Reference | Use in the research | Review status |
| --- | --- | --- |
| [CoinDesk: Coldcard sweep](https://www.coindesk.com/pt-br/tech/2026/07/31/major-bitcoin-wallet-flaw-drains-594-btc-in-25-minute-sweep) | Incident reporting and chronology | Read; not a complete participant-address ground truth |
| [Block Engineering](https://engineering.block.xyz/blog/predictable-rng-fallback-and-32-bit-reseed-in-coldcard-firmware) | Primary technical analysis of RNG integration | Read; preserve its assumptions and empirical-testing limits |
| [KuCoin](https://www.kucoin.com/news/flash/coldcard-wallet-entropy-flaw-leads-to-38m-bitcoin-theft) | Secondary incident summary | Read through web reader; direct HTTP returned a very short non-article response |
| [Bitcoin Magazine](https://bitcoinmagazine.com/news/coldcard-security-risk-immediate-action-required) | User-supplied lead | HTTP 403; content not claimed as verified |
| [Lookonchain feed](https://www.lookonchain.com/feeds/66268) | Dated early report, not an independent address list | Read; technical scope should not be carried forward as timeless |
| [CoinDesk: CryptoBilis](https://www.coindesk.com/tech/2026/10/12/ledger-claims-cryptobilis-cases-are-limited-as-up-to-usd93m-is-traced-usd10m-frozen) | Confirms the incident intended by the supplied reference | Read; media estimates are not a manufacturer-confirmed final total |
| [The Hacker News](https://thehackernews.com/2026/10/ledger-finds-unauthorized-hardware.html) | Incident/mechanism context | Read; later updates are not facts available on initial publication day |
| [Exame](https://exame.com/future-of-money/golpista-perde-r-24-milhoes-apos-sofrer-ataque-hacker-na-sua-carteira-cripto/) | Reported participant example in the same CryptoBilis incident | Read; no exact three-address/TXID mapping established |
| [Coinkite advisory](https://blog.coinkite.com/coldcard-mk3-seed-generation-warning/) | Manufacturer context linked by Block | Read as an updated advisory, not its original July snapshot |

The [machine-readable review](professor_reference_review_20261019.json) retains
the eight supplied URLs, direct-fetch hashes/statuses and review decisions.
Hashes identify retrieved bytes; they do not authenticate claims. Full articles
are not republished. Linked Ledger and Chainalysis posts could not be inspected
directly through the web reader. References sharing those posts are not separate
independent confirmations.

## Mechanism and evidence boundaries

Block describes a deterministic fallback and a reseed limited to one 32-bit
word on newer models, conditional on fixed fallback state and call history.
It does not demonstrate an end-to-end exploit of every device. Coinkite's updated
advisory describes affected seed generation and says devices were not remotely
taken over. Its Mk2/Mk3 version boundary differs from Block's; record that
discrepancy rather than choosing a universal entropy number or firmware range.

Early Lookonchain reporting leaves the sweep-to-vulnerability link unresolved
and excludes newer models, whereas later manufacturer guidance includes them.
Source date/revision matters. A current technical advisory cannot establish the
hardware used by each address in the course graph.

For CryptoBilis, the inspected reports describe unauthorized device implants and
recovery-phrase exposure. This differs from the Coldcard RNG mechanism. The
common research hypothesis is how funds are collected after key compromise,
not a common firmware exploit or an on-chain signature identifying a brand.

## Exame is a participant example, not a third incident

Exame attributes to Chainalysis a participant moving funds to three
Ledger-associated addresses on 22 September, then losing over 60 BTC on
9 October through payments to one recipient. It places this inside CryptoBilis.
The participant is also alleged to have run a task scam. Exact identifiers remain
unresolved; no addresses are guessed from amounts, dates or article illustrations.

Keep four distinct fields in any future labels:

| Dimension | Meaning |
| --- | --- |
| Incident role | Source reportedly drained, collection, consolidation or later recipient |
| Earlier activity | Separate source assertion about funds/behavior before this incident |
| Hardware evidence | Device association supported externally or unknown |
| Availability | When each specific role/device assertion became available |

Someone alleged to have committed an earlier scam can still be the victim of a
later theft. That does not make the later collector use the victim's device or
make all earlier transactions part of the later incident. The participant
example must remain in the CryptoBilis split group, not become an independent
case or a certified negative/positive merely through its earlier activity.

## Concrete next work

1. Keep the existing Coldcard/CryptoBilis histories and temporal measurements.
2. Obtain exact source-supported identifiers for the three-address example;
   until then, retain it only as an unresolved source claim.
3. Define a collection-pattern target separately from hardware-device control.
4. Add documented active comparison recipients and retain case/entity groups.
5. Evaluate interpretable temporal/graph baselines before adding a GNN; hold the
   entire second case out if making a transfer claim. Freeze feature/label
   availability before any prospective evaluation.

No new training, score tuning, hardware attribution or participant re-identification
was performed in this reference-integration step.

Verification: the six offline suites pass with **159 tests**. Historical data,
model parameters and numerical results remain unchanged. The
[execution log](../../verification/professor_references_20261019.json) records the
actual checks. Unreadable references remain explicitly unresolved.
