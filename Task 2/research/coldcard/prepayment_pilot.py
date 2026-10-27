"""Bounded source-history collection and block-cutoff-safe descriptive features."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
from statistics import median
import urllib.request

from build_source_registry import artifacts as registry_artifacts, digest, json_bytes, sat
from collect_theft_seeds import check_history

FEATURE_NAMES = (
    "confirmed_tx_count", "receipt_tx_count", "spending_tx_count",
    "received_output_count", "spent_output_count", "received_sat", "spent_sat",
    "balance_sat", "unspent_output_count", "active_block_count",
    "activity_span_blocks", "blocks_since_first_activity", "blocks_since_last_activity",
    "median_spending_tx_fee_rate_sat_vb")


def load_protocol(path):
    path = Path(path)
    protocol = json.loads(path.read_bytes())
    original = path.parent / protocol["registry_protocol_file"]
    if digest(original.read_bytes()) != protocol["registry_protocol_sha256"]:
        raise ValueError("Registry protocol checksum mismatch")
    files, _ = registry_artifacts(original)
    if digest(files["addresses.json"]) != protocol["registry_address_table_sha256"]:
        raise ValueError("Registry address table checksum mismatch")
    rows = [r for r in json.loads(files["addresses.json"])["records"]
            if protocol["population_scope"] in r["scopes"]]
    observations = {r["evidence_id"]: r for r in
                    map(json.loads, files["input_evidence.jsonl"].decode().splitlines())}
    def key(row):
        return digest((protocol["sampling_prefix"] + row["address"]).encode())
    selected = sorted(rows, key=key)[:protocol["sample_size"]]
    if len(selected) != protocol["sample_size"]:
        raise ValueError("Insufficient source population")
    records = []
    for index, row in enumerate(selected, 1):
        if len(row["payment_txids"]) != 1:
            raise ValueError("Pilot requires one unambiguous reference payment per source")
        obs = observations[row["evidence_ids"][0]]
        records.append(dict(pilot_id=f"source_{index:02d}", address=row["address"],
                            address_sha256=digest(row["address"].encode()),
                            payment_txid=obs["payment_txid"], cutoff_height=obs["block_height"],
                            cutoff_block_hash=obs["block_hash"],
                            registry_input_slots=row["spent_previous_output_count"]))
    return protocol, records


def get_json(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.load(response)


def collect_one(record, protocol):
    base, address = protocol["provider"], record["address"]
    def get(endpoint):
        return get_json(base + endpoint, protocol["timeout_seconds"])
    before = get(f"/address/{address}")
    transactions, exhausted, cursor = [], False, ""
    for _ in range(protocol["max_pages_per_address"]):
        page = get(f"/address/{address}/txs/chain" + ("/" + cursor if cursor else ""))
        if not page:
            exhausted = True
            break
        transactions.extend(page)
        cursor = page[-1]["txid"]
    after = get(f"/address/{address}")
    if before.get("address") != address or after.get("address") != address:
        raise ValueError("Provider address mismatch")
    audit = check_history(address, transactions, before, after, exhausted)
    return dict(address=address, provider=base, before=before, after=after,
                audit=audit, transactions=transactions,
                collected_at=datetime.now(timezone.utc).isoformat())


def collect(protocol_path, output):
    protocol, records = load_protocol(protocol_path)
    output.mkdir(parents=True, exist_ok=False)
    (output / "raw").mkdir()
    manifest = dict(schema_version=1, protocol_sha256=digest(protocol_path.read_bytes()),
                    selection_sha256=digest(json_bytes(records)),
                    population_size=500, sample_size=len(records), provider=protocol["provider"],
                    results=[])
    with ThreadPoolExecutor(max_workers=protocol["workers"]) as pool:
        futures = {pool.submit(collect_one, r, protocol): r for r in records}
        for future in as_completed(futures):
            record = futures[future]
            item = {k: record[k] for k in ("pilot_id", "address_sha256", "cutoff_height", "registry_input_slots")}
            try:
                data = future.result()
                raw = gzip.compress(json_bytes(data), mtime=0)
                filename = f"raw/{record['pilot_id']}.json.gz"
                (output / filename).write_bytes(raw)
                item.update(file=filename, sha256=digest(raw), bytes=len(raw),
                            collected_at=data["collected_at"], history_audit=data["audit"])
            except Exception as error:
                item["error"] = type(error).__name__ + ": " + str(error)
            manifest["results"].append(item)
            manifest["results"].sort(key=lambda r: r["pilot_id"])
            (output / "collection_manifest.json").write_bytes(json_bytes(manifest))
            print(record["pilot_id"] + ": " + ("collected" if "file" in item else "failed"), flush=True)


def normalize_prefix(address, transactions, cutoff_height):
    """Publish only prior-block evidence; never read future spent-status flags."""
    prefix = []
    for tx in transactions:
        if not tx["status"]["confirmed"]:
            raise ValueError("Unconfirmed transaction in confirmed history")
        height = tx["status"]["block_height"]
        if height >= cutoff_height:
            continue
        received = [dict(outpoint_id=digest(f"{tx['txid']}:{n}".encode()),
                         value_sat=sat(o["value"]))
                    for n, o in enumerate(tx["vout"])
                    if o.get("scriptpubkey_address") == address]
        spent = [dict(outpoint_id=digest(f"{i['txid']}:{i['vout']}".encode()),
                      value_sat=sat(i["prevout"]["value"]))
                 for i in tx["vin"]
                 if (i.get("prevout") or {}).get("scriptpubkey_address") == address]
        if not received and not spent:
            raise ValueError("History transaction unrelated to source")
        prefix.append(dict(transaction_id=digest(tx["txid"].encode()), height=height,
                           received=received, spent=spent,
                           spending_tx_fee_sat=sat(tx["fee"]) if spent else None,
                           spending_tx_vsize_vb=(tx["weight"] + 3)//4 if spent else None))
    return sorted(prefix, key=lambda r: (r["height"], r["transaction_id"]))


def features(prefix, cutoff_height):
    received, spent, ids, rates = {}, {}, set(), []
    for tx in prefix:
        if type(tx["height"]) is not int or tx["height"] >= cutoff_height:
            raise ValueError("Payment-block or future evidence in prefix")
        if tx["transaction_id"] in ids:
            raise ValueError("Duplicate prefix transaction")
        ids.add(tx["transaction_id"])
        for field, target in (("received", received), ("spent", spent)):
            for item in tx[field]:
                key = item["outpoint_id"]
                if key in target:
                    raise ValueError("Duplicate prefix outpoint")
                target[key] = (sat(item["value_sat"]), tx["height"])
        if tx["spent"]:
            if type(tx["spending_tx_vsize_vb"]) is not int or tx["spending_tx_vsize_vb"] <= 0:
                raise ValueError("Invalid spending transaction virtual size")
            rates.append(sat(tx["spending_tx_fee_sat"]) / tx["spending_tx_vsize_vb"])
    for key, (value, height) in spent.items():
        if key not in received or received[key][0] != value or received[key][1] > height:
            raise ValueError("Historical spent output absent or inconsistent with prior receipt")
    heights = {t["height"] for t in prefix}
    received_sat, spent_sat = sum(v for v, _ in received.values()), sum(v for v, _ in spent.values())
    result = dict(confirmed_tx_count=len(prefix), receipt_tx_count=sum(bool(t["received"]) for t in prefix),
                  spending_tx_count=sum(bool(t["spent"]) for t in prefix),
                  received_output_count=len(received), spent_output_count=len(spent),
                  received_sat=received_sat, spent_sat=spent_sat, balance_sat=received_sat-spent_sat,
                  unspent_output_count=len(received.keys()-spent.keys()), active_block_count=len(heights),
                  activity_span_blocks=max(heights)-min(heights) if heights else None,
                  blocks_since_first_activity=cutoff_height-min(heights) if heights else None,
                  blocks_since_last_activity=cutoff_height-max(heights) if heights else None,
                  median_spending_tx_fee_rate_sat_vb=median(rates) if rates else None)
    assert set(result) == set(FEATURE_NAMES)
    return result


def analyze(protocol_path, output):
    protocol, selected = load_protocol(protocol_path)
    manifest = json.loads((output / "collection_manifest.json").read_bytes())
    if manifest["protocol_sha256"] != digest(protocol_path.read_bytes()) or manifest["selection_sha256"] != digest(json_bytes(selected)):
        raise ValueError("Pilot protocol/selection mismatch")
    collected = {r["pilot_id"]: r for r in manifest["results"]}
    if len(collected) != len(manifest["results"]) or set(collected) != {r["pilot_id"] for r in selected}:
        raise ValueError("Pilot collection manifest coverage mismatch")
    proofs, rows = [], []
    for record in selected:
        item = collected[record["pilot_id"]]
        row = dict(pilot_id=record["pilot_id"], split_group=protocol["case_id"],
                   cutoff_height=record["cutoff_height"], compromise_label=None, hardware_label=None,
                   status="unavailable", features=None)
        if "file" not in item:
            row["reason"] = item.get("error", "Missing snapshot")
        else:
            raw = (output / item["file"]).read_bytes()
            if digest(raw) != item["sha256"]:
                raise ValueError("Collected history checksum mismatch")
            history = json.loads(gzip.decompress(raw))
            address = record["address"]
            if history["address"] != address or any(history[k].get("address") != address for k in ("before", "after")):
                raise ValueError("Collected source/history mismatch")
            audit = check_history(address, history["transactions"], history["before"], history["after"],
                                  history["audit"]["pagination_exhausted"])
            if not audit["coverage_complete_by_provider_counters"]:
                row["reason"] = "Incomplete or unstable provider history; features not computed"
            else:
                payments = [t for t in history["transactions"] if t["txid"] == record["payment_txid"]]
                if len(payments) != 1 or (payments[0]["status"]["block_height"], payments[0]["status"]["block_hash"]) != (record["cutoff_height"], record["cutoff_block_hash"]):
                    raise ValueError("Source payment absent or cutoff block anchor mismatch")
                prefix = normalize_prefix(address, history["transactions"], record["cutoff_height"])
                row.update(status="computed", features=features(prefix, record["cutoff_height"]))
                proofs.append(dict(pilot_id=record["pilot_id"], cutoff_height=record["cutoff_height"], transactions=prefix))
        rows.append(row)
    calculated = [r for r in rows if r["status"] == "computed"]
    columns = {name:[r["features"][name] for r in calculated] for name in FEATURE_NAMES}
    variable = [name for name,values in columns.items() if len({v for v in values if v is not None})>1]
    summary = dict(schema_version=1, status="complete" if len(calculated)==len(selected) else "partial",
                   case_id=protocol["case_id"], selected_sources=len(selected), computed_sources=len(calculated),
                   unavailable_sources=len(rows)-len(calculated), feature_count=len(FEATURE_NAMES),
                   sources_with_prior_spending=sum(r["features"]["spending_tx_count"]>0 for r in calculated),
                   prior_transaction_count=sum(r["features"]["confirmed_tx_count"] for r in calculated),
                   sample_sources_with_multiple_payment_inputs=sum(r["registry_input_slots"]>1 for r in selected),
                   all_missing_features=[name for name,values in columns.items() if not any(v is not None for v in values)],
                   constant_nonmissing_features=[name for name,values in columns.items() if values and
                                                all(v is not None for v in values) and len(set(values))==1],
                   duplicate_variable_feature_pairs=[[a,b] for i,a in enumerate(variable)
                                                      for b in variable[i+1:] if columns[a]==columns[b]],
                   feature_ranges={name: dict(min=min(v),max=max(v),nonmissing=len(v)) if
                                   (v:=[r["features"][name] for r in calculated if r["features"][name] is not None])
                                   else dict(min=None,max=None,nonmissing=0) for name in FEATURE_NAMES},
                   protocol_sha256=digest(protocol_path.read_bytes()),
                   generator_script_sha256=digest(Path(__file__).read_bytes()),
                   collection_manifest_sha256=digest((output/"collection_manifest.json").read_bytes()),
                   training_performed=False, incident_groups=1,
                   limitations=["Retrospective case-conditioned sample, not prospective detection or an independent test",
                                "All compromise/hardware labels remain unknown; no legitimate controls",
                                "Entire payment block excluded; intra-block prior activity is deliberately omitted",
                                "Sample is small and not representative; collection failures are not replaced",
                                "Complete provider counters do not prove cryptographic inclusion or historical API availability",
                                "Address history is not a complete wallet/entity history; fee features concern spending transactions, not proven device policy"])
    return {"prefix_evidence.json":json_bytes(proofs), "features.json":json_bytes(rows), "summary.json":json_bytes(summary)}


def verify(protocol_path, output):
    protocol, selected = load_protocol(protocol_path)
    planned = {r["pilot_id"]:r for r in selected}
    summary = json.loads((output/"summary.json").read_bytes())
    if summary["protocol_sha256"] != digest(protocol_path.read_bytes()) or summary["collection_manifest_sha256"] != digest((output/"collection_manifest.json").read_bytes()):
        raise ValueError("Published pilot input fingerprint mismatch")
    proofs = json.loads((output/"prefix_evidence.json").read_bytes())
    feature_rows = json.loads((output/"features.json").read_bytes())
    rows = {r["pilot_id"]:r for r in feature_rows}
    if len(rows)!=len(feature_rows) or set(rows)!=set(planned):
        raise ValueError("Published pilot row selection mismatch")
    for key,row in rows.items():
        if row["cutoff_height"] != planned[key]["cutoff_height"] or row["split_group"] != protocol["case_id"]:
            raise ValueError("Published cutoff or incident group differs from selection")
        if row["compromise_label"] is not None or row["hardware_label"] is not None:
            raise ValueError("Published evidence cannot supply supervised labels")
    expected = {key:r for key,r in rows.items() if r["status"]=="computed"}
    if len({p["pilot_id"] for p in proofs}) != len(proofs) or {p["pilot_id"] for p in proofs} != set(expected):
        raise ValueError("Prefix/feature coverage mismatch")
    for proof in proofs:
        row = rows[proof["pilot_id"]]
        if row["cutoff_height"] != proof["cutoff_height"] or row["features"] != features(proof["transactions"],proof["cutoff_height"]):
            raise ValueError("Prefix/feature reproduction mismatch")
    print(f"Offline prefix evidence reproduces {len(proofs)} feature rows")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("collect", "analyze", "reproduce", "verify"))
    parser.add_argument("protocol", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "collect":
        collect(args.protocol,args.output)
    elif args.command == "verify":
        verify(args.protocol,args.output)
    else:
        files=analyze(args.protocol,args.output)
        if args.command == "reproduce":
            for name,raw in files.items():
                if (args.output/name).read_bytes()!=raw:
                    raise ValueError("Raw-history reproduction mismatch: "+name)
        else:
            if any((args.output/name).exists() for name in files):
                raise ValueError("Analysis output already exists")
            for name,raw in files.items():
                (args.output/name).write_bytes(raw)
        print(files["summary.json"].decode())


if __name__ == "__main__":
    main()
