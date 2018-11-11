import sys, time
from subprocess import Popen, PIPE

from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site


configure_logging()


class MockServer:
    def __init__(self, module='tests.mockserver'):
        self.proc = None
        self.module = module

    def __enter__(self):
        self.proc = Popen(
            [sys.executable, '-u', '-m', self.module], stdout=PIPE)
        self.proc.stdout.readline()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.proc.kill()
        self.proc.wait()
        time.sleep(0.2)


class Leaf(Resource):
    isLeaf = True

    def __init__(self, data: str):
        super().__init__()
        self._data = data

    def render(self, request):
        return f'<div id="foo">{self._data}</div>'.encode('utf8')


class Root(Resource):
    def __init__(self):
        super().__init__()
        self._resources = [
            ('leaf-1', Leaf('data-1')),
            ('leaf-2', Leaf('data-2')),
        ]
        for url, r in self._resources:
            self.putChild(url.encode('utf8'), r)

    def getChild(self, name, request):
        return self

    def render(self, request):
        return (
            '<h1>Hi</h1>' +
            '<br/>'.join(
                f'<a href="{url}">{url}</a>' for url, _ in self._resources)
        ).encode('utf8')


PORT = 8781
ROOT_URL = f'http://127.0.0.1:{PORT}'


def main():
    http_port = reactor.listenTCP(PORT, Site(Root()))

    def print_listening():
        host = http_port.getHost()
        print('Mock server running at http://{}:{}'.format(
            host.host, host.port))

    reactor.callWhenRunning(print_listening)
    reactor.run()


if __name__ == "__main__":
    main()
