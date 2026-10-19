# Expanded external descriptive pilot

The fixed 19-feature model now scores ten saved provider-complete address histories. Training and threshold are identical to the previous pilot. The three previous external scores reproduce exactly. All seven added addresses are absent from both full Real-CATS files; the scoring script enforces this check. No external labels, scores or reserved-test outcomes tune the model.

| Evidence group | Addresses | Above fixed 0.15 threshold | Interpretation |
|---|---:|---:|---|
| EFF | 1 | 0 | Official donation purpose, not certified benign funds |
| BTCPay | 2 | 2 | One grouped incident; confidence differs between collectors |
| FBI TraderTraitor notice | 6 | 3 | Official reported stolen-funds holders, grouped conservatively |
| Binance 2019 | 1 | 1 | Research attribution resolved by unique output match |

## Address scores

| Address | Score | Threshold exceeded |
|---|---:|---|
| 3LTu6uavQ4A3kgDauZipyGqcHQEUSVe2so | 0.045173 | No |
| 19jSfadPiKa4aCefj4F7uEYbhMEt2L8SCH | 0.271938 | Yes |
| 17C7EZC1VTrXzSQneiaJv2W6tQh1vCRSnF | 0.210626 | Yes |
| 3LU8wRu4ZnXP4UM8Yo6kkTiGHM9BubgyiG | 0.118753 | No |
| 34VXKa5upLWVYMXmgid6bFM4BaQXHxSUoL | 0.233841 | Yes |
| 3AAUBbKJorvNhEUFhKnep9YTwmZECxE4Nk | 0.236503 | Yes |
| 3NbdrezMzAVVfXv5MTQJn4hWqKhYCTCJoB | 0.225124 | Yes |
| 3PjNaSeP8GzLjGeu51JR19Q2Lu8W2Te9oc | 0.148067 | No |
| 39idqitN9tYNmq3wYanwg3MitFB5TZCjWu | 0.143064 | No |
| bc1q8m9h3atn4cqeqhu3ekswdqxchp3g7d4v3qv3wm | 0.275116 | Yes |

The FBI notice of 22 August 2023 explicitly lists the six addresses as holding funds from several heists: https://www.fbi.gov/news/press-releases/fbi-identifies-cryptocurrency-funds-stolen-by-dprk. It does not map each address to an originating heist. Keep the six in one conservative group, not six independent incidents. Scoring uses October 10 saved complete histories, including later spending; it does not test detection at the 2023 publication date.

Three officially attributed holders remain below the threshold. This is evidence of missed flags in the descriptive pilot and motivates review of their feature profiles; do not lower the threshold to make these examples pass. Their source role is not identical to the original Real-CATS Hack/Theft target. No validated external recall or case-level accuracy is claimed.

The Binance address is supported by a research paper with an abbreviated identifier plus a unique on-chain amount match. The official incident transaction alone does not label all its outputs. The chosen output remains weaker evidence than the FBI exact-address attribution; other unresolved outputs are not scored as positives. See ../../research/external_cases/BINANCE_EVIDENCE.md.

## Limits and next step

This is three conservative reported theft groups plus one comparison entity, not a representative independent evaluation dataset. There is still only one fully collected donation comparison address; FSF and Archive histories remain uncollected. Evidence confidence, label availability and observation periods differ. Exact-address non-overlap does not prove entity/counterparty independence. Scores are not calibrated probabilities of theft. No precision/recall/F1 or confusion matrix is reported on this pilot.

Nine existing tests pass. Complete-history reconciliation, source hashes and overlap checks pass for all ten inputs; prior scores reproduce exactly. The updated script accepts the older Binance record field while retaining original evidence. Histories are reused from their existing repository paths without relabeling or republishing. The next useful review is the feature-level explanation of the three FBI addresses below threshold, followed by expanding independent comparison entities. Model settings remain frozen.
