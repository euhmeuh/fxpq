"""
Services that a server application can run.
"""

from core.application import Service


class DimensionService(Service):
    """Handles the list of dimensions available in a server"""

    def __init__(self):
        self.dimensions = []

    def subscribe(self, broker):
        super().subscribe(broker)

        broker.provide_res("dimension-list", self.get_dimensions)
        broker.receive_res("dimension", self.on_dimension_received)
        broker.on("dimension-disconnected", self.unregister_dimension)

    def on_dimension_received(self, dimension):
        self.dimensions.append(dimension)

    def unregister_dimension(self, id_):
        dimension = next((d for d in self.dimensions if d.id == id_), None)
        if dimension:
            self.dimensions.remove(dimension)

    def get_dimensions(self):
        return self.dimensions


class LoggingService:
    """Logs events sent by the clients"""

    def subscribe(self, broker):
        broker.receive_res("client-event", self.on_client_event_received)

    def on_client_event_received(self, event):
        print("[Event from {0}] {1} ({2})".format(event.client_id, event.name, ",".join(event.args)))


class AuthenticationService:
    """Handles player connection to a dimension"""


class ZoneService:
    """Handles instantiating zones for the players"""


class PhysicsService:
    """Handles physics simulation"""


class DoorService:
    """Handles players moving from zone to zone"""
