"""
Basic entities used in all fxpq files
"""

from fxpq.core import Object, Property, Quantity


class Reference(Object):
    def __init__(self):
        self.path = Property("")


class Rectangle(Object):
    def __init__(self):
        self.x = Property(0)
        self.y = Property(0)
        self.w = Property(0)
        self.h = Property(0)


class Change(Object):
    children = Property("")

    def __init__(self):
        self.version = Property("")
        self.date = Property("")
        self.breaking = Property(False)


class Author(Object):
    children = Property("")

    def __init__(self):
        self.section = Property("")
