# Results for all 49 training and test crossings

[Back to the 7 × 7 grid](2026-11-24-method-benchmark.md#browse-all-49-crossings) · [2,548 aggregate CSV rows](2026-11-24-method-benchmark.csv)

Each crossing includes all 14 methods. The main table pools the held-out observations for the selected test incident set. When multiple incidents are tested together, the incident tables show the corresponding subgroups. False alerts are witnesses flagged in the test set. AP is average precision.

Training cohorts: [Coldcard](#training-on-coldcard) · [CryptoBilis](#training-on-cryptobilis) · [BTCPay](#training-on-btcpay) · [Coldcard + CryptoBilis](#training-on-coldcard-and-cryptobilis) · [Coldcard + BTCPay](#training-on-coldcard-and-btcpay) · [CryptoBilis + BTCPay](#training-on-cryptobilis-and-btcpay) · [All three](#training-on-coldcard-and-cryptobilis-and-btcpay)

## Training on Coldcard

### Coldcard to Coldcard

**Internal** · 1471 training observations before fold splitting · 1471 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 38/971 | 99.6% | 3.9% | 0.961 | 0.984 | 0.995 |
| Smaller decision tree | 498/500 | 20/971 | 99.6% | 2.1% | 0.978 | 0.981 | 0.994 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 222/500 | 46/971 | 44.4% | 4.7% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 50/971 | 47.6% | 5.1% | 0.604 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 53/971 | 100.0% | 5.5% | 0.950 | 0.992 | 0.997 |
| Logistic, all 14 predictors | 500/500 | 56/971 | 100.0% | 5.8% | 0.947 | 0.995 | 0.998 |
| Logistic, without time since last activity | 498/500 | 52/971 | 99.6% | 5.4% | 0.949 | 0.994 | 0.998 |
| Logistic, without activity timing | 469/500 | 52/971 | 93.8% | 5.4% | 0.919 | 0.866 | 0.970 |
| Logistic, without timing and counts | 470/500 | 49/971 | 94.0% | 5.0% | 0.922 | 0.868 | 0.969 |
| Random forest | 500/500 | 51/971 | 100.0% | 5.3% | 0.951 | 0.994 | 0.998 |
| Histogram gradient boosting | 500/500 | 43/971 | 100.0% | 4.4% | 0.959 | 0.990 | 0.998 |
| Gaussian naive Bayes | 481/500 | 68/971 | 96.2% | 7.0% | 0.917 | 0.967 | 0.981 |
| RBF support vector machine | 500/500 | 49/971 | 100.0% | 5.0% | 0.953 | 0.998 | 0.999 |

### Coldcard to CryptoBilis

**External** · 1471 training observations before fold splitting · 267 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 49/122 | 5/145 | 40.2% | 3.4% | 0.557 | 0.663 | 0.688 |
| Smaller decision tree | 62/122 | 8/145 | 50.8% | 5.5% | 0.646 | 0.698 | 0.546 |
| Inactivity alone | 60/122 | 7/145 | 49.2% | 4.8% | 0.635 | 0.854 | 0.947 |
| Balance alone | 25/122 | 10/145 | 20.5% | 6.9% | 0.318 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.961 | 0.971 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.955 | 0.967 |
| Logistic, without time since last activity | 95/122 | 7/145 | 77.9% | 4.8% | 0.848 | 0.951 | 0.963 |
| Logistic, without activity timing | 59/122 | 10/145 | 48.4% | 6.9% | 0.618 | 0.830 | 0.883 |
| Logistic, without timing and counts | 60/122 | 10/145 | 49.2% | 6.9% | 0.625 | 0.829 | 0.883 |
| Random forest | 63/122 | 9/145 | 51.6% | 6.2% | 0.649 | 0.900 | 0.920 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.903 | 0.919 |
| Gaussian naive Bayes | 109/122 | 4/145 | 89.3% | 2.8% | 0.928 | 0.973 | 0.982 |
| RBF support vector machine | 105/122 | 10/145 | 86.1% | 6.9% | 0.886 | 0.936 | 0.939 |

### Coldcard to BTCPay

**External** · 1471 training observations before fold splitting · 38 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.421 | 0.477 |
| Smaller decision tree | 0/16 | 2/22 | 0.0% | 9.1% | 0.000 | 0.379 | 0.369 |
| Inactivity alone | 4/16 | 4/22 | 25.0% | 18.2% | 0.333 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.475 | 0.571 |
| Logistic, all 14 predictors | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.458 | 0.543 |
| Logistic, without time since last activity | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.449 | 0.511 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Random forest | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.500 | 0.574 |
| Histogram gradient boosting | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.503 | 0.597 |
| Gaussian naive Bayes | 1/16 | 3/22 | 6.2% | 13.6% | 0.100 | 0.469 | 0.580 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.353 | 0.327 |

### Coldcard to Coldcard and CryptoBilis

**Mixed** · 1471 training observations before fold splitting · 1738 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 547/622 | 43/1116 | 87.9% | 3.9% | 0.903 | 0.910 | 0.935 |
| Smaller decision tree | 560/622 | 28/1116 | 90.0% | 2.5% | 0.926 | 0.922 | 0.936 |
| Inactivity alone | 525/622 | 58/1116 | 84.4% | 5.2% | 0.871 | 0.928 | 0.976 |
| Balance alone | 247/622 | 56/1116 | 39.7% | 5.0% | 0.534 | 0.783 | 0.928 |
| Logistic, balance alone | 264/622 | 60/1116 | 42.4% | 5.4% | 0.558 | 0.780 | 0.927 |
| Logistic, inactivity + balance | 600/622 | 59/1116 | 96.5% | 5.3% | 0.937 | 0.982 | 0.991 |
| Logistic, all 14 predictors | 600/622 | 62/1116 | 96.5% | 5.6% | 0.935 | 0.985 | 0.992 |
| Logistic, without time since last activity | 593/622 | 59/1116 | 95.3% | 5.3% | 0.931 | 0.983 | 0.991 |
| Logistic, without activity timing | 528/622 | 62/1116 | 84.9% | 5.6% | 0.871 | 0.860 | 0.959 |
| Logistic, without timing and counts | 530/622 | 59/1116 | 85.2% | 5.3% | 0.875 | 0.863 | 0.958 |
| Random forest | 563/622 | 60/1116 | 90.5% | 5.4% | 0.904 | 0.970 | 0.979 |
| Histogram gradient boosting | 564/622 | 50/1116 | 90.7% | 4.5% | 0.913 | 0.969 | 0.982 |
| Gaussian naive Bayes | 590/622 | 72/1116 | 94.9% | 6.5% | 0.919 | 0.967 | 0.981 |
| RBF support vector machine | 605/622 | 59/1116 | 97.3% | 5.3% | 0.941 | 0.984 | 0.986 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 38/971 | 99.6% | 3.9% | 0.961 | 0.984 | 0.995 |
| Smaller decision tree | 498/500 | 20/971 | 99.6% | 2.1% | 0.978 | 0.981 | 0.994 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 222/500 | 46/971 | 44.4% | 4.7% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 50/971 | 47.6% | 5.1% | 0.604 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 53/971 | 100.0% | 5.5% | 0.950 | 0.992 | 0.997 |
| Logistic, all 14 predictors | 500/500 | 56/971 | 100.0% | 5.8% | 0.947 | 0.995 | 0.998 |
| Logistic, without time since last activity | 498/500 | 52/971 | 99.6% | 5.4% | 0.949 | 0.994 | 0.998 |
| Logistic, without activity timing | 469/500 | 52/971 | 93.8% | 5.4% | 0.919 | 0.866 | 0.970 |
| Logistic, without timing and counts | 470/500 | 49/971 | 94.0% | 5.0% | 0.922 | 0.868 | 0.969 |
| Random forest | 500/500 | 51/971 | 100.0% | 5.3% | 0.951 | 0.994 | 0.998 |
| Histogram gradient boosting | 500/500 | 43/971 | 100.0% | 4.4% | 0.959 | 0.990 | 0.998 |
| Gaussian naive Bayes | 481/500 | 68/971 | 96.2% | 7.0% | 0.917 | 0.967 | 0.981 |
| RBF support vector machine | 500/500 | 49/971 | 100.0% | 5.0% | 0.953 | 0.998 | 0.999 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 49/122 | 5/145 | 40.2% | 3.4% | 0.557 | 0.663 | 0.688 |
| Smaller decision tree | 62/122 | 8/145 | 50.8% | 5.5% | 0.646 | 0.698 | 0.546 |
| Inactivity alone | 60/122 | 7/145 | 49.2% | 4.8% | 0.635 | 0.854 | 0.947 |
| Balance alone | 25/122 | 10/145 | 20.5% | 6.9% | 0.318 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.961 | 0.971 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.955 | 0.967 |
| Logistic, without time since last activity | 95/122 | 7/145 | 77.9% | 4.8% | 0.848 | 0.951 | 0.963 |
| Logistic, without activity timing | 59/122 | 10/145 | 48.4% | 6.9% | 0.618 | 0.830 | 0.883 |
| Logistic, without timing and counts | 60/122 | 10/145 | 49.2% | 6.9% | 0.625 | 0.829 | 0.883 |
| Random forest | 63/122 | 9/145 | 51.6% | 6.2% | 0.649 | 0.900 | 0.920 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.903 | 0.919 |
| Gaussian naive Bayes | 109/122 | 4/145 | 89.3% | 2.8% | 0.928 | 0.973 | 0.982 |
| RBF support vector machine | 105/122 | 10/145 | 86.1% | 6.9% | 0.886 | 0.936 | 0.939 |

</details>

### Coldcard to Coldcard and BTCPay

**Mixed** · 1471 training observations before fold splitting · 1509 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/516 | 39/993 | 96.5% | 3.9% | 0.946 | 0.964 | 0.979 |
| Smaller decision tree | 498/516 | 22/993 | 96.5% | 2.2% | 0.961 | 0.967 | 0.982 |
| Inactivity alone | 469/516 | 55/993 | 90.9% | 5.5% | 0.902 | 0.947 | 0.975 |
| Balance alone | 222/516 | 46/993 | 43.0% | 4.6% | 0.566 | 0.780 | 0.925 |
| Logistic, balance alone | 238/516 | 50/993 | 46.1% | 5.0% | 0.592 | 0.777 | 0.925 |
| Logistic, inactivity + balance | 501/516 | 54/993 | 97.1% | 5.4% | 0.936 | 0.979 | 0.983 |
| Logistic, all 14 predictors | 501/516 | 57/993 | 97.1% | 5.7% | 0.933 | 0.983 | 0.984 |
| Logistic, without time since last activity | 498/516 | 53/993 | 96.5% | 5.3% | 0.933 | 0.981 | 0.983 |
| Logistic, without activity timing | 469/516 | 53/993 | 90.9% | 5.3% | 0.904 | 0.855 | 0.956 |
| Logistic, without timing and counts | 470/516 | 50/993 | 91.1% | 5.0% | 0.907 | 0.856 | 0.954 |
| Random forest | 501/516 | 52/993 | 97.1% | 5.2% | 0.937 | 0.980 | 0.982 |
| Histogram gradient boosting | 500/516 | 44/993 | 96.9% | 4.4% | 0.943 | 0.978 | 0.981 |
| Gaussian naive Bayes | 482/516 | 71/993 | 93.4% | 7.2% | 0.902 | 0.959 | 0.975 |
| RBF support vector machine | 500/516 | 50/993 | 96.9% | 5.0% | 0.938 | 0.979 | 0.974 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 38/971 | 99.6% | 3.9% | 0.961 | 0.984 | 0.995 |
| Smaller decision tree | 498/500 | 20/971 | 99.6% | 2.1% | 0.978 | 0.981 | 0.994 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 222/500 | 46/971 | 44.4% | 4.7% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 50/971 | 47.6% | 5.1% | 0.604 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 53/971 | 100.0% | 5.5% | 0.950 | 0.992 | 0.997 |
| Logistic, all 14 predictors | 500/500 | 56/971 | 100.0% | 5.8% | 0.947 | 0.995 | 0.998 |
| Logistic, without time since last activity | 498/500 | 52/971 | 99.6% | 5.4% | 0.949 | 0.994 | 0.998 |
| Logistic, without activity timing | 469/500 | 52/971 | 93.8% | 5.4% | 0.919 | 0.866 | 0.970 |
| Logistic, without timing and counts | 470/500 | 49/971 | 94.0% | 5.0% | 0.922 | 0.868 | 0.969 |
| Random forest | 500/500 | 51/971 | 100.0% | 5.3% | 0.951 | 0.994 | 0.998 |
| Histogram gradient boosting | 500/500 | 43/971 | 100.0% | 4.4% | 0.959 | 0.990 | 0.998 |
| Gaussian naive Bayes | 481/500 | 68/971 | 96.2% | 7.0% | 0.917 | 0.967 | 0.981 |
| RBF support vector machine | 500/500 | 49/971 | 100.0% | 5.0% | 0.953 | 0.998 | 0.999 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.421 | 0.477 |
| Smaller decision tree | 0/16 | 2/22 | 0.0% | 9.1% | 0.000 | 0.379 | 0.369 |
| Inactivity alone | 4/16 | 4/22 | 25.0% | 18.2% | 0.333 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.475 | 0.571 |
| Logistic, all 14 predictors | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.458 | 0.543 |
| Logistic, without time since last activity | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.449 | 0.511 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Random forest | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.500 | 0.574 |
| Histogram gradient boosting | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.503 | 0.597 |
| Gaussian naive Bayes | 1/16 | 3/22 | 6.2% | 13.6% | 0.100 | 0.469 | 0.580 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.353 | 0.327 |

</details>

### Coldcard to CryptoBilis and BTCPay

**External** · 1471 training observations before fold splitting · 305 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 49/138 | 6/167 | 35.5% | 3.6% | 0.508 | 0.631 | 0.664 |
| Smaller decision tree | 62/138 | 10/167 | 44.9% | 6.0% | 0.590 | 0.652 | 0.522 |
| Inactivity alone | 64/138 | 11/167 | 46.4% | 6.6% | 0.601 | 0.806 | 0.903 |
| Balance alone | 25/138 | 10/167 | 18.1% | 6.0% | 0.289 | 0.729 | 0.781 |
| Logistic, balance alone | 26/138 | 10/167 | 18.8% | 6.0% | 0.299 | 0.729 | 0.781 |
| Logistic, inactivity + balance | 101/138 | 7/167 | 73.2% | 4.2% | 0.821 | 0.918 | 0.917 |
| Logistic, all 14 predictors | 101/138 | 7/167 | 73.2% | 4.2% | 0.821 | 0.912 | 0.911 |
| Logistic, without time since last activity | 95/138 | 8/167 | 68.8% | 4.8% | 0.788 | 0.907 | 0.905 |
| Logistic, without activity timing | 59/138 | 11/167 | 42.8% | 6.6% | 0.567 | 0.790 | 0.828 |
| Logistic, without timing and counts | 60/138 | 11/167 | 43.5% | 6.6% | 0.574 | 0.789 | 0.826 |
| Random forest | 64/138 | 10/167 | 46.4% | 6.0% | 0.604 | 0.858 | 0.880 |
| Histogram gradient boosting | 64/138 | 8/167 | 46.4% | 4.8% | 0.610 | 0.858 | 0.883 |
| Gaussian naive Bayes | 110/138 | 7/167 | 79.7% | 4.2% | 0.863 | 0.934 | 0.940 |
| RBF support vector machine | 105/138 | 11/167 | 76.1% | 6.6% | 0.827 | 0.882 | 0.862 |

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 49/122 | 5/145 | 40.2% | 3.4% | 0.557 | 0.663 | 0.688 |
| Smaller decision tree | 62/122 | 8/145 | 50.8% | 5.5% | 0.646 | 0.698 | 0.546 |
| Inactivity alone | 60/122 | 7/145 | 49.2% | 4.8% | 0.635 | 0.854 | 0.947 |
| Balance alone | 25/122 | 10/145 | 20.5% | 6.9% | 0.318 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.961 | 0.971 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.955 | 0.967 |
| Logistic, without time since last activity | 95/122 | 7/145 | 77.9% | 4.8% | 0.848 | 0.951 | 0.963 |
| Logistic, without activity timing | 59/122 | 10/145 | 48.4% | 6.9% | 0.618 | 0.830 | 0.883 |
| Logistic, without timing and counts | 60/122 | 10/145 | 49.2% | 6.9% | 0.625 | 0.829 | 0.883 |
| Random forest | 63/122 | 9/145 | 51.6% | 6.2% | 0.649 | 0.900 | 0.920 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.903 | 0.919 |
| Gaussian naive Bayes | 109/122 | 4/145 | 89.3% | 2.8% | 0.928 | 0.973 | 0.982 |
| RBF support vector machine | 105/122 | 10/145 | 86.1% | 6.9% | 0.886 | 0.936 | 0.939 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.421 | 0.477 |
| Smaller decision tree | 0/16 | 2/22 | 0.0% | 9.1% | 0.000 | 0.379 | 0.369 |
| Inactivity alone | 4/16 | 4/22 | 25.0% | 18.2% | 0.333 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.475 | 0.571 |
| Logistic, all 14 predictors | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.458 | 0.543 |
| Logistic, without time since last activity | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.449 | 0.511 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Random forest | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.500 | 0.574 |
| Histogram gradient boosting | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.503 | 0.597 |
| Gaussian naive Bayes | 1/16 | 3/22 | 6.2% | 13.6% | 0.100 | 0.469 | 0.580 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.353 | 0.327 |

</details>

### Coldcard to Coldcard and CryptoBilis and BTCPay

**Mixed** · 1471 training observations before fold splitting · 1776 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 547/638 | 44/1138 | 85.7% | 3.9% | 0.890 | 0.897 | 0.923 |
| Smaller decision tree | 560/638 | 30/1138 | 87.8% | 2.6% | 0.912 | 0.911 | 0.927 |
| Inactivity alone | 529/638 | 62/1138 | 82.9% | 5.4% | 0.861 | 0.922 | 0.969 |
| Balance alone | 247/638 | 56/1138 | 38.7% | 4.9% | 0.525 | 0.773 | 0.911 |
| Logistic, balance alone | 264/638 | 60/1138 | 41.4% | 5.3% | 0.549 | 0.771 | 0.910 |
| Logistic, inactivity + balance | 601/638 | 60/1138 | 94.2% | 5.3% | 0.925 | 0.972 | 0.980 |
| Logistic, all 14 predictors | 601/638 | 63/1138 | 94.2% | 5.5% | 0.923 | 0.975 | 0.980 |
| Logistic, without time since last activity | 593/638 | 60/1138 | 92.9% | 5.3% | 0.919 | 0.973 | 0.979 |
| Logistic, without activity timing | 528/638 | 63/1138 | 82.8% | 5.5% | 0.859 | 0.852 | 0.948 |
| Logistic, without timing and counts | 530/638 | 60/1138 | 83.1% | 5.3% | 0.863 | 0.853 | 0.946 |
| Random forest | 564/638 | 61/1138 | 88.4% | 5.4% | 0.893 | 0.960 | 0.967 |
| Histogram gradient boosting | 564/638 | 51/1138 | 88.4% | 4.5% | 0.900 | 0.959 | 0.970 |
| Gaussian naive Bayes | 591/638 | 75/1138 | 92.6% | 6.6% | 0.906 | 0.960 | 0.975 |
| RBF support vector machine | 605/638 | 60/1138 | 94.8% | 5.3% | 0.929 | 0.969 | 0.966 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 38/971 | 99.6% | 3.9% | 0.961 | 0.984 | 0.995 |
| Smaller decision tree | 498/500 | 20/971 | 99.6% | 2.1% | 0.978 | 0.981 | 0.994 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 222/500 | 46/971 | 44.4% | 4.7% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 50/971 | 47.6% | 5.1% | 0.604 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 53/971 | 100.0% | 5.5% | 0.950 | 0.992 | 0.997 |
| Logistic, all 14 predictors | 500/500 | 56/971 | 100.0% | 5.8% | 0.947 | 0.995 | 0.998 |
| Logistic, without time since last activity | 498/500 | 52/971 | 99.6% | 5.4% | 0.949 | 0.994 | 0.998 |
| Logistic, without activity timing | 469/500 | 52/971 | 93.8% | 5.4% | 0.919 | 0.866 | 0.970 |
| Logistic, without timing and counts | 470/500 | 49/971 | 94.0% | 5.0% | 0.922 | 0.868 | 0.969 |
| Random forest | 500/500 | 51/971 | 100.0% | 5.3% | 0.951 | 0.994 | 0.998 |
| Histogram gradient boosting | 500/500 | 43/971 | 100.0% | 4.4% | 0.959 | 0.990 | 0.998 |
| Gaussian naive Bayes | 481/500 | 68/971 | 96.2% | 7.0% | 0.917 | 0.967 | 0.981 |
| RBF support vector machine | 500/500 | 49/971 | 100.0% | 5.0% | 0.953 | 0.998 | 0.999 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 49/122 | 5/145 | 40.2% | 3.4% | 0.557 | 0.663 | 0.688 |
| Smaller decision tree | 62/122 | 8/145 | 50.8% | 5.5% | 0.646 | 0.698 | 0.546 |
| Inactivity alone | 60/122 | 7/145 | 49.2% | 4.8% | 0.635 | 0.854 | 0.947 |
| Balance alone | 25/122 | 10/145 | 20.5% | 6.9% | 0.318 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.961 | 0.971 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.955 | 0.967 |
| Logistic, without time since last activity | 95/122 | 7/145 | 77.9% | 4.8% | 0.848 | 0.951 | 0.963 |
| Logistic, without activity timing | 59/122 | 10/145 | 48.4% | 6.9% | 0.618 | 0.830 | 0.883 |
| Logistic, without timing and counts | 60/122 | 10/145 | 49.2% | 6.9% | 0.625 | 0.829 | 0.883 |
| Random forest | 63/122 | 9/145 | 51.6% | 6.2% | 0.649 | 0.900 | 0.920 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.903 | 0.919 |
| Gaussian naive Bayes | 109/122 | 4/145 | 89.3% | 2.8% | 0.928 | 0.973 | 0.982 |
| RBF support vector machine | 105/122 | 10/145 | 86.1% | 6.9% | 0.886 | 0.936 | 0.939 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.421 | 0.477 |
| Smaller decision tree | 0/16 | 2/22 | 0.0% | 9.1% | 0.000 | 0.379 | 0.369 |
| Inactivity alone | 4/16 | 4/22 | 25.0% | 18.2% | 0.333 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.475 | 0.571 |
| Logistic, all 14 predictors | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.458 | 0.543 |
| Logistic, without time since last activity | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.449 | 0.511 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.403 | 0.480 |
| Random forest | 1/16 | 1/22 | 6.2% | 4.5% | 0.111 | 0.500 | 0.574 |
| Histogram gradient boosting | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.503 | 0.597 |
| Gaussian naive Bayes | 1/16 | 3/22 | 6.2% | 13.6% | 0.100 | 0.469 | 0.580 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.353 | 0.327 |

</details>

## Training on CryptoBilis

### CryptoBilis to Coldcard

**External** · 329 training observations before fold splitting · 1079 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/580 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 119/499 | 62/580 | 23.8% | 10.7% | 0.350 | 0.509 | 0.549 |
| Inactivity alone | 496/499 | 71/580 | 99.4% | 12.2% | 0.931 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/580 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 269/499 | 46/580 | 53.9% | 7.9% | 0.661 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 499/499 | 59/580 | 100.0% | 10.2% | 0.944 | 0.995 | 0.996 |
| Logistic, all 14 predictors | 494/499 | 72/580 | 99.0% | 12.4% | 0.928 | 0.989 | 0.991 |
| Logistic, without time since last activity | 485/499 | 70/580 | 97.2% | 12.1% | 0.920 | 0.986 | 0.987 |
| Logistic, without activity timing | 462/499 | 39/580 | 92.6% | 6.7% | 0.924 | 0.876 | 0.945 |
| Logistic, without timing and counts | 481/499 | 40/580 | 96.4% | 6.9% | 0.943 | 0.877 | 0.946 |
| Random forest | 484/499 | 69/580 | 97.0% | 11.9% | 0.920 | 0.949 | 0.973 |
| Histogram gradient boosting | 477/499 | 51/580 | 95.6% | 8.8% | 0.929 | 0.912 | 0.951 |
| Gaussian naive Bayes | 0/499 | 0/580 | 0.0% | 0.0% | 0.000 | 0.890 | 0.886 |
| RBF support vector machine | 466/499 | 64/580 | 93.4% | 11.0% | 0.906 | 0.977 | 0.978 |

### CryptoBilis to CryptoBilis

**Internal** · 329 training observations before fold splitting · 329 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.882 | 0.958 |
| Smaller decision tree | 47/122 | 3/207 | 38.5% | 1.4% | 0.547 | 0.880 | 0.953 |
| Inactivity alone | 102/122 | 11/207 | 83.6% | 5.3% | 0.868 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 31/122 | 12/207 | 25.4% | 5.8% | 0.376 | 0.734 | 0.863 |
| Logistic, inactivity + balance | 107/122 | 11/207 | 87.7% | 5.3% | 0.892 | 0.912 | 0.972 |
| Logistic, all 14 predictors | 116/122 | 12/207 | 95.1% | 5.8% | 0.928 | 0.926 | 0.976 |
| Logistic, without time since last activity | 114/122 | 13/207 | 93.4% | 6.3% | 0.916 | 0.939 | 0.975 |
| Logistic, without activity timing | 62/122 | 12/207 | 50.8% | 5.8% | 0.633 | 0.815 | 0.912 |
| Logistic, without timing and counts | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.819 | 0.914 |
| Random forest | 116/122 | 11/207 | 95.1% | 5.3% | 0.932 | 0.944 | 0.980 |
| Histogram gradient boosting | 108/122 | 11/207 | 88.5% | 5.3% | 0.896 | 0.949 | 0.984 |
| Gaussian naive Bayes | 22/122 | 4/207 | 18.0% | 1.9% | 0.297 | 0.750 | 0.868 |
| RBF support vector machine | 115/122 | 12/207 | 94.3% | 5.8% | 0.924 | 0.959 | 0.984 |

### CryptoBilis to BTCPay

**External** · 329 training observations before fold splitting · 41 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.438 | 0.570 |
| Smaller decision tree | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.431 | 0.568 |
| Inactivity alone | 7/16 | 6/25 | 43.8% | 24.0% | 0.483 | 0.559 | 0.645 |
| Balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, inactivity + balance | 2/16 | 5/25 | 12.5% | 20.0% | 0.174 | 0.503 | 0.593 |
| Logistic, all 14 predictors | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.513 | 0.615 |
| Logistic, without time since last activity | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.505 | 0.600 |
| Logistic, without activity timing | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.394 | 0.525 |
| Logistic, without timing and counts | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.392 | 0.520 |
| Random forest | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.467 | 0.618 |
| Histogram gradient boosting | 3/16 | 4/25 | 18.8% | 16.0% | 0.261 | 0.467 | 0.621 |
| Gaussian naive Bayes | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.446 | 0.613 |
| RBF support vector machine | 3/16 | 5/25 | 18.8% | 20.0% | 0.250 | 0.441 | 0.525 |

### CryptoBilis to Coldcard and CryptoBilis

**Mixed** · 329 training observations before fold splitting · 1408 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 601/621 | 47/787 | 96.8% | 6.0% | 0.947 | 0.927 | 0.968 |
| Smaller decision tree | 166/621 | 65/787 | 26.7% | 8.3% | 0.390 | 0.572 | 0.632 |
| Inactivity alone | 598/621 | 82/787 | 96.3% | 10.4% | 0.919 | 0.929 | 0.966 |
| Balance alone | 295/621 | 57/787 | 47.5% | 7.2% | 0.606 | 0.813 | 0.918 |
| Logistic, balance alone | 300/621 | 58/787 | 48.3% | 7.4% | 0.613 | 0.811 | 0.917 |
| Logistic, inactivity + balance | 606/621 | 70/787 | 97.6% | 8.9% | 0.934 | 0.983 | 0.987 |
| Logistic, all 14 predictors | 610/621 | 84/787 | 98.2% | 10.7% | 0.928 | 0.979 | 0.984 |
| Logistic, without time since last activity | 599/621 | 83/787 | 96.5% | 10.5% | 0.919 | 0.977 | 0.982 |
| Logistic, without activity timing | 524/621 | 51/787 | 84.4% | 6.5% | 0.876 | 0.868 | 0.940 |
| Logistic, without timing and counts | 542/621 | 50/787 | 87.3% | 6.4% | 0.894 | 0.870 | 0.940 |
| Random forest | 600/621 | 80/787 | 96.6% | 10.2% | 0.922 | 0.947 | 0.975 |
| Histogram gradient boosting | 585/621 | 62/787 | 94.2% | 7.9% | 0.923 | 0.920 | 0.961 |
| Gaussian naive Bayes | 22/621 | 4/787 | 3.5% | 0.5% | 0.068 | 0.819 | 0.873 |
| RBF support vector machine | 581/621 | 76/787 | 93.6% | 9.7% | 0.909 | 0.972 | 0.977 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/580 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 119/499 | 62/580 | 23.8% | 10.7% | 0.350 | 0.509 | 0.549 |
| Inactivity alone | 496/499 | 71/580 | 99.4% | 12.2% | 0.931 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/580 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 269/499 | 46/580 | 53.9% | 7.9% | 0.661 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 499/499 | 59/580 | 100.0% | 10.2% | 0.944 | 0.995 | 0.996 |
| Logistic, all 14 predictors | 494/499 | 72/580 | 99.0% | 12.4% | 0.928 | 0.989 | 0.991 |
| Logistic, without time since last activity | 485/499 | 70/580 | 97.2% | 12.1% | 0.920 | 0.986 | 0.987 |
| Logistic, without activity timing | 462/499 | 39/580 | 92.6% | 6.7% | 0.924 | 0.876 | 0.945 |
| Logistic, without timing and counts | 481/499 | 40/580 | 96.4% | 6.9% | 0.943 | 0.877 | 0.946 |
| Random forest | 484/499 | 69/580 | 97.0% | 11.9% | 0.920 | 0.949 | 0.973 |
| Histogram gradient boosting | 477/499 | 51/580 | 95.6% | 8.8% | 0.929 | 0.912 | 0.951 |
| Gaussian naive Bayes | 0/499 | 0/580 | 0.0% | 0.0% | 0.000 | 0.890 | 0.886 |
| RBF support vector machine | 466/499 | 64/580 | 93.4% | 11.0% | 0.906 | 0.977 | 0.978 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.882 | 0.958 |
| Smaller decision tree | 47/122 | 3/207 | 38.5% | 1.4% | 0.547 | 0.880 | 0.953 |
| Inactivity alone | 102/122 | 11/207 | 83.6% | 5.3% | 0.868 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 31/122 | 12/207 | 25.4% | 5.8% | 0.376 | 0.734 | 0.863 |
| Logistic, inactivity + balance | 107/122 | 11/207 | 87.7% | 5.3% | 0.892 | 0.912 | 0.972 |
| Logistic, all 14 predictors | 116/122 | 12/207 | 95.1% | 5.8% | 0.928 | 0.926 | 0.976 |
| Logistic, without time since last activity | 114/122 | 13/207 | 93.4% | 6.3% | 0.916 | 0.939 | 0.975 |
| Logistic, without activity timing | 62/122 | 12/207 | 50.8% | 5.8% | 0.633 | 0.815 | 0.912 |
| Logistic, without timing and counts | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.819 | 0.914 |
| Random forest | 116/122 | 11/207 | 95.1% | 5.3% | 0.932 | 0.944 | 0.980 |
| Histogram gradient boosting | 108/122 | 11/207 | 88.5% | 5.3% | 0.896 | 0.949 | 0.984 |
| Gaussian naive Bayes | 22/122 | 4/207 | 18.0% | 1.9% | 0.297 | 0.750 | 0.868 |
| RBF support vector machine | 115/122 | 12/207 | 94.3% | 5.8% | 0.924 | 0.959 | 0.984 |

</details>

### CryptoBilis to Coldcard and BTCPay

**External** · 329 training observations before fold splitting · 1120 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/515 | 41/605 | 96.9% | 6.8% | 0.946 | 0.928 | 0.961 |
| Smaller decision tree | 125/515 | 68/605 | 24.3% | 11.2% | 0.353 | 0.505 | 0.550 |
| Inactivity alone | 503/515 | 77/605 | 97.7% | 12.7% | 0.919 | 0.948 | 0.963 |
| Balance alone | 265/515 | 45/605 | 51.5% | 7.4% | 0.642 | 0.814 | 0.911 |
| Logistic, balance alone | 269/515 | 46/605 | 52.2% | 7.6% | 0.648 | 0.814 | 0.911 |
| Logistic, inactivity + balance | 501/515 | 64/605 | 97.3% | 10.6% | 0.928 | 0.986 | 0.983 |
| Logistic, all 14 predictors | 499/515 | 77/605 | 96.9% | 12.7% | 0.915 | 0.981 | 0.980 |
| Logistic, without time since last activity | 490/515 | 75/605 | 95.1% | 12.4% | 0.907 | 0.978 | 0.977 |
| Logistic, without activity timing | 462/515 | 40/605 | 89.7% | 6.6% | 0.909 | 0.868 | 0.933 |
| Logistic, without timing and counts | 481/515 | 41/605 | 93.4% | 6.8% | 0.928 | 0.869 | 0.933 |
| Random forest | 490/515 | 75/605 | 95.1% | 12.4% | 0.907 | 0.936 | 0.963 |
| Histogram gradient boosting | 480/515 | 55/605 | 93.2% | 9.1% | 0.914 | 0.899 | 0.940 |
| Gaussian naive Bayes | 0/515 | 0/605 | 0.0% | 0.0% | 0.000 | 0.881 | 0.879 |
| RBF support vector machine | 469/515 | 69/605 | 91.1% | 11.4% | 0.891 | 0.968 | 0.965 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/580 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 119/499 | 62/580 | 23.8% | 10.7% | 0.350 | 0.509 | 0.549 |
| Inactivity alone | 496/499 | 71/580 | 99.4% | 12.2% | 0.931 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/580 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 269/499 | 46/580 | 53.9% | 7.9% | 0.661 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 499/499 | 59/580 | 100.0% | 10.2% | 0.944 | 0.995 | 0.996 |
| Logistic, all 14 predictors | 494/499 | 72/580 | 99.0% | 12.4% | 0.928 | 0.989 | 0.991 |
| Logistic, without time since last activity | 485/499 | 70/580 | 97.2% | 12.1% | 0.920 | 0.986 | 0.987 |
| Logistic, without activity timing | 462/499 | 39/580 | 92.6% | 6.7% | 0.924 | 0.876 | 0.945 |
| Logistic, without timing and counts | 481/499 | 40/580 | 96.4% | 6.9% | 0.943 | 0.877 | 0.946 |
| Random forest | 484/499 | 69/580 | 97.0% | 11.9% | 0.920 | 0.949 | 0.973 |
| Histogram gradient boosting | 477/499 | 51/580 | 95.6% | 8.8% | 0.929 | 0.912 | 0.951 |
| Gaussian naive Bayes | 0/499 | 0/580 | 0.0% | 0.0% | 0.000 | 0.890 | 0.886 |
| RBF support vector machine | 466/499 | 64/580 | 93.4% | 11.0% | 0.906 | 0.977 | 0.978 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.438 | 0.570 |
| Smaller decision tree | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.431 | 0.568 |
| Inactivity alone | 7/16 | 6/25 | 43.8% | 24.0% | 0.483 | 0.559 | 0.645 |
| Balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, inactivity + balance | 2/16 | 5/25 | 12.5% | 20.0% | 0.174 | 0.503 | 0.593 |
| Logistic, all 14 predictors | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.513 | 0.615 |
| Logistic, without time since last activity | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.505 | 0.600 |
| Logistic, without activity timing | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.394 | 0.525 |
| Logistic, without timing and counts | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.392 | 0.520 |
| Random forest | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.467 | 0.618 |
| Histogram gradient boosting | 3/16 | 4/25 | 18.8% | 16.0% | 0.261 | 0.467 | 0.621 |
| Gaussian naive Bayes | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.446 | 0.613 |
| RBF support vector machine | 3/16 | 5/25 | 18.8% | 20.0% | 0.250 | 0.441 | 0.525 |

</details>

### CryptoBilis to CryptoBilis and BTCPay

**Mixed** · 329 training observations before fold splitting · 370 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/138 | 8/232 | 73.9% | 3.4% | 0.823 | 0.838 | 0.917 |
| Smaller decision tree | 53/138 | 9/232 | 38.4% | 3.9% | 0.530 | 0.829 | 0.910 |
| Inactivity alone | 109/138 | 17/232 | 79.0% | 7.3% | 0.826 | 0.802 | 0.922 |
| Balance alone | 30/138 | 12/232 | 21.7% | 5.2% | 0.333 | 0.706 | 0.804 |
| Logistic, balance alone | 31/138 | 12/232 | 22.5% | 5.2% | 0.343 | 0.693 | 0.799 |
| Logistic, inactivity + balance | 109/138 | 16/232 | 79.0% | 6.9% | 0.829 | 0.874 | 0.930 |
| Logistic, all 14 predictors | 121/138 | 17/232 | 87.7% | 7.3% | 0.877 | 0.887 | 0.938 |
| Logistic, without time since last activity | 119/138 | 18/232 | 86.2% | 7.8% | 0.865 | 0.899 | 0.936 |
| Logistic, without activity timing | 62/138 | 13/232 | 44.9% | 5.6% | 0.582 | 0.779 | 0.875 |
| Logistic, without timing and counts | 61/138 | 11/232 | 44.2% | 4.7% | 0.581 | 0.781 | 0.873 |
| Random forest | 122/138 | 17/232 | 88.4% | 7.3% | 0.881 | 0.892 | 0.938 |
| Histogram gradient boosting | 111/138 | 15/232 | 80.4% | 6.5% | 0.841 | 0.905 | 0.937 |
| Gaussian naive Bayes | 22/138 | 4/232 | 15.9% | 1.7% | 0.268 | 0.730 | 0.851 |
| RBF support vector machine | 118/138 | 17/232 | 85.5% | 7.3% | 0.864 | 0.911 | 0.931 |

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.882 | 0.958 |
| Smaller decision tree | 47/122 | 3/207 | 38.5% | 1.4% | 0.547 | 0.880 | 0.953 |
| Inactivity alone | 102/122 | 11/207 | 83.6% | 5.3% | 0.868 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 31/122 | 12/207 | 25.4% | 5.8% | 0.376 | 0.734 | 0.863 |
| Logistic, inactivity + balance | 107/122 | 11/207 | 87.7% | 5.3% | 0.892 | 0.912 | 0.972 |
| Logistic, all 14 predictors | 116/122 | 12/207 | 95.1% | 5.8% | 0.928 | 0.926 | 0.976 |
| Logistic, without time since last activity | 114/122 | 13/207 | 93.4% | 6.3% | 0.916 | 0.939 | 0.975 |
| Logistic, without activity timing | 62/122 | 12/207 | 50.8% | 5.8% | 0.633 | 0.815 | 0.912 |
| Logistic, without timing and counts | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.819 | 0.914 |
| Random forest | 116/122 | 11/207 | 95.1% | 5.3% | 0.932 | 0.944 | 0.980 |
| Histogram gradient boosting | 108/122 | 11/207 | 88.5% | 5.3% | 0.896 | 0.949 | 0.984 |
| Gaussian naive Bayes | 22/122 | 4/207 | 18.0% | 1.9% | 0.297 | 0.750 | 0.868 |
| RBF support vector machine | 115/122 | 12/207 | 94.3% | 5.8% | 0.924 | 0.959 | 0.984 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.438 | 0.570 |
| Smaller decision tree | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.431 | 0.568 |
| Inactivity alone | 7/16 | 6/25 | 43.8% | 24.0% | 0.483 | 0.559 | 0.645 |
| Balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, inactivity + balance | 2/16 | 5/25 | 12.5% | 20.0% | 0.174 | 0.503 | 0.593 |
| Logistic, all 14 predictors | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.513 | 0.615 |
| Logistic, without time since last activity | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.505 | 0.600 |
| Logistic, without activity timing | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.394 | 0.525 |
| Logistic, without timing and counts | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.392 | 0.520 |
| Random forest | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.467 | 0.618 |
| Histogram gradient boosting | 3/16 | 4/25 | 18.8% | 16.0% | 0.261 | 0.467 | 0.621 |
| Gaussian naive Bayes | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.446 | 0.613 |
| RBF support vector machine | 3/16 | 5/25 | 18.8% | 20.0% | 0.250 | 0.441 | 0.525 |

</details>

### CryptoBilis to Coldcard and CryptoBilis and BTCPay

**Mixed** · 329 training observations before fold splitting · 1449 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 601/637 | 48/812 | 94.3% | 5.9% | 0.935 | 0.918 | 0.959 |
| Smaller decision tree | 172/637 | 71/812 | 27.0% | 8.7% | 0.391 | 0.568 | 0.630 |
| Inactivity alone | 605/637 | 88/812 | 95.0% | 10.8% | 0.910 | 0.923 | 0.959 |
| Balance alone | 295/637 | 57/812 | 46.3% | 7.0% | 0.597 | 0.805 | 0.903 |
| Logistic, balance alone | 300/637 | 58/812 | 47.1% | 7.1% | 0.603 | 0.803 | 0.902 |
| Logistic, inactivity + balance | 608/637 | 75/812 | 95.4% | 9.2% | 0.921 | 0.976 | 0.978 |
| Logistic, all 14 predictors | 615/637 | 89/812 | 96.5% | 11.0% | 0.917 | 0.972 | 0.976 |
| Logistic, without time since last activity | 604/637 | 88/812 | 94.8% | 10.8% | 0.909 | 0.970 | 0.974 |
| Logistic, without activity timing | 524/637 | 52/812 | 82.3% | 6.4% | 0.864 | 0.861 | 0.930 |
| Logistic, without timing and counts | 542/637 | 51/812 | 85.1% | 6.3% | 0.881 | 0.863 | 0.930 |
| Random forest | 606/637 | 86/812 | 95.1% | 10.6% | 0.912 | 0.936 | 0.967 |
| Histogram gradient boosting | 588/637 | 66/812 | 92.3% | 8.1% | 0.911 | 0.910 | 0.951 |
| Gaussian naive Bayes | 22/637 | 4/812 | 3.5% | 0.5% | 0.066 | 0.814 | 0.868 |
| RBF support vector machine | 584/637 | 81/812 | 91.7% | 10.0% | 0.897 | 0.964 | 0.966 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/580 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 119/499 | 62/580 | 23.8% | 10.7% | 0.350 | 0.509 | 0.549 |
| Inactivity alone | 496/499 | 71/580 | 99.4% | 12.2% | 0.931 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/580 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 269/499 | 46/580 | 53.9% | 7.9% | 0.661 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 499/499 | 59/580 | 100.0% | 10.2% | 0.944 | 0.995 | 0.996 |
| Logistic, all 14 predictors | 494/499 | 72/580 | 99.0% | 12.4% | 0.928 | 0.989 | 0.991 |
| Logistic, without time since last activity | 485/499 | 70/580 | 97.2% | 12.1% | 0.920 | 0.986 | 0.987 |
| Logistic, without activity timing | 462/499 | 39/580 | 92.6% | 6.7% | 0.924 | 0.876 | 0.945 |
| Logistic, without timing and counts | 481/499 | 40/580 | 96.4% | 6.9% | 0.943 | 0.877 | 0.946 |
| Random forest | 484/499 | 69/580 | 97.0% | 11.9% | 0.920 | 0.949 | 0.973 |
| Histogram gradient boosting | 477/499 | 51/580 | 95.6% | 8.8% | 0.929 | 0.912 | 0.951 |
| Gaussian naive Bayes | 0/499 | 0/580 | 0.0% | 0.0% | 0.000 | 0.890 | 0.886 |
| RBF support vector machine | 466/499 | 64/580 | 93.4% | 11.0% | 0.906 | 0.977 | 0.978 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.882 | 0.958 |
| Smaller decision tree | 47/122 | 3/207 | 38.5% | 1.4% | 0.547 | 0.880 | 0.953 |
| Inactivity alone | 102/122 | 11/207 | 83.6% | 5.3% | 0.868 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 31/122 | 12/207 | 25.4% | 5.8% | 0.376 | 0.734 | 0.863 |
| Logistic, inactivity + balance | 107/122 | 11/207 | 87.7% | 5.3% | 0.892 | 0.912 | 0.972 |
| Logistic, all 14 predictors | 116/122 | 12/207 | 95.1% | 5.8% | 0.928 | 0.926 | 0.976 |
| Logistic, without time since last activity | 114/122 | 13/207 | 93.4% | 6.3% | 0.916 | 0.939 | 0.975 |
| Logistic, without activity timing | 62/122 | 12/207 | 50.8% | 5.8% | 0.633 | 0.815 | 0.912 |
| Logistic, without timing and counts | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.819 | 0.914 |
| Random forest | 116/122 | 11/207 | 95.1% | 5.3% | 0.932 | 0.944 | 0.980 |
| Histogram gradient boosting | 108/122 | 11/207 | 88.5% | 5.3% | 0.896 | 0.949 | 0.984 |
| Gaussian naive Bayes | 22/122 | 4/207 | 18.0% | 1.9% | 0.297 | 0.750 | 0.868 |
| RBF support vector machine | 115/122 | 12/207 | 94.3% | 5.8% | 0.924 | 0.959 | 0.984 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.438 | 0.570 |
| Smaller decision tree | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.431 | 0.568 |
| Inactivity alone | 7/16 | 6/25 | 43.8% | 24.0% | 0.483 | 0.559 | 0.645 |
| Balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, balance alone | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.312 | 0.338 |
| Logistic, inactivity + balance | 2/16 | 5/25 | 12.5% | 20.0% | 0.174 | 0.503 | 0.593 |
| Logistic, all 14 predictors | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.513 | 0.615 |
| Logistic, without time since last activity | 5/16 | 5/25 | 31.2% | 20.0% | 0.385 | 0.505 | 0.600 |
| Logistic, without activity timing | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.394 | 0.525 |
| Logistic, without timing and counts | 0/16 | 1/25 | 0.0% | 4.0% | 0.000 | 0.392 | 0.520 |
| Random forest | 6/16 | 6/25 | 37.5% | 24.0% | 0.429 | 0.467 | 0.618 |
| Histogram gradient boosting | 3/16 | 4/25 | 18.8% | 16.0% | 0.261 | 0.467 | 0.621 |
| Gaussian naive Bayes | 0/16 | 0/25 | 0.0% | 0.0% | 0.000 | 0.446 | 0.613 |
| RBF support vector machine | 3/16 | 5/25 | 18.8% | 20.0% | 0.250 | 0.441 | 0.525 |

</details>

## Training on BTCPay

### BTCPay to Coldcard

**External** · 48 training observations before fold splitting · 1103 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/500 | 162/603 | 0.0% | 26.9% | 0.000 | 0.453 | 0.366 |
| Smaller decision tree | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.453 | 0.333 |
| Inactivity alone | 419/500 | 24/603 | 83.8% | 4.0% | 0.889 | 0.955 | 0.973 |
| Balance alone | 378/500 | 55/603 | 75.6% | 9.1% | 0.810 | 0.822 | 0.931 |
| Logistic, balance alone | 0/500 | 71/603 | 0.0% | 11.8% | 0.000 | 0.284 | 0.069 |
| Logistic, inactivity + balance | 0/500 | 39/603 | 0.0% | 6.5% | 0.000 | 0.304 | 0.171 |
| Logistic, all 14 predictors | 0/500 | 35/603 | 0.0% | 5.8% | 0.000 | 0.354 | 0.351 |
| Logistic, without time since last activity | 0/500 | 38/603 | 0.0% | 6.3% | 0.000 | 0.352 | 0.345 |
| Logistic, without activity timing | 0/500 | 44/603 | 0.0% | 7.3% | 0.000 | 0.345 | 0.320 |
| Logistic, without timing and counts | 0/500 | 48/603 | 0.0% | 8.0% | 0.000 | 0.329 | 0.267 |
| Random forest | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.592 | 0.569 |
| Histogram gradient boosting | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.635 | 0.601 |
| Gaussian naive Bayes | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.389 | 0.444 |
| RBF support vector machine | 0/500 | 5/603 | 0.0% | 0.8% | 0.000 | 0.335 | 0.298 |

### BTCPay to CryptoBilis

**External** · 48 training observations before fold splitting · 296 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 6/122 | 49/174 | 4.9% | 28.2% | 0.068 | 0.397 | 0.384 |
| Smaller decision tree | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.402 | 0.354 |
| Inactivity alone | 20/122 | 4/174 | 16.4% | 2.3% | 0.274 | 0.854 | 0.956 |
| Balance alone | 40/122 | 14/174 | 32.8% | 8.0% | 0.455 | 0.755 | 0.855 |
| Logistic, balance alone | 0/122 | 21/174 | 0.0% | 12.1% | 0.000 | 0.263 | 0.145 |
| Logistic, inactivity + balance | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.292 | 0.270 |
| Logistic, all 14 predictors | 0/122 | 16/174 | 0.0% | 9.2% | 0.000 | 0.337 | 0.415 |
| Logistic, without time since last activity | 0/122 | 17/174 | 0.0% | 9.8% | 0.000 | 0.332 | 0.401 |
| Logistic, without activity timing | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.325 | 0.381 |
| Logistic, without timing and counts | 0/122 | 19/174 | 0.0% | 10.9% | 0.000 | 0.322 | 0.371 |
| Random forest | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.459 | 0.588 |
| Histogram gradient boosting | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.474 | 0.548 |
| Gaussian naive Bayes | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.382 | 0.506 |
| RBF support vector machine | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.332 | 0.391 |

### BTCPay to BTCPay

**Internal** · 48 training observations before fold splitting · 48 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.333 | 0.500 |
| Smaller decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.458 | 0.708 |
| Inactivity alone | 4/16 | 2/32 | 25.0% | 6.2% | 0.364 | 0.536 | 0.674 |
| Balance alone | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.544 | 0.715 |
| Logistic, inactivity + balance | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.586 | 0.736 |
| Logistic, all 14 predictors | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.609 | 0.773 |
| Logistic, without time since last activity | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.605 | 0.773 |
| Logistic, without activity timing | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.635 | 0.797 |
| Logistic, without timing and counts | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.613 | 0.770 |
| Random forest | 5/16 | 5/32 | 31.2% | 15.6% | 0.385 | 0.513 | 0.767 |
| Histogram gradient boosting | 0/16 | 4/32 | 0.0% | 12.5% | 0.000 | 0.485 | 0.737 |
| Gaussian naive Bayes | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.578 | 0.729 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.481 | 0.719 |

### BTCPay to Coldcard and CryptoBilis

**External** · 48 training observations before fold splitting · 1399 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 6/622 | 211/777 | 1.0% | 27.2% | 0.014 | 0.441 | 0.369 |
| Smaller decision tree | 0/622 | 0/777 | 0.0% | 0.0% | 0.000 | 0.440 | 0.337 |
| Inactivity alone | 439/622 | 28/777 | 70.6% | 3.6% | 0.806 | 0.929 | 0.966 |
| Balance alone | 418/622 | 69/777 | 67.2% | 8.9% | 0.754 | 0.812 | 0.917 |
| Logistic, balance alone | 0/622 | 92/777 | 0.0% | 11.8% | 0.000 | 0.278 | 0.083 |
| Logistic, inactivity + balance | 0/622 | 57/777 | 0.0% | 7.3% | 0.000 | 0.298 | 0.188 |
| Logistic, all 14 predictors | 0/622 | 51/777 | 0.0% | 6.6% | 0.000 | 0.347 | 0.362 |
| Logistic, without time since last activity | 0/622 | 55/777 | 0.0% | 7.1% | 0.000 | 0.345 | 0.354 |
| Logistic, without activity timing | 0/622 | 62/777 | 0.0% | 8.0% | 0.000 | 0.338 | 0.331 |
| Logistic, without timing and counts | 0/622 | 67/777 | 0.0% | 8.6% | 0.000 | 0.325 | 0.288 |
| Random forest | 0/622 | 0/777 | 0.0% | 0.0% | 0.000 | 0.548 | 0.572 |
| Histogram gradient boosting | 0/622 | 0/777 | 0.0% | 0.0% | 0.000 | 0.590 | 0.586 |
| Gaussian naive Bayes | 0/622 | 0/777 | 0.0% | 0.0% | 0.000 | 0.383 | 0.454 |
| RBF support vector machine | 0/622 | 5/777 | 0.0% | 0.6% | 0.000 | 0.331 | 0.317 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/500 | 162/603 | 0.0% | 26.9% | 0.000 | 0.453 | 0.366 |
| Smaller decision tree | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.453 | 0.333 |
| Inactivity alone | 419/500 | 24/603 | 83.8% | 4.0% | 0.889 | 0.955 | 0.973 |
| Balance alone | 378/500 | 55/603 | 75.6% | 9.1% | 0.810 | 0.822 | 0.931 |
| Logistic, balance alone | 0/500 | 71/603 | 0.0% | 11.8% | 0.000 | 0.284 | 0.069 |
| Logistic, inactivity + balance | 0/500 | 39/603 | 0.0% | 6.5% | 0.000 | 0.304 | 0.171 |
| Logistic, all 14 predictors | 0/500 | 35/603 | 0.0% | 5.8% | 0.000 | 0.354 | 0.351 |
| Logistic, without time since last activity | 0/500 | 38/603 | 0.0% | 6.3% | 0.000 | 0.352 | 0.345 |
| Logistic, without activity timing | 0/500 | 44/603 | 0.0% | 7.3% | 0.000 | 0.345 | 0.320 |
| Logistic, without timing and counts | 0/500 | 48/603 | 0.0% | 8.0% | 0.000 | 0.329 | 0.267 |
| Random forest | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.592 | 0.569 |
| Histogram gradient boosting | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.635 | 0.601 |
| Gaussian naive Bayes | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.389 | 0.444 |
| RBF support vector machine | 0/500 | 5/603 | 0.0% | 0.8% | 0.000 | 0.335 | 0.298 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 6/122 | 49/174 | 4.9% | 28.2% | 0.068 | 0.397 | 0.384 |
| Smaller decision tree | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.402 | 0.354 |
| Inactivity alone | 20/122 | 4/174 | 16.4% | 2.3% | 0.274 | 0.854 | 0.956 |
| Balance alone | 40/122 | 14/174 | 32.8% | 8.0% | 0.455 | 0.755 | 0.855 |
| Logistic, balance alone | 0/122 | 21/174 | 0.0% | 12.1% | 0.000 | 0.263 | 0.145 |
| Logistic, inactivity + balance | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.292 | 0.270 |
| Logistic, all 14 predictors | 0/122 | 16/174 | 0.0% | 9.2% | 0.000 | 0.337 | 0.415 |
| Logistic, without time since last activity | 0/122 | 17/174 | 0.0% | 9.8% | 0.000 | 0.332 | 0.401 |
| Logistic, without activity timing | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.325 | 0.381 |
| Logistic, without timing and counts | 0/122 | 19/174 | 0.0% | 10.9% | 0.000 | 0.322 | 0.371 |
| Random forest | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.459 | 0.588 |
| Histogram gradient boosting | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.474 | 0.548 |
| Gaussian naive Bayes | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.382 | 0.506 |
| RBF support vector machine | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.332 | 0.391 |

</details>

### BTCPay to Coldcard and BTCPay

**Mixed** · 48 training observations before fold splitting · 1151 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/516 | 162/635 | 0.0% | 25.5% | 0.000 | 0.437 | 0.359 |
| Smaller decision tree | 0/516 | 0/635 | 0.0% | 0.0% | 0.000 | 0.439 | 0.343 |
| Inactivity alone | 423/516 | 26/635 | 82.0% | 4.1% | 0.877 | 0.948 | 0.964 |
| Balance alone | 378/516 | 58/635 | 73.3% | 9.1% | 0.794 | 0.811 | 0.912 |
| Logistic, balance alone | 2/516 | 72/635 | 0.4% | 11.3% | 0.007 | 0.281 | 0.089 |
| Logistic, inactivity + balance | 2/516 | 41/635 | 0.4% | 6.5% | 0.007 | 0.300 | 0.184 |
| Logistic, all 14 predictors | 2/516 | 37/635 | 0.4% | 5.8% | 0.007 | 0.352 | 0.365 |
| Logistic, without time since last activity | 2/516 | 40/635 | 0.4% | 6.3% | 0.007 | 0.349 | 0.358 |
| Logistic, without activity timing | 2/516 | 46/635 | 0.4% | 7.2% | 0.007 | 0.343 | 0.336 |
| Logistic, without timing and counts | 2/516 | 49/635 | 0.4% | 7.7% | 0.007 | 0.327 | 0.285 |
| Random forest | 5/516 | 5/635 | 1.0% | 0.8% | 0.019 | 0.573 | 0.571 |
| Histogram gradient boosting | 0/516 | 4/635 | 0.0% | 0.6% | 0.000 | 0.610 | 0.598 |
| Gaussian naive Bayes | 0/516 | 0/635 | 0.0% | 0.0% | 0.000 | 0.392 | 0.454 |
| RBF support vector machine | 1/516 | 8/635 | 0.2% | 1.3% | 0.004 | 0.333 | 0.312 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/500 | 162/603 | 0.0% | 26.9% | 0.000 | 0.453 | 0.366 |
| Smaller decision tree | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.453 | 0.333 |
| Inactivity alone | 419/500 | 24/603 | 83.8% | 4.0% | 0.889 | 0.955 | 0.973 |
| Balance alone | 378/500 | 55/603 | 75.6% | 9.1% | 0.810 | 0.822 | 0.931 |
| Logistic, balance alone | 0/500 | 71/603 | 0.0% | 11.8% | 0.000 | 0.284 | 0.069 |
| Logistic, inactivity + balance | 0/500 | 39/603 | 0.0% | 6.5% | 0.000 | 0.304 | 0.171 |
| Logistic, all 14 predictors | 0/500 | 35/603 | 0.0% | 5.8% | 0.000 | 0.354 | 0.351 |
| Logistic, without time since last activity | 0/500 | 38/603 | 0.0% | 6.3% | 0.000 | 0.352 | 0.345 |
| Logistic, without activity timing | 0/500 | 44/603 | 0.0% | 7.3% | 0.000 | 0.345 | 0.320 |
| Logistic, without timing and counts | 0/500 | 48/603 | 0.0% | 8.0% | 0.000 | 0.329 | 0.267 |
| Random forest | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.592 | 0.569 |
| Histogram gradient boosting | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.635 | 0.601 |
| Gaussian naive Bayes | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.389 | 0.444 |
| RBF support vector machine | 0/500 | 5/603 | 0.0% | 0.8% | 0.000 | 0.335 | 0.298 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.333 | 0.500 |
| Smaller decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.458 | 0.708 |
| Inactivity alone | 4/16 | 2/32 | 25.0% | 6.2% | 0.364 | 0.536 | 0.674 |
| Balance alone | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.544 | 0.715 |
| Logistic, inactivity + balance | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.586 | 0.736 |
| Logistic, all 14 predictors | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.609 | 0.773 |
| Logistic, without time since last activity | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.605 | 0.773 |
| Logistic, without activity timing | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.635 | 0.797 |
| Logistic, without timing and counts | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.613 | 0.770 |
| Random forest | 5/16 | 5/32 | 31.2% | 15.6% | 0.385 | 0.513 | 0.767 |
| Histogram gradient boosting | 0/16 | 4/32 | 0.0% | 12.5% | 0.000 | 0.485 | 0.737 |
| Gaussian naive Bayes | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.578 | 0.729 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.481 | 0.719 |

</details>

### BTCPay to CryptoBilis and BTCPay

**Mixed** · 48 training observations before fold splitting · 344 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 6/138 | 49/206 | 4.3% | 23.8% | 0.062 | 0.367 | 0.373 |
| Smaller decision tree | 0/138 | 0/206 | 0.0% | 0.0% | 0.000 | 0.383 | 0.392 |
| Inactivity alone | 24/138 | 6/206 | 17.4% | 2.9% | 0.286 | 0.803 | 0.915 |
| Balance alone | 40/138 | 17/206 | 29.0% | 8.3% | 0.410 | 0.705 | 0.793 |
| Logistic, balance alone | 2/138 | 22/206 | 1.4% | 10.7% | 0.025 | 0.269 | 0.207 |
| Logistic, inactivity + balance | 2/138 | 20/206 | 1.4% | 9.7% | 0.025 | 0.300 | 0.314 |
| Logistic, all 14 predictors | 2/138 | 18/206 | 1.4% | 8.7% | 0.025 | 0.350 | 0.461 |
| Logistic, without time since last activity | 2/138 | 19/206 | 1.4% | 9.2% | 0.025 | 0.344 | 0.448 |
| Logistic, without activity timing | 2/138 | 20/206 | 1.4% | 9.7% | 0.025 | 0.337 | 0.432 |
| Logistic, without timing and counts | 2/138 | 20/206 | 1.4% | 9.7% | 0.025 | 0.333 | 0.419 |
| Random forest | 5/138 | 5/206 | 3.6% | 2.4% | 0.068 | 0.445 | 0.602 |
| Histogram gradient boosting | 0/138 | 4/206 | 0.0% | 1.9% | 0.000 | 0.448 | 0.560 |
| Gaussian naive Bayes | 0/138 | 0/206 | 0.0% | 0.0% | 0.000 | 0.407 | 0.537 |
| RBF support vector machine | 1/138 | 3/206 | 0.7% | 1.5% | 0.014 | 0.349 | 0.433 |

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 6/122 | 49/174 | 4.9% | 28.2% | 0.068 | 0.397 | 0.384 |
| Smaller decision tree | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.402 | 0.354 |
| Inactivity alone | 20/122 | 4/174 | 16.4% | 2.3% | 0.274 | 0.854 | 0.956 |
| Balance alone | 40/122 | 14/174 | 32.8% | 8.0% | 0.455 | 0.755 | 0.855 |
| Logistic, balance alone | 0/122 | 21/174 | 0.0% | 12.1% | 0.000 | 0.263 | 0.145 |
| Logistic, inactivity + balance | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.292 | 0.270 |
| Logistic, all 14 predictors | 0/122 | 16/174 | 0.0% | 9.2% | 0.000 | 0.337 | 0.415 |
| Logistic, without time since last activity | 0/122 | 17/174 | 0.0% | 9.8% | 0.000 | 0.332 | 0.401 |
| Logistic, without activity timing | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.325 | 0.381 |
| Logistic, without timing and counts | 0/122 | 19/174 | 0.0% | 10.9% | 0.000 | 0.322 | 0.371 |
| Random forest | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.459 | 0.588 |
| Histogram gradient boosting | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.474 | 0.548 |
| Gaussian naive Bayes | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.382 | 0.506 |
| RBF support vector machine | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.332 | 0.391 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.333 | 0.500 |
| Smaller decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.458 | 0.708 |
| Inactivity alone | 4/16 | 2/32 | 25.0% | 6.2% | 0.364 | 0.536 | 0.674 |
| Balance alone | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.544 | 0.715 |
| Logistic, inactivity + balance | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.586 | 0.736 |
| Logistic, all 14 predictors | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.609 | 0.773 |
| Logistic, without time since last activity | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.605 | 0.773 |
| Logistic, without activity timing | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.635 | 0.797 |
| Logistic, without timing and counts | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.613 | 0.770 |
| Random forest | 5/16 | 5/32 | 31.2% | 15.6% | 0.385 | 0.513 | 0.767 |
| Histogram gradient boosting | 0/16 | 4/32 | 0.0% | 12.5% | 0.000 | 0.485 | 0.737 |
| Gaussian naive Bayes | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.578 | 0.729 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.481 | 0.719 |

</details>

### BTCPay to Coldcard and CryptoBilis and BTCPay

**Mixed** · 48 training observations before fold splitting · 1447 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 6/638 | 211/809 | 0.9% | 26.1% | 0.014 | 0.428 | 0.364 |
| Smaller decision tree | 0/638 | 0/809 | 0.0% | 0.0% | 0.000 | 0.430 | 0.345 |
| Inactivity alone | 443/638 | 30/809 | 69.4% | 3.7% | 0.797 | 0.922 | 0.958 |
| Balance alone | 418/638 | 72/809 | 65.5% | 8.9% | 0.741 | 0.802 | 0.902 |
| Logistic, balance alone | 2/638 | 93/809 | 0.3% | 11.5% | 0.005 | 0.276 | 0.099 |
| Logistic, inactivity + balance | 2/638 | 59/809 | 0.3% | 7.3% | 0.006 | 0.296 | 0.199 |
| Logistic, all 14 predictors | 2/638 | 53/809 | 0.3% | 6.6% | 0.006 | 0.346 | 0.373 |
| Logistic, without time since last activity | 2/638 | 57/809 | 0.3% | 7.0% | 0.006 | 0.344 | 0.365 |
| Logistic, without activity timing | 2/638 | 64/809 | 0.3% | 7.9% | 0.006 | 0.337 | 0.344 |
| Logistic, without timing and counts | 2/638 | 68/809 | 0.3% | 8.4% | 0.006 | 0.324 | 0.301 |
| Random forest | 5/638 | 5/809 | 0.8% | 0.6% | 0.015 | 0.537 | 0.574 |
| Histogram gradient boosting | 0/638 | 4/809 | 0.0% | 0.5% | 0.000 | 0.572 | 0.586 |
| Gaussian naive Bayes | 0/638 | 0/809 | 0.0% | 0.0% | 0.000 | 0.387 | 0.462 |
| RBF support vector machine | 1/638 | 8/809 | 0.2% | 1.0% | 0.003 | 0.330 | 0.328 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/500 | 162/603 | 0.0% | 26.9% | 0.000 | 0.453 | 0.366 |
| Smaller decision tree | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.453 | 0.333 |
| Inactivity alone | 419/500 | 24/603 | 83.8% | 4.0% | 0.889 | 0.955 | 0.973 |
| Balance alone | 378/500 | 55/603 | 75.6% | 9.1% | 0.810 | 0.822 | 0.931 |
| Logistic, balance alone | 0/500 | 71/603 | 0.0% | 11.8% | 0.000 | 0.284 | 0.069 |
| Logistic, inactivity + balance | 0/500 | 39/603 | 0.0% | 6.5% | 0.000 | 0.304 | 0.171 |
| Logistic, all 14 predictors | 0/500 | 35/603 | 0.0% | 5.8% | 0.000 | 0.354 | 0.351 |
| Logistic, without time since last activity | 0/500 | 38/603 | 0.0% | 6.3% | 0.000 | 0.352 | 0.345 |
| Logistic, without activity timing | 0/500 | 44/603 | 0.0% | 7.3% | 0.000 | 0.345 | 0.320 |
| Logistic, without timing and counts | 0/500 | 48/603 | 0.0% | 8.0% | 0.000 | 0.329 | 0.267 |
| Random forest | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.592 | 0.569 |
| Histogram gradient boosting | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.635 | 0.601 |
| Gaussian naive Bayes | 0/500 | 0/603 | 0.0% | 0.0% | 0.000 | 0.389 | 0.444 |
| RBF support vector machine | 0/500 | 5/603 | 0.0% | 0.8% | 0.000 | 0.335 | 0.298 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 6/122 | 49/174 | 4.9% | 28.2% | 0.068 | 0.397 | 0.384 |
| Smaller decision tree | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.402 | 0.354 |
| Inactivity alone | 20/122 | 4/174 | 16.4% | 2.3% | 0.274 | 0.854 | 0.956 |
| Balance alone | 40/122 | 14/174 | 32.8% | 8.0% | 0.455 | 0.755 | 0.855 |
| Logistic, balance alone | 0/122 | 21/174 | 0.0% | 12.1% | 0.000 | 0.263 | 0.145 |
| Logistic, inactivity + balance | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.292 | 0.270 |
| Logistic, all 14 predictors | 0/122 | 16/174 | 0.0% | 9.2% | 0.000 | 0.337 | 0.415 |
| Logistic, without time since last activity | 0/122 | 17/174 | 0.0% | 9.8% | 0.000 | 0.332 | 0.401 |
| Logistic, without activity timing | 0/122 | 18/174 | 0.0% | 10.3% | 0.000 | 0.325 | 0.381 |
| Logistic, without timing and counts | 0/122 | 19/174 | 0.0% | 10.9% | 0.000 | 0.322 | 0.371 |
| Random forest | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.459 | 0.588 |
| Histogram gradient boosting | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.474 | 0.548 |
| Gaussian naive Bayes | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.382 | 0.506 |
| RBF support vector machine | 0/122 | 0/174 | 0.0% | 0.0% | 0.000 | 0.332 | 0.391 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.333 | 0.500 |
| Smaller decision tree | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.458 | 0.708 |
| Inactivity alone | 4/16 | 2/32 | 25.0% | 6.2% | 0.364 | 0.536 | 0.674 |
| Balance alone | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.544 | 0.715 |
| Logistic, inactivity + balance | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.586 | 0.736 |
| Logistic, all 14 predictors | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.609 | 0.773 |
| Logistic, without time since last activity | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.605 | 0.773 |
| Logistic, without activity timing | 2/16 | 2/32 | 12.5% | 6.2% | 0.200 | 0.635 | 0.797 |
| Logistic, without timing and counts | 2/16 | 1/32 | 12.5% | 3.1% | 0.211 | 0.613 | 0.770 |
| Random forest | 5/16 | 5/32 | 31.2% | 15.6% | 0.385 | 0.513 | 0.767 |
| Histogram gradient boosting | 0/16 | 4/32 | 0.0% | 12.5% | 0.000 | 0.485 | 0.737 |
| Gaussian naive Bayes | 0/16 | 0/32 | 0.0% | 0.0% | 0.000 | 0.578 | 0.729 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.481 | 0.719 |

</details>

## Training on Coldcard and CryptoBilis

### Coldcard and CryptoBilis to Coldcard

**Internal** · 1800 training observations before fold splitting · 1471 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 62/971 | 99.6% | 6.4% | 0.940 | 0.967 | 0.990 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.949 | 0.984 |
| Inactivity alone | 469/500 | 54/971 | 93.8% | 5.6% | 0.917 | 0.955 | 0.983 |
| Balance alone | 224/500 | 48/971 | 44.8% | 4.9% | 0.580 | 0.792 | 0.946 |
| Logistic, balance alone | 236/500 | 49/971 | 47.2% | 5.0% | 0.601 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 58/971 | 100.0% | 6.0% | 0.945 | 0.993 | 0.997 |
| Logistic, all 14 predictors | 499/500 | 59/971 | 99.8% | 6.1% | 0.943 | 0.993 | 0.997 |
| Logistic, without time since last activity | 497/500 | 57/971 | 99.4% | 5.9% | 0.943 | 0.993 | 0.997 |
| Logistic, without activity timing | 470/500 | 51/971 | 94.0% | 5.3% | 0.921 | 0.870 | 0.970 |
| Logistic, without timing and counts | 471/500 | 50/971 | 94.2% | 5.1% | 0.923 | 0.870 | 0.969 |
| Random forest | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.984 | 0.997 |
| Histogram gradient boosting | 499/500 | 60/971 | 99.8% | 6.2% | 0.942 | 0.994 | 0.998 |
| Gaussian naive Bayes | 467/500 | 69/971 | 93.4% | 7.1% | 0.902 | 0.943 | 0.965 |
| RBF support vector machine | 496/500 | 57/971 | 99.2% | 5.9% | 0.942 | 0.989 | 0.996 |

### Coldcard and CryptoBilis to CryptoBilis

**Internal** · 1800 training observations before fold splitting · 329 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.916 | 0.966 |
| Smaller decision tree | 90/122 | 4/207 | 73.8% | 1.9% | 0.833 | 0.932 | 0.967 |
| Inactivity alone | 68/122 | 8/207 | 55.7% | 3.9% | 0.687 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.740 | 0.865 |
| Logistic, inactivity + balance | 101/122 | 7/207 | 82.8% | 3.4% | 0.878 | 0.958 | 0.979 |
| Logistic, all 14 predictors | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.960 | 0.980 |
| Logistic, without time since last activity | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.959 | 0.979 |
| Logistic, without activity timing | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.824 | 0.916 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.823 | 0.915 |
| Random forest | 107/122 | 4/207 | 87.7% | 1.9% | 0.918 | 0.961 | 0.985 |
| Histogram gradient boosting | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.973 | 0.988 |
| Gaussian naive Bayes | 112/122 | 15/207 | 91.8% | 7.2% | 0.900 | 0.942 | 0.967 |
| RBF support vector machine | 107/122 | 7/207 | 87.7% | 3.4% | 0.907 | 0.966 | 0.980 |

### Coldcard and CryptoBilis to BTCPay

**External** · 1800 training observations before fold splitting · 38 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.429 | 0.527 |
| Smaller decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.456 | 0.550 |
| Inactivity alone | 4/16 | 5/22 | 25.0% | 22.7% | 0.320 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.487 | 0.580 |
| Logistic, all 14 predictors | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.482 | 0.591 |
| Logistic, without time since last activity | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.471 | 0.565 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.407 | 0.491 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.405 | 0.486 |
| Random forest | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.422 | 0.480 |
| Histogram gradient boosting | 2/16 | 5/22 | 12.5% | 22.7% | 0.174 | 0.445 | 0.554 |
| Gaussian naive Bayes | 2/16 | 4/22 | 12.5% | 18.2% | 0.182 | 0.464 | 0.577 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.428 | 0.491 |

### Coldcard and CryptoBilis to Coldcard and CryptoBilis

**Internal** · 1800 training observations before fold splitting · 1800 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 600/622 | 69/1178 | 96.5% | 5.9% | 0.930 | 0.956 | 0.984 |
| Smaller decision tree | 588/622 | 31/1178 | 94.5% | 2.6% | 0.948 | 0.944 | 0.980 |
| Inactivity alone | 537/622 | 62/1178 | 86.3% | 5.3% | 0.880 | 0.928 | 0.977 |
| Balance alone | 252/622 | 58/1178 | 40.5% | 4.9% | 0.541 | 0.782 | 0.931 |
| Logistic, balance alone | 265/622 | 59/1178 | 42.6% | 5.0% | 0.560 | 0.779 | 0.930 |
| Logistic, inactivity + balance | 601/622 | 65/1178 | 96.6% | 5.5% | 0.933 | 0.983 | 0.991 |
| Logistic, all 14 predictors | 601/622 | 67/1178 | 96.6% | 5.7% | 0.932 | 0.984 | 0.992 |
| Logistic, without time since last activity | 599/622 | 65/1178 | 96.3% | 5.5% | 0.932 | 0.984 | 0.992 |
| Logistic, without activity timing | 531/622 | 61/1178 | 85.4% | 5.2% | 0.875 | 0.863 | 0.961 |
| Logistic, without timing and counts | 534/622 | 60/1178 | 85.9% | 5.1% | 0.878 | 0.863 | 0.961 |
| Random forest | 604/622 | 62/1178 | 97.1% | 5.3% | 0.938 | 0.980 | 0.994 |
| Histogram gradient boosting | 609/622 | 67/1178 | 97.9% | 5.7% | 0.938 | 0.989 | 0.995 |
| Gaussian naive Bayes | 579/622 | 84/1178 | 93.1% | 7.1% | 0.901 | 0.941 | 0.965 |
| RBF support vector machine | 603/622 | 64/1178 | 96.9% | 5.4% | 0.936 | 0.982 | 0.992 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 62/971 | 99.6% | 6.4% | 0.940 | 0.967 | 0.990 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.949 | 0.984 |
| Inactivity alone | 469/500 | 54/971 | 93.8% | 5.6% | 0.917 | 0.955 | 0.983 |
| Balance alone | 224/500 | 48/971 | 44.8% | 4.9% | 0.580 | 0.792 | 0.946 |
| Logistic, balance alone | 236/500 | 49/971 | 47.2% | 5.0% | 0.601 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 58/971 | 100.0% | 6.0% | 0.945 | 0.993 | 0.997 |
| Logistic, all 14 predictors | 499/500 | 59/971 | 99.8% | 6.1% | 0.943 | 0.993 | 0.997 |
| Logistic, without time since last activity | 497/500 | 57/971 | 99.4% | 5.9% | 0.943 | 0.993 | 0.997 |
| Logistic, without activity timing | 470/500 | 51/971 | 94.0% | 5.3% | 0.921 | 0.870 | 0.970 |
| Logistic, without timing and counts | 471/500 | 50/971 | 94.2% | 5.1% | 0.923 | 0.870 | 0.969 |
| Random forest | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.984 | 0.997 |
| Histogram gradient boosting | 499/500 | 60/971 | 99.8% | 6.2% | 0.942 | 0.994 | 0.998 |
| Gaussian naive Bayes | 467/500 | 69/971 | 93.4% | 7.1% | 0.902 | 0.943 | 0.965 |
| RBF support vector machine | 496/500 | 57/971 | 99.2% | 5.9% | 0.942 | 0.989 | 0.996 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.916 | 0.966 |
| Smaller decision tree | 90/122 | 4/207 | 73.8% | 1.9% | 0.833 | 0.932 | 0.967 |
| Inactivity alone | 68/122 | 8/207 | 55.7% | 3.9% | 0.687 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.740 | 0.865 |
| Logistic, inactivity + balance | 101/122 | 7/207 | 82.8% | 3.4% | 0.878 | 0.958 | 0.979 |
| Logistic, all 14 predictors | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.960 | 0.980 |
| Logistic, without time since last activity | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.959 | 0.979 |
| Logistic, without activity timing | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.824 | 0.916 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.823 | 0.915 |
| Random forest | 107/122 | 4/207 | 87.7% | 1.9% | 0.918 | 0.961 | 0.985 |
| Histogram gradient boosting | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.973 | 0.988 |
| Gaussian naive Bayes | 112/122 | 15/207 | 91.8% | 7.2% | 0.900 | 0.942 | 0.967 |
| RBF support vector machine | 107/122 | 7/207 | 87.7% | 3.4% | 0.907 | 0.966 | 0.980 |

</details>

### Coldcard and CryptoBilis to Coldcard and BTCPay

**Mixed** · 1800 training observations before fold splitting · 1509 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/516 | 63/993 | 96.5% | 6.3% | 0.925 | 0.953 | 0.979 |
| Smaller decision tree | 498/516 | 28/993 | 96.5% | 2.8% | 0.956 | 0.937 | 0.968 |
| Inactivity alone | 473/516 | 59/993 | 91.7% | 5.9% | 0.903 | 0.947 | 0.975 |
| Balance alone | 224/516 | 48/993 | 43.4% | 4.8% | 0.569 | 0.780 | 0.925 |
| Logistic, balance alone | 236/516 | 49/993 | 45.7% | 4.9% | 0.589 | 0.778 | 0.925 |
| Logistic, inactivity + balance | 501/516 | 60/993 | 97.1% | 6.0% | 0.930 | 0.982 | 0.985 |
| Logistic, all 14 predictors | 500/516 | 61/993 | 96.9% | 6.1% | 0.929 | 0.984 | 0.988 |
| Logistic, without time since last activity | 498/516 | 59/993 | 96.5% | 5.9% | 0.928 | 0.983 | 0.987 |
| Logistic, without activity timing | 470/516 | 52/993 | 91.1% | 5.2% | 0.906 | 0.859 | 0.958 |
| Logistic, without timing and counts | 471/516 | 51/993 | 91.3% | 5.1% | 0.908 | 0.859 | 0.956 |
| Random forest | 497/516 | 59/993 | 96.3% | 5.9% | 0.927 | 0.973 | 0.985 |
| Histogram gradient boosting | 501/516 | 65/993 | 97.1% | 6.5% | 0.926 | 0.983 | 0.984 |
| Gaussian naive Bayes | 469/516 | 73/993 | 90.9% | 7.4% | 0.887 | 0.934 | 0.959 |
| RBF support vector machine | 496/516 | 58/993 | 96.1% | 5.8% | 0.927 | 0.975 | 0.979 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 62/971 | 99.6% | 6.4% | 0.940 | 0.967 | 0.990 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.949 | 0.984 |
| Inactivity alone | 469/500 | 54/971 | 93.8% | 5.6% | 0.917 | 0.955 | 0.983 |
| Balance alone | 224/500 | 48/971 | 44.8% | 4.9% | 0.580 | 0.792 | 0.946 |
| Logistic, balance alone | 236/500 | 49/971 | 47.2% | 5.0% | 0.601 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 58/971 | 100.0% | 6.0% | 0.945 | 0.993 | 0.997 |
| Logistic, all 14 predictors | 499/500 | 59/971 | 99.8% | 6.1% | 0.943 | 0.993 | 0.997 |
| Logistic, without time since last activity | 497/500 | 57/971 | 99.4% | 5.9% | 0.943 | 0.993 | 0.997 |
| Logistic, without activity timing | 470/500 | 51/971 | 94.0% | 5.3% | 0.921 | 0.870 | 0.970 |
| Logistic, without timing and counts | 471/500 | 50/971 | 94.2% | 5.1% | 0.923 | 0.870 | 0.969 |
| Random forest | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.984 | 0.997 |
| Histogram gradient boosting | 499/500 | 60/971 | 99.8% | 6.2% | 0.942 | 0.994 | 0.998 |
| Gaussian naive Bayes | 467/500 | 69/971 | 93.4% | 7.1% | 0.902 | 0.943 | 0.965 |
| RBF support vector machine | 496/500 | 57/971 | 99.2% | 5.9% | 0.942 | 0.989 | 0.996 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.429 | 0.527 |
| Smaller decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.456 | 0.550 |
| Inactivity alone | 4/16 | 5/22 | 25.0% | 22.7% | 0.320 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.487 | 0.580 |
| Logistic, all 14 predictors | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.482 | 0.591 |
| Logistic, without time since last activity | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.471 | 0.565 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.407 | 0.491 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.405 | 0.486 |
| Random forest | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.422 | 0.480 |
| Histogram gradient boosting | 2/16 | 5/22 | 12.5% | 22.7% | 0.174 | 0.445 | 0.554 |
| Gaussian naive Bayes | 2/16 | 4/22 | 12.5% | 18.2% | 0.182 | 0.464 | 0.577 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.428 | 0.491 |

</details>

### Coldcard and CryptoBilis to CryptoBilis and BTCPay

**Mixed** · 1800 training observations before fold splitting · 367 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/138 | 8/229 | 73.9% | 3.5% | 0.823 | 0.866 | 0.924 |
| Smaller decision tree | 90/138 | 5/229 | 65.2% | 2.2% | 0.773 | 0.889 | 0.914 |
| Inactivity alone | 72/138 | 13/229 | 52.2% | 5.7% | 0.646 | 0.803 | 0.922 |
| Balance alone | 28/138 | 10/229 | 20.3% | 4.4% | 0.318 | 0.707 | 0.804 |
| Logistic, balance alone | 29/138 | 10/229 | 21.0% | 4.4% | 0.328 | 0.699 | 0.801 |
| Logistic, inactivity + balance | 102/138 | 9/229 | 73.9% | 3.9% | 0.819 | 0.916 | 0.934 |
| Logistic, all 14 predictors | 103/138 | 10/229 | 74.6% | 4.4% | 0.821 | 0.919 | 0.941 |
| Logistic, without time since last activity | 103/138 | 10/229 | 74.6% | 4.4% | 0.821 | 0.916 | 0.936 |
| Logistic, without activity timing | 61/138 | 11/229 | 44.2% | 4.8% | 0.581 | 0.784 | 0.872 |
| Logistic, without timing and counts | 63/138 | 11/229 | 45.7% | 4.8% | 0.594 | 0.782 | 0.867 |
| Random forest | 107/138 | 5/229 | 77.5% | 2.2% | 0.856 | 0.907 | 0.934 |
| Histogram gradient boosting | 112/138 | 12/229 | 81.2% | 5.2% | 0.855 | 0.925 | 0.933 |
| Gaussian naive Bayes | 114/138 | 19/229 | 82.6% | 8.3% | 0.841 | 0.901 | 0.937 |
| RBF support vector machine | 107/138 | 8/229 | 77.5% | 3.5% | 0.846 | 0.910 | 0.918 |

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.916 | 0.966 |
| Smaller decision tree | 90/122 | 4/207 | 73.8% | 1.9% | 0.833 | 0.932 | 0.967 |
| Inactivity alone | 68/122 | 8/207 | 55.7% | 3.9% | 0.687 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.740 | 0.865 |
| Logistic, inactivity + balance | 101/122 | 7/207 | 82.8% | 3.4% | 0.878 | 0.958 | 0.979 |
| Logistic, all 14 predictors | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.960 | 0.980 |
| Logistic, without time since last activity | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.959 | 0.979 |
| Logistic, without activity timing | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.824 | 0.916 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.823 | 0.915 |
| Random forest | 107/122 | 4/207 | 87.7% | 1.9% | 0.918 | 0.961 | 0.985 |
| Histogram gradient boosting | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.973 | 0.988 |
| Gaussian naive Bayes | 112/122 | 15/207 | 91.8% | 7.2% | 0.900 | 0.942 | 0.967 |
| RBF support vector machine | 107/122 | 7/207 | 87.7% | 3.4% | 0.907 | 0.966 | 0.980 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.429 | 0.527 |
| Smaller decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.456 | 0.550 |
| Inactivity alone | 4/16 | 5/22 | 25.0% | 22.7% | 0.320 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.487 | 0.580 |
| Logistic, all 14 predictors | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.482 | 0.591 |
| Logistic, without time since last activity | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.471 | 0.565 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.407 | 0.491 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.405 | 0.486 |
| Random forest | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.422 | 0.480 |
| Histogram gradient boosting | 2/16 | 5/22 | 12.5% | 22.7% | 0.174 | 0.445 | 0.554 |
| Gaussian naive Bayes | 2/16 | 4/22 | 12.5% | 18.2% | 0.182 | 0.464 | 0.577 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.428 | 0.491 |

</details>

### Coldcard and CryptoBilis to Coldcard and CryptoBilis and BTCPay

**Mixed** · 1800 training observations before fold splitting · 1838 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 600/638 | 70/1200 | 94.0% | 5.8% | 0.917 | 0.945 | 0.975 |
| Smaller decision tree | 588/638 | 32/1200 | 92.2% | 2.7% | 0.935 | 0.935 | 0.967 |
| Inactivity alone | 541/638 | 67/1200 | 84.8% | 5.6% | 0.868 | 0.922 | 0.970 |
| Balance alone | 252/638 | 58/1200 | 39.5% | 4.8% | 0.532 | 0.772 | 0.914 |
| Logistic, balance alone | 265/638 | 59/1200 | 41.5% | 4.9% | 0.551 | 0.769 | 0.913 |
| Logistic, inactivity + balance | 602/638 | 67/1200 | 94.4% | 5.6% | 0.921 | 0.974 | 0.982 |
| Logistic, all 14 predictors | 602/638 | 69/1200 | 94.4% | 5.8% | 0.920 | 0.976 | 0.985 |
| Logistic, without time since last activity | 600/638 | 67/1200 | 94.0% | 5.6% | 0.920 | 0.975 | 0.984 |
| Logistic, without activity timing | 531/638 | 62/1200 | 83.2% | 5.2% | 0.863 | 0.855 | 0.952 |
| Logistic, without timing and counts | 534/638 | 61/1200 | 83.7% | 5.1% | 0.866 | 0.854 | 0.950 |
| Random forest | 604/638 | 63/1200 | 94.7% | 5.2% | 0.926 | 0.971 | 0.984 |
| Histogram gradient boosting | 611/638 | 72/1200 | 95.8% | 6.0% | 0.925 | 0.980 | 0.983 |
| Gaussian naive Bayes | 581/638 | 88/1200 | 91.1% | 7.3% | 0.889 | 0.934 | 0.960 |
| RBF support vector machine | 603/638 | 65/1200 | 94.5% | 5.4% | 0.923 | 0.971 | 0.978 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 62/971 | 99.6% | 6.4% | 0.940 | 0.967 | 0.990 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.949 | 0.984 |
| Inactivity alone | 469/500 | 54/971 | 93.8% | 5.6% | 0.917 | 0.955 | 0.983 |
| Balance alone | 224/500 | 48/971 | 44.8% | 4.9% | 0.580 | 0.792 | 0.946 |
| Logistic, balance alone | 236/500 | 49/971 | 47.2% | 5.0% | 0.601 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 500/500 | 58/971 | 100.0% | 6.0% | 0.945 | 0.993 | 0.997 |
| Logistic, all 14 predictors | 499/500 | 59/971 | 99.8% | 6.1% | 0.943 | 0.993 | 0.997 |
| Logistic, without time since last activity | 497/500 | 57/971 | 99.4% | 5.9% | 0.943 | 0.993 | 0.997 |
| Logistic, without activity timing | 470/500 | 51/971 | 94.0% | 5.3% | 0.921 | 0.870 | 0.970 |
| Logistic, without timing and counts | 471/500 | 50/971 | 94.2% | 5.1% | 0.923 | 0.870 | 0.969 |
| Random forest | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.984 | 0.997 |
| Histogram gradient boosting | 499/500 | 60/971 | 99.8% | 6.2% | 0.942 | 0.994 | 0.998 |
| Gaussian naive Bayes | 467/500 | 69/971 | 93.4% | 7.1% | 0.902 | 0.943 | 0.965 |
| RBF support vector machine | 496/500 | 57/971 | 99.2% | 5.9% | 0.942 | 0.989 | 0.996 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 102/122 | 7/207 | 83.6% | 3.4% | 0.883 | 0.916 | 0.966 |
| Smaller decision tree | 90/122 | 4/207 | 73.8% | 1.9% | 0.833 | 0.932 | 0.967 |
| Inactivity alone | 68/122 | 8/207 | 55.7% | 3.9% | 0.687 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.740 | 0.865 |
| Logistic, inactivity + balance | 101/122 | 7/207 | 82.8% | 3.4% | 0.878 | 0.958 | 0.979 |
| Logistic, all 14 predictors | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.960 | 0.980 |
| Logistic, without time since last activity | 102/122 | 8/207 | 83.6% | 3.9% | 0.879 | 0.959 | 0.979 |
| Logistic, without activity timing | 61/122 | 10/207 | 50.0% | 4.8% | 0.632 | 0.824 | 0.916 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.823 | 0.915 |
| Random forest | 107/122 | 4/207 | 87.7% | 1.9% | 0.918 | 0.961 | 0.985 |
| Histogram gradient boosting | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.973 | 0.988 |
| Gaussian naive Bayes | 112/122 | 15/207 | 91.8% | 7.2% | 0.900 | 0.942 | 0.967 |
| RBF support vector machine | 107/122 | 7/207 | 87.7% | 3.4% | 0.907 | 0.966 | 0.980 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.429 | 0.527 |
| Smaller decision tree | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.456 | 0.550 |
| Inactivity alone | 4/16 | 5/22 | 25.0% | 22.7% | 0.320 | 0.571 | 0.628 |
| Balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, balance alone | 0/16 | 0/22 | 0.0% | 0.0% | 0.000 | 0.355 | 0.375 |
| Logistic, inactivity + balance | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.487 | 0.580 |
| Logistic, all 14 predictors | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.482 | 0.591 |
| Logistic, without time since last activity | 1/16 | 2/22 | 6.2% | 9.1% | 0.105 | 0.471 | 0.565 |
| Logistic, without activity timing | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.407 | 0.491 |
| Logistic, without timing and counts | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.405 | 0.486 |
| Random forest | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.422 | 0.480 |
| Histogram gradient boosting | 2/16 | 5/22 | 12.5% | 22.7% | 0.174 | 0.445 | 0.554 |
| Gaussian naive Bayes | 2/16 | 4/22 | 12.5% | 18.2% | 0.182 | 0.464 | 0.577 |
| RBF support vector machine | 0/16 | 1/22 | 0.0% | 4.5% | 0.000 | 0.428 | 0.491 |

</details>

## Training on Coldcard and BTCPay

### Coldcard and BTCPay to Coldcard

**Internal** · 1519 training observations before fold splitting · 1471 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 496/500 | 33/971 | 99.2% | 3.4% | 0.964 | 0.987 | 0.996 |
| Smaller decision tree | 496/500 | 36/971 | 99.2% | 3.7% | 0.961 | 0.979 | 0.993 |
| Inactivity alone | 463/500 | 50/971 | 92.6% | 5.1% | 0.914 | 0.955 | 0.983 |
| Balance alone | 223/500 | 48/971 | 44.6% | 4.9% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 46/971 | 99.8% | 4.7% | 0.955 | 0.989 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 52/971 | 99.8% | 5.4% | 0.950 | 0.988 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.990 | 0.995 |
| Logistic, without activity timing | 472/500 | 49/971 | 94.4% | 5.0% | 0.925 | 0.869 | 0.970 |
| Logistic, without timing and counts | 478/500 | 49/971 | 95.6% | 5.0% | 0.931 | 0.870 | 0.969 |
| Random forest | 499/500 | 47/971 | 99.8% | 4.8% | 0.954 | 0.992 | 0.998 |
| Histogram gradient boosting | 498/500 | 45/971 | 99.6% | 4.6% | 0.955 | 0.995 | 0.998 |
| Gaussian naive Bayes | 469/500 | 69/971 | 93.8% | 7.1% | 0.904 | 0.942 | 0.966 |
| RBF support vector machine | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.998 | 0.999 |

### Coldcard and BTCPay to CryptoBilis

**External** · 1519 training observations before fold splitting · 267 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 72/122 | 15/145 | 59.0% | 10.3% | 0.689 | 0.739 | 0.599 |
| Smaller decision tree | 49/122 | 2/145 | 40.2% | 1.4% | 0.566 | 0.862 | 0.909 |
| Inactivity alone | 58/122 | 7/145 | 47.5% | 4.8% | 0.620 | 0.854 | 0.947 |
| Balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 96/122 | 5/145 | 78.7% | 3.4% | 0.861 | 0.965 | 0.975 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.968 | 0.977 |
| Logistic, without time since last activity | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.967 | 0.976 |
| Logistic, without activity timing | 64/122 | 10/145 | 52.5% | 6.9% | 0.653 | 0.832 | 0.888 |
| Logistic, without timing and counts | 67/122 | 10/145 | 54.9% | 6.9% | 0.673 | 0.831 | 0.886 |
| Random forest | 57/122 | 5/145 | 46.7% | 3.4% | 0.620 | 0.912 | 0.932 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.874 | 0.879 |
| Gaussian naive Bayes | 111/122 | 4/145 | 91.0% | 2.8% | 0.937 | 0.971 | 0.979 |
| RBF support vector machine | 104/122 | 10/145 | 85.2% | 6.9% | 0.881 | 0.953 | 0.959 |

### Coldcard and BTCPay to BTCPay

**Internal** · 1519 training observations before fold splitting · 48 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 7/16 | 6/32 | 43.8% | 18.8% | 0.483 | 0.458 | 0.715 |
| Smaller decision tree | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.409 | 0.635 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.271 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.437 | 0.572 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.469 | 0.660 |
| Logistic, without time since last activity | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.454 | 0.633 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.368 | 0.588 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.361 | 0.561 |
| Random forest | 4/16 | 5/32 | 25.0% | 15.6% | 0.320 | 0.485 | 0.709 |
| Histogram gradient boosting | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.483 | 0.740 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.462 | 0.715 |
| RBF support vector machine | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.309 | 0.420 |

### Coldcard and BTCPay to Coldcard and CryptoBilis

**Mixed** · 1519 training observations before fold splitting · 1738 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 568/622 | 48/1116 | 91.3% | 4.3% | 0.918 | 0.935 | 0.932 |
| Smaller decision tree | 545/622 | 38/1116 | 87.6% | 3.4% | 0.905 | 0.963 | 0.983 |
| Inactivity alone | 521/622 | 57/1116 | 83.8% | 5.1% | 0.868 | 0.928 | 0.976 |
| Balance alone | 249/622 | 58/1116 | 40.0% | 5.2% | 0.536 | 0.783 | 0.928 |
| Logistic, balance alone | 264/622 | 59/1116 | 42.4% | 5.3% | 0.559 | 0.781 | 0.927 |
| Logistic, inactivity + balance | 595/622 | 51/1116 | 95.7% | 4.6% | 0.938 | 0.979 | 0.989 |
| Logistic, all 14 predictors | 599/622 | 58/1116 | 96.3% | 5.2% | 0.937 | 0.978 | 0.989 |
| Logistic, without time since last activity | 597/622 | 58/1116 | 96.0% | 5.2% | 0.935 | 0.980 | 0.990 |
| Logistic, without activity timing | 536/622 | 59/1116 | 86.2% | 5.3% | 0.881 | 0.864 | 0.960 |
| Logistic, without timing and counts | 545/622 | 59/1116 | 87.6% | 5.3% | 0.889 | 0.864 | 0.959 |
| Random forest | 556/622 | 52/1116 | 89.4% | 4.7% | 0.904 | 0.973 | 0.984 |
| Histogram gradient boosting | 562/622 | 52/1116 | 90.4% | 4.7% | 0.909 | 0.972 | 0.980 |
| Gaussian naive Bayes | 580/622 | 73/1116 | 93.2% | 6.5% | 0.910 | 0.943 | 0.966 |
| RBF support vector machine | 603/622 | 64/1116 | 96.9% | 5.7% | 0.936 | 0.987 | 0.991 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 496/500 | 33/971 | 99.2% | 3.4% | 0.964 | 0.987 | 0.996 |
| Smaller decision tree | 496/500 | 36/971 | 99.2% | 3.7% | 0.961 | 0.979 | 0.993 |
| Inactivity alone | 463/500 | 50/971 | 92.6% | 5.1% | 0.914 | 0.955 | 0.983 |
| Balance alone | 223/500 | 48/971 | 44.6% | 4.9% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 46/971 | 99.8% | 4.7% | 0.955 | 0.989 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 52/971 | 99.8% | 5.4% | 0.950 | 0.988 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.990 | 0.995 |
| Logistic, without activity timing | 472/500 | 49/971 | 94.4% | 5.0% | 0.925 | 0.869 | 0.970 |
| Logistic, without timing and counts | 478/500 | 49/971 | 95.6% | 5.0% | 0.931 | 0.870 | 0.969 |
| Random forest | 499/500 | 47/971 | 99.8% | 4.8% | 0.954 | 0.992 | 0.998 |
| Histogram gradient boosting | 498/500 | 45/971 | 99.6% | 4.6% | 0.955 | 0.995 | 0.998 |
| Gaussian naive Bayes | 469/500 | 69/971 | 93.8% | 7.1% | 0.904 | 0.942 | 0.966 |
| RBF support vector machine | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.998 | 0.999 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 72/122 | 15/145 | 59.0% | 10.3% | 0.689 | 0.739 | 0.599 |
| Smaller decision tree | 49/122 | 2/145 | 40.2% | 1.4% | 0.566 | 0.862 | 0.909 |
| Inactivity alone | 58/122 | 7/145 | 47.5% | 4.8% | 0.620 | 0.854 | 0.947 |
| Balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 96/122 | 5/145 | 78.7% | 3.4% | 0.861 | 0.965 | 0.975 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.968 | 0.977 |
| Logistic, without time since last activity | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.967 | 0.976 |
| Logistic, without activity timing | 64/122 | 10/145 | 52.5% | 6.9% | 0.653 | 0.832 | 0.888 |
| Logistic, without timing and counts | 67/122 | 10/145 | 54.9% | 6.9% | 0.673 | 0.831 | 0.886 |
| Random forest | 57/122 | 5/145 | 46.7% | 3.4% | 0.620 | 0.912 | 0.932 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.874 | 0.879 |
| Gaussian naive Bayes | 111/122 | 4/145 | 91.0% | 2.8% | 0.937 | 0.971 | 0.979 |
| RBF support vector machine | 104/122 | 10/145 | 85.2% | 6.9% | 0.881 | 0.953 | 0.959 |

</details>

### Coldcard and BTCPay to Coldcard and BTCPay

**Internal** · 1519 training observations before fold splitting · 1519 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 503/516 | 39/1003 | 97.5% | 3.9% | 0.951 | 0.981 | 0.992 |
| Smaller decision tree | 497/516 | 40/1003 | 96.3% | 4.0% | 0.944 | 0.966 | 0.986 |
| Inactivity alone | 467/516 | 56/1003 | 90.5% | 5.6% | 0.899 | 0.947 | 0.975 |
| Balance alone | 223/516 | 49/1003 | 43.2% | 4.9% | 0.566 | 0.777 | 0.925 |
| Logistic, balance alone | 238/516 | 50/1003 | 46.1% | 5.0% | 0.592 | 0.775 | 0.925 |
| Logistic, inactivity + balance | 500/516 | 51/1003 | 96.9% | 5.1% | 0.937 | 0.979 | 0.984 |
| Logistic, all 14 predictors | 500/516 | 56/1003 | 96.9% | 5.6% | 0.933 | 0.979 | 0.987 |
| Logistic, without time since last activity | 498/516 | 55/1003 | 96.5% | 5.5% | 0.932 | 0.980 | 0.987 |
| Logistic, without activity timing | 472/516 | 50/1003 | 91.5% | 5.0% | 0.909 | 0.859 | 0.959 |
| Logistic, without timing and counts | 478/516 | 50/1003 | 92.6% | 5.0% | 0.916 | 0.859 | 0.957 |
| Random forest | 503/516 | 52/1003 | 97.5% | 5.2% | 0.939 | 0.985 | 0.992 |
| Histogram gradient boosting | 503/516 | 51/1003 | 97.5% | 5.1% | 0.940 | 0.990 | 0.995 |
| Gaussian naive Bayes | 471/516 | 75/1003 | 91.3% | 7.5% | 0.887 | 0.933 | 0.959 |
| RBF support vector machine | 500/516 | 56/1003 | 96.9% | 5.6% | 0.933 | 0.983 | 0.982 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 496/500 | 33/971 | 99.2% | 3.4% | 0.964 | 0.987 | 0.996 |
| Smaller decision tree | 496/500 | 36/971 | 99.2% | 3.7% | 0.961 | 0.979 | 0.993 |
| Inactivity alone | 463/500 | 50/971 | 92.6% | 5.1% | 0.914 | 0.955 | 0.983 |
| Balance alone | 223/500 | 48/971 | 44.6% | 4.9% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 46/971 | 99.8% | 4.7% | 0.955 | 0.989 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 52/971 | 99.8% | 5.4% | 0.950 | 0.988 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.990 | 0.995 |
| Logistic, without activity timing | 472/500 | 49/971 | 94.4% | 5.0% | 0.925 | 0.869 | 0.970 |
| Logistic, without timing and counts | 478/500 | 49/971 | 95.6% | 5.0% | 0.931 | 0.870 | 0.969 |
| Random forest | 499/500 | 47/971 | 99.8% | 4.8% | 0.954 | 0.992 | 0.998 |
| Histogram gradient boosting | 498/500 | 45/971 | 99.6% | 4.6% | 0.955 | 0.995 | 0.998 |
| Gaussian naive Bayes | 469/500 | 69/971 | 93.8% | 7.1% | 0.904 | 0.942 | 0.966 |
| RBF support vector machine | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.998 | 0.999 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 7/16 | 6/32 | 43.8% | 18.8% | 0.483 | 0.458 | 0.715 |
| Smaller decision tree | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.409 | 0.635 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.271 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.437 | 0.572 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.469 | 0.660 |
| Logistic, without time since last activity | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.454 | 0.633 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.368 | 0.588 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.361 | 0.561 |
| Random forest | 4/16 | 5/32 | 25.0% | 15.6% | 0.320 | 0.485 | 0.709 |
| Histogram gradient boosting | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.483 | 0.740 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.462 | 0.715 |
| RBF support vector machine | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.309 | 0.420 |

</details>

### Coldcard and BTCPay to CryptoBilis and BTCPay

**Mixed** · 1519 training observations before fold splitting · 315 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 79/138 | 21/177 | 57.2% | 11.9% | 0.664 | 0.720 | 0.623 |
| Smaller decision tree | 50/138 | 6/177 | 36.2% | 3.4% | 0.515 | 0.825 | 0.881 |
| Inactivity alone | 62/138 | 13/177 | 44.9% | 7.3% | 0.582 | 0.805 | 0.906 |
| Balance alone | 26/138 | 11/177 | 18.8% | 6.2% | 0.297 | 0.717 | 0.779 |
| Logistic, balance alone | 26/138 | 11/177 | 18.8% | 6.2% | 0.297 | 0.716 | 0.780 |
| Logistic, inactivity + balance | 97/138 | 10/177 | 70.3% | 5.6% | 0.792 | 0.916 | 0.922 |
| Logistic, all 14 predictors | 101/138 | 10/177 | 73.2% | 5.6% | 0.811 | 0.922 | 0.929 |
| Logistic, without time since last activity | 101/138 | 9/177 | 73.2% | 5.1% | 0.815 | 0.921 | 0.928 |
| Logistic, without activity timing | 64/138 | 11/177 | 46.4% | 6.2% | 0.601 | 0.792 | 0.842 |
| Logistic, without timing and counts | 67/138 | 11/177 | 48.6% | 6.2% | 0.620 | 0.790 | 0.839 |
| Random forest | 61/138 | 10/177 | 44.2% | 5.6% | 0.584 | 0.863 | 0.901 |
| Histogram gradient boosting | 69/138 | 13/177 | 50.0% | 7.3% | 0.627 | 0.835 | 0.862 |
| Gaussian naive Bayes | 113/138 | 10/177 | 81.9% | 5.6% | 0.866 | 0.924 | 0.934 |
| RBF support vector machine | 105/138 | 12/177 | 76.1% | 6.8% | 0.824 | 0.901 | 0.897 |

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 72/122 | 15/145 | 59.0% | 10.3% | 0.689 | 0.739 | 0.599 |
| Smaller decision tree | 49/122 | 2/145 | 40.2% | 1.4% | 0.566 | 0.862 | 0.909 |
| Inactivity alone | 58/122 | 7/145 | 47.5% | 4.8% | 0.620 | 0.854 | 0.947 |
| Balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 96/122 | 5/145 | 78.7% | 3.4% | 0.861 | 0.965 | 0.975 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.968 | 0.977 |
| Logistic, without time since last activity | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.967 | 0.976 |
| Logistic, without activity timing | 64/122 | 10/145 | 52.5% | 6.9% | 0.653 | 0.832 | 0.888 |
| Logistic, without timing and counts | 67/122 | 10/145 | 54.9% | 6.9% | 0.673 | 0.831 | 0.886 |
| Random forest | 57/122 | 5/145 | 46.7% | 3.4% | 0.620 | 0.912 | 0.932 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.874 | 0.879 |
| Gaussian naive Bayes | 111/122 | 4/145 | 91.0% | 2.8% | 0.937 | 0.971 | 0.979 |
| RBF support vector machine | 104/122 | 10/145 | 85.2% | 6.9% | 0.881 | 0.953 | 0.959 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 7/16 | 6/32 | 43.8% | 18.8% | 0.483 | 0.458 | 0.715 |
| Smaller decision tree | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.409 | 0.635 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.271 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.437 | 0.572 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.469 | 0.660 |
| Logistic, without time since last activity | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.454 | 0.633 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.368 | 0.588 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.361 | 0.561 |
| Random forest | 4/16 | 5/32 | 25.0% | 15.6% | 0.320 | 0.485 | 0.709 |
| Histogram gradient boosting | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.483 | 0.740 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.462 | 0.715 |
| RBF support vector machine | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.309 | 0.420 |

</details>

### Coldcard and BTCPay to Coldcard and CryptoBilis and BTCPay

**Mixed** · 1519 training observations before fold splitting · 1786 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 575/638 | 54/1148 | 90.1% | 4.7% | 0.908 | 0.931 | 0.929 |
| Smaller decision tree | 546/638 | 42/1148 | 85.6% | 3.7% | 0.891 | 0.952 | 0.977 |
| Inactivity alone | 525/638 | 63/1148 | 82.3% | 5.5% | 0.856 | 0.922 | 0.969 |
| Balance alone | 249/638 | 59/1148 | 39.0% | 5.1% | 0.526 | 0.771 | 0.911 |
| Logistic, balance alone | 264/638 | 60/1148 | 41.4% | 5.2% | 0.549 | 0.769 | 0.911 |
| Logistic, inactivity + balance | 596/638 | 56/1148 | 93.4% | 4.9% | 0.924 | 0.970 | 0.980 |
| Logistic, all 14 predictors | 600/638 | 62/1148 | 94.0% | 5.4% | 0.923 | 0.971 | 0.983 |
| Logistic, without time since last activity | 598/638 | 61/1148 | 93.7% | 5.3% | 0.922 | 0.972 | 0.982 |
| Logistic, without activity timing | 536/638 | 60/1148 | 84.0% | 5.2% | 0.869 | 0.856 | 0.951 |
| Logistic, without timing and counts | 545/638 | 60/1148 | 85.4% | 5.2% | 0.877 | 0.856 | 0.949 |
| Random forest | 560/638 | 57/1148 | 87.8% | 5.0% | 0.892 | 0.967 | 0.979 |
| Histogram gradient boosting | 567/638 | 58/1148 | 88.9% | 5.1% | 0.898 | 0.967 | 0.977 |
| Gaussian naive Bayes | 582/638 | 79/1148 | 91.2% | 6.9% | 0.896 | 0.936 | 0.960 |
| RBF support vector machine | 604/638 | 66/1148 | 94.7% | 5.7% | 0.924 | 0.975 | 0.978 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 496/500 | 33/971 | 99.2% | 3.4% | 0.964 | 0.987 | 0.996 |
| Smaller decision tree | 496/500 | 36/971 | 99.2% | 3.7% | 0.961 | 0.979 | 0.993 |
| Inactivity alone | 463/500 | 50/971 | 92.6% | 5.1% | 0.914 | 0.955 | 0.983 |
| Balance alone | 223/500 | 48/971 | 44.6% | 4.9% | 0.578 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 46/971 | 99.8% | 4.7% | 0.955 | 0.989 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 52/971 | 99.8% | 5.4% | 0.950 | 0.988 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.990 | 0.995 |
| Logistic, without activity timing | 472/500 | 49/971 | 94.4% | 5.0% | 0.925 | 0.869 | 0.970 |
| Logistic, without timing and counts | 478/500 | 49/971 | 95.6% | 5.0% | 0.931 | 0.870 | 0.969 |
| Random forest | 499/500 | 47/971 | 99.8% | 4.8% | 0.954 | 0.992 | 0.998 |
| Histogram gradient boosting | 498/500 | 45/971 | 99.6% | 4.6% | 0.955 | 0.995 | 0.998 |
| Gaussian naive Bayes | 469/500 | 69/971 | 93.8% | 7.1% | 0.904 | 0.942 | 0.966 |
| RBF support vector machine | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.998 | 0.999 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 72/122 | 15/145 | 59.0% | 10.3% | 0.689 | 0.739 | 0.599 |
| Smaller decision tree | 49/122 | 2/145 | 40.2% | 1.4% | 0.566 | 0.862 | 0.909 |
| Inactivity alone | 58/122 | 7/145 | 47.5% | 4.8% | 0.620 | 0.854 | 0.947 |
| Balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, balance alone | 26/122 | 10/145 | 21.3% | 6.9% | 0.329 | 0.766 | 0.841 |
| Logistic, inactivity + balance | 96/122 | 5/145 | 78.7% | 3.4% | 0.861 | 0.965 | 0.975 |
| Logistic, all 14 predictors | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.968 | 0.977 |
| Logistic, without time since last activity | 100/122 | 6/145 | 82.0% | 4.1% | 0.877 | 0.967 | 0.976 |
| Logistic, without activity timing | 64/122 | 10/145 | 52.5% | 6.9% | 0.653 | 0.832 | 0.888 |
| Logistic, without timing and counts | 67/122 | 10/145 | 54.9% | 6.9% | 0.673 | 0.831 | 0.886 |
| Random forest | 57/122 | 5/145 | 46.7% | 3.4% | 0.620 | 0.912 | 0.932 |
| Histogram gradient boosting | 64/122 | 7/145 | 52.5% | 4.8% | 0.663 | 0.874 | 0.879 |
| Gaussian naive Bayes | 111/122 | 4/145 | 91.0% | 2.8% | 0.937 | 0.971 | 0.979 |
| RBF support vector machine | 104/122 | 10/145 | 85.2% | 6.9% | 0.881 | 0.953 | 0.959 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 7/16 | 6/32 | 43.8% | 18.8% | 0.483 | 0.458 | 0.715 |
| Smaller decision tree | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.409 | 0.635 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.271 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.437 | 0.572 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.469 | 0.660 |
| Logistic, without time since last activity | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.454 | 0.633 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.368 | 0.588 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.361 | 0.561 |
| Random forest | 4/16 | 5/32 | 25.0% | 15.6% | 0.320 | 0.485 | 0.709 |
| Histogram gradient boosting | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.483 | 0.740 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.462 | 0.715 |
| RBF support vector machine | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.309 | 0.420 |

</details>

## Training on CryptoBilis and BTCPay

### CryptoBilis and BTCPay to Coldcard

**External** · 377 training observations before fold splitting · 1078 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.926 | 0.965 |
| Inactivity alone | 468/499 | 50/579 | 93.8% | 8.6% | 0.920 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/579 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 294/499 | 47/579 | 58.9% | 8.1% | 0.700 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 497/499 | 47/579 | 99.6% | 8.1% | 0.953 | 0.993 | 0.994 |
| Logistic, all 14 predictors | 479/499 | 54/579 | 96.0% | 9.3% | 0.928 | 0.981 | 0.981 |
| Logistic, without time since last activity | 467/499 | 50/579 | 93.6% | 8.6% | 0.919 | 0.975 | 0.972 |
| Logistic, without activity timing | 452/499 | 36/579 | 90.6% | 6.2% | 0.916 | 0.869 | 0.933 |
| Logistic, without timing and counts | 481/499 | 39/579 | 96.4% | 6.7% | 0.944 | 0.874 | 0.937 |
| Random forest | 459/499 | 51/579 | 92.0% | 8.8% | 0.910 | 0.923 | 0.965 |
| Histogram gradient boosting | 491/499 | 38/579 | 98.4% | 6.6% | 0.955 | 0.926 | 0.961 |
| Gaussian naive Bayes | 411/499 | 47/579 | 82.4% | 8.1% | 0.859 | 0.925 | 0.897 |
| RBF support vector machine | 466/499 | 55/579 | 93.4% | 9.5% | 0.914 | 0.977 | 0.978 |

### CryptoBilis and BTCPay to CryptoBilis

**Internal** · 377 training observations before fold splitting · 329 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 108/122 | 7/207 | 88.5% | 3.4% | 0.911 | 0.946 | 0.978 |
| Smaller decision tree | 88/122 | 6/207 | 72.1% | 2.9% | 0.815 | 0.907 | 0.958 |
| Inactivity alone | 77/122 | 8/207 | 63.1% | 3.9% | 0.744 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 32/122 | 12/207 | 26.2% | 5.8% | 0.386 | 0.738 | 0.864 |
| Logistic, inactivity + balance | 100/122 | 9/207 | 82.0% | 4.3% | 0.866 | 0.926 | 0.975 |
| Logistic, all 14 predictors | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.954 | 0.980 |
| Logistic, without time since last activity | 106/122 | 7/207 | 86.9% | 3.4% | 0.902 | 0.954 | 0.978 |
| Logistic, without activity timing | 65/122 | 10/207 | 53.3% | 4.8% | 0.660 | 0.816 | 0.912 |
| Logistic, without timing and counts | 64/122 | 10/207 | 52.5% | 4.8% | 0.653 | 0.819 | 0.914 |
| Random forest | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.937 | 0.980 |
| Histogram gradient boosting | 109/122 | 7/207 | 89.3% | 3.4% | 0.916 | 0.955 | 0.982 |
| Gaussian naive Bayes | 59/122 | 3/207 | 48.4% | 1.4% | 0.641 | 0.846 | 0.877 |
| RBF support vector machine | 111/122 | 7/207 | 91.0% | 3.4% | 0.925 | 0.959 | 0.983 |

### CryptoBilis and BTCPay to BTCPay

**Internal** · 377 training observations before fold splitting · 48 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 2/32 | 0.0% | 6.2% | 0.000 | 0.408 | 0.652 |
| Smaller decision tree | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.362 | 0.557 |
| Inactivity alone | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.266 |
| Logistic, inactivity + balance | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.455 | 0.605 |
| Logistic, all 14 predictors | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.506 | 0.703 |
| Logistic, without time since last activity | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.496 | 0.688 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.399 | 0.623 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.393 | 0.604 |
| Random forest | 3/16 | 6/32 | 18.8% | 18.8% | 0.240 | 0.461 | 0.719 |
| Histogram gradient boosting | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.434 | 0.701 |
| Gaussian naive Bayes | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.452 | 0.705 |
| RBF support vector machine | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.419 | 0.561 |

### CryptoBilis and BTCPay to Coldcard and CryptoBilis

**Mixed** · 377 training observations before fold splitting · 1407 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 607/621 | 47/786 | 97.7% | 6.0% | 0.952 | 0.939 | 0.973 |
| Smaller decision tree | 587/621 | 46/786 | 94.5% | 5.9% | 0.936 | 0.922 | 0.964 |
| Inactivity alone | 545/621 | 58/786 | 87.8% | 7.4% | 0.891 | 0.929 | 0.966 |
| Balance alone | 295/621 | 57/786 | 47.5% | 7.3% | 0.606 | 0.813 | 0.918 |
| Logistic, balance alone | 326/621 | 59/786 | 52.5% | 7.5% | 0.648 | 0.811 | 0.917 |
| Logistic, inactivity + balance | 597/621 | 56/786 | 96.1% | 7.1% | 0.937 | 0.982 | 0.987 |
| Logistic, all 14 predictors | 584/621 | 61/786 | 94.0% | 7.8% | 0.923 | 0.973 | 0.978 |
| Logistic, without time since last activity | 573/621 | 57/786 | 92.3% | 7.3% | 0.916 | 0.968 | 0.970 |
| Logistic, without activity timing | 517/621 | 46/786 | 83.3% | 5.9% | 0.873 | 0.862 | 0.930 |
| Logistic, without timing and counts | 545/621 | 49/786 | 87.8% | 6.2% | 0.897 | 0.867 | 0.933 |
| Random forest | 569/621 | 58/786 | 91.6% | 7.4% | 0.912 | 0.927 | 0.969 |
| Histogram gradient boosting | 600/621 | 45/786 | 96.6% | 5.7% | 0.948 | 0.933 | 0.968 |
| Gaussian naive Bayes | 470/621 | 50/786 | 75.7% | 6.4% | 0.824 | 0.903 | 0.888 |
| RBF support vector machine | 577/621 | 62/786 | 92.9% | 7.9% | 0.916 | 0.971 | 0.976 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.926 | 0.965 |
| Inactivity alone | 468/499 | 50/579 | 93.8% | 8.6% | 0.920 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/579 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 294/499 | 47/579 | 58.9% | 8.1% | 0.700 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 497/499 | 47/579 | 99.6% | 8.1% | 0.953 | 0.993 | 0.994 |
| Logistic, all 14 predictors | 479/499 | 54/579 | 96.0% | 9.3% | 0.928 | 0.981 | 0.981 |
| Logistic, without time since last activity | 467/499 | 50/579 | 93.6% | 8.6% | 0.919 | 0.975 | 0.972 |
| Logistic, without activity timing | 452/499 | 36/579 | 90.6% | 6.2% | 0.916 | 0.869 | 0.933 |
| Logistic, without timing and counts | 481/499 | 39/579 | 96.4% | 6.7% | 0.944 | 0.874 | 0.937 |
| Random forest | 459/499 | 51/579 | 92.0% | 8.8% | 0.910 | 0.923 | 0.965 |
| Histogram gradient boosting | 491/499 | 38/579 | 98.4% | 6.6% | 0.955 | 0.926 | 0.961 |
| Gaussian naive Bayes | 411/499 | 47/579 | 82.4% | 8.1% | 0.859 | 0.925 | 0.897 |
| RBF support vector machine | 466/499 | 55/579 | 93.4% | 9.5% | 0.914 | 0.977 | 0.978 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 108/122 | 7/207 | 88.5% | 3.4% | 0.911 | 0.946 | 0.978 |
| Smaller decision tree | 88/122 | 6/207 | 72.1% | 2.9% | 0.815 | 0.907 | 0.958 |
| Inactivity alone | 77/122 | 8/207 | 63.1% | 3.9% | 0.744 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 32/122 | 12/207 | 26.2% | 5.8% | 0.386 | 0.738 | 0.864 |
| Logistic, inactivity + balance | 100/122 | 9/207 | 82.0% | 4.3% | 0.866 | 0.926 | 0.975 |
| Logistic, all 14 predictors | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.954 | 0.980 |
| Logistic, without time since last activity | 106/122 | 7/207 | 86.9% | 3.4% | 0.902 | 0.954 | 0.978 |
| Logistic, without activity timing | 65/122 | 10/207 | 53.3% | 4.8% | 0.660 | 0.816 | 0.912 |
| Logistic, without timing and counts | 64/122 | 10/207 | 52.5% | 4.8% | 0.653 | 0.819 | 0.914 |
| Random forest | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.937 | 0.980 |
| Histogram gradient boosting | 109/122 | 7/207 | 89.3% | 3.4% | 0.916 | 0.955 | 0.982 |
| Gaussian naive Bayes | 59/122 | 3/207 | 48.4% | 1.4% | 0.641 | 0.846 | 0.877 |
| RBF support vector machine | 111/122 | 7/207 | 91.0% | 3.4% | 0.925 | 0.959 | 0.983 |

</details>

### CryptoBilis and BTCPay to Coldcard and BTCPay

**Mixed** · 377 training observations before fold splitting · 1126 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/515 | 42/611 | 96.9% | 6.9% | 0.945 | 0.932 | 0.964 |
| Smaller decision tree | 499/515 | 41/611 | 96.9% | 6.7% | 0.946 | 0.918 | 0.954 |
| Inactivity alone | 473/515 | 56/611 | 91.8% | 9.2% | 0.906 | 0.948 | 0.963 |
| Balance alone | 265/515 | 46/611 | 51.5% | 7.5% | 0.642 | 0.812 | 0.910 |
| Logistic, balance alone | 294/515 | 48/611 | 57.1% | 7.9% | 0.686 | 0.812 | 0.910 |
| Logistic, inactivity + balance | 500/515 | 52/611 | 97.1% | 8.5% | 0.937 | 0.985 | 0.982 |
| Logistic, all 14 predictors | 482/515 | 58/611 | 93.6% | 9.5% | 0.914 | 0.973 | 0.972 |
| Logistic, without time since last activity | 470/515 | 54/611 | 91.3% | 8.8% | 0.905 | 0.967 | 0.963 |
| Logistic, without activity timing | 452/515 | 37/611 | 87.8% | 6.1% | 0.900 | 0.861 | 0.922 |
| Logistic, without timing and counts | 481/515 | 40/611 | 93.4% | 6.5% | 0.929 | 0.866 | 0.926 |
| Random forest | 462/515 | 57/611 | 89.7% | 9.3% | 0.894 | 0.910 | 0.958 |
| Histogram gradient boosting | 492/515 | 43/611 | 95.5% | 7.0% | 0.937 | 0.913 | 0.955 |
| Gaussian naive Bayes | 412/515 | 49/611 | 80.0% | 8.0% | 0.844 | 0.917 | 0.890 |
| RBF support vector machine | 469/515 | 60/611 | 91.1% | 9.8% | 0.898 | 0.968 | 0.966 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.926 | 0.965 |
| Inactivity alone | 468/499 | 50/579 | 93.8% | 8.6% | 0.920 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/579 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 294/499 | 47/579 | 58.9% | 8.1% | 0.700 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 497/499 | 47/579 | 99.6% | 8.1% | 0.953 | 0.993 | 0.994 |
| Logistic, all 14 predictors | 479/499 | 54/579 | 96.0% | 9.3% | 0.928 | 0.981 | 0.981 |
| Logistic, without time since last activity | 467/499 | 50/579 | 93.6% | 8.6% | 0.919 | 0.975 | 0.972 |
| Logistic, without activity timing | 452/499 | 36/579 | 90.6% | 6.2% | 0.916 | 0.869 | 0.933 |
| Logistic, without timing and counts | 481/499 | 39/579 | 96.4% | 6.7% | 0.944 | 0.874 | 0.937 |
| Random forest | 459/499 | 51/579 | 92.0% | 8.8% | 0.910 | 0.923 | 0.965 |
| Histogram gradient boosting | 491/499 | 38/579 | 98.4% | 6.6% | 0.955 | 0.926 | 0.961 |
| Gaussian naive Bayes | 411/499 | 47/579 | 82.4% | 8.1% | 0.859 | 0.925 | 0.897 |
| RBF support vector machine | 466/499 | 55/579 | 93.4% | 9.5% | 0.914 | 0.977 | 0.978 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 2/32 | 0.0% | 6.2% | 0.000 | 0.408 | 0.652 |
| Smaller decision tree | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.362 | 0.557 |
| Inactivity alone | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.266 |
| Logistic, inactivity + balance | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.455 | 0.605 |
| Logistic, all 14 predictors | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.506 | 0.703 |
| Logistic, without time since last activity | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.496 | 0.688 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.399 | 0.623 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.393 | 0.604 |
| Random forest | 3/16 | 6/32 | 18.8% | 18.8% | 0.240 | 0.461 | 0.719 |
| Histogram gradient boosting | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.434 | 0.701 |
| Gaussian naive Bayes | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.452 | 0.705 |
| RBF support vector machine | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.419 | 0.561 |

</details>

### CryptoBilis and BTCPay to CryptoBilis and BTCPay

**Internal** · 377 training observations before fold splitting · 377 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 108/138 | 9/239 | 78.3% | 3.8% | 0.847 | 0.904 | 0.947 |
| Smaller decision tree | 88/138 | 7/239 | 63.8% | 2.9% | 0.755 | 0.861 | 0.920 |
| Inactivity alone | 82/138 | 14/239 | 59.4% | 5.9% | 0.701 | 0.802 | 0.924 |
| Balance alone | 30/138 | 13/239 | 21.7% | 5.4% | 0.331 | 0.696 | 0.801 |
| Logistic, balance alone | 32/138 | 13/239 | 23.2% | 5.4% | 0.350 | 0.687 | 0.798 |
| Logistic, inactivity + balance | 103/138 | 14/239 | 74.6% | 5.9% | 0.808 | 0.881 | 0.933 |
| Logistic, all 14 predictors | 108/138 | 11/239 | 78.3% | 4.6% | 0.840 | 0.909 | 0.947 |
| Logistic, without time since last activity | 109/138 | 11/239 | 79.0% | 4.6% | 0.845 | 0.910 | 0.944 |
| Logistic, without activity timing | 65/138 | 11/239 | 47.1% | 4.6% | 0.607 | 0.781 | 0.879 |
| Logistic, without timing and counts | 64/138 | 11/239 | 46.4% | 4.6% | 0.601 | 0.782 | 0.877 |
| Random forest | 113/138 | 13/239 | 81.9% | 5.4% | 0.856 | 0.893 | 0.954 |
| Histogram gradient boosting | 110/138 | 12/239 | 79.7% | 5.0% | 0.846 | 0.911 | 0.959 |
| Gaussian naive Bayes | 60/138 | 5/239 | 43.5% | 2.1% | 0.591 | 0.812 | 0.858 |
| RBF support vector machine | 114/138 | 12/239 | 82.6% | 5.0% | 0.864 | 0.910 | 0.935 |

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 108/122 | 7/207 | 88.5% | 3.4% | 0.911 | 0.946 | 0.978 |
| Smaller decision tree | 88/122 | 6/207 | 72.1% | 2.9% | 0.815 | 0.907 | 0.958 |
| Inactivity alone | 77/122 | 8/207 | 63.1% | 3.9% | 0.744 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 32/122 | 12/207 | 26.2% | 5.8% | 0.386 | 0.738 | 0.864 |
| Logistic, inactivity + balance | 100/122 | 9/207 | 82.0% | 4.3% | 0.866 | 0.926 | 0.975 |
| Logistic, all 14 predictors | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.954 | 0.980 |
| Logistic, without time since last activity | 106/122 | 7/207 | 86.9% | 3.4% | 0.902 | 0.954 | 0.978 |
| Logistic, without activity timing | 65/122 | 10/207 | 53.3% | 4.8% | 0.660 | 0.816 | 0.912 |
| Logistic, without timing and counts | 64/122 | 10/207 | 52.5% | 4.8% | 0.653 | 0.819 | 0.914 |
| Random forest | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.937 | 0.980 |
| Histogram gradient boosting | 109/122 | 7/207 | 89.3% | 3.4% | 0.916 | 0.955 | 0.982 |
| Gaussian naive Bayes | 59/122 | 3/207 | 48.4% | 1.4% | 0.641 | 0.846 | 0.877 |
| RBF support vector machine | 111/122 | 7/207 | 91.0% | 3.4% | 0.925 | 0.959 | 0.983 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 2/32 | 0.0% | 6.2% | 0.000 | 0.408 | 0.652 |
| Smaller decision tree | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.362 | 0.557 |
| Inactivity alone | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.266 |
| Logistic, inactivity + balance | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.455 | 0.605 |
| Logistic, all 14 predictors | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.506 | 0.703 |
| Logistic, without time since last activity | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.496 | 0.688 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.399 | 0.623 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.393 | 0.604 |
| Random forest | 3/16 | 6/32 | 18.8% | 18.8% | 0.240 | 0.461 | 0.719 |
| Histogram gradient boosting | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.434 | 0.701 |
| Gaussian naive Bayes | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.452 | 0.705 |
| RBF support vector machine | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.419 | 0.561 |

</details>

### CryptoBilis and BTCPay to Coldcard and CryptoBilis and BTCPay

**Mixed** · 377 training observations before fold splitting · 1455 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 607/637 | 49/818 | 95.3% | 6.0% | 0.939 | 0.932 | 0.967 |
| Smaller decision tree | 587/637 | 47/818 | 92.2% | 5.7% | 0.924 | 0.914 | 0.955 |
| Inactivity alone | 550/637 | 64/818 | 86.3% | 7.8% | 0.879 | 0.923 | 0.959 |
| Balance alone | 295/637 | 58/818 | 46.3% | 7.1% | 0.596 | 0.803 | 0.903 |
| Logistic, balance alone | 326/637 | 60/818 | 51.2% | 7.3% | 0.637 | 0.801 | 0.902 |
| Logistic, inactivity + balance | 600/637 | 61/818 | 94.2% | 7.5% | 0.924 | 0.975 | 0.977 |
| Logistic, all 14 predictors | 587/637 | 65/818 | 92.2% | 7.9% | 0.911 | 0.966 | 0.971 |
| Logistic, without time since last activity | 576/637 | 61/818 | 90.4% | 7.5% | 0.904 | 0.961 | 0.963 |
| Logistic, without activity timing | 517/637 | 47/818 | 81.2% | 5.7% | 0.861 | 0.855 | 0.922 |
| Logistic, without timing and counts | 545/637 | 50/818 | 85.6% | 6.1% | 0.885 | 0.860 | 0.924 |
| Random forest | 572/637 | 64/818 | 89.8% | 7.8% | 0.899 | 0.918 | 0.964 |
| Histogram gradient boosting | 601/637 | 50/818 | 94.3% | 6.1% | 0.933 | 0.923 | 0.963 |
| Gaussian naive Bayes | 471/637 | 52/818 | 73.9% | 6.4% | 0.812 | 0.897 | 0.882 |
| RBF support vector machine | 580/637 | 67/818 | 91.1% | 8.2% | 0.903 | 0.963 | 0.966 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.939 | 0.972 |
| Smaller decision tree | 499/499 | 40/579 | 100.0% | 6.9% | 0.961 | 0.926 | 0.965 |
| Inactivity alone | 468/499 | 50/579 | 93.8% | 8.6% | 0.920 | 0.956 | 0.973 |
| Balance alone | 265/499 | 45/579 | 53.1% | 7.8% | 0.655 | 0.824 | 0.929 |
| Logistic, balance alone | 294/499 | 47/579 | 58.9% | 8.1% | 0.700 | 0.824 | 0.929 |
| Logistic, inactivity + balance | 497/499 | 47/579 | 99.6% | 8.1% | 0.953 | 0.993 | 0.994 |
| Logistic, all 14 predictors | 479/499 | 54/579 | 96.0% | 9.3% | 0.928 | 0.981 | 0.981 |
| Logistic, without time since last activity | 467/499 | 50/579 | 93.6% | 8.6% | 0.919 | 0.975 | 0.972 |
| Logistic, without activity timing | 452/499 | 36/579 | 90.6% | 6.2% | 0.916 | 0.869 | 0.933 |
| Logistic, without timing and counts | 481/499 | 39/579 | 96.4% | 6.7% | 0.944 | 0.874 | 0.937 |
| Random forest | 459/499 | 51/579 | 92.0% | 8.8% | 0.910 | 0.923 | 0.965 |
| Histogram gradient boosting | 491/499 | 38/579 | 98.4% | 6.6% | 0.955 | 0.926 | 0.961 |
| Gaussian naive Bayes | 411/499 | 47/579 | 82.4% | 8.1% | 0.859 | 0.925 | 0.897 |
| RBF support vector machine | 466/499 | 55/579 | 93.4% | 9.5% | 0.914 | 0.977 | 0.978 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 108/122 | 7/207 | 88.5% | 3.4% | 0.911 | 0.946 | 0.978 |
| Smaller decision tree | 88/122 | 6/207 | 72.1% | 2.9% | 0.815 | 0.907 | 0.958 |
| Inactivity alone | 77/122 | 8/207 | 63.1% | 3.9% | 0.744 | 0.854 | 0.963 |
| Balance alone | 30/122 | 12/207 | 24.6% | 5.8% | 0.366 | 0.748 | 0.868 |
| Logistic, balance alone | 32/122 | 12/207 | 26.2% | 5.8% | 0.386 | 0.738 | 0.864 |
| Logistic, inactivity + balance | 100/122 | 9/207 | 82.0% | 4.3% | 0.866 | 0.926 | 0.975 |
| Logistic, all 14 predictors | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.954 | 0.980 |
| Logistic, without time since last activity | 106/122 | 7/207 | 86.9% | 3.4% | 0.902 | 0.954 | 0.978 |
| Logistic, without activity timing | 65/122 | 10/207 | 53.3% | 4.8% | 0.660 | 0.816 | 0.912 |
| Logistic, without timing and counts | 64/122 | 10/207 | 52.5% | 4.8% | 0.653 | 0.819 | 0.914 |
| Random forest | 110/122 | 7/207 | 90.2% | 3.4% | 0.921 | 0.937 | 0.980 |
| Histogram gradient boosting | 109/122 | 7/207 | 89.3% | 3.4% | 0.916 | 0.955 | 0.982 |
| Gaussian naive Bayes | 59/122 | 3/207 | 48.4% | 1.4% | 0.641 | 0.846 | 0.877 |
| RBF support vector machine | 111/122 | 7/207 | 91.0% | 3.4% | 0.925 | 0.959 | 0.983 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 0/16 | 2/32 | 0.0% | 6.2% | 0.000 | 0.408 | 0.652 |
| Smaller decision tree | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.362 | 0.557 |
| Inactivity alone | 5/16 | 6/32 | 31.2% | 18.8% | 0.370 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.266 |
| Logistic, inactivity + balance | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.455 | 0.605 |
| Logistic, all 14 predictors | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.506 | 0.703 |
| Logistic, without time since last activity | 3/16 | 4/32 | 18.8% | 12.5% | 0.261 | 0.496 | 0.688 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.399 | 0.623 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.393 | 0.604 |
| Random forest | 3/16 | 6/32 | 18.8% | 18.8% | 0.240 | 0.461 | 0.719 |
| Histogram gradient boosting | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.434 | 0.701 |
| Gaussian naive Bayes | 1/16 | 2/32 | 6.2% | 6.2% | 0.105 | 0.452 | 0.705 |
| RBF support vector machine | 3/16 | 5/32 | 18.8% | 15.6% | 0.250 | 0.419 | 0.561 |

</details>

## Training on Coldcard and CryptoBilis and BTCPay

### Coldcard and CryptoBilis and BTCPay to Coldcard

**Internal** · 1848 training observations before fold splitting · 1471 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 57/971 | 99.6% | 5.9% | 0.944 | 0.970 | 0.992 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.945 | 0.983 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 225/500 | 48/971 | 45.0% | 4.9% | 0.582 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 51/971 | 99.8% | 5.3% | 0.950 | 0.990 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.989 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.989 | 0.995 |
| Logistic, without activity timing | 476/500 | 48/971 | 95.2% | 4.9% | 0.930 | 0.870 | 0.970 |
| Logistic, without timing and counts | 477/500 | 48/971 | 95.4% | 4.9% | 0.931 | 0.870 | 0.969 |
| Random forest | 496/500 | 56/971 | 99.2% | 5.8% | 0.943 | 0.988 | 0.997 |
| Histogram gradient boosting | 498/500 | 49/971 | 99.6% | 5.0% | 0.951 | 0.996 | 0.999 |
| Gaussian naive Bayes | 462/500 | 70/971 | 92.4% | 7.2% | 0.895 | 0.925 | 0.952 |
| RBF support vector machine | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.988 | 0.995 |

### Coldcard and CryptoBilis and BTCPay to CryptoBilis

**Internal** · 1848 training observations before fold splitting · 329 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 91/122 | 7/207 | 74.6% | 3.4% | 0.827 | 0.895 | 0.927 |
| Smaller decision tree | 91/122 | 4/207 | 74.6% | 1.9% | 0.839 | 0.928 | 0.970 |
| Inactivity alone | 65/122 | 8/207 | 53.3% | 3.9% | 0.667 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.742 | 0.866 |
| Logistic, inactivity + balance | 96/122 | 6/207 | 78.7% | 2.9% | 0.857 | 0.958 | 0.980 |
| Logistic, all 14 predictors | 99/122 | 8/207 | 81.1% | 3.9% | 0.865 | 0.965 | 0.983 |
| Logistic, without time since last activity | 100/122 | 8/207 | 82.0% | 3.9% | 0.870 | 0.964 | 0.982 |
| Logistic, without activity timing | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.825 | 0.917 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.824 | 0.916 |
| Random forest | 101/122 | 3/207 | 82.8% | 1.4% | 0.894 | 0.962 | 0.985 |
| Histogram gradient boosting | 107/122 | 5/207 | 87.7% | 2.4% | 0.915 | 0.970 | 0.986 |
| Gaussian naive Bayes | 110/122 | 13/207 | 90.2% | 6.3% | 0.898 | 0.918 | 0.946 |
| RBF support vector machine | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.970 | 0.983 |

### Coldcard and CryptoBilis and BTCPay to BTCPay

**Internal** · 1848 training observations before fold splitting · 48 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 2/16 | 5/32 | 12.5% | 15.6% | 0.174 | 0.378 | 0.570 |
| Smaller decision tree | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.382 | 0.588 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.268 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.442 | 0.582 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.484 | 0.684 |
| Logistic, without time since last activity | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.473 | 0.660 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.371 | 0.590 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.376 | 0.578 |
| Random forest | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.458 | 0.691 |
| Histogram gradient boosting | 1/16 | 6/32 | 6.2% | 18.8% | 0.087 | 0.451 | 0.716 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.458 | 0.715 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.374 | 0.535 |

### Coldcard and CryptoBilis and BTCPay to Coldcard and CryptoBilis

**Internal** · 1848 training observations before fold splitting · 1800 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 589/622 | 64/1178 | 94.7% | 5.4% | 0.924 | 0.954 | 0.978 |
| Smaller decision tree | 589/622 | 31/1178 | 94.7% | 2.6% | 0.948 | 0.940 | 0.980 |
| Inactivity alone | 530/622 | 59/1178 | 85.2% | 5.0% | 0.875 | 0.928 | 0.977 |
| Balance alone | 253/622 | 58/1178 | 40.7% | 4.9% | 0.542 | 0.782 | 0.931 |
| Logistic, balance alone | 267/622 | 59/1178 | 42.9% | 5.0% | 0.563 | 0.779 | 0.930 |
| Logistic, inactivity + balance | 595/622 | 57/1178 | 95.7% | 4.8% | 0.934 | 0.979 | 0.990 |
| Logistic, all 14 predictors | 598/622 | 62/1178 | 96.1% | 5.3% | 0.933 | 0.980 | 0.990 |
| Logistic, without time since last activity | 597/622 | 60/1178 | 96.0% | 5.1% | 0.934 | 0.980 | 0.990 |
| Logistic, without activity timing | 539/622 | 58/1178 | 86.7% | 4.9% | 0.884 | 0.864 | 0.962 |
| Logistic, without timing and counts | 540/622 | 58/1178 | 86.8% | 4.9% | 0.885 | 0.863 | 0.961 |
| Random forest | 597/622 | 59/1178 | 96.0% | 5.0% | 0.934 | 0.983 | 0.993 |
| Histogram gradient boosting | 605/622 | 54/1178 | 97.3% | 4.6% | 0.945 | 0.990 | 0.995 |
| Gaussian naive Bayes | 572/622 | 83/1178 | 92.0% | 7.0% | 0.896 | 0.921 | 0.951 |
| RBF support vector machine | 602/622 | 65/1178 | 96.8% | 5.5% | 0.934 | 0.981 | 0.991 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 57/971 | 99.6% | 5.9% | 0.944 | 0.970 | 0.992 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.945 | 0.983 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 225/500 | 48/971 | 45.0% | 4.9% | 0.582 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 51/971 | 99.8% | 5.3% | 0.950 | 0.990 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.989 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.989 | 0.995 |
| Logistic, without activity timing | 476/500 | 48/971 | 95.2% | 4.9% | 0.930 | 0.870 | 0.970 |
| Logistic, without timing and counts | 477/500 | 48/971 | 95.4% | 4.9% | 0.931 | 0.870 | 0.969 |
| Random forest | 496/500 | 56/971 | 99.2% | 5.8% | 0.943 | 0.988 | 0.997 |
| Histogram gradient boosting | 498/500 | 49/971 | 99.6% | 5.0% | 0.951 | 0.996 | 0.999 |
| Gaussian naive Bayes | 462/500 | 70/971 | 92.4% | 7.2% | 0.895 | 0.925 | 0.952 |
| RBF support vector machine | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.988 | 0.995 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 91/122 | 7/207 | 74.6% | 3.4% | 0.827 | 0.895 | 0.927 |
| Smaller decision tree | 91/122 | 4/207 | 74.6% | 1.9% | 0.839 | 0.928 | 0.970 |
| Inactivity alone | 65/122 | 8/207 | 53.3% | 3.9% | 0.667 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.742 | 0.866 |
| Logistic, inactivity + balance | 96/122 | 6/207 | 78.7% | 2.9% | 0.857 | 0.958 | 0.980 |
| Logistic, all 14 predictors | 99/122 | 8/207 | 81.1% | 3.9% | 0.865 | 0.965 | 0.983 |
| Logistic, without time since last activity | 100/122 | 8/207 | 82.0% | 3.9% | 0.870 | 0.964 | 0.982 |
| Logistic, without activity timing | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.825 | 0.917 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.824 | 0.916 |
| Random forest | 101/122 | 3/207 | 82.8% | 1.4% | 0.894 | 0.962 | 0.985 |
| Histogram gradient boosting | 107/122 | 5/207 | 87.7% | 2.4% | 0.915 | 0.970 | 0.986 |
| Gaussian naive Bayes | 110/122 | 13/207 | 90.2% | 6.3% | 0.898 | 0.918 | 0.946 |
| RBF support vector machine | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.970 | 0.983 |

</details>

### Coldcard and CryptoBilis and BTCPay to Coldcard and BTCPay

**Internal** · 1848 training observations before fold splitting · 1519 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 500/516 | 62/1003 | 96.9% | 6.2% | 0.928 | 0.955 | 0.980 |
| Smaller decision tree | 498/516 | 30/1003 | 96.5% | 3.0% | 0.954 | 0.931 | 0.972 |
| Inactivity alone | 469/516 | 57/1003 | 90.9% | 5.7% | 0.900 | 0.947 | 0.975 |
| Balance alone | 225/516 | 49/1003 | 43.6% | 4.9% | 0.570 | 0.777 | 0.925 |
| Logistic, balance alone | 238/516 | 50/1003 | 46.1% | 5.0% | 0.592 | 0.775 | 0.925 |
| Logistic, inactivity + balance | 500/516 | 56/1003 | 96.9% | 5.6% | 0.933 | 0.980 | 0.984 |
| Logistic, all 14 predictors | 500/516 | 58/1003 | 96.9% | 5.8% | 0.931 | 0.980 | 0.988 |
| Logistic, without time since last activity | 498/516 | 56/1003 | 96.5% | 5.6% | 0.931 | 0.980 | 0.987 |
| Logistic, without activity timing | 476/516 | 49/1003 | 92.2% | 4.9% | 0.915 | 0.860 | 0.959 |
| Logistic, without timing and counts | 477/516 | 49/1003 | 92.4% | 4.9% | 0.916 | 0.860 | 0.957 |
| Random forest | 497/516 | 60/1003 | 96.3% | 6.0% | 0.926 | 0.980 | 0.990 |
| Histogram gradient boosting | 499/516 | 55/1003 | 96.7% | 5.5% | 0.933 | 0.990 | 0.994 |
| Gaussian naive Bayes | 464/516 | 76/1003 | 89.9% | 7.6% | 0.879 | 0.915 | 0.946 |
| RBF support vector machine | 498/516 | 61/1003 | 96.5% | 6.1% | 0.927 | 0.976 | 0.982 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 57/971 | 99.6% | 5.9% | 0.944 | 0.970 | 0.992 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.945 | 0.983 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 225/500 | 48/971 | 45.0% | 4.9% | 0.582 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 51/971 | 99.8% | 5.3% | 0.950 | 0.990 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.989 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.989 | 0.995 |
| Logistic, without activity timing | 476/500 | 48/971 | 95.2% | 4.9% | 0.930 | 0.870 | 0.970 |
| Logistic, without timing and counts | 477/500 | 48/971 | 95.4% | 4.9% | 0.931 | 0.870 | 0.969 |
| Random forest | 496/500 | 56/971 | 99.2% | 5.8% | 0.943 | 0.988 | 0.997 |
| Histogram gradient boosting | 498/500 | 49/971 | 99.6% | 5.0% | 0.951 | 0.996 | 0.999 |
| Gaussian naive Bayes | 462/500 | 70/971 | 92.4% | 7.2% | 0.895 | 0.925 | 0.952 |
| RBF support vector machine | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.988 | 0.995 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 2/16 | 5/32 | 12.5% | 15.6% | 0.174 | 0.378 | 0.570 |
| Smaller decision tree | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.382 | 0.588 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.268 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.442 | 0.582 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.484 | 0.684 |
| Logistic, without time since last activity | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.473 | 0.660 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.371 | 0.590 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.376 | 0.578 |
| Random forest | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.458 | 0.691 |
| Histogram gradient boosting | 1/16 | 6/32 | 6.2% | 18.8% | 0.087 | 0.451 | 0.716 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.458 | 0.715 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.374 | 0.535 |

</details>

### Coldcard and CryptoBilis and BTCPay to CryptoBilis and BTCPay

**Internal** · 1848 training observations before fold splitting · 377 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 93/138 | 12/239 | 67.4% | 5.0% | 0.765 | 0.838 | 0.890 |
| Smaller decision tree | 91/138 | 7/239 | 65.9% | 2.9% | 0.771 | 0.872 | 0.931 |
| Inactivity alone | 69/138 | 14/239 | 50.0% | 5.9% | 0.624 | 0.802 | 0.924 |
| Balance alone | 28/138 | 11/239 | 20.3% | 4.6% | 0.316 | 0.696 | 0.801 |
| Logistic, balance alone | 29/138 | 11/239 | 21.0% | 4.6% | 0.326 | 0.690 | 0.799 |
| Logistic, inactivity + balance | 97/138 | 11/239 | 70.3% | 4.6% | 0.789 | 0.909 | 0.934 |
| Logistic, all 14 predictors | 100/138 | 12/239 | 72.5% | 5.0% | 0.800 | 0.922 | 0.948 |
| Logistic, without time since last activity | 101/138 | 12/239 | 73.2% | 5.0% | 0.805 | 0.918 | 0.942 |
| Logistic, without activity timing | 63/138 | 11/239 | 45.7% | 4.6% | 0.594 | 0.785 | 0.878 |
| Logistic, without timing and counts | 63/138 | 11/239 | 45.7% | 4.6% | 0.594 | 0.783 | 0.874 |
| Random forest | 102/138 | 7/239 | 73.9% | 2.9% | 0.826 | 0.916 | 0.952 |
| Histogram gradient boosting | 108/138 | 11/239 | 78.3% | 4.6% | 0.840 | 0.929 | 0.963 |
| Gaussian naive Bayes | 112/138 | 19/239 | 81.2% | 7.9% | 0.833 | 0.872 | 0.918 |
| RBF support vector machine | 106/138 | 10/239 | 76.8% | 4.2% | 0.835 | 0.916 | 0.932 |

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 91/122 | 7/207 | 74.6% | 3.4% | 0.827 | 0.895 | 0.927 |
| Smaller decision tree | 91/122 | 4/207 | 74.6% | 1.9% | 0.839 | 0.928 | 0.970 |
| Inactivity alone | 65/122 | 8/207 | 53.3% | 3.9% | 0.667 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.742 | 0.866 |
| Logistic, inactivity + balance | 96/122 | 6/207 | 78.7% | 2.9% | 0.857 | 0.958 | 0.980 |
| Logistic, all 14 predictors | 99/122 | 8/207 | 81.1% | 3.9% | 0.865 | 0.965 | 0.983 |
| Logistic, without time since last activity | 100/122 | 8/207 | 82.0% | 3.9% | 0.870 | 0.964 | 0.982 |
| Logistic, without activity timing | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.825 | 0.917 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.824 | 0.916 |
| Random forest | 101/122 | 3/207 | 82.8% | 1.4% | 0.894 | 0.962 | 0.985 |
| Histogram gradient boosting | 107/122 | 5/207 | 87.7% | 2.4% | 0.915 | 0.970 | 0.986 |
| Gaussian naive Bayes | 110/122 | 13/207 | 90.2% | 6.3% | 0.898 | 0.918 | 0.946 |
| RBF support vector machine | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.970 | 0.983 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 2/16 | 5/32 | 12.5% | 15.6% | 0.174 | 0.378 | 0.570 |
| Smaller decision tree | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.382 | 0.588 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.268 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.442 | 0.582 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.484 | 0.684 |
| Logistic, without time since last activity | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.473 | 0.660 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.371 | 0.590 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.376 | 0.578 |
| Random forest | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.458 | 0.691 |
| Histogram gradient boosting | 1/16 | 6/32 | 6.2% | 18.8% | 0.087 | 0.451 | 0.716 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.458 | 0.715 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.374 | 0.535 |

</details>

### Coldcard and CryptoBilis and BTCPay to Coldcard and CryptoBilis and BTCPay

**Internal** · 1848 training observations before fold splitting · 1848 test observations

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 591/638 | 69/1210 | 92.6% | 5.7% | 0.911 | 0.942 | 0.969 |
| Smaller decision tree | 589/638 | 34/1210 | 92.3% | 2.8% | 0.934 | 0.929 | 0.971 |
| Inactivity alone | 534/638 | 65/1210 | 83.7% | 5.4% | 0.863 | 0.922 | 0.970 |
| Balance alone | 253/638 | 59/1210 | 39.7% | 4.9% | 0.533 | 0.771 | 0.914 |
| Logistic, balance alone | 267/638 | 60/1210 | 41.8% | 5.0% | 0.553 | 0.767 | 0.913 |
| Logistic, inactivity + balance | 596/638 | 62/1210 | 93.4% | 5.1% | 0.920 | 0.971 | 0.981 |
| Logistic, all 14 predictors | 599/638 | 66/1210 | 93.9% | 5.5% | 0.919 | 0.972 | 0.984 |
| Logistic, without time since last activity | 598/638 | 64/1210 | 93.7% | 5.3% | 0.920 | 0.972 | 0.983 |
| Logistic, without activity timing | 539/638 | 59/1210 | 84.5% | 4.9% | 0.872 | 0.855 | 0.953 |
| Logistic, without timing and counts | 540/638 | 59/1210 | 84.6% | 4.9% | 0.873 | 0.855 | 0.951 |
| Random forest | 598/638 | 63/1210 | 93.7% | 5.2% | 0.921 | 0.976 | 0.988 |
| Histogram gradient boosting | 606/638 | 60/1210 | 95.0% | 5.0% | 0.929 | 0.985 | 0.991 |
| Gaussian naive Bayes | 574/638 | 89/1210 | 90.0% | 7.4% | 0.882 | 0.913 | 0.945 |
| RBF support vector machine | 603/638 | 68/1210 | 94.5% | 5.6% | 0.921 | 0.971 | 0.981 |

<details>
<summary>Coldcard results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 498/500 | 57/971 | 99.6% | 5.9% | 0.944 | 0.970 | 0.992 |
| Smaller decision tree | 498/500 | 27/971 | 99.6% | 2.8% | 0.972 | 0.945 | 0.983 |
| Inactivity alone | 465/500 | 51/971 | 93.0% | 5.3% | 0.915 | 0.955 | 0.983 |
| Balance alone | 225/500 | 48/971 | 45.0% | 4.9% | 0.582 | 0.792 | 0.946 |
| Logistic, balance alone | 238/500 | 49/971 | 47.6% | 5.0% | 0.605 | 0.790 | 0.946 |
| Logistic, inactivity + balance | 499/500 | 51/971 | 99.8% | 5.3% | 0.950 | 0.990 | 0.995 |
| Logistic, all 14 predictors | 499/500 | 54/971 | 99.8% | 5.6% | 0.948 | 0.989 | 0.995 |
| Logistic, without time since last activity | 497/500 | 52/971 | 99.4% | 5.4% | 0.948 | 0.989 | 0.995 |
| Logistic, without activity timing | 476/500 | 48/971 | 95.2% | 4.9% | 0.930 | 0.870 | 0.970 |
| Logistic, without timing and counts | 477/500 | 48/971 | 95.4% | 4.9% | 0.931 | 0.870 | 0.969 |
| Random forest | 496/500 | 56/971 | 99.2% | 5.8% | 0.943 | 0.988 | 0.997 |
| Histogram gradient boosting | 498/500 | 49/971 | 99.6% | 5.0% | 0.951 | 0.996 | 0.999 |
| Gaussian naive Bayes | 462/500 | 70/971 | 92.4% | 7.2% | 0.895 | 0.925 | 0.952 |
| RBF support vector machine | 497/500 | 58/971 | 99.4% | 6.0% | 0.942 | 0.988 | 0.995 |

</details>

<details>
<summary>CryptoBilis results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 91/122 | 7/207 | 74.6% | 3.4% | 0.827 | 0.895 | 0.927 |
| Smaller decision tree | 91/122 | 4/207 | 74.6% | 1.9% | 0.839 | 0.928 | 0.970 |
| Inactivity alone | 65/122 | 8/207 | 53.3% | 3.9% | 0.667 | 0.854 | 0.963 |
| Balance alone | 28/122 | 10/207 | 23.0% | 4.8% | 0.350 | 0.748 | 0.868 |
| Logistic, balance alone | 29/122 | 10/207 | 23.8% | 4.8% | 0.360 | 0.742 | 0.866 |
| Logistic, inactivity + balance | 96/122 | 6/207 | 78.7% | 2.9% | 0.857 | 0.958 | 0.980 |
| Logistic, all 14 predictors | 99/122 | 8/207 | 81.1% | 3.9% | 0.865 | 0.965 | 0.983 |
| Logistic, without time since last activity | 100/122 | 8/207 | 82.0% | 3.9% | 0.870 | 0.964 | 0.982 |
| Logistic, without activity timing | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.825 | 0.917 |
| Logistic, without timing and counts | 63/122 | 10/207 | 51.6% | 4.8% | 0.646 | 0.824 | 0.916 |
| Random forest | 101/122 | 3/207 | 82.8% | 1.4% | 0.894 | 0.962 | 0.985 |
| Histogram gradient boosting | 107/122 | 5/207 | 87.7% | 2.4% | 0.915 | 0.970 | 0.986 |
| Gaussian naive Bayes | 110/122 | 13/207 | 90.2% | 6.3% | 0.898 | 0.918 | 0.946 |
| RBF support vector machine | 105/122 | 7/207 | 86.1% | 3.4% | 0.897 | 0.970 | 0.983 |

</details>

<details>
<summary>BTCPay results</summary>

| Method | Sources retrieved | False alerts | Recall | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 2/16 | 5/32 | 12.5% | 15.6% | 0.174 | 0.378 | 0.570 |
| Smaller decision tree | 0/16 | 3/32 | 0.0% | 9.4% | 0.000 | 0.382 | 0.588 |
| Inactivity alone | 4/16 | 6/32 | 25.0% | 18.8% | 0.308 | 0.536 | 0.674 |
| Balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.245 | 0.275 |
| Logistic, balance alone | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.243 | 0.268 |
| Logistic, inactivity + balance | 1/16 | 5/32 | 6.2% | 15.6% | 0.091 | 0.442 | 0.582 |
| Logistic, all 14 predictors | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.484 | 0.684 |
| Logistic, without time since last activity | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.473 | 0.660 |
| Logistic, without activity timing | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.371 | 0.590 |
| Logistic, without timing and counts | 0/16 | 1/32 | 0.0% | 3.1% | 0.000 | 0.376 | 0.578 |
| Random forest | 1/16 | 4/32 | 6.2% | 12.5% | 0.095 | 0.458 | 0.691 |
| Histogram gradient boosting | 1/16 | 6/32 | 6.2% | 18.8% | 0.087 | 0.451 | 0.716 |
| Gaussian naive Bayes | 2/16 | 6/32 | 12.5% | 18.8% | 0.167 | 0.458 | 0.715 |
| RBF support vector machine | 1/16 | 3/32 | 6.2% | 9.4% | 0.100 | 0.374 | 0.535 |

</details>
