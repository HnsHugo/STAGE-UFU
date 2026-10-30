"""Ensure keepalive transport retains provider and denial boundaries."""
import asyncio
import unittest
import urllib.error

from comparison_http import PersistentHTTP
from collect_comparison_histories import provider_denied


class PersistentHTTPTests(unittest.TestCase):
    def test_transport_refuses_other_hosts_before_any_request(self):
        client=PersistentHTTP()
        with self.assertRaises(ValueError):
            asyncio.run(client.request('https://other.invalid/api/',15))

    def test_proxy_403_remains_a_detectable_denial(self):
        import aiohttp
        class Response:
            async def __aenter__(self):
                raise aiohttp.ClientHttpProxyError(None,(),status=403,message='Forbidden')
            async def __aexit__(self,*args):pass
        class Client:
            def get(self,*args,**kwargs):return Response()
        async def check():
            client=PersistentHTTP();client.aiohttp=aiohttp;client.client=Client()
            client.loop=asyncio.get_running_loop();client.lock=asyncio.Lock();client.next_start=0
            with self.assertRaises(urllib.error.URLError) as caught:
                await client.request('https://blockstream.info/api/blocks/tip/height',15)
            self.assertTrue(provider_denied(dict(error_type='URLError',reason=str(caught.exception))))
        asyncio.run(check())


if __name__=='__main__':unittest.main()
