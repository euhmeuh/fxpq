"""
Fxpq server
"""

from core.application import Application
from server.services import LoggingService, NetworkingService, DimensionListService, AuthenticationService, ZoneService, PhysicsService, DoorService


class MasterServer(Application):
    """Master server that lists registered servers"""

    def __init__(self):
        super().__init__()

        self.services = [
            LoggingService(),
            NetworkingService(8448),
            DimensionListService()
        ]


class DimensionServer(Application):
    """Server that handles all players connected to the same dimension"""

    def __init__(self, master_server=""):
        super().__init__(master_server)

        self.services = [
            LoggingService(),
            AuthenticationService(),
            #ZoneListService()
        ]


class ZoneServer(Application):
    """Server that handles a single zone in the game"""

    def __init__(self, master_dimension=""):
        super().__init__(master_dimension)

        self.services = [
            NetworkingService(8448),
            LoggingService(),
            PhysicsService(),
            DoorService(),
            ZoneService("data/Manafia/golfia.fxpq")
        ]
