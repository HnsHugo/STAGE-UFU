import os
import pandas as pd

DATA_DIR = "data/elliptic_bitcoin_dataset"
RESULTS_DIR = "results"

os.makedirs(RESULTS_DIR, exist_ok=True)

# Load datasets
classes = pd.read_csv(f"{DATA_DIR}/elliptic_txs_classes.csv")
edges = pd.read_csv(f"{DATA_DIR}/elliptic_txs_edgelist.csv")
features = pd.read_csv(
    f"{DATA_DIR}/elliptic_txs_features.csv",
    header=None
)

# Basic statistics
total = len(classes)

unknown = (classes["class"] == "unknown").sum()
licit = (classes["class"] == "2").sum()
illicit = (classes["class"] == "1").sum()

labeled = licit + illicit

time_min = features[1].min()
time_max = features[1].max()
time_count = features[1].nunique()

# Build summary
summary = f"""
=== Elliptic Dataset Summary ===

Dataset shapes:
Classes: {classes.shape}
Edges: {edges.shape}
Features: {features.shape}

Transactions:
Total: {total}

Labels:
Unknown: {unknown} ({unknown / total * 100:.2f}%)
Licit: {licit} ({licit / total * 100:.2f}%)
Illicit: {illicit} ({illicit / total * 100:.2f}%)

Among labeled transactions:
Licit: {licit / labeled * 100:.2f}%
Illicit: {illicit / labeled * 100:.2f}%

Graph:
Transactions / nodes: {len(features)}
Edges: {len(edges)}

Features:
Number of features: {features.shape[1] - 1}

Time steps:
Minimum: {time_min}
Maximum: {time_max}
Number of time steps: {time_count}

Label mapping:
1 = illicit
2 = licit
unknown = unlabeled
"""

print(summary)

# Save summary
with open(f"{RESULTS_DIR}/summary.txt", "w") as f:
    f.write(summary)

print("Summary saved to results/summary.txt")