import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer
from twisted.trial.unittest import TestCase

from scrapy_pyppeteer import BrowserRequest, BrowserResponse
from .mockserver import MockServer, ROOT_URL


class BaseSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_pyppeteer.ScrapyPyppeteerDownloaderMiddleware': 1000,
        }
    }


class FollowAllSpider(BaseSpider):
    def start_requests(self):
        yield BrowserRequest(ROOT_URL)

    async def parse(self, response: BrowserResponse):
        page = response.browser_tab
        yield {'url': response.url}
        for link in await page.querySelectorAll('a'):
            url = await page.evaluate('link => link.href', link)
            yield BrowserRequest(url)


class CrawlTestCase(TestCase):

    def setUp(self):
        self.mockserver = MockServer()
        self.mockserver.__enter__()
        self.runner = CrawlerRunner()

    def tearDown(self):
        self.mockserver.__exit__(None, None, None)

    @defer.inlineCallbacks
    def test_follow_all(self):
        crawler = self.runner.create_crawler(FollowAllSpider)
        yield crawler.crawl()
        assert crawler.stats.get_value('item_scraped_count') == 3
