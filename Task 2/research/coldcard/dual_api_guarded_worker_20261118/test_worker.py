import tempfile
import unittest
from pathlib import Path
from worker import guarded, read


class LifecycleContract(unittest.TestCase):
    def test_identity_is_durable_before_collector_starts(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            def collect():
                identity = read(work / 'worker_lifecycle.json')
                self.assertEqual(identity['phase'], 'running')
                self.assertTrue(identity['boot_id'])
                self.assertTrue(identity['process_start_ticks'].isdigit())
                return {'result': 'ok'}
            self.assertEqual(guarded(collect, work, 'fresh', 'commit'), {'result': 'ok'})
            self.assertEqual(read(work / 'worker_lifecycle.json')['phase'], 'finished')

    def test_exception_propagates_with_finished_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            def fail():
                raise RuntimeError('test interruption')
            with self.assertRaises(RuntimeError):
                guarded(fail, work, 'fresh', 'commit')
            identity = read(work / 'worker_lifecycle.json')
            self.assertEqual(identity['phase'], 'finished')
            self.assertEqual(identity['error_type'], 'RuntimeError')

    def test_consumed_identity_cannot_launch_second_collector(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            guarded(lambda: None, work, 'fresh', 'commit')
            calls = []
            with self.assertRaises(ValueError):
                guarded(lambda: calls.append('unexpected'), work, 'fresh', 'commit')
            self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()
