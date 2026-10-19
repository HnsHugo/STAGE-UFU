# Plain-English glossary

| Term | Meaning in this project |
| --- | --- |
| Input / output | A transaction spends previous outputs as inputs and creates new outputs. An output is not necessarily an external payment; it can be change. |
| Parent transaction | A transaction that created an output later spent by another transaction. A parent relationship alone does not establish theft. |
| Feature | A measured property supplied to the classifier, such as fee rate or output count. |
| Label / target | The category the model tries to predict. Its meaning depends on the evidence; source categories are not automatically independently verified truth. |
| Candidate | A transaction related to the studied case by the recorded rule. It is not automatically a confirmed theft. |
| Unattributed / unknown | We do not have the required attribution. This is not the same as legitimate. |
| Training | Data used to fit model parameters and preprocessing statistics. |
| Validation | Data used to compare settings or diagnose behavior. Repeatedly inspecting it does not make it an independent test. |
| Test | Data reserved for a defined final evaluation. Previously inspected tests must not become tuning targets. |
| Grouped split | Keep a related group outside training when evaluating it. Candidate groups do not automatically correspond to independent incidents. |
| Precision | Of the model's alerts, the fraction matching the positive target under the recorded labels. |
| Recall | Of the labeled positives, the fraction the model alerts on. A model alerting almost everything can have high recall and poor precision. |
| F1 | Harmonic mean of precision and recall at one decision rule. It is not accuracy, and it cannot be compared fairly across unrelated targets as if it were one progress score. |
| Average precision (AP) | A summary of positive-label retrieval as the model's ranking is traversed. It does not require choosing one alert threshold. A constant score has AP equal to positive prevalence. |
| Threshold | The rule converting a score into an alert. Different thresholds change the precision/recall trade-off. |
| Seed | A fixed input to a pseudorandom generator. Changing a model seed measures algorithmic variation, not independence of cases or data. |
| Permutation importance | Change in a score when selected inputs are shuffled. It measures reliance under that perturbation, not causation. |
| Ablation | Remove a defined feature family and retrain. Other features can sometimes compensate, unlike perturbing an already fitted model. |
| Generalization | Performance outside the information used to develop the method. Its scope depends on the split: new rows, groups, entities, incidents or time periods are different tests. |
| Hardware wallet / cold storage | A signing-device property versus an operational key-storage arrangement. Neither is proved solely by an address or transaction shape. |

[Back to the main path](../README.md)
