"""Boundary checks for the pinned no-HTTP cooldown gate."""
from datetime import datetime, timedelta, timezone
import unittest
from run_after_cooldown import cooldown_due


class CooldownGuardTests(unittest.TestCase):
    def test_future_cooldown_blocks_before_due_time(self):
        due = datetime(2026, 11, 11, 23, 18, 37, tzinfo=timezone.utc)
        self.assertFalse(cooldown_due({'network_not_before':due.isoformat()}, due-timedelta(microseconds=1)))

    def test_due_boundary_and_timezone_are_enforced(self):
        due = datetime(2026, 11, 11, 23, 18, 37, tzinfo=timezone.utc)
        self.assertTrue(cooldown_due({'network_not_before':due.isoformat()}, due.astimezone(timezone(timedelta(hours=-3)))))
        with self.assertRaises(ValueError):
            cooldown_due({'network_not_before':'2026-11-11T23:18:37'}, due)


if __name__ == '__main__':
    unittest.main()
