from datetime import datetime,timezone,timedelta
import unittest
from provider_backoff import deadline
class BackoffContracts(unittest.TestCase):
    def test_retry_after_longer_than_local_cap_is_respected(self):
        now=datetime(2026,11,17,tzinfo=timezone.utc)
        due,local=deadline(dict(http_status=429,retry_after='172800'),dict(last_retry_delay_seconds=86400),now)
        self.assertEqual(local,86400);self.assertEqual(datetime.fromisoformat(due),now+timedelta(days=2))
    def test_429_doubles_only_its_own_provider_delay(self):
        now=datetime(2026,11,17,tzinfo=timezone.utc)
        due,local=deadline(dict(http_status=429),dict(last_retry_delay_seconds=14400),now)
        self.assertEqual(local,28800)
    def test_http_date_overrides_two_hour_transient_delay(self):
        now=datetime(2026,11,17,tzinfo=timezone.utc)
        due,local=deadline(dict(http_status=503,retry_after='Wed, 18 Nov 2026 00:00:00 GMT'),{},now)
        self.assertEqual(local,7200);self.assertEqual(datetime.fromisoformat(due),now+timedelta(days=1))
if __name__=='__main__':unittest.main()
