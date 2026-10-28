"""Extend the source pilot while keeping its feature extractor byte-for-byte fixed."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import json
from pathlib import Path

import prepayment_pilot as fixed
from build_source_registry import artifacts, digest, json_bytes
from collect_theft_seeds import check_history


def choose(rows, protocol):
    eligible = [r for r in rows if protocol["population_scope"] in r["scopes"]
                and r["spent_previous_output_count"] >= protocol["min_payment_inputs"]]
    selected = sorted(eligible, key=lambda r: digest((protocol["sampling_prefix"]+r["address"]).encode()))[:protocol["sample_size"]]
    if len(selected) != protocol["sample_size"]:
        raise ValueError("Insufficient eligible source population")
    return selected, len(eligible)


def load(path):
    protocol = json.loads(path.read_bytes())
    original = path.parent/protocol["registry_protocol_file"]
    if digest(original.read_bytes()) != protocol["registry_protocol_sha256"]:
        raise ValueError("Registry protocol checksum mismatch")
    if digest(Path(fixed.__file__).read_bytes()) != protocol["feature_extractor_sha256"]:
        raise ValueError("Frozen feature extractor checksum mismatch")
    files, _ = artifacts(original)
    if digest(files["addresses.json"]) != protocol["registry_address_table_sha256"]:
        raise ValueError("Source registry checksum mismatch")
    comparison_raw = (path.parent/protocol["comparison_feature_file"]).read_bytes()
    if digest(comparison_raw) != protocol["comparison_feature_sha256"]:
        raise ValueError("Comparison cohort checksum mismatch")
    selected, population = choose(json.loads(files["addresses.json"])["records"],protocol)
    evidence = {r["evidence_id"]:r for r in map(json.loads,files["input_evidence.jsonl"].decode().splitlines())}
    records = []
    for n,row in enumerate(selected,1):
        if len(row["payment_txids"]) != 1:
            raise ValueError("Reference payment must be unambiguous")
        obs=evidence[row["evidence_ids"][0]]
        records.append(dict(pilot_id=f"multi_{n:02d}",address=row["address"],
                            address_sha256=digest(row["address"].encode()),
                            payment_txid=obs["payment_txid"],cutoff_height=obs["block_height"],
                            cutoff_block_hash=obs["block_hash"],
                            registry_input_slots=row["spent_previous_output_count"]))
    return protocol,records,population,json.loads(comparison_raw)


def collect(protocol_path,output):
    protocol,records,population,_=load(protocol_path)
    output.mkdir(parents=True,exist_ok=False);(output/"raw").mkdir()
    manifest=dict(protocol_sha256=digest(protocol_path.read_bytes()),
                  selection_sha256=digest(json_bytes(records)),population_size=population,
                  sample_size=len(records),provider=protocol["provider"],results=[])
    with ThreadPoolExecutor(max_workers=protocol["workers"]) as pool:
        pending={pool.submit(fixed.collect_one,r,protocol):r for r in records}
        for future in as_completed(pending):
            record=pending[future]
            item={k:record[k] for k in ("pilot_id","address_sha256","cutoff_height","registry_input_slots")}
            try:
                data=future.result();raw=gzip.compress(json_bytes(data),mtime=0)
                filename=f"raw/{record['pilot_id']}.json.gz";(output/filename).write_bytes(raw)
                item.update(file=filename,sha256=digest(raw),bytes=len(raw),
                            collected_at=data["collected_at"],history_audit=data["audit"])
            except Exception as error:
                item["error"]=type(error).__name__+": "+str(error)
            manifest["results"].append(item);manifest["results"].sort(key=lambda x:x["pilot_id"])
            (output/"collection_manifest.json").write_bytes(json_bytes(manifest))
            print(record["pilot_id"]+": "+("collected" if "file" in item else "failed"),flush=True)


def prefix_for(record,history):
    address=record["address"]
    if history["address"]!=address or any(history[k].get("address")!=address for k in ("before","after")):
        raise ValueError("Source/history identity mismatch")
    audit=check_history(address,history["transactions"],history["before"],history["after"],
                        history["audit"]["pagination_exhausted"])
    if not audit["coverage_complete_by_provider_counters"]:
        return None
    payment=[t for t in history["transactions"] if t["txid"]==record["payment_txid"]]
    if len(payment)!=1 or (payment[0]["status"]["block_height"],payment[0]["status"]["block_hash"])!=(record["cutoff_height"],record["cutoff_block_hash"]):
        raise ValueError("Reference payment/cutoff anchor mismatch")
    return fixed.normalize_prefix(address,history["transactions"],record["cutoff_height"])


def cohort_summary(rows):
    eligible=[r for r in rows if r["status"]=="computed"]
    return dict(selected=len(rows),computed=len(eligible),
                prior_transactions=sum(r["features"]["confirmed_tx_count"] for r in eligible),
                sources_with_prior_spending=sum(r["features"]["spending_tx_count"]>0 for r in eligible),
                ranges={name:dict(min=min(v),max=max(v),nonmissing=len(v)) if
                        (v:=[r["features"][name] for r in eligible if r["features"][name] is not None])
                        else dict(min=None,max=None,nonmissing=0) for name in fixed.FEATURE_NAMES})


def analyze(protocol_path,output):
    protocol,selected,population,comparison=load(protocol_path)
    manifest_raw=(output/"collection_manifest.json").read_bytes();manifest=json.loads(manifest_raw)
    if manifest["protocol_sha256"]!=digest(protocol_path.read_bytes()) or manifest["selection_sha256"]!=digest(json_bytes(selected)):
        raise ValueError("Collection protocol/selection mismatch")
    collected={r["pilot_id"]:r for r in manifest["results"]}
    if len(collected)!=len(manifest["results"]) or set(collected)!={r["pilot_id"] for r in selected}:
        raise ValueError("Collection coverage mismatch")
    rows,proofs=[],[]
    for record in selected:
        item=collected[record["pilot_id"]]
        row=dict(pilot_id=record["pilot_id"],split_group=protocol["case_id"],
                 cutoff_height=record["cutoff_height"],compromise_label=None,hardware_label=None,
                 status="unavailable",features=None)
        if "file" not in item:
            row["reason"]=item.get("error","Missing snapshot")
        else:
            raw=(output/item["file"]).read_bytes()
            if digest(raw)!=item["sha256"]:raise ValueError("Raw snapshot checksum mismatch")
            prefix=prefix_for(record,json.loads(gzip.decompress(raw)))
            if prefix is None:
                row["reason"]="Incomplete/unstable history; no feature vector"
            else:
                row.update(status="computed",features=fixed.features(prefix,record["cutoff_height"]))
                proofs.append(dict(pilot_id=record["pilot_id"],cutoff_height=record["cutoff_height"],transactions=prefix))
        rows.append(row)
    result=cohort_summary(rows)
    summary=dict(status="complete" if result["computed"]==len(selected) else "partial",
                 case_id=protocol["case_id"],eligible_population=population,feature_count=len(fixed.FEATURE_NAMES),
                 multi_input=result,previous_eight=cohort_summary(comparison),
                 selected_payment_input_counts=[r["registry_input_slots"] for r in selected],
                 protocol_sha256=digest(protocol_path.read_bytes()),
                 collection_manifest_sha256=digest(manifest_raw),
                 feature_extractor_sha256=protocol["feature_extractor_sha256"],
                 driver_sha256=digest(Path(__file__).read_bytes()),
                 comparison_feature_sha256=protocol["comparison_feature_sha256"],
                 incident_groups=1,training_performed=False,verified_compromise_labels=0,verified_hardware_labels=0,
                 limitations=["Small selected subsets; not independent incidents or a population estimate",
                              "Retrospective case-conditioned cohort; hardware/compromise labels remain unknown",
                              "Whole reference-payment block excluded; prior activity in that block is omitted",
                              "Incomplete histories cannot produce zero-valued features; failures are not replaced",
                              "No legitimate controls, model fitting, performance metric or cryptographic inclusion proof"])
    return {"features.json":json_bytes(rows),"prefix_evidence.json":json_bytes(proofs),"summary.json":json_bytes(summary)}


def verify(protocol_path,output):
    protocol,selected,_,_=load(protocol_path);planned={r["pilot_id"]:r for r in selected}
    summary=json.loads((output/"summary.json").read_bytes())
    if summary["protocol_sha256"]!=digest(protocol_path.read_bytes()) or summary["collection_manifest_sha256"]!=digest((output/"collection_manifest.json").read_bytes()):
        raise ValueError("Published input fingerprint mismatch")
    rows=json.loads((output/"features.json").read_bytes());proofs=json.loads((output/"prefix_evidence.json").read_bytes())
    by_id={r["pilot_id"]:r for r in rows}
    if len(by_id)!=len(rows) or set(by_id)!=set(planned):raise ValueError("Published selection mismatch")
    for key,row in by_id.items():
        if row["cutoff_height"]!=planned[key]["cutoff_height"] or row["split_group"]!=protocol["case_id"]:
            raise ValueError("Published cutoff/group mismatch")
        if row["compromise_label"] is not None or row["hardware_label"] is not None:
            raise ValueError("Unsupported supervised label")
        if row["status"]=="unavailable" and row["features"] is not None:
            raise ValueError("Incomplete source must not have a feature vector")
    if len({p["pilot_id"] for p in proofs})!=len(proofs) or {p["pilot_id"] for p in proofs}!={r["pilot_id"] for r in rows if r["status"]=="computed"}:
        raise ValueError("Published evidence coverage mismatch")
    for proof in proofs:
        row=by_id[proof["pilot_id"]]
        if proof["cutoff_height"]!=row["cutoff_height"] or fixed.features(proof["transactions"],proof["cutoff_height"])!=row["features"]:
            raise ValueError("Published feature reproduction mismatch")
    print(f"Offline evidence reproduces {len(proofs)} multi-input source vectors")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("collect","analyze","reproduce","verify"))
    parser.add_argument("protocol",type=Path);parser.add_argument("output",type=Path)
    args=parser.parse_args()
    if args.command=="collect":collect(args.protocol,args.output)
    elif args.command=="verify":verify(args.protocol,args.output)
    else:
        files=analyze(args.protocol,args.output)
        if args.command=="reproduce":
            if any((args.output/n).read_bytes()!=b for n,b in files.items()):
                raise ValueError("Raw-snapshot reproduction mismatch")
        else:
            if any((args.output/n).exists() for n in files):raise ValueError("Analysis output already exists")
            for name,raw in files.items():(args.output/name).write_bytes(raw)
        print(files["summary.json"].decode())


if __name__=="__main__":main()
