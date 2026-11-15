from copy import deepcopy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import recorded_twenty_campaign as campaign
from prepare_frontier_checkpoint import write


class RecordedTwentyTests(unittest.TestCase):
    def fixture(self):
        native = campaign.FIRST + [f'other_{i:02d}' for i in range(10)]
        queue = {s:dict(native_pages=178 if i<3 else 194 if i<6 else 212 if i<8 else 228)
                 for i,s in enumerate(native)}
        legacy = [f'legacy_{i}' for i in range(4)]
        return native,queue,legacy

    def test_exact_twenty_preserve_the_six_previously_unattempted_first(self):
        native,queue,legacy = self.fixture()
        units = campaign.units_for(native,queue,legacy)
        flattened = sum((u['source_ids'] for u in units),[])
        self.assertEqual(flattened[:6],campaign.FIRST)
        self.assertEqual(len(flattened),len(set(flattened)))
        self.assertEqual(set(flattened),set(native+legacy))
        self.assertTrue(all(1<=len(u['source_ids'])<=3 for u in units))
        self.assertTrue(all(len({queue[s]['native_pages'] for s in u['source_ids']})==1
                            for u in units if u['kind']=='native'))

    def test_duplicate_or_short_selection_cannot_be_frozen_as_twenty(self):
        native,queue,legacy = self.fixture()
        with self.assertRaises(AssertionError):
            campaign.units_for(native,queue,legacy[:-1])
        with self.assertRaises(AssertionError):
            campaign.units_for(native,queue,[legacy[0]]*4)

    def test_failed_collection_evidence_needs_explicit_scientific_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);origin=base/'stopped';origin.mkdir()
            write(origin/'independent_verification.json',dict(status='failed'))
            write(origin/'private_cache_backup.json',dict(saved_privately=True))
            row=dict(source_id='source',precutoff_history_provenance=dict(pass_name='stopped'))
            with patch.object(campaign,'BASE',base):
                with self.assertRaises(AssertionError):campaign.evidence_for(row)
                admitted=base/'admission';admitted.mkdir()
                write(admitted/'independent_verification.json',dict(status='passed',original_failure_preserved=True,
                    admitted_partial_evidence_source_ids=['source'],admitted_complete_source_ids=[]))
                row['precutoff_history_provenance']['offline_data_admission_scope']='admission'
                self.assertEqual(campaign.evidence_for(row)[0],origin)
                wrong=deepcopy(row);wrong['source_id']='unadmitted'
                with self.assertRaises(AssertionError):campaign.evidence_for(wrong)


if __name__=='__main__':unittest.main()
