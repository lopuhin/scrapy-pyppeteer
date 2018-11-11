from scrapy.http.response import Response
from pyppeteer.page import Page


class BrowserResponse(Response):
    def __init__(self, *args, **kwargs):
        self.browser_tab: Page = kwargs.pop('browser_tab')
        super(BrowserResponse, self).__init__(*args, **kwargs)
