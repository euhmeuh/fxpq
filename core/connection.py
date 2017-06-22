"""
Networking logic
"""

from twisted.spread import pb
from twisted.internet import reactor

from core.events import EventEmitter


class Resource:
    pass


class Connection:
    def __init__(self, url):
        self.url = url


class Broker(EventEmitter, pb.Root):
    """Main object owner that sends and receives data from local and online sources"""

    def __init__(self, url=""):
        super().__init__()

        self.connections = []
        self.resources = {}

        if url:
            self.connections.add(Connection(url))

    def listen(self):
        reactor.listenTCP(8448, pb.PBServerFactory(self))
        reactor.run()

    def provide_res(self, name, get_method):
        """Call this from your service to register yourself as a resource provider"""
        self.resources[name] = get_method

    def receive_res(self, name, send_method):
        """Call this from your service to tell the broker you are interested in receiving a resource"""
        self.on("{}-received".format(name), send_method)

    def fetch_res(self, name):
        """Immediately ask for a resource"""
        results = []

        method = self.resources.get(name, None)
        if method:
            res = method()
            if res:
                results.append(res)

        for connection in self.connections:
            res = connection.fetch_res(name)
            if res:
                results.append(res)

        return Resource.merge(results)

    def send_res(self, name, res):
        """Immediately send a resource"""
        self.emit("{}-received".format(name), res)

        for connection in self.connections:
            connection.send_res(name, res)

    def emit_event(self, name, *args):
        self.emit(name, *args)

        for connection in self.connections:
            connection.emit_event(name, *args)
