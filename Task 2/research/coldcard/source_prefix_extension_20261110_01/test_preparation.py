"""Reject incomplete evidence, mismatched cursors and ineligible selections."""
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import prepare_scope
import recover_cache


class EvidenceGuards(unittest.TestCase):
    def test_truncated_container_never_yields_partial_member(self):
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w') as archive:
            for name, data in [('first', b'complete'), ('second', os.urandom(4096))]:
                member = tarfile.TarInfo(name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        compressed = gzip.compress(raw.getvalue())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'partial.tar.gz'
            path.write_bytes(compressed[:len(compressed)//2])
            accepted = []
            with self.assertRaises((EOFError, tarfile.ReadError)):
                for name, data in recover_cache.complete_members(path):
                    accepted.append((name, data))
            self.assertEqual(accepted, [('first', b'complete')])

    def test_complete_or_closed_source_cannot_be_selected(self):
        resume = dict(next_extension_source_ids=['comparison_0001'],
            coldcard_unextended_at_16_page_bound_source_ids=['comparison_0001'],
            source_ids=[])
        with self.assertRaisesRegex(ValueError, 'Complete prefix'):
            prepare_scope.choose_sources(resume, {'rows': [dict(source_id='comparison_0001', features={})]})
        resume['source_ids'] = ['comparison_0001']
        with self.assertRaisesRegex(ValueError, 'Closed extension'):
            prepare_scope.choose_sources(resume, {'rows': [dict(source_id='comparison_0001', features=None)]})

    def cached_case(self, kind):
        record = dict(pilot_id='comparison_0001', payment_txid='anchor', address='address', cutoff_height=100)
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            folder = work/'requests'/record['pilot_id']
            folder.mkdir(parents=True)
            for key, data, endpoint in [
                ('reference', {}, '/tx/anchor'),
                ('tail_0000', [dict(txid='prior', status=dict(confirmed=True,
                    block_height=101 if kind == 'future' else 99, block_hash='hash'))],
                 '/address/address/txs/chain/' + ('wrong' if kind == 'cursor' else 'anchor'))]:
                body = gzip.compress(json.dumps(data).encode(), mtime=0)
                meta = dict(source_id=record['pilot_id'], key=key, http_status=200,
                    sha256=hashlib.sha256(body).hexdigest(),
                    endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest())
                (folder/(key+'.json')).write_text(json.dumps(meta))
                (folder/(key+'.json.gz')).write_bytes(body + (b'changed' if kind == 'body' and key.startswith('tail') else b''))
            with patch.object(prepare_scope.tail, 'anchor_check'):
                with self.assertRaises(ValueError):
                    prepare_scope.validate_cached(record, work)

    def test_changed_response_body_is_rejected(self):
        self.cached_case('body')

    def test_wrong_cursor_is_rejected(self):
        self.cached_case('cursor')

    def test_future_height_is_rejected(self):
        self.cached_case('future')


if __name__ == '__main__':
    unittest.main()
