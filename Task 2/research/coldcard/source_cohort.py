"""Resumable bounded collection for the fixed Coldcard source-address cohort."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import tempfile

from build_source_registry import digest, json_bytes
import multiinput_pilot as helper


def atomic_write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name+".", delete=False) as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
        temporary=Path(stream.name)
    temporary.replace(path)


def plan(protocol_path):
    protocol,records,population,_=helper.load(protocol_path)
    if population!=500 or len(records)!=500:
        raise ValueError("Expected the fixed 500-source candidate cohort")
    for i,record in enumerate(records,1):
        record["pilot_id"]=f"cohort_{i:04d}"
    return protocol,records


def empty_state(protocol_path,records):
    return dict(schema_version=1,protocol_sha256=digest(protocol_path.read_bytes()),
                plan_sha256=digest(json_bytes(records)),entries={},batches=[])


def validate(state,protocol_path,records,work=None):
    if state["protocol_sha256"]!=digest(protocol_path.read_bytes()) or state["plan_sha256"]!=digest(json_bytes(records)):
        raise ValueError("Checkpoint protocol/plan mismatch")
    targets={r["pilot_id"]:r for r in records}
    for key,entry in state["entries"].items():
        if key not in targets or entry["source_id"]!=key:raise ValueError("Unknown source in checkpoint")
        record=targets[key]
        if (entry["address_sha256"],entry["cutoff_height"])!=(record["address_sha256"],record["cutoff_height"]):
            raise ValueError("Checkpoint source/cutoff mismatch")
        if entry["compromise_label"] is not None or entry["hardware_label"] is not None:
            raise ValueError("Unsupported supervised label")
        if entry["status"]=="complete":
            if not entry["history_audit"].get("coverage_complete_by_provider_counters"):
                raise ValueError("Complete checkpoint requires audited history")
            if helper.fixed.features(entry["prefix"],record["cutoff_height"])!=entry["features"]:
                raise ValueError("Checkpoint feature/evidence mismatch")
        elif entry["status"] not in ("incomplete","error") or entry["features"] is not None or entry["prefix"] is not None:
            raise ValueError("Invalid unavailable checkpoint entry")
        if work is not None and entry.get("raw_file"):
            path=work/entry["raw_file"]
            if path.exists() and digest(path.read_bytes())!=entry["raw_sha256"]:
                raise ValueError("Cached raw history checksum mismatch")
    used=set();running=0
    for batch in state["batches"]:
        ids=batch["source_ids"]
        if len(set(ids))!=len(ids) or used.intersection(ids) or not set(ids)<=set(targets):
            raise ValueError("Invalid repeated batch plan")
        used.update(ids)
        if batch["status"] not in ("running","completed"):
            raise ValueError("Invalid batch status")
        if batch["status"]=="completed" and not set(ids)<=set(state["entries"]):
            raise ValueError("Completed batch lacks results")
        running+=batch["status"]=="running"
    if running>1:raise ValueError("Multiple unfinished batches")


def base_entry(record,origin):
    return dict(source_id=record["pilot_id"],address_sha256=record["address_sha256"],
                cutoff_height=record["cutoff_height"],origin=origin,status="error",
                compromise_label=None,hardware_label=None,features=None,prefix=None)


def from_history(record,history,raw,origin):
    entry=base_entry(record,origin)
    audit=helper.check_history(record["address"],history["transactions"],history["before"],history["after"],
                               history["audit"]["pagination_exhausted"])
    entry.update(raw_file=f"raw/{record['pilot_id']}.json.gz",raw_sha256=digest(raw),
                 raw_bytes=len(raw),collected_at=history.get("collected_at"),history_audit=audit)
    prefix=helper.prefix_for(record,history)
    if prefix is None:
        entry.update(status="incomplete",reason="Bounded history incomplete/unstable; no feature vector")
    else:
        entry.update(status="complete",prefix=prefix,features=helper.fixed.features(prefix,record["cutoff_height"]))
    return entry


def import_reuse(protocol_path,protocol,records,state,work):
    by_hash={r["address_sha256"]:r for r in records}
    for source in protocol.get("reuse_sources",[]):
        inputs={}
        for key in ("manifest","features","proof"):
            path=protocol_path.parent/source[key+"_file"];raw=path.read_bytes()
            if digest(raw)!=source[key+"_sha256"]:raise ValueError("Reuse input checksum mismatch")
            inputs[key]=json.loads(raw)
        rows={r["pilot_id"]:r for r in inputs["features"]}
        proofs={r["pilot_id"]:r for r in inputs["proof"]}
        for item in inputs["manifest"]["results"]:
            record=by_hash.get(item["address_sha256"])
            if record is None or record["pilot_id"] in state["entries"]:continue
            row=rows[item["pilot_id"]]
            if row["status"]!="computed":continue
            proof=proofs[item["pilot_id"]]
            if row["cutoff_height"]!=record["cutoff_height"] or proof["cutoff_height"]!=record["cutoff_height"]:
                raise ValueError("Reuse cutoff mismatch")
            if row["compromise_label"] is not None or row["hardware_label"] is not None:
                raise ValueError("Reuse contains unsupported labels")
            if not item["history_audit"]["coverage_complete_by_provider_counters"]:
                raise ValueError("Reuse history was not complete")
            entry=base_entry(record,"reuse")
            entry.update(status="complete",features=row["features"],prefix=proof["transactions"],
                         raw_file=f"raw/{record['pilot_id']}.json.gz",raw_sha256=item["sha256"],
                         raw_bytes=item["bytes"],collected_at=item["collected_at"],history_audit=item["history_audit"],
                         reused_manifest=source["manifest_file"],reused_manifest_sha256=source["manifest_sha256"])
            source_raw=protocol_path.parent/Path(source["manifest_file"]).parent/item["file"]
            target=work/entry["raw_file"]
            if source_raw.exists():
                raw=source_raw.read_bytes()
                if digest(raw)!=item["sha256"]:raise ValueError("Reuse raw checksum mismatch")
                checked=from_history(record,json.loads(gzip.decompress(raw)),raw,"reuse")
                if checked["features"]!=entry["features"]:raise ValueError("Reuse raw/prefix mismatch")
                if target.exists() and target.read_bytes()!=raw:raise ValueError("Existing raw cache differs")
                if not target.exists():atomic_write(target,raw)
            state["entries"][record["pilot_id"]]=entry
            atomic_write(work/"state.json",json_bytes(state))


def run(protocol_path,work,limit,restore=None):
    protocol,records=plan(protocol_path)
    if not 0<=limit<=protocol["default_batch_size"]:
        raise ValueError("Run limit exceeds the fixed per-run budget")
    work.mkdir(parents=True,exist_ok=True)
    state_path=work/"state.json"
    if state_path.exists():state=json.loads(state_path.read_bytes())
    elif restore is not None:state=json.loads(restore.read_bytes())
    else:state=empty_state(protocol_path,records)
    validate(state,protocol_path,records,work)
    atomic_write(state_path,json_bytes(state))
    import_reuse(protocol_path,protocol,records,state,work)
    # Recover a complete raw response saved just before an interrupted state update.
    for record in records:
        path=work/f"raw/{record['pilot_id']}.json.gz"
        if record["pilot_id"] not in state["entries"] and path.exists():
            raw=path.read_bytes()
            state["entries"][record["pilot_id"]]=from_history(record,json.loads(gzip.decompress(raw)),raw,"recovered")
            atomic_write(state_path,json_bytes(state))
    active=next((b for b in state["batches"] if b["status"]=="running"),None)
    if active is None and limit:
        ids=[r["pilot_id"] for r in records if r["pilot_id"] not in state["entries"]][:limit]
        if ids:
            active=dict(batch_id=len(state["batches"])+1,source_ids=ids,status="running")
            state["batches"].append(active)
    if active is not None:
        by_id={r["pilot_id"]:r for r in records}
        selected=[by_id[key] for key in active["source_ids"] if key not in state["entries"]][:limit]
        atomic_write(state_path,json_bytes(state))
        with ThreadPoolExecutor(max_workers=protocol["workers"]) as pool:
            pending={pool.submit(helper.fixed.collect_one,r,protocol):r for r in selected}
            for future in as_completed(pending):
                record=pending[future];entry=base_entry(record,"network")
                try:
                    history=future.result();raw=gzip.compress(json_bytes(history),mtime=0)
                    path=work/f"raw/{record['pilot_id']}.json.gz"
                    if path.exists():raise ValueError("Raw evidence already exists")
                    atomic_write(path,raw)
                    entry.update(raw_file=f"raw/{record['pilot_id']}.json.gz",raw_sha256=digest(raw),raw_bytes=len(raw))
                    entry=from_history(record,history,raw,"network")
                except Exception as error:
                    entry["reason"]=type(error).__name__+": "+str(error)
                state["entries"][record["pilot_id"]]=entry
                atomic_write(state_path,json_bytes(state))
                print(record["pilot_id"]+": "+entry["status"],flush=True)
        if all(key in state["entries"] for key in active["source_ids"]):active["status"]="completed"
    validate(state,protocol_path,records,work)
    atomic_write(state_path,json_bytes(state))
    print(json.dumps(counts(state,len(records)),indent=2))
    return state


def counts(state,population):
    entries=list(state["entries"].values());complete=[e for e in entries if e["status"]=="complete"]
    return dict(population_sources=population,complete_sources=len(complete),
                incomplete_sources=sum(e["status"]=="incomplete" for e in entries),
                error_sources=sum(e["status"]=="error" for e in entries),pending_sources=population-len(entries),
                reused_sources=sum(e["origin"]=="reuse" for e in entries),
                prior_transaction_observations=sum(e["features"]["confirmed_tx_count"] for e in complete),
                sources_with_prior_spending=sum(e["features"]["spending_tx_count"]>0 for e in complete),
                incident_groups=1,training_performed=False)


def exports(state,protocol_path,records):
    rows=[dict(source_id=key,split_group="coldcard_2026",cutoff_height=e["cutoff_height"],
               status=e["status"],features=e["features"],compromise_label=None,hardware_label=None)
          for key,e in sorted(state["entries"].items())]
    checkpoint=json_bytes(state)
    progress=counts(state,len(records))
    progress.update(protocol_sha256=digest(protocol_path.read_bytes()),checkpoint_sha256=digest(checkpoint),
                    feature_count=len(helper.fixed.FEATURE_NAMES),
                    feature_extractor_sha256=digest(Path(helper.fixed.__file__).read_bytes()),
                    verified_compromise_labels=0,verified_hardware_labels=0,
                    limitations=["Coverage, not classifier accuracy; one case and unknown compromise/hardware labels",
                                 "Fixed pending order and fixed batch before requests; errors are not replaced or retried automatically",
                                 "All predictor evidence precedes the reference-payment block; no current spent flags",
                                 "Raw API histories are local; published checkpoints contain the normalized prefix evidence",
                                 "Complete stable provider counters are not cryptographic inclusion proofs"])
    return {"checkpoint.json":checkpoint,"features.json":json_bytes(rows),"progress.json":json_bytes(progress)}


def snapshot(protocol_path,work,output):
    _,records=plan(protocol_path);state=json.loads((work/"state.json").read_bytes())
    validate(state,protocol_path,records,work)
    output.mkdir(parents=True,exist_ok=False)
    for name,raw in exports(state,protocol_path,records).items():(output/name).write_bytes(raw)


def verify(protocol_path,output):
    _,records=plan(protocol_path);state=json.loads((output/"checkpoint.json").read_bytes())
    validate(state,protocol_path,records)
    for name,raw in exports(state,protocol_path,records).items():
        if (output/name).read_bytes()!=raw:raise ValueError("Snapshot reproduction mismatch: "+name)
    print("Offline checkpoint and feature reproduction passed")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("run","snapshot","verify"))
    parser.add_argument("protocol",type=Path);parser.add_argument("path",type=Path)
    parser.add_argument("--limit",type=int,default=20)
    parser.add_argument("--restore",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.command=="run":run(args.protocol,args.path,args.limit,args.restore)
    elif args.command=="verify":verify(args.protocol,args.path)
    else:
        if args.output is None:parser.error("snapshot requires --output")
        snapshot(args.protocol,args.path,args.output)


if __name__=="__main__":main()
