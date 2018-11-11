import scrapy


class BrowserRequest(scrapy.Request):
    _BLANK_URL = 'about:blank'

    @classmethod
    def blank(cls):
        return BrowserRequest(cls._BLANK_URL, dont_filter=True)

    @property
    def is_blank(self):
        return self.url == self._BLANK_URL
