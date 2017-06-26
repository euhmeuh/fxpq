"""
Application base class.
Used to implement a server or a client. It runs a given list of services in an infinite loop.
"""

import time

from core.connection import Broker


class Service:
    can_run = False

    def subscribe(self, broker):
        self.broker = broker

    def run(self, delta_time):
        pass

    def fetch_res(self, name):
        return self.broker.fetch_res(name)

    def send_res(self, name, res):
        self.broker.send_res(name, res)


class Application:
    """Base application class for the server and the client"""

    def __init__(self, source_url=""):
        self.broker = Broker()
        self.services = []
        self.running = False

        self.fps = 60
        self.frame_time = 1.0 / self.fps
        self.service_times = {}

    def run(self):
        if self.running:
            return

        print("Application started.")

        for service in self.services:
            service.subscribe(self.broker)

        self.running = True
        try:
            self.broker.listen()
            self._loop()
        except KeyboardInterrupt:
            self.running = False
        finally:
            self.broker.close()

        print("Application stopped.")

    def _loop(self):
        self._init_times()

        while True:
            loop_time = time.perf_counter()

            for service in self.services:
                delta_time = time.perf_counter() - self.service_times[service]

                if service.can_run and service.run(delta_time):
                    # when the service returns True, it means it finished what it was doing,
                    # so we reset the delta_time for the next time
                    self.service_times[service] = time.perf_counter()

            total_delta = time.perf_counter() - loop_time

            if total_delta < self.frame_time:
                # we can sleep if we spent less than a frame time
                # so that the game runs at an almost constant pace
                time.sleep(self.frame_time - total_delta)

    def _init_times(self):
        """Initialize delta_time couters for every service"""

        for service in self.services:
            self.service_times[service] = time.perf_counter()
