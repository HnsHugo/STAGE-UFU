# Task 2 working instructions

Read [ALIGNMENT.md](ALIGNMENT.md) and the current priority in
[PROJECT_STATUS.md](PROJECT_STATUS.md) before selecting work. Explicit professor
instructions and the user's current direction take precedence over assistant
plans and older report recommendations.

- Work only on `task-2-wallet-analysis`. Never merge into main, rewrite history,
  delete original evidence, incur costs or contact people.
- The Coldcard **source-address evidence registry** is now built; see
  `research/coldcard/source_registry_20261027/README.md`. The pre-payment pilot
  also ran: eight complete source histories, fourteen features, strict prior-block
  cutoff; see `research/coldcard/prepayment_pilot_20261027/README.md`.
  The multi-input extension also ran: four complete source histories and the
  same fourteen features; see `research/coldcard/multiinput_pilot_20261028/README.md`.
  Resumable collection is now implemented: `source_cohort.py`, protocol
  `source_cohort_protocol_20261028.json`, saved state
  `research/coldcard/source_cohort_20261028/batch_0021/checkpoint.json`.
  Coverage: 407 complete (12 reused), 24 retained errors, 1 incomplete, 68 pending.
  Incomplete source `cohort_0191`: 100/110 provider transactions under the four-page
  cap, with null features; its raw history/audit is retained. No automatic retry.
  User requested faster collection: use `run-many` to chain fixed 20-source
  batches without another message per batch, preserving per-source saves and
  verifying/exporting each batch. Keep two workers and the original protocol.
  Set a soft time/batch budget, then commit and publish the completed unit.
  Next starts at `batch_0022`. Restore the latest checkpoint if the
  ignored working state is missing; do not recollect completed sources.
  The registry has graph candidates, not verified compromised/device labels.
  The address dataset/model is not replaced by collector ranking or benchmarks.
- Keep the existing numbered-part structure. Write repository content in English;
  give Hugo short French updates. Avoid creating competing plans/reorganizations.
- Before an experiment, state the requirement, unit, target/label meaning,
  evidence, cutoff/split and deliverable. Execute one useful unit, verify it and
  save it before another. Ordinary authorized work does not need confirmation.
- Reuse validated local artifacts. Do not restart historical audits/experiments
  or broad searches without a concrete need. If data are missing, try the
  documented retrieval path briefly, then deliver the achievable aligned result.
- Preserve historical outputs. Use a distinct dated output for a new experiment.
  Review staged files; keep excluded raw data and unrelated files out of commits.
  Publish completed units and verify the remote commit when access permits.
- Separate source, victim, collector, consolidation and onward-recipient roles.
  An input relation is not proof of victim status or hardware use. Unknown is not
  legitimate; many addresses in one incident are not independent cases.
- Keep incident/entity groups apart as justified and prevent temporal leakage.
  Distinguish retrospective reconstruction from detection at a historical date.
  Hardware signing, cold storage, service attribution and illicit activity differ.
- Never present recipient coverage, a proxy F1 or a model score as validated
  hardware identification or a calibrated theft probability. Report failures.
- Do not resume collector-ranking, donation-control, Real-CATS or hot/cold
  extensions unless they directly serve the aligned objective or fix a defect.
  Do not train on the September storage windows without time-valid labels.
- Preserve the external 19-feature forest: 100 trees, depth 20, minimum 20 samples
  per leaf, sqrt features, equal class weights, seed 42, training-fitted imputation
  with missing indicators and strict score > 0.15. No external-example tuning.
- GNN/GCN/SHAP and alternatives require literature review and justification from
  the actual dataset/target. Do not launch an expensive model as a substitute for
  establishing usable labels. Ivan's missing code does not block source tracing.
- End with actual work/results, checks, limitations, published commit and the next
  aligned unit. Do not imply work continues after the response.
