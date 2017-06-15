"""
Networking logic
"""

from twisted.spread import pb
from twisted.internet import reactor

from core.events import EventEmitter


class LocalSource:
    pass


class ServerSource:

    def __init__(self, url):
        self.url = url


class Broker(pb.Root, EventEmitter):
    """Main object owner that sends and receives data from local and online sources"""

    def __init__(self, source_url=""):
        super().__init__()

        self.sources = [LocalSource()]

        if source_url:
            self.sources.add(ServerSource(source_url))

    def listen(self):
        reactor.listenTCP(8448, pb.PBServerFactory(self))
        reactor.run()

    def remote_register_dimension(self, dimension):
        self.emit("register-dimension", dimension)

    def remote_unregister_dimension(self):
        client_id = "TODO"
        self.emit("unregister-dimension", client_id)
