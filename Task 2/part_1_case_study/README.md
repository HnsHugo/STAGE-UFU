# Part 1 — Understand the case and follow the funds

[Back to the main path](../README.md) · [Next: Part 2](../part_2_dataset/README.md)

## Goal

Explain the transactions associated with the course address before discussing machine learning. Describe observed flows, addresses, fees and times without equating every receipt with stolen funds.

## Read these results

1. [Case financial report](../research/coldcard/case_flows_20261015/CASE_FLOWS.md).
2. [Flow verification](../research/coldcard/case_flows_20261015/VERIFICATION.md).
3. [Recovered-parent coverage](../research/coldcard/PARENT_AUDIT.md).

The address has 507 saved confirmed transactions: 506 incoming and one spending transaction. Observed lifetime receipts are 594.47728031 BTC. The selected consolidation consumes 562.02666941 BTC from 341 recovered parent transactions. These are flow measurements, not a separately certified stolen total or victim count.

Five consolidation outputs were reported unspent in the saved 14 October observations. This is a dated provider observation, not their current status and not evidence of cold storage.

## Code and inputs

- [analyze_case_flows.py](../research/coldcard/analyze_case_flows.py): reconcile histories and produce the financial report.
- [audit_coldcard_parents.py](../research/coldcard/audit_coldcard_parents.py): identify the source-attributed transactions and recover parents from selected blocks.
- Raw block archive and complete target history: supplied separately; see [Data access](../DATA_ACCESS.md).

To reproduce with your own local copies and a new output directory:

```bash
python "Task 2/research/coldcard/analyze_case_flows.py" analyze "/path/to/blocos(1).tgz" /path/to/new_case_output \
  --parents /path/to/parents.json \
  --history /path/to/coldcard_target_history_20261014.json.gz \
  --outspends /path/to/coldcard_seed_outspends_20261014.json
```

## What to explain to Ivan

“I reconstructed what the saved transactions show, measured coverage and separated received funds, spending, fees and timing. I have not treated every address as a victim or inferred the signing device from transaction shape.”
