"""
Services that a server application can run.
"""

from core.application import Service
from core.connection import ServerConnection


class NetworkingService(Service):
    def __init__(self, port):
        self.port = port

    def subscribe(self, broker):
        super().subscribe(broker)

        self.connection = ServerConnection(broker, self.port)
        broker.connect(self.connection)


class DimensionListService(Service):
    """Handles the list of dimensions available in a server"""

    def __init__(self):
        self.dimensions = set()

    def subscribe(self, broker):
        super().subscribe(broker)

        broker.provide_res("dimension-list", self.get_dimensions)
        broker.receive_res("dimension", self.on_dimension_received)
        broker.on("dimension-disconnected", self.on_dimension_disconnected)

    def on_dimension_received(self, sender, dimension):
        self.dimensions.add(dimension)

    def on_dimension_disconnected(self, sender, id_):
        dimension = next((d for d in self.dimensions if d.id == id_), None)
        if dimension:
            self.dimensions.remove(dimension)

    def get_dimensions(self):
        return self.dimensions


class LoggingService(Service):
    """Log broker events"""

    def subscribe(self, broker):
        broker.on_any(self.on_event_received)

    def on_event_received(self, sender, event, *args):
        print("[Event {0}] {1}".format(event, ",".join(args)))


class AuthenticationService(Service):
    """Handles player connection to a dimension"""


class ZoneService(Service):
    """Handles instantiating zones for the players"""


class PhysicsService(Service):
    """Handles physics simulation"""


class DoorService(Service):
    """Handles players moving from zone to zone"""
