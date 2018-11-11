import scrapy
from scrapy_pyppeteer import BrowserRequest, BrowserResponse


class BooksSpider(scrapy.Spider):
    """ Example spider for books.toscrape.com, using the headless browser
    for all scraping, based on https://github.com/scrapy/booksbot/
    """
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_pyppeteer.ScrapyPyppeteerDownloaderMiddleware': 1000,
        }
    }

    def start_requests(self):
        start_url = 'http://books.toscrape.com'
        yield BrowserRequest(start_url)

    async def parse(self, response: BrowserResponse):
        page = response.browser_tab
        yield {'url': response.url}
        for link in await page.querySelectorAll('a'):
            url = await page.evaluate('link => link.href', link)
            yield BrowserRequest(url)
