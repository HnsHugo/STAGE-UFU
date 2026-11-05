# How the current work maps to the Overleaf outline

The outline shared by Ivan is a proposed research article, not a completed paper.
The original main, introduction, hardware-background, related-work, annotation
and bibliography files were supplied on 27 October. Read
[ALIGNMENT.md](../ALIGNMENT.md) for their reconciliation with Teams and Hugo's
notes. The earlier [reference review](../research/external_cases/PROFESSOR_REFERENCES.md)
retains the evidence available at its own date.

**Integrated write-up, 2 November 2026:** The
[source-address study](../source_address_study/README.md) now provides the complete
English methods/results text, a five-page PDF and two LaTeX fragments for the
supplied `Our Work` / `Results` sections. The original article files were read
for layout; neither those originals nor a live Overleaf project was edited.
The [integration guide](../source_address_study/README.md#article-integration)
lists the small preamble addition and exact input locations. Data, model, scores,
groups, cutoffs and unknown labels remain unchanged.

**Frozen transfer supplement, 4 November 2026:** The
[Coldcard-to-CryptoBilis supplement](../source_transfer_study_20261104/README.md)
adds a checked four-page PDF, `transfer_methods.tex`, `transfer_results.tex` and
an importable Overleaf folder. Both new fragments compile together with the
earlier Coldcard fragments, without duplicate labels or layout warnings.
It preserves the external membership F1 0.629834, all 67 errors, the stronger
inactivity ranking (AP 0.854026 versus 0.688142), attrition and evidence limits.
These are exploratory proxy-transfer results for one inspected external incident;
entity independence and verified theft/device detection remain unestablished.
The original article, authors, bibliography and live Overleaf project are unchanged.

**Integrated review copy, 5 November 2026 UTC**

The review copy uses the supplied 27 October export and the four LaTeX
fragments pinned at commit 0d741135ffac72d1a19b5ec568c0d959acf63306.
It contains a ten-page PDF and an editable source ZIP with the six original
files archived together. A clean build of the extracted archive reproduces
the reviewed PDF text. The manuscript and source archive are held separately
for author review.

| Article section | Current review copy | Focus for author review |
| --- | --- | --- |
| Introduction | Retrospective membership question and frozen transfer to a second source-linkage proxy | Confirm the research question and provisional title |
| Related work | Elliptic transaction classification and public-chain link prediction | Review the scope of the literature discussion and the distinction between transaction and address units |
| Hardware wallet and Bitcoin transactions | Signing context, referenced outputs, address-level features and separate coverage measures | Verify the distinction between ledger evidence and device attribution |
| Our Work | Observed collector-flow context, the fixed Coldcard cohort and fourteen predictors, and the CryptoBilis selection and quarantine protocol | Review the source definitions, the strict block cutoff and completeness criteria |
| Results | Internal membership F1 0.989796 and external proxy F1 0.629834, with fixed comparator rankings and error counts | Check the scope of each target and evaluated population |
| Conclusions | Limited frozen-tree transfer and stronger inactivity ranking on the selected external proxy | Check the limits on interpretation and the evidence needed for prospective evaluation |

The original outline's GNN question now sits in the methodological context.
The completed analysis uses the prespecified shallow decision tree and fixed
rankings. A graph-learning extension would require a defined prediction unit,
time-available inputs and an independent evaluation protocol.
