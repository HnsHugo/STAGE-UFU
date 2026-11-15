from datetime import datetime, timezone, timedelta
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from prepare_frontier_checkpoint import read, write
from recorded_mempool_resume import (DispatchClock, RecordedRequests,
    OriginalGuardedRequests, verify_dispatch_evidence)


class DispatchEvidenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_early_wake_cannot_dispatch_before_the_declared_bound(self):
        state = dict(ns=10**12, wall=datetime(2026, 11, 15, tzinfo=timezone.utc), calls=0)
        async def sleep(seconds):
            state['calls'] += 1
            elapsed = seconds / 2 if state['calls'] == 1 else seconds
            state['ns'] += round(elapsed * 1e9)
            state['wall'] += timedelta(seconds=elapsed)
        clock = DispatchClock(monotonic_ns=lambda: state['ns'], wall_now=lambda: state['wall'], sleep=sleep)
        first = await clock.reserve()
        second = await clock.reserve()
        self.assertGreaterEqual(second['monotonic_ns'] - first['monotonic_ns'], 5_250_000_000)
        self.assertGreater(state['calls'], 1)
        markers = [dict(dispatch_at=e['wall_at'], dispatch_clock_evidence=e) for e in [first, second]]
        self.assertEqual(verify_dispatch_evidence(markers)['sent_requests'], 2)
        self.assertEqual(verify_dispatch_evidence(list(reversed(markers)))['sent_requests'], 2)

    async def test_wall_clock_step_is_stopped_before_a_new_dispatch(self):
        state = dict(ns=10**12, wall=datetime(2026, 11, 15, tzinfo=timezone.utc))
        clock = DispatchClock(monotonic_ns=lambda: state['ns'], wall_now=lambda: state['wall'])
        first = await clock.reserve()
        state['ns'] += 5_250_000_000
        state['wall'] += timedelta(seconds=4.79656)
        with self.assertRaisesRegex(ValueError, 'no request sent'):
            await clock.reserve()
        self.assertEqual(clock.previous, first)
        self.assertEqual(clock.sequence, 1)

    async def test_preflight_failure_cannot_inherit_an_earlier_dispatch_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            record = dict(pilot_id='comparison_test')
            previous = dict(session_id='one', sequence=1, monotonic_ns=10**12,
                            wall_at='2026-11-15T00:00:00+00:00', enforced_minimum_seconds=5.25)
            requests = RecordedRequests.__new__(RecordedRequests)
            requests.work = Path(directory)
            requests.http = SimpleNamespace(last_dispatch_evidence=previous)
            marker = requests.work / 'requests/comparison_test/test.json'
            marker.parent.mkdir(parents=True)
            def fail(*args):
                write(marker, dict(dispatch_at=previous['wall_at'], error_type='ValueError'))
                raise ValueError('stopped before dispatch')
            with patch.object(OriginalGuardedRequests, 'get', fail):
                with self.assertRaises(ValueError):
                    requests.get(record, 'test', '/not-sent')
            meta = read(marker)
            self.assertIsNone(meta['dispatch_at'])
            self.assertIsNone(meta['dispatch_clock_evidence'])
            self.assertTrue(meta['dispatch_not_attempted'])
            self.assertEqual(verify_dispatch_evidence([meta])['unsent_intents'], 1)

    async def test_missing_or_too_close_monotonic_evidence_is_rejected(self):
        first = dict(session_id='one', sequence=1, monotonic_ns=10**12,
                     wall_at='2026-11-15T00:00:00+00:00', enforced_minimum_seconds=5.25)
        second = dict(first, sequence=2, monotonic_ns=10**12 + 4_796_560_000,
                      wall_at='2026-11-15T00:00:05.250000+00:00')
        markers = [dict(dispatch_at=e['wall_at'], dispatch_clock_evidence=e) for e in [first, second]]
        with self.assertRaisesRegex(ValueError, 'Monotonic'):
            verify_dispatch_evidence(markers)
        with self.assertRaisesRegex(ValueError, 'Missing'):
            verify_dispatch_evidence([dict(dispatch_at=first['wall_at'])])

    async def test_success_records_this_requests_clock_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            record = dict(pilot_id='comparison_test')
            requests = RecordedRequests.__new__(RecordedRequests)
            requests.work = Path(directory)
            requests.http = SimpleNamespace(last_dispatch_evidence=None)
            marker = requests.work / 'requests/comparison_test/test.json'
            marker.parent.mkdir(parents=True)
            evidence = dict(session_id='one', sequence=1, monotonic_ns=10**12,
                            wall_at='2026-11-15T00:00:00+00:00', enforced_minimum_seconds=5.25)
            def succeed(*args):
                requests.http.last_dispatch_evidence = evidence
                write(marker, dict(http_status=200, dispatch_at=evidence['wall_at']))
                return ['saved response']
            with patch.object(OriginalGuardedRequests, 'get', succeed):
                self.assertEqual(requests.get(record, 'test', '/sent'), ['saved response'])
            meta = read(marker)
            self.assertFalse(meta['dispatch_not_attempted'])
            self.assertEqual(meta['dispatch_clock_evidence'], evidence)
            self.assertEqual(verify_dispatch_evidence([meta])['sent_requests'], 1)

    async def test_multiple_transport_sessions_cannot_be_combined(self):
        first = dict(session_id='one', sequence=1, monotonic_ns=10**12,
                     wall_at='2026-11-15T00:00:00+00:00', enforced_minimum_seconds=5.25)
        second = dict(first, session_id='two', monotonic_ns=10**12+5_250_000_000,
                      wall_at='2026-11-15T00:00:05.250000+00:00')
        with self.assertRaisesRegex(ValueError, 'More than one'):
            verify_dispatch_evidence([dict(dispatch_at=e['wall_at'], dispatch_clock_evidence=e)
                                      for e in [first, second]])


if __name__ == '__main__':
    unittest.main()
