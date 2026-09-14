import os
import json
import math
import requests

# =========================
# Transaction to analyze
# =========================

txid = "6ff38500426cc256ffebf9a5b42e875d7ab05a60e99aed73a1710606ced0e96e"

# =========================
# API request
# =========================

url = f"https://blockstream.info/api/tx/{txid}"

response = requests.get(url)
response.raise_for_status()

data = response.json()

# =========================
# General information
# =========================

print("=== Transaction information ===")
print("TXID:", data["txid"])
print("Number of inputs:", len(data["vin"]))
print("Number of outputs:", len(data["vout"]))

# =========================
# Detect coinbase
# =========================

is_coinbase = (
    len(data["vin"]) > 0
    and data["vin"][0].get("is_coinbase", False)
)

# =========================
# Calculate transaction size
# =========================

weight = data.get("weight")

if weight is not None:
    vsize = math.ceil(weight / 4)
else:
    vsize = None

# =========================
# Output value
# =========================

output_value = sum(
    output["value"]
    for output in data["vout"]
)

# =========================
# Base analysis object
# =========================

analysis = {
    "txid": data["txid"],
    "is_coinbase": is_coinbase,
    "number_of_inputs": len(data["vin"]),
    "number_of_outputs": len(data["vout"]),
    "weight": weight,
    "vsize": vsize
}

# =========================
# Normal transaction
# =========================

if not is_coinbase:

    input_value = sum(
        vin["prevout"]["value"]
        for vin in data["vin"]
        if vin.get("prevout")
    )

    fee = input_value - output_value

    if vsize is not None and vsize > 0:
        fee_rate = fee / vsize
    else:
        fee_rate = None

    # Simple local classification
    if fee_rate is None:
        fee_level = "unknown"
    elif fee_rate < 5:
        fee_level = "low"
    elif fee_rate < 20:
        fee_level = "normal"
    elif fee_rate < 100:
        fee_level = "high"
    else:
        fee_level = "very_high"

    analysis.update({
        "input_value_sats": input_value,
        "input_value_btc": input_value / 100_000_000,
        "output_value_sats": output_value,
        "output_value_btc": output_value / 100_000_000,
        "fee_sats": fee,
        "fee_btc": fee / 100_000_000,
        "fee_rate_sat_vb": fee_rate,
        "fee_level": fee_level
    })

    print("\n=== Values ===")
    print("Total input:", input_value, "sats")
    print("Total input:", input_value / 100_000_000, "BTC")

    print("Total output:", output_value, "sats")
    print("Total output:", output_value / 100_000_000, "BTC")

    print("Fee:", fee, "sats")
    print("Fee in BTC:", fee / 100_000_000)

    print("\n=== Fee analysis ===")
    print("Weight:", weight, "WU")
    print("Virtual size:", vsize, "vB")

    if fee_rate is not None:
        print("Fee rate:", round(fee_rate, 2), "sat/vB")
        print("Fee level:", fee_level)

# =========================
# Coinbase transaction
# =========================

else:

    analysis.update({
        "output_value_sats": output_value,
        "output_value_btc": output_value / 100_000_000,
        "fee_sats": None,
        "fee_btc": None,
        "fee_rate_sat_vb": None,
        "fee_level": "coinbase"
    })

    print("\n=== Coinbase transaction ===")
    print("This transaction creates the block reward.")
    print("There are no normal UTXOs used as inputs.")

    print("Total output:", output_value, "sats")
    print("Total output:", output_value / 100_000_000, "BTC")

    print("Weight:", weight, "WU")
    print("Virtual size:", vsize, "vB")

# =========================
# Inputs
# =========================

print("\n=== Inputs ===")

for i, vin in enumerate(data["vin"]):

    if vin.get("is_coinbase"):
        print(f"Input {i}: Coinbase input")

    elif vin.get("prevout"):
        prevout = vin["prevout"]

        address = prevout.get(
            "scriptpubkey_address",
            "No standard address"
        )

        value = prevout["value"]

        print(
            f"Input {i}:",
            address,
            "-",
            value,
            "sats",
            f"({value / 100_000_000} BTC)"
        )

# =========================
# Outputs
# =========================

print("\n=== Outputs ===")

for i, output in enumerate(data["vout"]):

    address = output.get(
        "scriptpubkey_address",
        "No standard address"
    )

    value = output["value"]

    print(
        f"Output {i}:",
        address,
        "-",
        value,
        "sats",
        f"({value / 100_000_000} BTC)"
    )

# =========================
# Create folder
# =========================

os.makedirs("transactions", exist_ok=True)

# =========================
# Save raw + analysis
# =========================

result = {
    "raw_transaction": data,
    "analysis": analysis
}

filename = f"transactions/{data['txid']}.json"

with open(filename, "w", encoding="utf-8") as f:
    json.dump(
        result,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\n=== Saved ===")
print(f"Transaction saved in: {filename}")