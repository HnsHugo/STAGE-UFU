"""Ensure lease/lock/cooldown failures never enter the original HTTP client."""
from datetime import datetime,timedelta,timezone
import fcntl
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

import run_scope

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))


class AccessGuards(unittest.TestCase):
    def run_case(self,kind):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);work=root/'work';work.mkdir();output=root/'out'
            lock=root/'historical.lock';lock.write_text('')
            manifest=work/'historical_locks.json';manifest.write_text(json.dumps([str(lock)]))
            protocol=root/'protocol.json';protocol.write_text(json.dumps({'pass_name':'new_scope','private_lock_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}))
            now=datetime.now(timezone.utc)
            permit={'published_commit':'a'*40,'next_network_attempt_not_before':None,'collector_lease':{'state':'running','owner':'new_scope','protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'expires_at':(now+timedelta(hours=1)).isoformat()}}
            if kind=='foreign':permit['collector_lease']['owner']='other'
            if kind=='expired':permit['collector_lease']['expires_at']=(now-timedelta(hours=1)).isoformat()
            if kind=='cooldown':permit['next_network_attempt_not_before']=(now+timedelta(hours=1)).isoformat()
            if kind!='missing':(work/'lease_published').write_text(json.dumps(permit))
            import collect_reference_tail as tail
            import collect_reference_tail_many as many
            from comparison_http import PersistentHTTP
            old_http,old_guarded=tail.PersistentHTTP,tail.guarded
            def enter_client(*args):
                with tail.PersistentHTTP(1):pass
            try:
                with patch.object(many,'main',side_effect=enter_client) as invoked,patch.object(PersistentHTTP,'__enter__',side_effect=AssertionError('HTTP client entered')) as http:
                    if kind=='locked':
                        with lock.open('a+') as held:
                            fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
                            run_scope.main(protocol,output,work)
                        self.assertFalse(invoked.called)
                        self.assertEqual(json.loads((output/'run_receipt.json').read_text())['provider_requests'],0)
                    else:
                        with self.assertRaises((ValueError,FileNotFoundError)):
                            run_scope.main(protocol,output,work)
                    self.assertFalse(http.called)
            finally:tail.PersistentHTTP,tail.guarded=old_http,old_guarded

    def test_missing_lease(self):self.run_case('missing')
    def test_foreign_lease(self):self.run_case('foreign')
    def test_expired_lease(self):self.run_case('expired')
    def test_future_cooldown(self):self.run_case('cooldown')
    def test_held_historical_lock(self):self.run_case('locked')


if __name__=='__main__':unittest.main()
