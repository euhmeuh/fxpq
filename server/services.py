"""
Services that a server application can run.
"""


class DimensionService:
    """Handles the list of dimensions available in a server"""

    def __init__(self):
        self.dimensions = []

    def subscribe(self, broker):
        broker.on("register-dimension", self.register_dimension)
        broker.on("unregister-dimension", self.unregister_dimension)
        broker.on("sync-dimensions", self.sync_dimensions)

    def register_dimension(self, broker, dimension):
        self.dimensions.append(dimension)

    def unregister_dimension(self, broker, id_):
        dimension = next((d for d in self.dimensions if d.id == id_), None)
        if dimension:
            self.dimensions.remove(dimension)

    def sync_dimensions(self, broker, obj):
        obj.dimensions = self.dimensions


class LoggingService:
    """Logs events sent by the clients"""

    def subscribe(self, broker):
        broker.on("client-event-received", self.on_client_event_received)

    def on_client_event_received(self, client_id, event):
        print("[Event from {0}] {1} ({2})".format(client_id, event.name, ",".join(event.args)))


class AuthenticationService:
    """Handles player connection to a dimension"""


class ZoneService:
    """Handles instantiating zones for the players"""


class PhysicsService:
    """Handles physics simulation"""


class DoorService:
    """Handles players moving from zone to zone"""
