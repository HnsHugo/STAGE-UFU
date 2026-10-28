"""Test checkpoint recovery, fixed batches and reuse without redundant requests."""
import contextlib
import copy
import gzip
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build_source_registry import digest, json_bytes
from collect_theft_seeds import check_history
import source_cohort as cohort
from test_prepayment_pilot import history_transactions


def records(n=4):
    return [dict(pilot_id=f"cohort_{i:04d}",address=f"source{i}",
                 address_sha256=digest(f"source{i}".encode()),payment_txid="c"*64,
                 cutoff_height=20,cutoff_block_hash="f"*64) for i in range(1,n+1)]


def history(record,protocol=None):
    address=record["address"];transactions=history_transactions()
    for tx in transactions:
        for output in tx["vout"]:
            if output["scriptpubkey_address"]=="source":output["scriptpubkey_address"]=address
        for item in tx["vin"]:
            if (item.get("prevout") or {}).get("scriptpubkey_address")=="source":item["prevout"]["scriptpubkey_address"]=address
    counters=dict(tx_count=4,funded_txo_count=3,funded_txo_sum=1100,spent_txo_count=2,spent_txo_sum=100)
    data=dict(address=address,transactions=transactions,collected_at="2026-10-28T00:00:00+00:00",
              before=dict(address=address,chain_stats=counters),after=dict(address=address,chain_stats=copy.deepcopy(counters)))
    data["audit"]=check_history(address,transactions,data["before"],data["after"],True)
    return data


class SourceCohortTests(unittest.TestCase):
    def setup(self,folder):
        root=Path(folder);path=root/"protocol.json";path.write_bytes(b"{}")
        protocol=dict(workers=1,default_batch_size=2,reuse_sources=[])
        return path,root/"work",protocol,records()

    def test_completed_sources_are_not_requested_again(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,protocol,targets=self.setup(folder)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history) as get,contextlib.redirect_stdout(io.StringIO()):
                cohort.run(path,work,2);state=cohort.run(path,work,1)
            self.assertEqual([c.args[0]["pilot_id"] for c in get.call_args_list],[r["pilot_id"] for r in targets[:3]])
            self.assertEqual(len(state["entries"]),3)
            self.assertTrue(all(b["status"]=="completed" for b in state["batches"]))

    def test_unfinished_batch_and_orphan_raw_response_are_recovered(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,protocol,targets=self.setup(folder)
            state=cohort.empty_state(path,targets)
            state["batches"]=[dict(batch_id=1,source_ids=[r["pilot_id"] for r in targets[:2]],status="running")]
            cohort.atomic_write(work/"state.json",json_bytes(state))
            cohort.atomic_write(work/f"raw/{targets[0]['pilot_id']}.json.gz",gzip.compress(json_bytes(history(targets[0])),mtime=0))
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history) as get,contextlib.redirect_stdout(io.StringIO()):
                state=cohort.run(path,work,2)
            self.assertEqual([c.args[0]["pilot_id"] for c in get.call_args_list],[targets[1]["pilot_id"]])
            self.assertEqual(len(state["entries"]),2)
            self.assertEqual(state["entries"][targets[0]["pilot_id"]]["origin"],"recovered")

    def test_failed_source_is_retained_without_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,protocol,targets=self.setup(folder)
            def get(record,proto):
                if record["pilot_id"]==targets[0]["pilot_id"]:raise TimeoutError("bounded fixture")
                return history(record)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=get) as mock,contextlib.redirect_stdout(io.StringIO()):
                state=cohort.run(path,work,2)
            self.assertEqual(mock.call_count,2)
            self.assertEqual(state["entries"][targets[0]["pilot_id"]]["status"],"error")
            self.assertIsNone(state["entries"][targets[0]["pilot_id"]]["features"])
            self.assertNotIn(targets[2]["pilot_id"],state["entries"])

    def test_published_checkpoint_restores_without_raw_files_or_requests(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,protocol,targets=self.setup(folder);snapshot=Path(folder)/"snapshot"
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history) as get,contextlib.redirect_stdout(io.StringIO()):
                cohort.run(path,work,1);cohort.snapshot(path,work,snapshot);cohort.verify(path,snapshot)
                state=cohort.run(path,Path(folder)/"restored",0,snapshot/"checkpoint.json")
            self.assertEqual(get.call_count,1)
            self.assertEqual(len(state["entries"]),1)
            self.assertFalse((Path(folder)/"restored/raw").exists())

    def test_changed_raw_bytes_labels_cutoffs_or_features_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,protocol,targets=self.setup(folder)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history),contextlib.redirect_stdout(io.StringIO()):
                state=cohort.run(path,work,1)
            for field,value in [("hardware_label",1),("cutoff_height",21)]:
                changed=copy.deepcopy(state);changed["entries"][targets[0]["pilot_id"]][field]=value
                with self.assertRaises(ValueError):cohort.validate(changed,path,targets)
            changed=copy.deepcopy(state);changed["entries"][targets[0]["pilot_id"]]["features"]["balance_sat"]+=1
            with self.assertRaisesRegex(ValueError,"feature/evidence"):cohort.validate(changed,path,targets)
            raw=work/state["entries"][targets[0]["pilot_id"]]["raw_file"];raw.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError,"raw history checksum"):cohort.validate(state,path,targets,work)

    def test_missing_completed_result_and_overwrite_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,protocol,targets=self.setup(folder)
            state=cohort.empty_state(path,targets)
            state["batches"]=[dict(batch_id=1,source_ids=[targets[0]["pilot_id"]],status="completed")]
            with self.assertRaisesRegex(ValueError,"lacks results"):cohort.validate(state,path,targets)
            with patch("source_cohort.plan",return_value=(protocol,targets)),contextlib.redirect_stdout(io.StringIO()):
                cohort.run(path,work,0);snapshot=Path(folder)/"snapshot";cohort.snapshot(path,work,snapshot)
                before=(snapshot/"checkpoint.json").read_bytes()
                with self.assertRaises(FileExistsError):cohort.snapshot(path,work,snapshot)
                self.assertEqual(before,(snapshot/"checkpoint.json").read_bytes())

    def test_twelve_published_pilot_histories_are_reused_without_network(self):
        protocol=Path(__file__).parent/"source_cohort_protocol_20261028.json"
        with tempfile.TemporaryDirectory() as folder,patch("source_cohort.helper.fixed.collect_one",side_effect=AssertionError("No request expected")),contextlib.redirect_stdout(io.StringIO()):
            state=cohort.run(protocol,Path(folder),0)
        self.assertEqual(len(state["entries"]),12)
        self.assertTrue(all(e["status"]=="complete" and e["origin"]=="reuse" for e in state["entries"].values()))


if __name__=="__main__":unittest.main()
