import io,json,tempfile,unittest,urllib.error
from pathlib import Path
from journaled_esplora import JournaledEsplora
from dual_api_frontier import PROVIDERS
from prepare_frontier_checkpoint import read,sha

class Response(io.BytesIO):
    status=200
class Fake:
    def __init__(self,fail=False):self.calls=[];self.fail=fail
    def open(self,url,timeout):
        self.calls.append((url,timeout))
        if self.fail:raise urllib.error.HTTPError(url,503,'unavailable',{'Retry-After':'120'},None)
        return Response(b'[]')
class TransportContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.work=Path(self.tmp.name)
    def test_provider_selected_once_bodies_fingerprinted_and_no_saved_request_repeated(self):
        for i,p in enumerate(PROVIDERS):
            fake=Fake();c=JournaledEsplora(p,self.work,str(i),2,lambda:None,opener=fake)
            self.assertEqual(c.get('page_0000','/address/source/txs/chain/cursor'),[])
            m=read(self.work/'requests'/str(i)/'page_0000.json')
            self.assertEqual(m['sha256'],sha(self.work/'requests'/str(i)/'page_0000.json.gz'))
            with self.assertRaisesRegex(ValueError,'Consumed'):c.get('page_0000','/address/source/txs/chain/cursor')
            self.assertEqual(fake.calls,[(p+'/address/source/txs/chain/cursor',45)])
    def test_failure_journal_preserves_status_and_retry_after_and_forbids_retry(self):
        fake=Fake(True);c=JournaledEsplora(PROVIDERS[1],self.work,'a',2,lambda:None,opener=fake)
        with self.assertRaises(urllib.error.HTTPError):c.get('page_0000','/tx/cursor/status')
        m=read(self.work/'requests/a/page_0000.json')
        self.assertEqual((m['http_status'],m['retry_after']),(503,'120'))
        with self.assertRaisesRegex(ValueError,'stopped'):c.get('another','/tx/cursor/status')
        self.assertEqual(len(fake.calls),1)
    def test_lease_denial_prevents_dispatch_and_intent(self):
        fake=Fake()
        def denied():raise ValueError('lease held elsewhere')
        c=JournaledEsplora(PROVIDERS[0],self.work,'a',1,denied,opener=fake)
        with self.assertRaisesRegex(ValueError,'lease'):c.get('page_0000','/tx/cursor/status')
        self.assertEqual(fake.calls,[]);self.assertFalse((self.work/'requests/a/page_0000.json').exists())
if __name__=='__main__':unittest.main()
