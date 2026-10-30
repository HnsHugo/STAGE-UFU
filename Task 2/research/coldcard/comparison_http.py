"""Persistent original-route HTTPS, two connections and a shared rate limit."""
import asyncio
import json
from threading import Thread
import urllib.error


class PersistentHTTP:
    def __init__(self, requests_per_second=3):
        if not 0<requests_per_second<=3:raise ValueError('HTTP rate must be within (0, 3]')
        self.interval=1/requests_per_second

    def __enter__(self):
        import aiohttp
        self.aiohttp=aiohttp
        self.loop=asyncio.new_event_loop()
        self.thread=Thread(target=self.loop.run_forever,daemon=True)
        self.thread.start()
        try:asyncio.run_coroutine_threadsafe(self.start(),self.loop).result()
        except Exception:
            self.loop.call_soon_threadsafe(self.loop.stop);self.thread.join();self.loop.close()
            raise
        return self

    async def start(self):
        self.lock=asyncio.Lock();self.next_start=0
        self.client=self.aiohttp.ClientSession(trust_env=True,
            connector=self.aiohttp.TCPConnector(limit=2,limit_per_host=2))

    async def request(self,url,timeout):
        if not url.startswith('https://blockstream.info/api/'):
            raise ValueError('Persistent transport is restricted to the original provider')
        async with self.lock:
            delay=max(0,self.next_start-self.loop.time())
            if delay:await asyncio.sleep(delay)
            self.next_start=self.loop.time()+self.interval
        bound=self.aiohttp.ClientTimeout(total=None,connect=timeout,sock_read=timeout)
        try:
            async with self.client.get(url,timeout=bound,allow_redirects=False) as response:
                if response.status>=400:
                    raise urllib.error.HTTPError(url,response.status,response.reason,response.headers,None)
                return json.loads(await response.read())
        except self.aiohttp.ClientHttpProxyError as error:
            raise urllib.error.URLError(f'Tunnel connection failed: {error.status}') from error
        except asyncio.TimeoutError as error:
            raise TimeoutError('Comparison API request timeout') from error
        except self.aiohttp.ClientError as error:
            raise urllib.error.URLError('Comparison API transport failed: '+type(error).__name__) from error

    def get_json(self,url,timeout):
        return asyncio.run_coroutine_threadsafe(self.request(url,timeout),self.loop).result()

    async def close(self):
        await self.client.close()
        await asyncio.sleep(.25)

    def __exit__(self,kind,value,traceback):
        try:asyncio.run_coroutine_threadsafe(self.close(),self.loop).result()
        finally:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()
            self.loop.close()
