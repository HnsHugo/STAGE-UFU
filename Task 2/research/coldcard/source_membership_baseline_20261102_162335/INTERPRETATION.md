# Interpretation of the frozen membership baseline

The prespecified tree separates the covered Coldcard core from the fixed
same-window comparison sources very strongly. In the frozen 234-address test
partition, it has 97 true-positive memberships, 135 true-negative memberships,
one false-positive membership and one false-negative membership. Membership
precision, recall and F1 are each **0.9897959184**. This is a within-window
development result from one previously inspected incident, with coverage bias.

| Fixed test ranking method | Membership AP | Membership ROC-AUC |
| --- | ---: | ---: |
| Training prevalence constant | 0.418803 | 0.500000 |
| Larger prior-block balance | 0.765014 | 0.911877 |
| Longer prior-block inactivity | 0.982880 | 0.986645 |
| Prespecified tree | 0.993757 | 0.994748 |

Inactivity alone already separates this cohort strongly. The tree's AP exceeds
that comparator by approximately 1.09 percentage points in this fixed test
partition. This descriptive difference is not an independent-incident result or
a significance claim. No further feature/parameter/threshold search was run.

The tree uses only `balance_sat` and `blocks_since_last_activity`. At the fixed
score threshold, its positive-membership region requires float32-converted
balance greater than **14,820,511.5 satoshis** and inactivity greater than
**1,006.5 blocks**. A further inactivity split at 8,750 blocks distinguishes the
two positive scores. This describes the fitted cohort rule, not a transferable
theft or hardware rule. The raw fitted tree also retains a redundant split
between two zero-score comparison leaves; no post-hoc pruning changed it.

`tree.svg` rounds numeric labels to eight significant digits for display; its
root label `14820512` represents the exact threshold `14820511.5`. Use the exact
conditions in `rules.json` or `model.json`, and float32 input conversion, when
replaying the model. All 1,378 exported scores exactly match the fitted estimator.

No explicit missingness indicator was selected. No observed address reached a
numeric split using an imputed value for that split column. The median-fill and
fourteen-indicator preparation nevertheless remains frozen and exported; this
observation is limited to the covered addresses scored here.

| Held-out membership error | Source ID | Relevant prior-block evidence | Interpretation |
| --- | --- | --- | --- |
| Test false negative | `cohort_0191` | Balance 69,145,962 sat; last activity 409 blocks earlier; 105 earlier receipt transactions | A known case source is more recently active than the fitted positive region. |
| Test false positive | `comparison_0401` | Balance 40,096,077 sat; last activity 7,000 blocks earlier; one earlier receipt transaction | A source outside the core has a similar balance/inactivity profile. |
| Validation false positive | `comparison_0328` | Balance 16,604,900 sat; last activity 145,611 blocks earlier; one earlier receipt transaction | Another source outside the core matches the old-funded profile. |

These are membership errors. Neither a comparison prediction nor its correction
establishes legitimate ownership, compromise, seed provenance or signing-device
identity. Independently verified compromise/device labels remain unknown for all
1,500 selections; the one owner report remains a separate evidence tier.

The 122 unfinished comparison prefixes remain excluded without replacement or
scores. Full-current-history coverage is still separately 864 complete / 136
incomplete comparisons. The missing comparisons have much larger saved current
histories, so this complete-case separation must not be generalized to every
selected source or the blockchain. Unknown prior links through excluded
histories are not claimed absent. The next aligned deliverable is a research
write-up of these fixed results and limitations; independent transfer needs a
separately justified dataset and protocol.
