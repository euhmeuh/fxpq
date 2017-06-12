"""
Application base class.
Used to implement a server or a client. It runs a given list of services in an infinite loop.
"""

import time

from core.connection import Broker


class Application:
    """Base server class"""

    def __init__(self, source_url=""):
        self.broker = Broker(source_url)
        self.services = []
        self.running = False

        self.fps = 60
        self.frame_time = 1.0 / self.fps
        self.service_times = {}

    def run(self):
        if self.running:
            return

        print("Server started.")

        self.running = True
        try:
            self._loop()
        except KeyboardInterrupt:
            self.running = False

        print("Server stopped.")

    def _loop(self):
        self._init_times()

        while self.running:
            loop_time = time.perf_counter()

            for service in self.services:
                delta_time = time.perf_counter() - self.service_times[service]
                if service.run(self.broker, delta_time):
                    self.service_times[service] = time.perf_counter()

            total_delta = time.perf_counter() - loop_time

            if total_delta < self.frame_time:
                time.sleep(self.frame_time - total_delta)

    def _init_times(self):
        """Initialize delta_time couters for every service"""

        for service in self.services:
            self.service_times[service] = time.perf_counter()
