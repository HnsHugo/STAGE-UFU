# Which model are we talking about?

The repository contains different scientific questions. A better or worse score in one does not revise another experiment's result.

| Experiment | One row represents | Target being learned | Main limit |
| --- | --- | --- | --- |
| Classroom Coldcard tree | A transaction, ten course features | Payment to the course address versus selected unattributed comparison | The small test shares the same address/case |
| Extended grouped Coldcard tree | A transaction, sixteen features | Direct-parent candidate versus unattributed background | Four related groups from one case; unknown background relationships |
| Elliptic++ benchmark | A source-dataset address profile | Original illicit/licit source categories | Source labels, anonymous IDs and historical profile limitations |
| Real-CATS historical benchmark | An address profile, 22 numerical features | Hack/Theft source categories versus the source comparison category | Address-disjoint does not establish incident/entity independence |
| Frozen external Real-CATS model | An address profile, 19 reconciled base features plus missingness indicators | A source-category score applied to external examples | Fixed model/threshold; external examples are a descriptive pilot, not calibrated theft probabilities |
| Hot/cold pilot | An address and a time window | No trained storage target currently validated | Missing temporal label validity and insufficient independent entities |

The 22-feature benchmark's selected threshold is 0.30. The external 19-feature model uses strict score >0.15 and remains frozen. These are separate models. Neither is a confirmed hardware-wallet identifier.

The exported all-data Coldcard tree is also different from each fold-specific evaluation tree: its training-data replay is not a separate generalization score.

## What does a successful result mean?

- A correct classroom answer demonstrates the exercise on that sample.
- A grouped score measures transfer to the candidate group left out of training, within the recorded case.
- A source-category benchmark measures agreement with that source's labels under its split.
- A new-incident or hardware-wallet claim requires evidence and evaluation designed for that claim.

Use [Parts 1–5](../README.md) for the main story and the [glossary](GLOSSARY.md) for metric definitions.
