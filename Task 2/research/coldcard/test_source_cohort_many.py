"""Verify unattended batching preserves ordering, checkpoints and failures."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import source_cohort as cohort
from test_source_cohort import history, records


class MultipleBatchTests(unittest.TestCase):
    def setup(self,folder,n=5):
        root=Path(folder);protocol=root/"protocol.json";protocol.write_bytes(b"{}")
        return protocol,root/"work",root/"snapshots",dict(workers=1,default_batch_size=2,reuse_sources=[]),records(n)

    def test_two_batches_then_resume_to_population_end_without_recollection(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,out,protocol,targets=self.setup(folder)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history) as get,contextlib.redirect_stdout(io.StringIO()):
                result=cohort.run_many(path,work,out,max_batches=2)
                first=(out/"batch_0001/checkpoint.json").read_bytes()
                self.assertEqual(result["completed_batch_ids"],[1,2])
                self.assertEqual(result["new_source_attempts"],4)
                self.assertEqual(result["stop_reason"],"max_batches")
                result=cohort.run_many(path,work,out,max_batches=2)
                self.assertEqual(result["stop_reason"],"population_exhausted")
                self.assertEqual(result["new_source_attempts"],1)
                for n in (1,2,3):cohort.verify(path,out/f"batch_{n:04d}")
            self.assertEqual([c.args[0]["pilot_id"] for c in get.call_args_list],[r["pilot_id"] for r in targets])
            self.assertEqual(first,(out/"batch_0001/checkpoint.json").read_bytes())

    def test_soft_budget_stops_between_batches(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,out,protocol,targets=self.setup(folder)
            ticks=iter([0,0,2,2])
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history) as get,contextlib.redirect_stdout(io.StringIO()):
                result=cohort.run_many(path,work,out,max_batches=3,max_seconds=1,clock=lambda:next(ticks))
            self.assertEqual(result["stop_reason"],"time_budget")
            self.assertEqual(get.call_count,2)
            self.assertTrue((out/"batch_0001/checkpoint.json").exists())
            self.assertFalse((out/"batch_0002").exists())

    def test_terminal_failure_does_not_replace_or_retry_source(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,out,protocol,targets=self.setup(folder,4)
            def collect(record,proto):
                if record==targets[0]:raise TimeoutError("fixture")
                return history(record)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=collect) as get,contextlib.redirect_stdout(io.StringIO()):
                result=cohort.run_many(path,work,out,max_batches=2)
            self.assertEqual(get.call_count,4)
            self.assertEqual(result["coverage"]["complete_sources"],3)
            self.assertEqual(result["coverage"]["error_sources"],1)

    def test_missing_export_is_recovered_before_next_batch(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,out,protocol,targets=self.setup(folder,4)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history),contextlib.redirect_stdout(io.StringIO()):
                cohort.run(path,work,2)
            def collect(record,proto):
                self.assertTrue((out/"batch_0001/checkpoint.json").exists())
                return history(record)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=collect) as get,contextlib.redirect_stdout(io.StringIO()):
                cohort.run_many(path,work,out,max_batches=1)
            self.assertEqual(get.call_count,2)

    def test_conflicting_export_fails_before_new_requests(self):
        with tempfile.TemporaryDirectory() as folder:
            path,work,out,protocol,targets=self.setup(folder)
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one",side_effect=history),contextlib.redirect_stdout(io.StringIO()):
                cohort.run_many(path,work,out,max_batches=1)
            damaged=out/"batch_0001/features.json";damaged.write_bytes(b"[]")
            with patch("source_cohort.plan",return_value=(protocol,targets)),patch("source_cohort.helper.fixed.collect_one") as get,contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError,"export differs"):
                    cohort.run_many(path,work,out)
            get.assert_not_called()
            self.assertEqual(damaged.read_bytes(),b"[]")

    def test_invalid_budgets_fail_before_collection(self):
        for batches,seconds in [(0,1),(1,0),(1,-1),(1,float("nan")),(1,float("inf"))]:
            with patch("source_cohort.run") as run:
                with self.assertRaises(ValueError):cohort.run_many(Path("missing"),Path("work"),Path("out"),batches,seconds)
                run.assert_not_called()


if __name__=="__main__":unittest.main()
