"""
Networking logic
"""

from enum import Enum

from threading import Thread

from twisted.spread import pb
from twisted.internet import reactor, threads, defer

from core.events import EventEmitter


def to_defer(func):
    """Make the decorated function return a Deferred"""
    def threaded_func(*args, **kwargs):
        return threads.deferToThread(func, *args, **kwargs)
    return threaded_func


def call_from_reactor(func):
    """Call the decorated function from the reactor thread"""
    def threaded_func(*args, **kwargs):
        return threads.blockingCallFromThread(reactor, func, *args, **kwargs)
    return threaded_func


class Direction(Enum):
    LOCAL = 0
    UP = 1
    DOWN = 2
    BOTH = 3


class Resource:
    @classmethod
    def merge(cls, res_list):
        return res_list


class ServerConnection(pb.Root):
    """Connection from a server to clients."""

    def __init__(self, broker, port):
        self.thread = None
        self.broker = broker
        self.port = port

    def listen(self):
        self.factory = pb.PBServerFactory(self)
        reactor.listenTCP(self.port, self.factory)
        reactor.run(False)

    @to_defer
    @call_from_reactor
    def fetch_res(self, name):
        """Ask clients for a resource"""
        raise NotImplementedError
        return self.clients.callRemote("fetch_res", name)

    @call_from_reactor
    def send_res(self, name, res):
        """Send a resource to the clients"""
        raise NotImplementedError
        self.clients.callRemote("send_res", name, res)

    def close(self):
        reactor.stop()
        if self.thread:
            self.thread.join()

    def remote_fetch_res(self, name):
        """The client asked for a resource"""
        deferred = defer.Deferred()
        self.broker.fetch_res(name, lambda result: deferred.callback(result), direction=Direction.UP)
        return deferred

    def remote_send_res(self, name, res):
        """The client sent a resource"""
        self.broker.send_res(name, res, direction=Direction.UP)


class ClientConnection(pb.Referenceable):
    """Connection from a client to a server.
    Also the interface used by the server to talk to a client
    """

    def __init__(self, broker, url, port):
        self.broker = broker
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

    def close(self):
        reactor.stop()
        if self.thread:
            self.thread.join()

    @to_defer
    @call_from_reactor
    def fetch_res(self, name):
        """Ask the server for a resource"""
        if not self.server:
            return None

        try:
            return self.server.callRemote("fetch_res", name)
        except pb.DeadReferenceError as e:
            self.on_connection_failed(e)
            return None

    @call_from_reactor
    def send_res(self, name, res):
        """Send a resource to the server"""
        if self.server:
            try:
                self.server.callRemote("send_res", name, res)
            except pb.DeadReferenceError as e:
                self.on_connection_failed(e)

    def remote_fetch_res(self, name):
        """The server asked for a resource"""
        deferred = defer.Deferred()
        self.broker.fetch_res(name, lambda result: deferred.callback(result), direction=Direction.DOWN)
        return deferred

    def remote_send_res(self, name, res):
        """The server sent a resource"""
        self.broker.send_res(name, res, direction=Direction.DOWN)

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

    def receive_res(self, name, on_received_callback):
        """Call this from your service to tell the broker you are interested in receiving a resource"""
        self.on("{}-received".format(name), on_received_callback)

    def fetch_res(self, name, on_received_callback, direction=Direction.LOCAL):
        """Immediately ask for a resource"""
        results = []

        method = self.resources.get(name, None)
        if method:
            res = method()
            if res:
                results.append(res)

        if self.connections:
            self._fetch_online_res(name, results, on_received_callback, direction=direction)
        else:
            on_received_callback(Resource.merge(results))

    def send_res(self, name, res, direction=Direction.LOCAL):
        """Immediately send a resource"""
        self.emit("{}-received".format(name), res)

        if self.connections:
            self._send_online_res(name, res, direction=direction)

    def emit_event(self, name, *args, direction=Direction.LOCAL):
        self.emit(name, *args)

        if self.connections:
            self._emit_online_event(name, *args, direction=direction)

    @to_defer
    @call_from_reactor
    def _fetch_online_res(self, name, local_res, on_received_callback, direction=Direction.LOCAL):
        local_deferred = defer.Deferred()
        defer_list = [local_deferred]

        for connection in self._get_connections(direction):
            df = connection.fetch_res(name)
            defer_list.append(df)

        deferred = defer.gatherResults(defer_list)

        deferred.pause()
        deferred.addCallback(lambda results: Resource.merge(results))
        deferred.addCallback(on_received_callback)
        deferred.unpause()

        local_deferred.callback(local_res)

    def _send_online_res(self, name, res, direction=Direction.LOCAL):
        for connection in self._get_connections(direction):
            connection.send_res(name, res)

    def _emit_online_event(self, name, *args, direction=Direction.LOCAL):
        for connection in self._get_connections(direction):
            connection.emit_event(name, *args)

    def _get_connections(self, direction=Direction.BOTH):
        """Get all the broker's connections in a given direction"""

        if direction == Direction.LOCAL:
            return []

        if direction == Direction.BOTH:
            return self.connections

        if direction == Direction.UP:
            return [c for c in self.connections if isinstance(c, ClientConnection)]

        if direction == Direction.DOWN:
            return [c for c in self.connections if isinstance(c, ServerConnection)]
