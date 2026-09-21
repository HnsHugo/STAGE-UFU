import os
import numpy as np
import pandas as pd
import networkx as nx


# ============================================================
# Paths
# ============================================================

DATA_DIR = "data/elliptic_bitcoin_dataset"
RESULTS_DIR = "results"
RESULTS_PATH = os.path.join(RESULTS_DIR, "summary.txt")

CLASSES_PATH = os.path.join(DATA_DIR, "elliptic_txs_classes.csv")
EDGES_PATH = os.path.join(DATA_DIR, "elliptic_txs_edgelist.csv")
FEATURES_PATH = os.path.join(DATA_DIR, "elliptic_txs_features.csv")


# ============================================================
# Load dataset
# ============================================================

def load_data():
    print("Loading Elliptic dataset...")

    classes = pd.read_csv(CLASSES_PATH)
    edges = pd.read_csv(EDGES_PATH)
    features = pd.read_csv(FEATURES_PATH, header=None)

    # Make sure labels are strings
    classes["class"] = classes["class"].astype(str)

    print("Dataset loaded successfully.\n")

    return classes, edges, features


# ============================================================
# Dataset statistics
# ============================================================

def analyze_dataset(classes, edges, features):
    lines = []

    lines.append("=== Elliptic Dataset Summary ===")
    lines.append("")

    lines.append(f"Transactions: {len(classes)}")
    lines.append(f"Edges: {len(edges)}")
    lines.append(f"Feature columns: {features.shape[1]}")
    lines.append(f"Number of features per transaction: {features.shape[1] - 1}")
    lines.append("")

    # Class distribution
    class_counts = classes["class"].value_counts()

    unknown_count = class_counts.get("unknown", 0)
    licit_count = class_counts.get("2", 0)
    illicit_count = class_counts.get("1", 0)

    total = len(classes)
    labeled_total = licit_count + illicit_count

    lines.append("=== Class Distribution ===")
    lines.append("")

    lines.append(f"Unknown: {unknown_count}")
    lines.append(f"Licit: {licit_count}")
    lines.append(f"Illicit: {illicit_count}")
    lines.append("")

    lines.append(
        f"Unknown percentage: {(unknown_count / total) * 100:.2f}%"
    )
    lines.append(
        f"Licit percentage: {(licit_count / total) * 100:.2f}%"
    )
    lines.append(
        f"Illicit percentage: {(illicit_count / total) * 100:.2f}%"
    )
    lines.append("")

    if labeled_total > 0:
        lines.append("Among labeled transactions:")
        lines.append(
            f"Licit: {(licit_count / labeled_total) * 100:.2f}%"
        )
        lines.append(
            f"Illicit: {(illicit_count / labeled_total) * 100:.2f}%"
        )

    return lines


# ============================================================
# Graph construction and statistics
# ============================================================

def analyze_graph(edges, classes):
    print("Building transaction graph...")

    G = nx.from_pandas_edgelist(
        edges,
        source="txId1",
        target="txId2",
        create_using=nx.DiGraph()
    )

    # Add class labels to graph nodes
    label_map = dict(zip(classes["txId"], classes["class"]))
    nx.set_node_attributes(G, label_map, "class")

    print("Graph built successfully.\n")

    lines = []

    lines.append("")
    lines.append("=== Graph Analysis ===")
    lines.append("")

    nodes = G.number_of_nodes()
    edge_count = G.number_of_edges()

    avg_in_degree = (
        sum(dict(G.in_degree()).values()) / nodes
        if nodes > 0 else 0
    )

    avg_out_degree = (
        sum(dict(G.out_degree()).values()) / nodes
        if nodes > 0 else 0
    )

    max_in_degree = max(
        dict(G.in_degree()).values(),
        default=0
    )

    max_out_degree = max(
        dict(G.out_degree()).values(),
        default=0
    )

    lines.append(f"Nodes: {nodes}")
    lines.append(f"Edges: {edge_count}")
    lines.append(f"Average in-degree: {avg_in_degree:.4f}")
    lines.append(f"Average out-degree: {avg_out_degree:.4f}")
    lines.append(f"Maximum in-degree: {max_in_degree}")
    lines.append(f"Maximum out-degree: {max_out_degree}")

    return G, lines


# ============================================================
# Licit vs illicit average degree comparison
# ============================================================

def compare_graph_classes(G):
    lines = []

    lines.append("")
    lines.append("=== Licit vs Illicit Graph Comparison ===")
    lines.append("")

    groups = {
        "Licit": "2",
        "Illicit": "1"
    }

    for name, label in groups.items():

        nodes = [
            node
            for node, data in G.nodes(data=True)
            if data.get("class") == label
        ]

        in_degrees = [G.in_degree(node) for node in nodes]
        out_degrees = [G.out_degree(node) for node in nodes]

        avg_in = np.mean(in_degrees) if in_degrees else 0
        avg_out = np.mean(out_degrees) if out_degrees else 0

        lines.append(f"{name} transactions:")
        lines.append(f"Count: {len(nodes)}")
        lines.append(f"Average in-degree: {avg_in:.4f}")
        lines.append(f"Average out-degree: {avg_out:.4f}")
        lines.append("")

    return lines


# ============================================================
# Degree distribution comparison
# ============================================================

def compare_degree_distributions(G):
    lines = []

    lines.append("=== Degree Distribution Comparison ===")
    lines.append("")

    groups = {
        "Licit": "2",
        "Illicit": "1"
    }

    for name, label in groups.items():

        in_degrees = []
        out_degrees = []
        total_degrees = []

        for node, data in G.nodes(data=True):

            if data.get("class") == label:

                in_degree = G.in_degree(node)
                out_degree = G.out_degree(node)

                in_degrees.append(in_degree)
                out_degrees.append(out_degree)
                total_degrees.append(in_degree + out_degree)

        lines.append(f"{name} transactions:")
        lines.append("")

        metrics = [
            ("In-degree", in_degrees),
            ("Out-degree", out_degrees),
            ("Total degree", total_degrees)
        ]

        for metric_name, values in metrics:

            if not values:
                continue

            values = np.array(values)

            mean = np.mean(values)
            median = np.median(values)
            p90 = np.percentile(values, 90)
            maximum = np.max(values)

            lines.append(
                f"{metric_name}: "
                f"mean={mean:.4f}, "
                f"median={median:.4f}, "
                f"p90={p90:.4f}, "
                f"max={maximum}"
            )

        lines.append("")

    return lines


# ============================================================
# Save results
# ============================================================

def save_results(lines):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    text = "\n".join(lines)

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(text)
    print(f"\nResults saved to: {RESULTS_PATH}")


# ============================================================
# Main
# ============================================================

def main():

    classes, edges, features = load_data()

    all_results = []

    # Dataset statistics
    all_results.extend(
        analyze_dataset(classes, edges, features)
    )

    # Graph analysis
    G, graph_results = analyze_graph(edges, classes)
    all_results.extend(graph_results)

    # Licit vs illicit averages
    all_results.extend(
        compare_graph_classes(G)
    )

    # Degree distributions
    all_results.extend(
        compare_degree_distributions(G)
    )

    # Save everything
    save_results(all_results)


if __name__ == "__main__":
    main()