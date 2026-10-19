"""Reconstruct the course-address flows without equating relations with theft.

The archive provides selected blocks, not an address history. Optional confirmed
Esplora history is independently reconciled with stable provider counters. Values
are integer satoshis; transaction IDs and outpoint indices prevent double counts.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import tarfile

from audit_coldcard_parents import SEEDS, SOURCE
from collect_theft_seeds import check_history, get

COURSE_ADDRESS = "bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0"


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if value is not None else None


def btc(value):
    sign, value = ("-" if value < 0 else ""), abs(value)
    return f"{sign}{value // 100000000}.{value % 100000000:08d}"


def span(values):
    values = list(values)
    return dict(first_utc=utc(min(values)), last_utc=utc(max(values)),
                seconds=max(values) - min(values)) if values else None


def iter_blocks(path):
    """Do not extract archive members onto disk; validate the JSON block envelope."""
    path = Path(path)
    def checked(block, name):
        if block["hash"] != Path(name).name or block["n_tx"] != len(block["tx"]):
            raise ValueError("Block filename/hash or transaction count mismatch")
        if not block.get("main_chain", False):
            raise ValueError("Non-main-chain block")
        return block
    if path.is_dir():
        for name in sorted(path.iterdir()):
            if name.is_file() and re.fullmatch(r"[0-9a-f]{64}", name.name):
                yield checked(json.loads(name.read_text()), name.name)
    else:
        with tarfile.open(path, "r|gz") as archive:
            for item in archive:
                if item.isfile():
                    yield checked(json.load(archive.extractfile(item)), item.name)


def normalized(block, tx):
    return dict(txid=tx["hash"], index=tx["tx_index"], height=block["height"],
                block_hash=block["hash"], block_time=block["time"], provider_transaction_time=tx["time"],
                inputs=[i.get("prev_out") or {} for i in tx["inputs"]],
                outputs=tx["out"], fee_sat=tx["fee"])


def address_summary(transactions, address, esplora=False):
    """Describe all received outputs and consumed prevouts, each exactly once.

    Input addresses describe sources of funding transactions. They are neither
    owners nor necessarily the source of each particular output in a multi-output
    transaction. Self-change is kept in gross receipts and disclosed explicitly.
    """
    txids, received, spent, source_addresses = set(), {}, {}, set()
    receipts, spends, source_missing, self_receipts = [], [], 0, 0
    for tx in transactions:
        tid = tx["txid"]
        if tid in txids:
            raise ValueError("Duplicate transaction")
        txids.add(tid)
        if esplora:
            inputs = [i.get("prevout") or {} for i in tx["vin"]]
            outputs = tx["vout"]
            refs = [(i.get("txid"), i.get("vout")) for i in tx["vin"]]
            address_key = "scriptpubkey_address"
            timestamp = tx["status"]["block_time"]
        else:
            inputs, outputs = tx["inputs"], tx["outputs"]
            refs = [(i.get("tx_index"), i.get("n")) for i in inputs]
            address_key, timestamp = "addr", tx["block_time"]
        matching = [(i, o) for i, o in enumerate(outputs) if o.get(address_key) == address]
        matched_inputs = [(i, o) for i, o in enumerate(inputs) if o.get(address_key) == address]
        if matching:
            receipts.append((tid, timestamp))
            source_addresses.update(i[address_key] for i in inputs if i.get(address_key))
            source_missing += sum(not i.get(address_key) for i in inputs)
            if matched_inputs:
                self_receipts += len(matching)
            for n, out in matching:
                index = n if esplora else out["n"]
                key = (tid, index)
                if key in received:
                    raise ValueError("Duplicate received outpoint")
                received[key] = out["value"]
        if matched_inputs:
            spends.append(dict(txid=tid, block_time=timestamp,
                              consumed_output_count=len(matched_inputs),
                              consumed_sat=sum(i["value"] for _, i in matched_inputs),
                              all_inputs_from_address=len(matched_inputs) == len(inputs),
                              outputs=[dict(index=n if esplora else o["n"],
                                            address=o.get(address_key), value_sat=o["value"])
                                       for n, o in enumerate(outputs)]))
            for position, prev in matched_inputs:
                key = refs[position]
                if None in key or key in spent:
                    raise ValueError("Missing or duplicate consumed outpoint")
                spent[key] = prev["value"]
    return dict(address=address, receipt_transaction_count=len(receipts),
                received_output_count=len(received), received_sat=sum(received.values()),
                spending_transaction_count=len(spends), spent_output_count=len(spent),
                spent_input_sat=sum(spent.values()),
                observed_receipts_minus_spent_sat=sum(received.values()) - sum(spent.values()),
                funding_transaction_distinct_input_addresses=len(source_addresses),
                funding_transaction_missing_input_address_slots=source_missing,
                self_receipt_output_count=self_receipts,
                receipt_confirmation_span=span(t for _, t in receipts),
                spending_transactions=sorted(spends, key=lambda t: (t["block_time"], t["txid"])))


def reconcile_received_prevouts(transactions, address):
    """Check every consumed address output against its funding transaction.

    Requires a complete confirmed address history. This checks provider records,
    not transaction serialization, signatures, or cryptographic block inclusion.
    """
    by_id = {tx["txid"]: tx for tx in transactions}
    if len(by_id) != len(transactions):
        raise ValueError("Duplicate transaction")
    consumed, amount = set(), 0
    for tx in transactions:
        for item in tx["vin"]:
            previous = item.get("prevout") or {}
            if previous.get("scriptpubkey_address") != address:
                continue
            key = item.get("txid"), item.get("vout")
            if key in consumed:
                raise ValueError("Duplicate consumed outpoint")
            parent = by_id.get(key[0])
            n = key[1]
            if parent is None or type(n) is not int or not 0 <= n < len(parent["vout"]):
                raise ValueError("Consumed address output absent from complete history")
            actual = parent["vout"][n]
            if (actual.get("scriptpubkey_address"), actual["value"]) != (address, previous["value"]):
                raise ValueError("Consumed prevout differs from recorded received output")
            if (actual.get("scriptpubkey") is not None and previous.get("scriptpubkey") is not None
                    and actual["scriptpubkey"] != previous["scriptpubkey"]):
                raise ValueError("Consumed prevout script differs from recorded received output")
            if parent["status"]["block_height"] > tx["status"]["block_height"]:
                raise ValueError("Consumed output confirmed after its spending transaction")
            consumed.add(key)
            amount += actual["value"]
    return dict(consumed_outpoints_reconciled=len(consumed), consumed_sat=amount,
                cryptographic_inclusion_verified=False)


def check_parent_report(data, seeds, parents):
    """Cross-check the prior independent parent audit, including each row."""
    wanted = {}
    for seed in seeds.values():
        for previous in seed["inputs"]:
            wanted.setdefault(previous["tx_index"], set()).add(previous["n"])
    expected_summary = dict(source=SOURCE,
        source_attributed_seeds_found=sorted(seeds),
        source_attributed_seeds_missing=sorted(SEEDS - seeds.keys()),
        distinct_parent_indices_requested=len(wanted),
        parent_transactions_found=len(parents),
        parent_transactions_missing=len(wanted.keys() - parents.keys()))
    for key, expected in expected_summary.items():
        if data.get(key) != expected:
            raise ValueError(f"Parent audit summary mismatch: {key}")
    expected = {}
    for index, parent in parents.items():
        expected[parent["txid"]] = dict(txid=parent["txid"], height=parent["height"],
            input_count=len(parent["inputs"]), output_count=len(parent["outputs"]),
            distinct_input_addresses=len({i["addr"] for i in parent["inputs"] if i.get("addr")}),
            spent_output_indices=sorted(wanted[index]), label="unknown",
            relationship="direct_parent_of_source_attributed_transaction")
    rows = data["parents"]
    actual = {p["txid"]: p for p in rows}
    if len(actual) != len(rows) or actual != expected:
        raise ValueError("Parent audit rows differ from reconstructed graph")
    return dict(rows_reconciled=len(actual), **expected_summary)


def seed_summary(seed, parents):
    """Match the specific parent output spent, not the entire parent output sum."""
    indices, unique_outpoints, collectors, source_addresses = set(), set(), {}, set()
    recovered, found_amount, missing_amount, missing_address_slots = {}, 0, 0, 0
    for previous in seed["inputs"]:
        index, n = previous["tx_index"], previous["n"]
        key = index, n
        if key in unique_outpoints:
            raise ValueError("Duplicate seed input outpoint")
        unique_outpoints.add(key)
        indices.add(index)
        collector = previous.get("addr")
        row = collectors.setdefault(collector, dict(address=collector, input_output_count=0,
                                                    input_value_sat=0, recovered_parent_count=0))
        row["input_output_count"] += 1
        row["input_value_sat"] += previous["value"]
        if index not in parents:
            missing_amount += previous["value"]
            continue
        parent = parents[index]
        matches = [out for out in parent["outputs"] if out["n"] == n]
        if len(matches) != 1:
            raise ValueError("Missing or duplicate parent output index")
        out = matches[0]
        if out["value"] != previous["value"] or out.get("addr") != collector:
            raise ValueError("Parent output value/address differs from seed prevout")
        found_amount += out["value"]
        recovered[index] = parent
    for parent in recovered.values():
        source_addresses.update(i["addr"] for i in parent["inputs"] if i.get("addr"))
        missing_address_slots += sum(not i.get("addr") for i in parent["inputs"])
        parent_collectors = {o.get("addr") for o in parent["outputs"]
                             if (parent["index"], o["n"]) in unique_outpoints}
        for collector in parent_collectors:
            collectors[collector]["recovered_parent_count"] += 1
    amount_in = sum(i["value"] for i in seed["inputs"])
    amount_out = sum(o["value"] for o in seed["outputs"])
    if amount_in != amount_out + seed["fee_sat"]:
        raise ValueError("Seed input/output/fee reconciliation failed")
    times = [p["provider_transaction_time"] for p in recovered.values()]
    block_times = [p["block_time"] for p in recovered.values()]
    return dict(txid=seed["txid"], block_height=seed["height"],
                confirmed_utc=utc(seed["block_time"]),
                provider_transaction_utc=utc(seed["provider_transaction_time"]),
                input_sat=amount_in, output_sat=amount_out, fee_sat=seed["fee_sat"],
                parent_output_count=len(unique_outpoints),
                distinct_parent_transactions_requested=len(indices),
                parent_transactions_recovered=len(recovered),
                parent_transactions_missing=len(indices - recovered.keys()),
                recovered_parent_output_sat=found_amount,
                missing_parent_output_sat=missing_amount,
                recovered_funding_distinct_input_addresses=len(source_addresses),
                recovered_funding_missing_input_address_slots=missing_address_slots,
                collectors=sorted(collectors.values(), key=lambda r: r["address"] or ""),
                recovered_funding_confirmation_span=span(block_times),
                recovered_funding_provider_time_span=span(times),
                first_recovered_funding_to_seed_provider_seconds=(
                    seed["provider_transaction_time"] - min(times) if times else None),
                outputs=[dict(index=o["n"], address=o.get("addr"), value_sat=o["value"],
                              archival_spent_flag=o.get("spent")) for o in seed["outputs"]])


def analyze(blocks, history_path=None, outspends_path=None, parents_path=None):
    seeds, target, seen_blocks, seen_txids = {}, [], set(), set()
    block_times = []
    for block in iter_blocks(blocks):
        if block["hash"] in seen_blocks:
            raise ValueError("Duplicate block")
        seen_blocks.add(block["hash"])
        block_times.append(block["time"])
        for tx in block["tx"]:
            tid = tx["hash"]
            if tid in seen_txids:
                raise ValueError("Duplicate transaction in block archive")
            seen_txids.add(tid)
            if tid in SEEDS:
                seeds[tid] = normalized(block, tx)
            if (any(o.get("addr") == COURSE_ADDRESS for o in tx["out"]) or
                    any((i.get("prev_out") or {}).get("addr") == COURSE_ADDRESS for i in tx["inputs"])):
                target.append(normalized(block, tx))
    wanted = {i["tx_index"] for seed in seeds.values() for i in seed["inputs"]}
    parents, seed_outpoints, observed_spends = {}, {}, []
    for seed in seeds.values():
        for o in seed["outputs"]:
            seed_outpoints[(seed["index"], o["n"])] = seed["txid"]
    for block in iter_blocks(blocks):
        for tx in block["tx"]:
            if tx["tx_index"] in wanted:
                if tx["tx_index"] in parents:
                    raise ValueError("Duplicate provider parent transaction index")
                parents[tx["tx_index"]] = normalized(block, tx)
            for item in tx["inputs"]:
                previous = item.get("prev_out") or {}
                key = previous.get("tx_index"), previous.get("n")
                if key in seed_outpoints:
                    observed_spends.append(dict(parent_txid=seed_outpoints[key], vout=key[1],
                                                spending_txid=tx["hash"], height=block["height"]))
    summaries = [seed_summary(s, parents) for s in sorted(seeds.values(), key=lambda r: r["txid"])]
    if sum(s["parent_output_count"] for s in summaries) != len({(i["tx_index"], i["n"]) for s in seeds.values() for i in s["inputs"]}):
        raise ValueError("An input outpoint is reused across source-attributed seeds")
    report = dict(schema_version=1, course_address=COURSE_ADDRESS,
                  provenance=dict(source_attribution_url=SOURCE,
                                  original_task="aula4.pdf, course address and questions, pages 97 and 99",
                                  labels="Graph roles only; theft and hardware control unknown"),
                  archive=dict(file=Path(blocks).name,
                               sha256=sha256(blocks) if Path(blocks).is_file() else None,
                               block_count=len(seen_blocks), transaction_count=len(seen_txids),
                               block_confirmation_span=span(block_times),
                               coverage="Selected blocks; not complete address history"),
                  source_attributed_seed_count=len(seeds), missing_seed_txids=sorted(SEEDS - seeds.keys()),
                  source_attributed_seeds=summaries,
                  unique_parent_transactions_requested=len(wanted),
                  unique_parent_transactions_recovered=len(parents),
                  selected_seed_output_sum_sat=sum(s["output_sat"] for s in summaries),
                  selected_seed_fee_sum_sat=sum(s["fee_sat"] for s in summaries),
                  observed_seed_output_spends_in_selected_blocks=observed_spends,
                  course_address_in_selected_blocks=address_summary(target, COURSE_ADDRESS))
    if parents_path:
        prior = json.loads(Path(parents_path).read_text())
        report["prior_parent_audit_reconciliation"] = dict(file=Path(parents_path).name,
            sha256=sha256(parents_path), **check_parent_report(prior, seeds, parents))
    if history_path:
        raw = Path(history_path).read_bytes()
        history = json.loads(gzip.decompress(raw) if str(history_path).endswith(".gz") else raw)
        if history["address"] != COURSE_ADDRESS:
            raise ValueError("History address differs from course address")
        if any(history[when].get("address") != COURSE_ADDRESS for when in ("before", "after")):
            raise ValueError("History provider counter address mismatch")
        audit = check_history(COURSE_ADDRESS, history["transactions"], history["before"],
                              history["after"], history["audit"]["pagination_exhausted"])
        if not audit["coverage_complete_by_provider_counters"]:
            raise ValueError("Complete stable provider history required")
        descriptive = address_summary(history["transactions"], COURSE_ADDRESS, esplora=True)
        api_ids = {t["txid"] for t in history["transactions"]}
        archive_ids = {t["txid"] for t in target}
        if archive_ids - api_ids:
            raise ValueError("Selected-block course transactions absent from complete history")
        # Check shared outputs against a second provider schema, not just aggregate totals.
        api_by_id = {t["txid"]: t for t in history["transactions"]}
        for tx in target:
            api = api_by_id[tx["txid"]]
            status = api["status"]
            if (tx["block_hash"], tx["height"], tx["block_time"]) != (
                    status["block_hash"], status["block_height"], status["block_time"]):
                raise ValueError("Providers disagree on transaction block anchor")
            if len(tx["outputs"]) != len(api["vout"]):
                raise ValueError("Providers disagree on output count")
            for o in tx["outputs"]:
                other = api["vout"][o["n"]]
                if (o["value"], o.get("addr")) != (other["value"], other.get("scriptpubkey_address")):
                    raise ValueError("Providers disagree on transaction output")
        report["complete_course_history"] = dict(file=Path(history_path).name,
            sha256=hashlib.sha256(raw).hexdigest(), provider=history["provider"],
            collected_at=history["collected_at"], audit=audit, summary=descriptive,
            extra_txids_outside_archive=sorted(api_ids - archive_ids),
            shared_transaction_outputs_reconciled=len(archive_ids),
            shared_transaction_block_anchors_reconciled=len(archive_ids),
            received_prevouts_reconciliation=reconcile_received_prevouts(history["transactions"], COURSE_ADDRESS))
    if outspends_path:
        result = json.loads(Path(outspends_path).read_text())
        expected = {(s["txid"], o["index"]): o["address"] for s in summaries for o in s["outputs"]}
        records = {(q["txid"], q["vout"]): q for q in result["queries"]}
        if len(records) != len(result["queries"]) or set(records) != set(expected):
            raise ValueError("Outspend query coverage mismatch")
        for (tid, n), q in records.items():
            if q.get("endpoint") != f"{result['provider']}/tx/{tid}/outspend/{n}":
                raise ValueError("Outspend endpoint mismatch")
            if q.get("address") != expected[tid, n]:
                raise ValueError("Outspend destination address mismatch")
            if not q.get("collected_at"):
                raise ValueError("Outspend collection timestamp missing")
        report["current_seed_outspends"] = dict(file=Path(outspends_path).name,
            sha256=sha256(outspends_path), provider=result["provider"], queries=result["queries"],
            cryptographic_inclusion_verified=False)
    report["limitations"] = [
        "A graph relation or textbook selection is not verified theft or hardware-wallet control.",
        "Distinct funding input addresses are not distinct people, victims, or independent cases.",
        "Lifetime gross receipts can include unrelated later deposits and self-change.",
        "Selected-block parent coverage is incomplete; missing source addresses cannot be counted.",
        "Block timestamps date confirmations approximately; provider transaction times are not exact attack times.",
        "Spent flags and Esplora counters are provider observations, not verified cryptographic proofs.",
        "Destination addresses are structural candidates only; neither owner nor intent is established."]
    return report


def markdown(report):
    target = report["course_address_in_selected_blocks"]
    rows = report["source_attributed_seeds"]
    course_seed = next((s for s in rows if any(c["address"] == COURSE_ADDRESS for c in s["collectors"])), None)
    lines = ["# Coldcard case: verified flow findings", "",
        "The roles below describe the observed transactions. The amounts are not an independent estimate of the stolen amount, and addresses prove neither identity nor control of a hardware wallet.", "",
        "## Exercise address", "", f"`{COURSE_ADDRESS}`", "",
        f"Within the {report['archive']['block_count']} supplied blocks, {target['receipt_transaction_count']} transactions fund this address: **{btc(target['received_sat'])} BTC** in total. The file alone provides partial coverage.", ""]
    if report.get("complete_course_history"):
        hist = report["complete_course_history"]
        s = hist["summary"]
        lines += [f"The confirmed history collected on {hist['collected_at']} contains **{hist['audit']['observed']['tx_count']} transactions**, including **{s['receipt_transaction_count']} incoming** and **{s['spending_transaction_count']} outgoing**. Pagination is complete and stable counters have been reconciled: **{btc(s['received_sat'])} BTC received**, **{btc(s['spent_input_sat'])} BTC in consumed outputs**, observed balance **{btc(s['observed_receipts_minus_spent_sat'])} BTC**. This checks the provider's counters; it is not a cryptographic proof.", "",
            f"Incoming transactions have **{s['funding_transaction_distinct_input_addresses']} distinct input addresses**; {s['funding_transaction_missing_input_address_slots']} input slots have no decoded address. This is not a victim count. {len(hist['extra_txids_outside_archive'])} transactions in this history are absent from the supplied blocks.", ""]
        if s["receipt_confirmation_span"]:
            lines += [f"Receipt confirmations range from {s['receipt_confirmation_span']['first_utc']} to {s['receipt_confirmation_span']['last_utc']} ({s['receipt_confirmation_span']['seconds']} seconds). This full activity span is not a demonstrated theft duration.", ""]
        if hist.get("received_prevouts_reconciliation"):
            checked = hist["received_prevouts_reconciliation"]
            lines += [f"The **{checked['consumed_outpoints_reconciled']} consumed outputs** match the received outputs exactly: parent TXID, index, address, value and script where available. Outputs and confirmation anchors for **{hist['shared_transaction_outputs_reconciled']} shared transactions** were compared across the two provider formats. These checks do not cryptographically verify inclusion in blocks.", ""]
    if course_seed:
        lines += ["## Subset spent in the case consolidation", "",
            f"Transaction `{course_seed['txid']}` consumes **{course_seed['parent_output_count']} outputs**, with **{course_seed['parent_transactions_recovered']} parents recovered out of {course_seed['distinct_parent_transactions_requested']} referenced**. The total value of consumed inputs is **{btc(course_seed['input_sat'])} BTC**. The total value of created outputs is **{btc(course_seed['output_sat'])} BTC**, with **{course_seed['fee_sat']} satoshis** in fees.", "",
            f"The recovered parents use **{course_seed['recovered_funding_distinct_input_addresses']} distinct input addresses**. The consolidation's own inputs are at the collection address; counting them as original source addresses would give a misleading result.", "",
            ]
        if course_seed["recovered_funding_confirmation_span"]:
            lines += [f"From the first recovered parent to the consolidation, the gap between the provider's transaction timestamps is **{course_seed['first_recovered_funding_to_seed_provider_seconds']} seconds**. Parent confirmation timestamps span {course_seed['recovered_funding_confirmation_span']['seconds']} seconds. These are distinct measurements and do not establish the actual start of an incident.", ""]
    lines += ["## Other destinations in the case structure", "",
        f"The {len(rows)} consolidations recovered among the {len(SEEDS)} source-attributed transactions yield the following destinations. They remain graph leads; no guilt is inferred.", "",
        "| Destination | Output BTC | Parents recovered / requested | Input addresses of recovered parents |",
        "|---|---:|---:|---:|"]
    for s in rows:
        for o in s["outputs"]:
            lines.append(f"| `{o['address']}` | {btc(o['value_sat'])} | {s['parent_transactions_recovered']} / {s['distinct_parent_transactions_requested']} | {s['recovered_funding_distinct_input_addresses']} |")
    lines += ["", f"Sum of unique outputs from these {len(rows)} consolidations: **{btc(report['selected_seed_output_sum_sat'])} BTC**. Do not add parent deposits to this sum: that would count the same funds again. Of {report['unique_parent_transactions_requested']} distinct referenced parent transactions, {report['unique_parent_transactions_recovered']} are available. The missing transactions prevent a complete count of source addresses.", ""]
    if report.get("prior_parent_audit_reconciliation"):
        lines += [f"The **{report['prior_parent_audit_reconciliation']['rows_reconciled']} rows** in `parents.json` were recomputed from the archive and are identical: TXID, block, input/output counts, distinct input addresses, spent indices and labels are unchanged.", ""]
    if report.get("current_seed_outspends"):
        qs = report["current_seed_outspends"]["queries"]
        good = [q for q in qs if isinstance(q.get("response", {}).get("spent"), bool)]
        spent = sum(q["response"]["spent"] for q in good)
        lines += ["## Subsequent spending", "",
            f"{len(good)} of {len(qs)} outputs have a usable provider response; **{spent} are reported as spent**. The exact dates and URLs of each query appear in `case_flows.json`. An unspent output does not demonstrate cold or hardware storage. The collection-address balance and the status of these consolidation outputs are two different things.", ""]
    lines += ["## Scope and reproduction", "",
        "Numerical results are computed from the data and accompanied by their SHA256 hashes in `case_flows.json`. No amount is converted to dollars without a date and exchange rate. No model is trained here.", "",
        "```bash", "python analyze_case_flows.py analyze /path/to/blocos.tgz new_output \\",
        "  --parents /path/to/parents.json \\",
        "  --history /path/to/coldcard_target_history_20261014.json.gz \\",
        "  --outspends /path/to/coldcard_seed_outspends_20261014.json", "```", "",
        "Public observations may change. For a new collection (a new file is required):", "",
        "```bash", "python analyze_case_flows.py collect new_history.json.gz --max-pages 100",
        "python analyze_case_flows.py collect-outspends new_output/case_flows.json new_outspends.json", "```", "",
        "Attribution source: " + SOURCE + ". Output verification does not confirm this source's allegations.", ""]
    return "\n".join(lines)


def collect(output, address, max_pages):
    if output.exists():
        raise ValueError("Output already exists")
    if max_pages < 1:
        raise ValueError("Positive page limit required")
    base = "https://blockstream.info/api"
    before = get(f"{base}/address/{address}")
    txs, cursor, exhausted, seen = [], "", False, set()
    for _ in range(max_pages):
        page = get(f"{base}/address/{address}/txs/chain" + (f"/{cursor}" if cursor else ""))
        if not page:
            exhausted = True
            break
        for tx in page:
            if tx["txid"] in seen:
                raise ValueError("Repeated transaction during pagination")
            seen.add(tx["txid"])
            txs.append(tx)
        cursor = page[-1]["txid"]
    after = get(f"{base}/address/{address}")
    if before.get("address") != address or after.get("address") != address:
        raise ValueError("Provider address mismatch")
    result = dict(address=address, provider=base, collected_at=datetime.now(timezone.utc).isoformat(),
                  before=before, after=after, transactions=txs,
                  audit=check_history(address, txs, before, after, exhausted),
                  source_record=dict(role="course_seed_address", theft_label="unknown", hardware_control="unknown"))
    raw = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if str(output).endswith(".gz"):
        raw = gzip.compress(raw, mtime=0)
    with output.open("xb") as stream:
        stream.write(raw)
    print(json.dumps(dict(file=str(output), sha256=hashlib.sha256(raw).hexdigest(), audit=result["audit"])))


def collect_outspends(report_path, output):
    """Save a new observation of the report's exact consolidation outpoints."""
    if output.exists():
        raise ValueError("Output already exists")
    report = json.loads(Path(report_path).read_text())
    base, queries, seen = "https://blockstream.info/api", [], set()
    for seed in report["source_attributed_seeds"]:
        for out in seed["outputs"]:
            tid, n = seed["txid"], out["index"]
            if not re.fullmatch(r"[0-9a-f]{64}", tid) or type(n) is not int or n < 0:
                raise ValueError("Invalid consolidation outpoint")
            if (tid, n) in seen:
                raise ValueError("Duplicate consolidation outpoint")
            seen.add((tid, n))
            endpoint = f"{base}/tx/{tid}/outspend/{n}"
            query = dict(txid=tid, vout=n, address=out["address"], endpoint=endpoint)
            try:
                response = get(endpoint)
                if not isinstance(response, dict) or type(response.get("spent")) is not bool:
                    raise ValueError("Invalid outspend provider response")
                query["response"] = response
            except Exception as error:
                query["error"] = str(error)
            query["collected_at"] = datetime.now(timezone.utc).isoformat()
            queries.append(query)
    result = dict(provider=base, input_report_sha256=sha256(report_path), queries=queries)
    with output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(file=str(output), sha256=sha256(output), queried=len(queries),
                          usable=sum("response" in q for q in queries))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("analyze")
    command.add_argument("blocks", type=Path)
    command.add_argument("output", type=Path)
    command.add_argument("--history", type=Path)
    command.add_argument("--outspends", type=Path)
    command.add_argument("--parents", type=Path,
                         help="Reconcile every row of the existing parent audit against the blocks")
    command = commands.add_parser("collect")
    command.add_argument("output", type=Path)
    command.add_argument("--address", default=COURSE_ADDRESS)
    command.add_argument("--max-pages", type=int, default=100)
    command = commands.add_parser("collect-outspends")
    command.add_argument("report", type=Path)
    command.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "collect":
        collect(args.output, args.address, args.max_pages)
    elif args.command == "collect-outspends":
        collect_outspends(args.report, args.output)
    else:
        if args.output.exists():
            raise ValueError("Output directory must be new")
        result = analyze(args.blocks, args.history, args.outspends, args.parents)
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "case_flows.json").write_text(json.dumps(result, indent=2) + "\n")
        (args.output / "CASE_FLOWS.md").write_text(markdown(result))
        print(json.dumps(dict(output=str(args.output), blocks=result["archive"]["block_count"],
                              recovered_parents=result["unique_parent_transactions_recovered"])))


if __name__ == "__main__":
    main()
