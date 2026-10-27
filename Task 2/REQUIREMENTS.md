# Requirements and evidence of completion

Updated on 27 October 2026 with the original Teams screenshots, meeting notes
and Overleaf files now supplied by Hugo. Read [ALIGNMENT.md](ALIGNMENT.md) for
the source-by-source reconciliation and current source-address priority.

The primary course source reviewed earlier is `aula4.pdf`, Ivan Sendin,
FACOM/UFU, dated 24 September 2026, 99 pages, supplied by Hugo. Pages 97 and 99
define the classroom exercise. It was not reread in this alignment session.
The original support is retained separately; it is not republished here.

The supplied Teams Coldcard post explicitly prioritizes transaction training and
validation on the supplied blocks, **then a dataset of robbed source addresses
and a model to detect those addresses**, expected to relate to hardware wallets.
Its post date is cropped and must not be inferred from a reply. No minimum
performance, final architecture or deadline is established by the supplied
instructions. Assistant proposals are not professor requirements.

## Original course requirements

| Requirement and source | Evidence | Status and limitation |
| --- | --- | --- |
| P.97: retrieve transactions paying the course address | 504 payments in selected blocks; complete saved address history has 507 transactions, 506 incoming | Completed within recorded coverage; two incoming transactions are outside the block corpus |
| P.97: size, weight, fee, value statistics, input/output counts | [Ten course features](research/coldcard/COURSE_EXERCISE.md) | Completed; `v` is interpreted as output values because the slide does not explicitly define it |
| P.97: 100 case transactions, 100 comparisons, decision tree | Deterministic 200-row cohort, 140/60 split, tree and predictions | Completed as an address-relation exercise; background remains unattributed |
| P.99: how much was stolen? | [Observed receipts, consolidation and fees](research/coldcard/case_flows_20261015/CASE_FLOWS.md) | Flows measured; no independently certified total stolen amount |
| P.99: how many source addresses? | Input-address counts and missing-data coverage | Completed as observed address counts, not victim counts |
| P.99: for how long? | Reception period, parent windows, interval to consolidation | Completed; provider/block timestamps distinguished from actual attack timing |
| P.99: how were funds spent? | Address spending, five consolidations, dated output observations | Completed at the observed first level; unspent status belongs to the collection date |
| P.99: is the classifier good? | Classroom, random, chronological, grouped and baseline experiments | Completed analysis; clear failures and limitations retained |
| P.99: find other destinations and check their quality | 8,158 alerts from 492,135 unused transactions, 20 review leads | Search executed; no newly confirmed theft destination |
| P.99: cold-address dataset and classifier | [Storage pilot and eligibility check](supplementary/wallet_storage/STORAGE_READINESS.md) | Partial: insufficient independent entities and time-valid labels; no September hot/cold training |
| Explicit Teams follow-up: robbed source-address dataset and model | Source-input counts, recovered funding parents and label protocol | Partial: no completed validated compromised-source/hardware-address model; Elliptic++, Real-CATS and recipient rankings do not complete this requirement |

## Additional explicit Teams instructions

- The 24 September fee discussion requests a literature review of network-relative
  fees, CPFP and RBF, and whether they are used before training a classifier.
  An accuracy benefit from filtering is a hypothesis to investigate, not a
  demonstrated result or a blanket filtering rule.
- The 9 September work plan assigns Hugo evaluation of GNN/GCN/SHAP and their
  scope for anomaly detection. Rayene's separate darkweb brief is not
  automatically Hugo's deliverable. Shared background includes H1/change
  heuristics and temporal, value and network features.

## Later article and meeting direction

The shared Overleaf outline requests related work, hardware-wallet background,
useful transaction information, an initial-dataset description,
financial/topological/H1 results, model explanations and application to other
blockchain periods. The introduction proposes a GNN but the main outline asks
whether GNN is the right/only solution and requests alternatives. Model choice
needs justification; the drafts do not establish a final architecture. See the
[article map](docs/ARTICLE_MAP.md).

Hugo's meeting notes mention tracking addresses, finding hardware wallets,
recent hacks, Ledger and combining another case with Coldcard. The original
Overleaf files were supplied on 27 October and name CryptoBilis. Exact source
identifiers/device mappings and Ivan's promised code remain unresolved. The notes
also mention a final paper/tool/results, GitHub and an INSA presentation. Five
versus six cases and the shorthand `bmppl`/`M` remain ambiguous; do not invent
their meaning. [Part 5](part_5_cross_case/README.md) records the extension policy.

## Scientific requirements that remain in force

- Address, entity, incident, transaction and temporal independence are different checks.
- Unknown background is not a legitimate class. Victim addresses must not become attacker labels.
- Hardware signing, cold storage, service attribution and illicit activity remain separate properties.
- Provider-counter reconciliation is not cryptographic blockchain inclusion proof.
- The frozen external 19-feature forest and strict threshold 0.15 must not be tuned to external examples.
- New experiments need separate outputs, explicit provenance and justified splits.

WalletExplorer and CPFP occur in the meeting notes; the additional Teams evidence
establishes the fee/CPFP/RBF literature question explicitly. Hardware background
and graph-method exploration are requested work, not completed deliverables.
Neither hardware attribution from transaction shape nor a successful GNN result
can be assumed in advance.

For the current reading order, use [Parts 1–5](README.md). For completed, partial and blocked work, use [Project status](PROJECT_STATUS.md).
