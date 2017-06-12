#!/usr/bin/env python3

from server.application import MasterServer


if __name__ == '__main__':
    server = MasterServer()
    server.run()
