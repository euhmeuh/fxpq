"""
Root entities allowed once in every fxpq file
"""

from fxpq.core import Object, Property, Quantity
from fxpq.entities import Rectangle, Change, Author


class Zone(Object):
    root = True
    children = Property(Object, quantity=Quantity.ZeroOrMore)

    def __init__(self):
        self.map = Property("")
        self.display_name = Property("")
        self.rectangles = Property(Rectangle, quantity=Quantity.OneOrMore, required=True)


class Dimension(Object):
    root = True
    children = Property(Zone, quantity=Quantity.ZeroOrMore)

    def __init__(self):
        self.version = Property("")
        self.guid = Property("")
        self.display_name = Property("")
        self.changelog = Property(Change, quantity=Quantity.ZeroOrMore)
        self.authors = Property(Author, quantity=Quantity.OneOrMore)
        self.description = Property("")
        self.cellsize = Property(0)
