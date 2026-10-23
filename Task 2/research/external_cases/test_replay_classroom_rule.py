import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from replay_classroom_rule import classify_fee, saved_rule, run

ROOT=Path(__file__).resolve().parent
COURSE=ROOT.parent/'coldcard/course_results_20261014'


class ClassroomReplayTests(unittest.TestCase):
    def test_strict_frozen_boundary_in_integer_satoshis(self):
        threshold=saved_rule((COURSE/'tree.txt').read_text())
        self.assertEqual(threshold,2815)
        self.assertEqual(classify_fee(2815,threshold),0)
        self.assertEqual(classify_fee(2816,threshold),1)

    def test_rule_reduction_rejects_changed_class_structure(self):
        tree=(COURSE/'tree.txt').read_text()
        with self.assertRaisesRegex(ValueError,'Saved tree'):
            saved_rule(tree.replace('class: 0','class: 1',1))

    def test_invalid_fees_are_not_silently_zero_filled(self):
        for fee in (None,-1,2816.0,True):
            with self.assertRaises(ValueError):classify_fee(fee,2815)

    def test_changed_protocol_rejected_before_reading_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'protocol.json').write_text('{}')
            (root/'summary.json').write_text(json.dumps({'protocol_sha256':'wrong'}))
            with self.assertRaisesRegex(ValueError,'Protocol checksum'):
                run(root/'protocol.json',root/'summary.json',root/'absent',root/'absent')

    def test_saved_replay_is_bound_to_the_original_model_and_cohort(self):
        report=json.loads((ROOT/'neighbor_results_20261022/classroom_replay_20261022.json').read_text())
        for key,file in [('tree','tree.txt'),('cohort','cohort.csv'),('report','report.json')]:
            self.assertEqual(report['hashes'][key],hashlib.sha256((COURSE/file).read_bytes()).hexdigest())
        self.assertEqual(sum(report['classroom_test_confusion_reproduced'].values()),60)


if __name__=='__main__':unittest.main()
