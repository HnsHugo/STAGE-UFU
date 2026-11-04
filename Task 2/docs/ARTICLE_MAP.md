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

| Article section | Existing material | Remaining work |
| --- | --- | --- |
| Introduction | Transaction exercise, financial case analysis and completed source-membership baseline | Frame the achieved target as retrospective membership; independent compromise/device targets remain unresolved |
| Related work | Initial source-selection and evidence reviews | A structured review of primary research with suitable citations |
| Hardware wallet | Distinction between hardware signing, cold storage and attribution | Evidence-backed observable hypotheses |
| Bitcoin transactions | Part 2 and the write-up define all fourteen address predictors and units | Keep reference/future outcomes outside predictors and separate address from transaction features |
| GNN and alternatives | Completed prespecified shallow source tree; historical transaction baselines | Reconcile the introduction's proposed GNN with the completed tabular baseline; no GNN result is claimed |
| Initial dataset / Our Work | `source_methods.tex` preserves the Coldcard dataset; `transfer_methods.tex` adds 122 CryptoBilis case sources, 244 fixed comparisons, 329 vectors and the 275-source quarantine-qualified evaluation | Integrate both fragments into the current editable article; independent entities and verified labels remain future evidence needs |
| Results | `source_results.tex` preserves internal F1 0.989796; `transfer_results.tex` adds external proxy F1 0.629834, all fixed comparators, 67 errors and attrition | Reconcile the different target/population meanings; prospective and independent-incident validation remain unestablished |
| Conclusions | The supplement reports limited frozen-tree transport and stronger inactivity ranking on the selected external proxy | Align the article's claims with these limits; broader theft/device claims need separate evidence and evaluation |

A GCN is a type of graph neural network; SHAP explains predictions rather than
replacing a classifier. The introduction proposes GNN training; the main outline
questions its suitability and requests alternatives. This tension requires
methodological justification, not an assumed completed model. CryptoBilis is the
second incident; exact compromised-source identifiers and device mappings remain
to substantiate. The Teams source-address objective is now explicit even though
its operational label definition still needs care.
