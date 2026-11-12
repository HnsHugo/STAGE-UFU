import asyncio
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from independent_mempool_pilot import MempoolHTTP, PROVIDER
from prepare_frontier_checkpoint import write
from resume_mempool_slow_response import SlowResponseHTTP, run


class SlowResponseContracts(unittest.TestCase):
    def test_declared_timeout_reaches_transport_despite_legacy_fifteen_second_argument(self):
        transport=SlowResponseHTTP(.2);transport.response_timeout_seconds=45
        with patch.object(MempoolHTTP,'request',new_callable=AsyncMock,return_value=[]) as request:
            self.assertEqual(asyncio.run(transport.request(PROVIDER+'/tx/reference',15)),[])
            request.assert_awaited_once_with(PROVIDER+'/tx/reference',45)

    def test_excessive_timeout_is_rejected_before_collector_or_http(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'protocol.json';write(p,dict(timeout_seconds=46))
            with patch('resume_mempool_slow_response.collector.run') as collector:
                with self.assertRaisesRegex(ValueError,'declared bound'):run(p,Path(folder))
                collector.assert_not_called()


if __name__=='__main__':unittest.main()
