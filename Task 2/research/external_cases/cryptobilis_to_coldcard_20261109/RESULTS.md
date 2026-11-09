# Completed reverse transfer, 9 November 2026

Protocol and code were published before the one fit in commit
`ce13503e5756b719684fbe46e86608c2ca7f8fa2`. The original protocol, fit implementation
and verifier are preserved unchanged. No blockchain-provider request or
parameter/threshold search was made by this experiment.

## Result on the eligible Coldcard population

The CryptoBilis-trained tree evaluates 1,066 Coldcard addresses (499 case sources
and 567 comparisons): **499 TP / 478 TN / 89 FP / 0 FN**. Precision is
**0.848639**, recall **1.000000**, F1 **0.918123**, AP **0.937248** and ROC-AUC
**0.970537**. The 89 positives outside the case cohort are membership errors;
this does not adjudicate whether their owners were compromised or used hardware.

| Fixed method | AP | ROC-AUC |
| --- | ---: | ---: |
| Reverse-transfer tree | 0.937248 | 0.970537 |
| Prior inactivity | 0.955619 | 0.971969 |
| Prior balance | 0.847143 | 0.937561 |
| Constant training prevalence | 0.468105 | 0.500000 |

Inactivity ranks above the tree on this sample. The tree recovered all 499
eligible case sources, not all 500 selected Coldcard case sources: cohort_0191
was prespecified for overlap quarantine. All 1,866 selected records remain in
the eligibility manifest, including 159 unavailable prefixes and the 312 complete
Coldcard vectors quarantined on the evaluation side. The previous forward study
used 275 eligible CryptoBilis rows and remains unchanged. Its F1 0.629834 and
this reverse F1 concern different fitted models, eligible populations and
incident-specific operational labels; they are not a paired comparison or
proof of prospective incident generalization.

At the fixed >=0.5 decision threshold, the fitted tree decision is equivalent
to training-filled prior inactivity greater than 951 blocks on every scored
row. Balance splits alter the ranking scores, but not this binary decision.
This describes the fitted cohort rule, not an operational theft threshold.

## Verification

All 1,707 available vectors independently recount from the normalized prefixes;
all 1,281 rebuilt components match the old audit. Seven failure-oriented tests
pass. A standard-library implementation exactly replays all 1,395 training/test
float32 leaf assignments and final scores, recomputes training-only medians and
balanced node counts, independently verifies eight ranking metric sets and both
confusion/classification summaries, and checks every one of the 89 external
errors. It performs no fitting and uses no sklearn or NumPy.

## Transparent export correction, with no additional fit

The initial exporter divided already normalized sklearn 1.8 tree values by their
floating-point sum. This caused 149 exported score differences no larger than
1.1102230246251565e-16, affecting two leaf probabilities. Every path and every
decision already matched. The correction copies the exact saved estimator leaf
scores from the preserved predictions; all fitted leaves are observed in the
training predictions. It changes no threshold, model structure, prediction,
metric or error. The initial model and summary remain byte-preserved in
model_export_initial.json and summary_initial.json. export_correction.json pins
the inputs, corrected model, code and maximum delta. The frozen fit code is
retained; reproduction runs repair_export.py after fit_model.py, before the
independent verifier. The fit count remains exactly one.

## Scope and next work

This is previously inspected, reverse-time (October to July) exploratory source-
membership transfer. Device/seed/compromise labels stay unknown; missing links
through incomplete histories remain unknown. Full-current-history status is not
promoted. Coverage extension and the third-incident selection remain separate
workstreams; a pooled-training test cannot be claimed until its third incident
is defined and kept out of selection/tuning.
