"""Audit direct parents of externally attributed Coldcard transactions.
No parent transaction is automatically labelled stolen.
Usage: python audit_coldcard_parents.py blocos.tgz > parents.json
Requires the complete archive previously inspected (207436070 bytes).
"""
import collections
import json
import os
import sys
import tarfile

SEEDS = set("""
4b50d61a3d6e54c62ee0be13d7e9a8b69bffe7fc2b2cab4e14da56e4e20440d2
14edd9ee8445793c320e92e3b50365a0e18b8b25f424044bce337463f007fdd2
0c6bf853a645b699a3b2cd6d8e3c44cf1a02a16f538df08212a44753f75d9d01
ba119968ec4b82c28f557dfc6cbb2c1834d55145e5a352872c533296d19d3082
38b6dc366fcac50e2fe4a7fa901bfea957361c51157ad037d46e0febf89187de
""".split())
SOURCE = "https://bitquery.io/investigations/coldcard-wallet-hack"

def transactions(path):
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            if member.isfile():
                block = json.load(archive.extractfile(member))
                for tx in block["tx"]:
                    yield block["height"], tx

def audit(path):
    wanted = collections.defaultdict(set)
    seeds_found = set()
    for height, tx in transactions(path):
        if tx["hash"] in SEEDS:
            seeds_found.add(tx["hash"])
            for item in tx["inputs"]:
                previous = item["prev_out"]
                wanted[previous["tx_index"]].add(previous["n"])
    parents = []
    found = set()
    for height, tx in transactions(path):
        index = tx["tx_index"]
        if index not in wanted:
            continue
        found.add(index)
        addresses = {i.get("prev_out", {}).get("addr") for i in tx["inputs"]}
        addresses.discard(None)
        parents.append({
            "txid": tx["hash"], "height": height,
            "input_count": len(tx["inputs"]), "output_count": len(tx["out"]),
            "distinct_input_addresses": len(addresses),
            "spent_output_indices": sorted(wanted[index]),
            "label": "unknown",
            "relationship": "direct_parent_of_source_attributed_transaction",
        })
    return {
        "source": SOURCE,
        "interpretation": "Graph relationship only; not proof of theft or hardware control.",
        "source_attributed_seeds_found": sorted(seeds_found),
        "source_attributed_seeds_missing": sorted(SEEDS - seeds_found),
        "distinct_parent_indices_requested": len(wanted),
        "parent_transactions_found": len(found),
        "parent_transactions_missing": len(set(wanted) - found),
        "parents": sorted(parents, key=lambda row: (row["height"], row["txid"])),
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python audit_coldcard_parents.py blocos.tgz")
    if os.path.getsize(sys.argv[1]) != 207436070:
        sys.exit("Archive size differs from inspected upload; obtain the complete original file.")
    try:
        result = audit(sys.argv[1])
    except (tarfile.TarError, EOFError, json.JSONDecodeError, KeyError) as error:
        sys.exit("Audit failed; no complete report generated: " + str(error))
    print(json.dumps(result, indent=2))
