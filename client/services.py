"""
Services that a client application can run.
"""

from core.application import Service
from core.connection import ClientConnection, Direction


class NetworkingService(Service):
    def __init__(self, url, port):
        self.url = url
        self.port = port

    def subscribe(self, broker):
        super().subscribe(broker)

        self.connection = ClientConnection(broker, self.url, self.port)
        broker.connect(self.connection)


class DimensionService(Service):

    can_run = True

    def subscribe(self, broker):
        super().subscribe(broker)

        broker.provide_res("dimension-list", lambda: {"local_dim"})

    def run(self, delta_time):
        if delta_time > 2.0:
            self.broker.send_res("dimension", "http://rilouw.eu/fxp2/manafia", direction=Direction.UP)
            self.broker.fetch_res("dimension-list", self.on_dimension_list_received, direction=Direction.UP)
            return True

    def on_dimension_list_received(self, dimension_list):
        print(dimension_list)


class LoggingService(Service):
    """Log broker events"""

    def subscribe(self, broker):
        broker.on_any(self.on_event_received)

    def on_event_received(self, sender, event, *args):
        print("[Event {0}] {1}".format(event, ",".join(args)))


class DisplayService(Service):
    """Handles object display on the player's screen"""

    def __init__(self):
        pass
