"""Prevent inherited-pin loss and accidental reselection of completed sources."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from prepare_coldcard_checkpoint import retain_lineage,validate_selection


class CheckpointWorkflowTests(unittest.TestCase):
    def test_inherited_name_collisions_preserve_every_file_hash_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);parent=root/'parent';out=root/'out';parent.mkdir();out.mkdir()
            for name in ['old','older','new']:(parent/name).write_text(name)
            pin=lambda name:dict(file=name,sha256=hashlib.sha256((parent/name).read_bytes()).hexdigest())
            old={'parent_protocol':pin('old'),'inherited_parent_protocol':pin('older')}
            inputs={'parent_protocol':dict(file='../parent/new',sha256=pin('new')['sha256']),
                    'inherited_parent_protocol':dict(file='../parent/older',sha256=pin('older')['sha256'])}
            retain_lineage(inputs,old,parent,out)
            pairs={((out/p['file']).resolve(),p['sha256']) for p in inputs.values()}
            for name in ['old','older','new']:self.assertIn(((parent/name).resolve(),pin(name)['sha256']),pairs)

    def test_complete_source_is_never_reselected(self):
        with self.assertRaisesRegex(ValueError,'Complete source'):
            validate_selection(['source'],{'source':dict(status='bounded_incomplete',features=None,pages_fetched=96)},
                               {'source':dict(features={'confirmed_tx_count':10})},96)

    def test_queue_requires_the_exact_audited_previous_checkpoint(self):
        with self.assertRaisesRegex(ValueError,'preceding checkpoint'):
            validate_selection(['source'],{'source':dict(status='bounded_incomplete',features=None,pages_fetched=64)},
                               {'source':dict(features=None)},96)


if __name__=='__main__':unittest.main()
