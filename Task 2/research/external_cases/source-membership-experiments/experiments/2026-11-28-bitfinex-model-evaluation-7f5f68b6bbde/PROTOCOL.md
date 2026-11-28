# Protocol

## Unit and evidence

The unit is an address at a confirmed reference payment. The target is documented source-cohort membership. Historical witnesses provide an incident-matched comparison population. All 14 features are extracted from confirmed transactions strictly below the reference height. The three historical incident inputs and the expanded Bitfinex corpus were replayed against their frozen versions. Missing historical replays exclude observations from fitting and scoring but leave their known identities in the overlap audit. A Bitfinex triplet becomes ineligible if a witness has a catalogued source spend. A triplet contains one source and two witnesses from the same reference block.

## Dependency and eligibility

Edges encode the same address, reference transaction, earlier transaction, referenced outpoint, known funding parent, observed input partnership or direct flow, or reference block. Frozen component links from the previous studies are retained. A test observation sharing a component with any identity from a training incident is quarantined for external scoring. Matching full feature vectors are audited as a diagnostic. Group membership is stable within a split, and each outer test group is absent from both its inner fitting and calibration.

The primary Phase 1 test excludes every component connected to any of the seven pilot reference blocks or to a selected pilot observation. The sensitivity uses all otherwise eligible Bitfinex observations. Both receive the same training model and cutoffs for each method and subset. All seven models are trained using only Coldcard, CryptoBilis and BTCPay; their training reference dates follow Bitfinex. The operating points and training calibration were frozen before scoring Bitfinex. Both populations and their results were saved before starting Phase 2.

Phase 2 evaluates the 225 ordered nonempty subset pairs for four incidents. An incident included in training receives outer held-out predictions at test. Other incidents receive full-training fits after the external quarantine. Model calibration is rerun in the training portion of each outer fold. The isolated Phase 1 fit is reused only when the permitted test rows, fit population and calibration folds agree. Reference comparisons are chronological only if every relevant training reference strictly precedes every relevant test reference. A later training reference makes the corresponding transfer retrospective.

## Methods and operating points

The 14 base benchmark methods include two decision trees, two score-only rules, six logistic specifications, random forest, histogram boosting, Gaussian naive Bayes, and an RBF SVM. The established activity masks remove last activity, the four timing variables, or those timing variables and six transaction/output counters. The inventory enumerates each distinct applicable feature configuration once. Removing the only predictor of inactivity would make its score undefined. Balance retains its single score for every mask. Logistic masks already appear in its six specifications.

Each fit uses training medians and missingness indicators. The rank rules use the selected imputed predictor. Non-tree classifiers use signed-log features and training standardization. Tree scores and probabilistic classifiers use source probabilities, except that Gaussian naive Bayes uses log odds and SVM uses the decision function. The prior settings and hyperparameters were fixed before scoring. [Feature and parameter inventory](methods.csv)

The 5% operating point calibrates on pooled held-out training witness scores. Stratified group folds use up to 5 folds and seed 42, with smaller group counts tried if needed and at least 2 folds required. Every fit requires both labels. The cutoff lies immediately above the next disallowed witness score and handles ties as a group. The tree also has its historical 0.5 cutoff. The inactivity rule has its training-only maximum F1 cutoff, with ties resolved by choosing the higher cutoff. A higher score is flagged at or above the cutoff. The realized witness false-alert rate is measured on the test population.

## Measures and review

Each row reports the same eligible observations across method comparisons, counts of observed sources and witnesses, groups and scored rows. Precision is undefined when no alerts fire. Recall counts the fraction of sources flagged. False-alert rate counts the fraction of witnesses flagged. Average precision integrates precision over discrete recall increments at tied score levels. Single-class results have no AP. Missing grouped support, fitting failures, and coverage shortfalls are retained. Complete pooled metrics require complete two-class results in every included incident. No model threshold or method is selected from these test outcomes.
