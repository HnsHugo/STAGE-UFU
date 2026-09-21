import os
import pandas as pd
import networkx as nx

DATA_DIR = "data/elliptic_bitcoin_dataset"

# 1. Charger les données AVANT d'appeler analyze_graph
classes = pd.read_csv(
    f"{DATA_DIR}/elliptic_txs_classes.csv"
)

edges = pd.read_csv(
    f"{DATA_DIR}/elliptic_txs_edgelist.csv"
)

features = pd.read_csv(
    f"{DATA_DIR}/elliptic_txs_features.csv",
    header=None
)

# 2. Définir la fonction
def analyze_graph(edges, classes, results_path="results/summary.txt"):

    print("\n=== Building graph ===")

    G = nx.from_pandas_edgelist(
        edges,
        source="txId1",
        target="txId2",
        create_using=nx.DiGraph()
    )

    nodes_count = G.number_of_nodes()
    edges_count = G.number_of_edges()

    in_degrees = [degree for _, degree in G.in_degree()]
    out_degrees = [degree for _, degree in G.out_degree()]

    avg_in_degree = sum(in_degrees) / len(in_degrees)
    avg_out_degree = sum(out_degrees) / len(out_degrees)

    max_in_degree = max(in_degrees)
    max_out_degree = max(out_degrees)

    print("Nodes:", nodes_count)
    print("Edges:", edges_count)
    print("Average in-degree:", avg_in_degree)
    print("Average out-degree:", avg_out_degree)
    print("Maximum in-degree:", max_in_degree)
    print("Maximum out-degree:", max_out_degree)

    # Add labels
    label_map = dict(
        zip(classes["txId"], classes["class"])
    )

    nx.set_node_attributes(
        G,
        label_map,
        "class"
    )

    graph_licit = 0
    graph_illicit = 0
    graph_unknown = 0

    for node in G.nodes:
        label = G.nodes[node].get("class", "unknown")

        if label == "1":
            graph_illicit += 1
        elif label == "2":
            graph_licit += 1
        else:
            graph_unknown += 1

    print("\n=== Graph labels ===")
    print("Licit nodes:", graph_licit)
    print("Illicit nodes:", graph_illicit)
    print("Unknown nodes:", graph_unknown)

    graph_summary = f"""

=== Graph Analysis ===

Nodes: {nodes_count}
Edges: {edges_count}

Average in-degree: {avg_in_degree:.4f}
Average out-degree: {avg_out_degree:.4f}

Maximum in-degree: {max_in_degree}
Maximum out-degree: {max_out_degree}

Graph labels:
Licit: {graph_licit}
Illicit: {graph_illicit}
Unknown: {graph_unknown}
"""

    with open(results_path, "a", encoding="utf-8") as f:
        f.write(graph_summary)

    print(f"\nGraph results saved to {results_path}")

    return G


# 3. Appeler la fonction EN DERNIER
G = analyze_graph(
    edges,
    classes
)