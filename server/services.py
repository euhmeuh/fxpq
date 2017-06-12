"""
Services that a server application can run.
"""


class DimensionService:
    """Handles the list of dimensions available in a server"""

    def __init__(self):
        pass

    def run(self, broker, delta_time):
        if delta_time > 1.0:
            print("lol")
            return True

        return False


class AuthenticationService:
    """Handles player connection to a dimension"""

    def __init__(self):
        pass

    def run(self, broker, delta_time):
        pass


class ZoneService:
    """Handles """

    def __init__(self):
        pass

    def run(self, broker, delta_time):
        pass


class PhysicsService:
    """"""

    def __init__(self):
        pass

    def run(self, broker, delta_time):
        pass


class DoorService:
    """"""

    def __init__(self):
        pass

    def run(self, broker, delta_time):
        pass
