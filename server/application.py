"""
Fxpq server
"""

from core.application import Application
from server.services import DimensionService, AuthenticationService, ZoneService, PhysicsService, DoorService


class MasterServer(Application):
    """Master server that lists registered servers"""

    def __init__(self):
        super().__init__()

        self.services = [
            DimensionService()
        ]


class DimensionServer(Application):
    """Server that handles all players connected to the same dimension"""

    def __init__(self, master_server=""):
        super().__init__(master_server)

        self.services = [
            AuthenticationService(),
            ZoneService()
        ]


class ZoneServer(Application):
    """Server that handles a single zone in the game"""

    def __init__(self, master_dimension=""):
        super().__init__(master_dimension)

        self.services = [
            PhysicsService(),
            DoorService()
        ]
