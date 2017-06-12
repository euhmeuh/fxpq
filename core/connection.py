"""
Networking logic
"""


class LocalSource:
    pass


class ServerSource:

    def __init__(self, url):
        self.url = url


class Broker:
    """Main object owner that sends and receives data from local and online sources"""

    def __init__(self, source_url=""):
        self.sources = [LocalSource()]

        if source_url:
            self.sources.add(ServerSource(source_url))
