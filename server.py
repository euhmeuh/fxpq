#!/usr/bin/env python3

from server.application import ZoneServer


if __name__ == '__main__':
    server = ZoneServer()
    server.run()
