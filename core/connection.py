"""
Networking logic
"""

from threading import Thread

from twisted.spread import pb
from twisted.internet import reactor

from core.events import EventEmitter


class Resource:
    pass


class Connection(pb.Root):

    def __init__(self):
        self.thread = None
        self.broker = None

    def listen(self):
        raise NotImplementedError

    def fetch_res(self, name):
        raise NotImplementedError

    def send_res(self, name, res):
        raise NotImplementedError

    def close(self):
        if self.thread:
            self.thread.join()

    def remote_fetch_res(self, name):
        if not self.broker:
            return

        return self.broker.fetch_res(name)

    def remote_send_res(self, name, res):
        if not self.broker:
            return

        self.broker.send_res(name, res)


class ServerConnection(Connection):
    """Remote interface the clients connect to"""

    def __init__(self, port):
        super().__init__()
        self.port = port

    def listen(self):
        self.factory = pb.PBServerFactory(self)
        reactor.listenTCP(self.port, self.factory)
        reactor.run(False)

    def fetch_res(self, name):
        return self.factory.callOnThread(self.thread, "fetch_res", name)

    def send_res(self, name, res):
        self.factory.callOnThread(self.thread, "send_res", name, res)


class ClientConnection(Connection):
    """Interface used by the server to talk to a client"""

    def __init__(self, url, port):
        super().__init__()
        self.state = "disconnected"
        self.url = url
        self.port = port

    def listen(self):
        self.factory = pb.PBClientFactory(self)
        reactor.connectTCP(self.url, self.port, self.factory)
        deferred = self.factory.getRootObject()
        deferred.addCallback(self.on_connected)
        deferred.addErrback(self.on_connection_failed)
        reactor.run(False)

    def fetch_res(self, name):
        return self.server.callOnThread(self.thread, "fetch_res", name)

    def send_res(self, name, res):
        self.server.callOnThread(self.thread, "send_res", name, res)

    def on_connected(self, server):
        self.server = server
        self.state = "connected"
        self.broker.emit_event("client-connected")

    def on_connection_failed(self, error):
        self.server = None
        self.state = "disconnected"
        self.broker.emit_event("connection-failed")


class Broker(EventEmitter):
    """Main object owner that sends and receives data from local and online sources"""

    def __init__(self):
        super().__init__()

        self.connections = []
        self.resources = {}

    def connect(self, connection):
        connection.broker = self
        self.connections.append(connection)

    def listen(self):
        for connection in self.connections:
            connection.thread = Thread(target=connection.listen)
            connection.thread.start()

    def close(self):
        for connection in self.connections:
            connection.close()

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
