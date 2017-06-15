"""
Application base class.
Used to implement a server or a client. It runs a given list of services in an infinite loop.
"""

from core.connection import Broker


class Application:
    """Base server class"""

    def __init__(self, source_url=""):
        self.broker = Broker(source_url)
        self.services = []
        self.running = False

    def run(self):
        if self.running:
            return

        print("Application started.")

        for service in self.services:
            service.subscribe(self.broker)

        self.running = True
        try:
            self.broker.listen()
        except KeyboardInterrupt:
            self.running = False

        print("Application stopped.")
