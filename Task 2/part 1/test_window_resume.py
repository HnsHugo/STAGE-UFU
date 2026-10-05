import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import URLError
from collect_history import sample
from collect_window import checkpoint_getter, prepare_output, parse_utc
from test_collect_history import A, tx, stats


class ResumeTests(unittest.TestCase):
    def test_interruption_reuses_pages_and_live_stats_are_checked(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'pages.json'
            def first(url):
                if url == '/address/' + A:
                    return stats(26), {'url': url}
                if url.endswith('/chain'):
                    return [tx(str(i)) for i in range(25)], {'url': url}
                raise URLError('interrupted')
            with self.assertRaises(URLError):
                sample(A, 2, checkpoint_getter(A, path, first), sleeper=lambda _: None)
            calls = []
            def second(url):
                calls.append(url)
                if url == '/address/' + A:
                    return stats(26), {'url': url}
                self.assertTrue(url.endswith('/24'))
                return [tx('last')], {'url': url}
            result = sample(A, 2, checkpoint_getter(A, path, second), sleeper=lambda _: None)
            self.assertEqual(result['summary']['coverage'], 'count_matches_stable_stats')
            self.assertEqual(len(calls), 3)
            self.assertNotIn('/address/' + A + '/txs/chain', calls)
            with self.assertRaisesRegex(ValueError, 'Chain stats changed'):
                checkpoint_getter(A, path, lambda _: (stats(27), {}))('/address/' + A)

    def test_manifest_pins_input_and_dates(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'input.csv'
            path.write_text('input')
            output = Path(root) / 'out'
            start, end = map(parse_utc, ['2026-09-01T00:00:00Z', '2026-10-01T00:00:00Z'])
            prepare_output(path, output, start, end)
            prepare_output(path, output, start, end)
            path.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'Input, dates'):
                prepare_output(path, output, start, end)

    def test_changed_stats_at_end_rejects_mixed_snapshot(self):
        with tempfile.TemporaryDirectory() as root:
            responses = iter([(stats(1), {}), ([tx()], {}), (stats(2), {})])
            with self.assertRaisesRegex(ValueError, 'Chain stats changed'):
                sample(A, 1, checkpoint_getter(A, Path(root)/'pages.json', lambda _: next(responses)),
                       sleeper=lambda _: None)
