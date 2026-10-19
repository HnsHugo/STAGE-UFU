# Binance recipient attribution from a research case study

## Evidence chain

Incident source: https://www.binance.com/en/support/announcement/detail/360028031711
Research source: https://yong-wang.org/publication/23-SMC-Intention-Discovery.pdf
Title: Toward Intention Discovery for Early Malice Detection in Cryptocurrency, by Ling Cheng, Feida Zhu, Yong Wang, Ruicheng Liang and Huiwen Liu.

Section VII.F, printed page 6, attributes an attacker address abbreviated as bc1q***v3wm and describes its initial receipt of 567.997 BTC through 71 inputs. In the saved incident transaction, exactly one output matches the prefix, suffix and amount: output 6, address `bc1q8m9h3atn4cqeqhu3ekswdqxchp3g7d4v3qv3wm`, value 56,799,700,000 satoshis.

The complete address is inferred by this unique match, not fully printed in the paper. The role is recorded as research_attributed_attacker_recipient, with the evidence level research_attribution_resolved_by_unique_prefix_suffix_amount_match. It is not independently verified ownership or identity. The paper's introduction refers to 2017, while its case section states 7 May 2019; the discrepancy is retained. Source publication time and historical label availability remain unknown.

## On-chain check and snapshot

The complete confirmed address history was collected from Blockstream. It contains 3 distinct transactions: two receipts and a subsequent spend. Reconstructed received/spent amounts and counts match stable before/after provider counters, and pagination was exhausted. This is provider consistency, not cryptographic inclusion verification. Files and evidence references have SHA-256 checksums.

binance_asof_first9hours.json uses a cutoff nine hours after the first observed confirmed receipt. Features use only transactions earlier than that cutoff and a seven-day lookback. The later receipt and spend do not enter this snapshot. The resulting single receipt is 56,799,700,000 satoshis; no spending is observed by the cutoff. The label is retrospective and is not shown to have been available at that time.

## What changes in the corpus

One of 44 Binance output candidates now has a documented research attribution. The remaining 43 outputs retain unknown roles. This adds one address in a second incident group alongside the six FBI addresses; it does not create 44 labeled attacker addresses. Evidence strength and observation maturity differ from the FBI snapshot. No pooled supervised model or external performance score is produced.

DMM searches did not yield a usable complete-address attribution in the sources inspected in this pass. There are still no documented negative controls. More independent cases and a common observation-maturity policy are required.

## Reproduction

```bash
python collect_binance_research_seed.py ../coldcard/external_cases/binance_2019_transaction.json new_binance_collection
python -m unittest discover -p 'test_*.py' -v
```

The collector requires a unique prefix/suffix/amount match and checks history coverage before interpretation. Six theft-case tests pass, including rejection of ambiguous matches and identifier-only matches with the wrong amount.
