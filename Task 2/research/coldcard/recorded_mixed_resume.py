"""Resume multiple verified mixed histories beyond their crossed legacy boundary.

The old single-source collector stays fingerprint-stable. Its pure seed and
collection routines are reused with a per-source private seed specification.
Actual native cursors, rather than the last TXID of a sorted union, are pinned.
"""
from pathlib import Path

import resume_fifty_bridge as inherited
from prepare_frontier_checkpoint import read, sha
from independent_mempool_pilot import require

_seed = inherited.seed


def seed(record, work, q):
    index = work / 'bridge_seed_index.json'
    require(sha(index) == q['private_bridge_seed_index_sha256'], 'Mixed seed index differs')
    spec = read(index)[record['pilot_id']]
    folder = work / 'seeds' / record['pilot_id']
    return _seed(record, folder, dict(q,
        private_bridge_seed_sha256=spec['spec_sha256'],
        native_start_cursor_sha256=spec['native_cursor_sha256']))


def collect(record, requests, work, q, unused):
    previous = inherited.seed
    inherited.seed = seed
    try:
        return inherited.collect(record, requests, work, q, unused)
    finally:
        inherited.seed = previous
