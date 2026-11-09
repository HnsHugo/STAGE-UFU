# Research direction after Ivan's feedback, reported 9 November 2026

This record translates Hugo's main explanation of Ivan's feedback and Hugo's
preferred execution order. The main explanation takes precedence over the
shorthand notes. It is a user-reported supervision update, not a verbatim
statement from Ivan. It supersedes manuscript review as the next research
priority; the manuscripts and completed results remain preserved.

## Scope and current evidence

Ivan emphasized obtaining the missing observations, experimenting with transfer
and pooled incident datasets, prioritizing deep learning and graph
representations, and investigating a possible change in exchange-directed
activity after the Coldcard incident. Hugo requests the order below: finish a
bounded set of experiments on the existing tables, construct graph versions of
the same cohorts with richer observed information, repeat the experiments with
deep learning, then study the possible behavioral break. Coverage work starts
immediately and must not be hidden by complete-case metrics.

The [offline coverage inventory](../research/source_coverage_review_20261109/coverage_inventory.json)
recounts the exports pinned to `04aae8dd928241fc422fb9bf47e5fae3f1c20bd9`:

| Dataset | Selected | Available prior-prefix vectors | Bounded-incomplete prefixes |
| --- | ---: | ---: | ---: |
| Coldcard | 1,500 | 1,378 (500 case / 878 comparison) | 122 |
| CryptoBilis | 366 | 329 (122 case / 207 comparison) | 37 |
| Total | 1,866 | 1,707 | 159 |

The original fixed network continuations have no network/unattempted IDs left.
The 159 missing vectors are retained bounded outcomes requiring a new coverage
scope. All are comparisons. The original frozen CryptoBilis evaluation also
excluded 54 complete vectors for measured links to Coldcard; these are not
missing acquisitions. Its scored population remains 275.

Full-current-history status stays separate: Coldcard has 500 complete case
histories and 864 complete / 136 incomplete comparison histories. CryptoBilis
individual full-current histories were not collected by the prefix protocol.
Some valid feature fields, such as fees without prior spending, are naturally
undefined even when a prefix is complete.

The current target is retrospective incident-source membership. Verified
compromise, signing-device and seed-origin labels remain unknown. New graph or
deep-learning experiments can study this explicit proxy without upgrading it to
verified hardware-wallet identification. The same distinction applies to every
new incident and to the migration question.

## Immediate coverage work

1. Preserve all selected sources, old results, raw-response fingerprints,
   checkpoints and consumed markers. Reuse valid private caches if available.
2. Diagnose the 122 + 37 missing prefixes and estimate additional pages,
   storage and execution time. Old whole-history request estimates are historical
   and must not be presented as the cost of these exact 159 current gaps.
3. Specify a new resumable extension beyond the exhausted 16-page prefix scope.
   A streaming/memory-bounded executor and durable checkpoints may be needed for
   high-activity addresses. Do not restart the stopped collectors or enable the
   old automation. Keep the old `network_source_ids=[]` unchanged.
4. Before provider traffic, verify current published lease, held local locks,
   due time, Retry-After and original provider/route/TLS. Retain two workers,
   one global request start/second and 15-second timeout unless a new justified
   protocol explicitly changes a bound. Stop on the first 403/429 and keep the
   existing refusal/backoff rules; no provider/account/proxy/IP/TLS workaround.
5. Require exhausted validated prefixes before computing vectors. Preserve the
   original 14 definitions, strict reference-block cutoff and unknown labels.
   Publish a new composed view and rerun the relevant overlap/eligibility audit
   after coverage changes. Never impute an entire missing prefix or substitute
   easier addresses to reach 1,500/1,866 rows.

Coverage and descriptive/exploratory work on the current snapshot can advance
together. Any current-snapshot experiment must report attrition and be kept
separate from confirmation on an extended snapshot. Additional coverage alone
does not certify the device/compromise labels or fix the class-selection bias.

## Phase 1: bounded experiments on the current tables

| Experiment | Training incidents | Evaluation incident | Status at this update |
| --- | --- | --- | --- |
| A | Coldcard | CryptoBilis | Original frozen-tree result preserved: F1 0.629834 |
| B | CryptoBilis | Coldcard | New experiment to prespecify and execute |
| C | Coldcard + CryptoBilis | A third incident | Third-incident cohort and evidence still to identify and freeze |

These directions are then repeated with the graph/deep-learning representation
in Phase 2. Keep this table stage bounded; it supplies comparative references
and is not a prolonged hyperparameter search instead of the requested GNN work.

For each new experiment, pin input views, operational labels, overlap policy,
training-only preprocessing, validation groups, model settings, decision
threshold, metrics and exclusions before fitting. Recompute direction-specific
eligibility; do not assume the old 275-row forward-test manifest can simply be
reversed. Shared transactions, repeated addresses, exact vectors and graph
neighborhoods must not bridge fitting and evaluation unnoticed. Retain existing
frozen groups/scores and write new outputs under distinct experiment names.

Coldcard-to-CryptoBilis results and both cohorts have already been inspected;
report the new work as retrospective/exploratory. Training on October
CryptoBilis and evaluating July Coldcard is reverse-time transfer, not a claim
of forecasting a future incident. A third independent incident must remain
outside fitting, threshold selection and model selection, with compatible
source selection and reference-time rules. Another collector or participant
from CryptoBilis is not a third incident. Cross-incident pooling keeps incident
IDs and does not create more independent incidents than are actually observed.

Report precision, recall, F1, AP, ROC-AUC, confusion counts, class support,
coverage/overlap attrition and fixed-rule errors. Preserve the original Coldcard
internal F1 0.989796 and CryptoBilis external F1 0.629834, together with the
stronger external inactivity AP 0.854026 versus tree AP 0.688142. Historical
models and already inspected tests are not silently refitted or rebranded.

## Phase 2: same cohorts as graphs, deep learning as the main modeling axis

Start from the same source IDs, case/comparison selections and reference anchors
to make comparisons interpretable. Build a candidate directed typed graph with
address and transaction nodes: an address-to-transaction edge records a decoded
spent output; a transaction-to-address edge records an output created for an
address. Preserve UTXO/outpoint linkage, value, block height and observable time
as appropriate edge/transaction attributes. Keep the 14 existing variables as
auditable candidate source-node attributes. Tables remain useful feature and
evaluation views of the graph; conversion must preserve their evidence.

Define the observed neighborhood radius, required parent/neighbor closure,
coverage statuses and feature availability explicitly. More data means observed
transactions/relations with documented coverage, not fabricated complete
neighborhoods. Identifiers are linkage keys rather than learned predictors.
Co-spending is an observed relation, not established common ownership.

Every target source has its own reference cutoff. All sampled nodes, edges,
timestamps and derived features used for that prediction must respect heights
strictly below that reference block, including every multi-hop path. A graph
built with all future edges and only masked test labels would violate that
boundary. Specify whether evaluation is inductive/transductive and prevent
unreported cross-incident message passing or validation/test access.

Choose the first small address-compatible GNN and its training protocol from
the reviewed literature and actual graph schema; the exact architecture and
hyperparameters are not selected by this meeting record. Weber supports a
controlled tabular/graph comparison; ChronoWave-GNN provides a temporal deep
learning candidate; Smolenkova motivates auditing relational feature quality.
Keep Random Forest/the shallow tree/inactivity as comparative baselines while
deep learning becomes the principal new modeling work.

Separate the effects of architecture and additional information: compare a
tabular reference and a GNN with the original attributes/declared relations,
then measure a documented richer graph variant. Repeat A/B/C using compatible
populations and report any graph-driven coverage or quarantine changes.

## Phase 3: possible pre/post-Coldcard exchange-directed activity break

Treat movement from hardware wallets to exchanges as a hypothesis, not an
established observation. Define the event date, pre/post windows, cohort and
time-valid exchange attribution before inspecting the effect. In particular,
source hardware usage needs external evidence or a clearly named proxy;
blockchain signatures alone do not establish the signing device.

Possible outcomes include the share of outgoing transactions/value sent to
identified exchanges, new exchange counterparties and transfer frequency.
Assess an interrupted time series and, where comparable data exist, a control
cohort/difference-in-differences design. Check general Bitcoin activity, fees,
market conditions, other incidents and pre-trends. Avoid counting attacker
drains, consolidation or laundering as a voluntary migration by wallet owners.
An observed break or correlation does not by itself prove that Coldcard caused
a migration. This analysis has a separate post-event observation window from
the strict pre-event inputs used for incident-source classification.

## Completion of this update and immediate next executable unit

This update records the new direction and reproduces the public coverage
inventory offline. It performs no new collection, fitting, scoring, graph
construction or migration analysis. Existing model/data bytes, cutoffs,
unknown labels, original snapshots and disabled automations are preserved.

Next: diagnose the exact 159 bounded prefixes from available cached evidence,
prepare a new bounded/resumable coverage-extension protocol with a capacity
estimate, and prespecify experiment B on the current snapshot. Advance the
bounded table comparisons before Phase 2, while coverage work remains visible.
Identify an eligible third incident before claiming experiment C is executable.
