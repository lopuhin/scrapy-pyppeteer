import asyncio

import pyppeteer
from twisted.internet.defer import Deferred

from .browser_request import BrowserRequest, BrowserResponse


class ScrapyPyppeteerDownloaderMiddleware:
    """ Handles launching browser tabs, acts as a downloader.
    Probably eventually this should be moved to scrapy core as a downloader.
    """
    def __init__(self):
        # TODO handle pyppeteer.launch configuration here (e.g. headless=True)
        self._browser = None

    def process_request(self, request, spider):
        if isinstance(request, BrowserRequest):
            return aio_as_deferred(self.process_browser_request(request))
        else:
            return request

    async def process_browser_request(self, request: BrowserRequest):
        if self._browser is None:
            self._browser = await pyppeteer.launch()
        page = await self._browser.newPage()
        if request.is_blank:
            url = request.url
        else:
            await page.goto(request.url)
            url = page.url
            # TODO set status and headers
        return BrowserResponse(url=url, browser_tab=page)


def aio_as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))
