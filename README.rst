scrapy-pyppeeteer: use pyppeteer from a Scrapy spider
=====================================================

.. image:: https://img.shields.io/travis/lopuhin/scrapy-pyppeteer/master.svg
   :target: http://travis-ci.org/lopuhin/scrapy-pyppeteer
   :alt: Build Status

.. image:: https://codecov.io/github/lopuhin/scrapy-pyppeteer/coverage.svg?branch=master
   :target: https://codecov.io/github/lopuhin/scrapy-pyppeteer?branch=master
   :alt: Code Coverage

The goal is to allow using `pyppeteer <https://github.com/miyakogi/pyppeteer>`_
(a python port of puppeteer) from a `scrapy <https://scrapy.org>`_ spider.
This allows to scrape sites that require JS to function properly
and to make the scraper more similar to humans.

Current status is experimental, most likely the library will remain
in experimental state, with a proper solution included in Scrapy later
(which will be very different).
Documentation assumes Scrapy knowledge.

Installation
------------

Python 3.6+ is required for
`PEP 525 <https://www.python.org/dev/peps/pep-0525/>`_ (Asynchronous Generators).

The library requires async def parse support in scrapy, until this is merged,
please install scrapy from a branch::

    pip install git+https://github.com/lopuhin/scrapy.git@async-def-parse

Also this requires a pyppeteer fork for some fixes that are not released yet::

    pip install git+https://github.com/lopuhin/pyppeteer.git

Finally, install scrapy-pyppeteer itself::

    pip install git+https://github.com/lopuhin/scrapy-pyppeteer.git

Usage
-----

At the moment, browser management is implemented as a downloader middleware,
which you need to activate (update ``DOWNLOADER_MIDDLEWARES`` in settings)::

   DOWNLOADER_MIDDLEWARES = {
       'scrapy_pyppeteer.ScrapyPyppeteerDownloaderMiddleware': 1000,
   }

After that you can use ``scrapy_pyppeteer.BrowserRequest``, and you'll get
``scrapy_pyppeteer.BrowserResponse`` in your ``parse`` method.
``BrowserResponse`` has an empty body, and has an extra attribute
``browser_window`` which is a ``pyppeteer.page.Page`` instance (a browser tab).
If you used ``BrowserResponse.empty()``, you'll get an empty tab,
and if you specified a URL, then you'll get a tab where ``page.goto(url)``
has been awaited.

To do anything with ``response.browser_window``, you need to define your
parse callback as ``async def``, and use ``await`` syntax.
All actions performed via ``await`` are executed directly, without going
to the scheduler (although in the same global event loop). You can also
``yield`` items and new requests, which will work normally.

Short example of the parse method
(see more self-contained examples in "examples" folder of this repo)::

    async def parse(self, response: BrowserResponse):
        page = response.browser_tab
        yield {'url': response.url}
        for link in await page.querySelectorAll('a'):
            url = await page.evaluate('link => link.href', link)
            yield BrowserRequest(url)
        await page.close()

Settings
--------

- ``PYPPETEER_LAUNCH``: a dict with pyppeteer launch options, see
  ``pyppeteer.launch`` docstring.


Notes on memory usage
---------------------

- You need to explicitly close the browser tab once you don't need it
  (e.g. at the end of the parse method)
- Items yielded from a single parse method are kept in memory
  while the parse method is running, as well as all local variables
  (the former is less obvious). Yielding a large number of big items from one
  parse method can increase the memory usage of your spider.
  Consider splitting work into several other parse methods.

Debugging
---------

If you wanted to put a ``pdb.set_trace()`` into the spider parse method
and check results of some manipulations with the page which need to be awaited,
this won't work, because ``pdb`` is blocking the event loop. One way which
works is shown below
(although this does not use the spider or this library at all)::

    import asyncio
    import pyppeteer
    loop = asyncio.new_event_loop()
    run = loop.run_until_complete  # use "run(x)" instead of "await x" here
    browser = run(pyppeteer.launch(headless=False))  # headless=True to see what is executed
    page = run(browser.newPage())
    run(page.goto('http://books.toscrape.com'))
    print(len(run(page.xpath('//a[@href]'))))  # print number

-- this allows to interact with a page from a REPL and observe effects in the
browser window.

TODO
----

- More tests, set up CI
- Set response status and headers
- A way to control max number of tabs open
- A way to schedule interactions reusing the same window
  (to continue working in the same time but go through the scheduler)
- Nice extraction API (like parsel)
