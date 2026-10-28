# Task 2 alignment — 27 October 2026

## Purpose and current decision

This is the current scope reference, reconciled with the Teams screenshots,
meeting notes and original Overleaf files supplied by Hugo on 27 October.
It corrects earlier assistant priorities; it does not replace Ivan's instructions
or change any historical experiment, metric or label.

**The research priority concerns the source addresses whose funds were reportedly
stolen, starting with Coldcard. Collector detection and onward tracing support
that work but do not substitute for it.** The supplied Teams message establishes
two stages: train/validate a transaction model on the supplied blocks, then obtain
a dataset of the addresses that were robbed and train an address model. The
message expects a hardware-wallet relationship; it does not independently verify
the device behind each address.

## Evidence and precedence

Use explicit professor instructions first, then Hugo's current direction. Treat
meeting shorthand as supporting context, and assistant plans as proposals.
Where the article drafts conflict, preserve the uncertainty instead of inventing
a settled requirement. Private source files are retained outside this repository;
the following identifiers let Hugo locate the originals without republishing them.

| Source | What it establishes | Qualification |
| --- | --- | --- |
| Teams overview, 8 September, 13:02; screenshot `image(6).png` | Case analysis, ML classifier, cold-wallet dataset, financial analysis | Does not define verified address-to-device labels |
| Teams initial work plan, 9 September, 21:27; `image(7).png` | Hugo studies GNN/GCN/SHAP, defines their scope and application to anomaly detection; shared background includes temporal/value/network features and H1/change heuristics | The separate darkweb work assigned to Rayene is not automatically Hugo's deliverable |
| Teams Task 1, 10 September, 14:38; `image(8).png` | Shared data-acquisition background and resources | Background is not a requirement to use every listed platform |
| Teams fee discussion, 24 September, 14:57 and follow-up 18:44; `image(9).png` | Literature review of network-relative high/low fees, CPFP and RBF, specifically their use before classifier training | A filter improving accuracy is Ivan's hypothesis, not an established result or an instruction to discard all such transactions |
| Teams Coldcard post; `image(10).png` | First transaction training/validation on supplied blocks, then dataset and model of robbed source addresses, expected to relate to hardware wallets | Main post date is cropped; the visible 5 October reply date must not be assigned to it |
| Previously documented `aula4.pdf`, 24 September, pp.97/99 | Ten features, 100+100 decision-tree exercise, financial questions and destination search | Source was reviewed earlier; not reread in this alignment session |
| Original Overleaf `main (1).tex`, `intro.tex`, `hw.tex`, `related.tex`, `annotation.tex`, `mybib.bib` | Article, hardware background, related work, dataset, financial/topological/H1 results, explanation and other-period application; Coldcard and CryptoBilis references | Introduction proposes a GNN, while the main outline explicitly questions whether it is the right/only solution; model choice requires justification |
| Hugo's meeting notes | Source tracking, hardware association, CPFP, WalletExplorer, decision tree, Chainabuse, Ledger/CryptoBilis extension, PyTorch, papers, final paper/GitHub/INSA presentation | `bmppl` and `M` are unresolved shorthand; five versus six cases is not a settled incident list |
| Hugo's explicit scope correction, conversation | Compromised source addresses first; destinations afterward; keep one coherent experiment | Governs the next unit rather than expanding collector ranking again |

## Requirement-to-work map

Status means the evidence available now, not an invented completion percentage.

| Requirement | Verified existing work | Remaining aligned work |
| --- | --- | --- |
| Supplied-block transaction exercise | 98 blocks, 493,571 unique transactions; ten features; 100+100 sample; saved tree and 60/60 sample-test decisions | Preserve this completed exercise and explain its narrow target |
| Financial case reconstruction and address tracking | 504 payments in the block corpus; complete saved collector history has 506 incoming and one outgoing transaction; flows, fees, timestamps and parent coverage documented | Separate the suspected incident window from later activity; develop source-side reconstruction without calling all inputs victims |
| Dataset of robbed source addresses | [Graph-evidence registry executed](research/coldcard/source_registry_20261027/README.md): 500 candidate-day addresses / 1,324 input records; five additional later addresses kept separate; exact outpoints, roles, dates and confidence retained | Compromise/device labels remain unverified; build cutoff-safe address features and assess supervised-label eligibility |
| Address classifier for the requested target | Transaction baselines and supplementary address-category benchmarks exist | No validated compromised-source/hardware-address classifier has been established; define the address target and eligible labels before training |
| Fees, CPFP and RBF literature/preprocessing | Fee and fee-rate measurements and historical exploratory material exist | A focused literature synthesis answering Ivan's three questions and a justified, separately tested preprocessing experiment are not evidenced as complete in the reviewed main-path material |
| Financial, topological and H1 analysis of hardware-related sources | Financial flows and transaction/group analyses exist | A source-address graph, explicit H1 assumptions, CoinJoin/change limitations and interpretable topology remain to consolidate |
| Additional hardware-related case | CryptoBilis is named in the supplied annotations; recipient observations and references exist | Recover exact source-supported compromised-address identifiers and compatible labels; combine only after preserving incident/entity groups |
| Model interpretation and transfer | Readable fee-dominated tree, grouped failures, simple baselines and a frozen replay on CryptoBilis receipts exist | Explain source-address decisions and evaluate the actual address target on appropriate groups/periods; existing recipient coverage is not this validation |
| GNN/GCN, alternatives and related work | Relevant references were located/reviewed at varying access levels; no completed Task 2 GNN result | Compare papers by task, graph, features, labels, split and limitations; justify whether a graph model adds value after the dataset is defined |
| Final paper, code/results and presentation | Repository, reproducibility tools and article outline exist | A finished technical report/paper and INSA presentation are not demonstrated by the supplied outline |

The 505 and 341 source-address counts refer to different populations and must not
be added. The 341 parents fund the collector before consolidation; the
consolidation's own repeated collector inputs are not the original victims.

## What the results actually establish

- [Classroom exercise](research/coldcard/COURSE_EXERCISE.md): 30/30 sampled case
  payments and 30/30 sampled comparisons classified correctly, proxy F1 1.00.
  The class decisions reduce to total fee strictly above 2,815 satoshis. Training
  and sample test share the same case/address and blocks; this is not hardware
  identification or an independent theft benchmark.
- [Grouped experiment](research/coldcard/GROUPED_EXPERIMENT.md): 874/1,070 direct
  parent candidates recovered and 1,072 unattributed-background alerts, pooled
  proxy F1 about 0.580. This is a different target/protocol, not proof that the
  classroom model deteriorated. Unknown background is not certified legitimate.
- [Historical recipient experiment](CENTRAL_EXPERIMENT.md): the frozen classroom
  rule alerts 122/122 payments to the two supplied CryptoBilis recipients in the
  saved windows. This is retrospective receipt coverage; it neither identifies
  122 compromised keys nor validates a hardware/source-address classifier.
- Real-CATS, Elliptic++, FBI, donation-address and hot/cold investigations remain
  supplementary. Their different labels and splits do not answer the missing
  source-address requirement. Their valid findings and failures are preserved.

Thus high early F1 and weaker later results are not directly comparable:
the unit, label definition, background, prevalence and split changed. The main
gap is the requested address-level dataset/model, not merely a lower metric.

## Executed unit: Coldcard source-address evidence registry

The following specification was executed after the alignment session; see the
[registry report](research/coldcard/source_registry_20261027/README.md).
The complete pinned 19 October history was reused without API collection or
model fitting. The graph registry is complete for that history, while verified
compromise/device labels remain absent. The steps below describe its acceptance
criteria rather than an instruction to repeat the build.

1. Fix a source-supported incident interval and distinguish it from the full
   collector activity period. Retain outside-window observations separately.
2. Reconstruct the direction source input -> suspected sweep -> known collector
   -> consolidation. Define one address-level record with links to its exact
   funding/sweep TXID and previous outpoints; retain values in integer satoshis.
3. Apply the existing [label protocol](research/coldcard/LABEL_PROTOCOL.md): keep
   observed graph relationship, reported compromise, independently supported role
   and hardware-device evidence separate. Repeated inputs, address reuse, missing
   data and possible collaborative transactions need explicit treatment.
4. Record evidence URL, publication/review dates, event/observation period,
   label-availability date, incident/entity group, role confidence and hardware
   confidence. Missing evidence stays unknown. Do not publish unnecessary
   re-identification material or bulk unknown-address accusations.
5. Deliver the versioned registry, coverage/missingness summary, focused tests and
   reproduction command. Use a new dated output; preserve all historical bytes.

Acceptance: every included source observation can be traced back to saved
transaction evidence; source and collector roles cannot be interchanged; coverage
is reconciled; no on-chain relationship automatically becomes a victim or device
label. If labels remain insufficient, deliver the candidate registry and exact
eligibility gap rather than switching silently to another ML task.

The [pre-payment pilot](research/coldcard/prepayment_pilot_20261027/README.md)
is now executed: eight complete source histories, fourteen prior-block features,
no earlier spending in this sample, and published offline prefix evidence.
The [multi-input extension](research/coldcard/multiinput_pilot_20261028/README.md)
is also executed: four complete histories among 81 eligible sources, unchanged
feature extraction and no prior spending. Twelve distinct source histories are
now available, but no individual compromise/device labels are established.
The [resumable cohort pipeline](research/coldcard/source_cohort_20261028/README.md)
is executed through batch 1: 30 complete histories, two timeouts and 468 pending
sources. Its checkpoint can restore feature-complete records without raw files.
**Next unit:** one further fixed batch of at most twenty pending sources, verify
and publish `batch_0002`. Keep feature definitions and the strict prior-block
cutoff fixed. Decide
whether the experiment is retrospective reconstruction or pre-event detection;
these use different permissible features. Do not encode a known destination or
later label as a shortcut to claim general hardware identification. A clearly
named relation/proxy baseline can be useful, but must not be reported as the
requested ground-truth detector. With adequate labels, start with interpretable
baselines and prespecified grouped/temporal evaluation, then test CryptoBilis
transfer. That case has already been explored; it is not an untouched final test.

## Boundaries that prevent another scope drift

- No further collector-ranking, donation-control, Real-CATS or hot/cold extension
  as the default next task. Use existing artifacts when they directly support the
  source-address objective or fix a concrete defect.
- Review the incident references, but do not turn six brands in a press roundup
  into six independent compromised-key datasets. Personal/order-data leaks are
  not automatically private-key thefts. Exame's participant is inside CryptoBilis,
  not a third independent case; exact identifiers remain unresolved.
- Chainabuse is supporting report evidence, not a ready-made victim/hardware
  dataset. A missing report does not certify legitimacy. WalletExplorer service
  attribution does not prove device, storage mode or ownership at every date.
- H1/common-input grouping is a heuristic, not identity proof. RBF signaling is
  not proof of replacement; a confirmed parent/child link alone does not prove
  the unconfirmed CPFP context. Study the available evidence before filtering.
- Explore GNN/GCN/SHAP as requested, without treating SHAP as a classifier or
  PyTorch as a required architecture. Hardware association, theft role and cold
  storage are different targets.
- Keep the external 19-feature model frozen: 100 trees, maximum depth 20,
  minimum 20 samples per leaf, `max_features="sqrt"`, equal class weights,
  seed 42, training-fitted imputation with missing indicators, alert strictly
  above 0.15. Do not tune it on external examples.
- Ivan's promised code is useful for comparison when supplied; its absence does
  not block source reconstruction. A positive model result cannot be promised.

## Session rule and handoff

Before an experiment, state the requirement served, observation unit, target,
evidence, cutoff/split and expected artifact. Choose one short verifiable unit;
test it, document actual results and save a commit on `task-2-wallet-analysis`.
Do not ask routine permission or start unrelated work after a blocker.

At handoff, report: what was executed, results and limits, checks, published
commit, and one next action. Separate completed work from prepared protocols.
New professor/user instructions can revise this document; assistant suggestions
must not silently replace it.
