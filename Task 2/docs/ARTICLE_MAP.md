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

| Article section | Existing material | Remaining work |
| --- | --- | --- |
| Introduction | Transaction exercise, financial case analysis and completed source-membership baseline | Frame the achieved target as retrospective membership; independent compromise/device targets remain unresolved |
| Related work | Initial source-selection and evidence reviews | A structured review of primary research with suitable citations |
| Hardware wallet | Distinction between hardware signing, cold storage and attribution | Evidence-backed observable hypotheses |
| Bitcoin transactions | Part 2 and the write-up define all fourteen address predictors and units | Keep reference/future outcomes outside predictors and separate address from transaction features |
| GNN and alternatives | Completed prespecified shallow source tree; historical transaction baselines | Reconcile the introduction's proposed GNN with the completed tabular baseline; no GNN result is claimed |
| Initial dataset / Our Work | `source_methods.tex`: 500 cases, 1,000 fixed comparisons, 1,378 vectors, acquisition, cutoffs, groups and training-only preparation | Additional independent incidents and verified device/compromise labels remain future work |
| Results | `source_results.tex`: fixed test membership F1 0.989796, comparisons, rules, errors and coverage limits; historical Parts 1/3/4 remain distinct | Cross-incident transfer and prospective validation are not established |
| Conclusions | Write-up bounds the supported result to covered single-incident membership | Broader theft/device claims require separate evidence and evaluation |

A GCN is a type of graph neural network; SHAP explains predictions rather than
replacing a classifier. The introduction proposes GNN training; the main outline
questions its suitability and requests alternatives. This tension requires
methodological justification, not an assumed completed model. CryptoBilis is the
second incident; exact compromised-source identifiers and device mappings remain
to substantiate. The Teams source-address objective is now explicit even though
its operational label definition still needs care.
