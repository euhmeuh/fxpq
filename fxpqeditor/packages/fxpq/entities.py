"""
Basic entities used in all fxpq files
"""

from fxpq.core import Object, Property, Quantity


class Reference(Object):
    pass


class Rectangle(Object):
    def __init__(self):
        self.x = Property(0)
        self.y = Property(0)
        self.w = Property(0)
        self.h = Property(0)


class Change(Object):
    pass


class Author(Object):
    pass
