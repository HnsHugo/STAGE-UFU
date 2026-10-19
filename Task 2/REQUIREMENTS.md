# Requirements and evidence of completion

Updated for navigation on 19 October 2026. The primary course source reviewed earlier is `aula4.pdf`, Ivan Sendin, FACOM/UFU, dated 24 September 2026, 99 pages, supplied by Hugo. Pages 97 and 99 define the Coldcard exercise. The original support is retained separately; it is not republished here.

The reported 8 October instructions prioritized training/validation on the supplied blocks and then an address dataset related to thefts. No separate signed specification establishing minimum performance, architecture or deadline was found. Assistant proposals are not professor requirements.

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
| Reported follow-up: theft-related address model | Elliptic++, Real-CATS and descriptive external pilot | Supplementary benchmarks completed; independent theft detection not demonstrated |

## Later article and meeting direction

The shared Overleaf outline requests related work, hardware-wallet background, useful transaction information, an initial-dataset description, financial/topological results, model explanations and application to other blockchain periods. It explicitly leaves GNN and alternatives open. See the [article map](docs/ARTICLE_MAP.md).

Hugo's 19 October meeting notes mention tracking addresses, finding hardware wallets, recent hacks, Ledger and combining another case with Coldcard. These are provisional notes, not an exact incident specification. The relevant Overleaf files/references and Ivan's promised code are not supplied here. [Part 5](part_5_cross_case/README.md) records what must be established before extending labels.

## Scientific requirements that remain in force

- Address, entity, incident, transaction and temporal independence are different checks.
- Unknown background is not a legitimate class. Victim addresses must not become attacker labels.
- Hardware signing, cold storage, service attribution and illicit activity remain separate properties.
- Provider-counter reconciliation is not cryptographic blockchain inclusion proof.
- The frozen external 19-feature forest and strict threshold 0.15 must not be tuned to external examples.
- New experiments need separate outputs, explicit provenance and justified splits.

CPFP and WalletExplorer were part of the earlier provisional pilot; the course pages reviewed do not establish CPFP as a mandatory result. GNN/GCN, SHAP and a broader tool remain research options, not completed deliverables or automatic prerequisites.

For the current reading order, use [Parts 1–5](README.md). For completed, partial and blocked work, use [Project status](PROJECT_STATUS.md).
