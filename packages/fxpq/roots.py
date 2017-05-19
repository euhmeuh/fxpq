"""
Root entities allowed once in every fxpq file
"""

from fxpq.core import Object, Property, Quantity
from fxpq.entities import Rectangle, Change, Author


class Zone(Object):
    root = True
    children = Property(Object, quantity=Quantity.ZeroOrMore)

    map = Property(str)
    display_name = Property(str)
    rectangles = Property(Rectangle, quantity=Quantity.OneOrMore, required=True)


class Dimension(Object):
    root = True
    children = Property(Zone, quantity=Quantity.ZeroOrMore)

    version = Property(str)
    guid = Property(str)
    display_name = Property(str)
    changelog = Property(Change, quantity=Quantity.ZeroOrMore)
    authors = Property(Author, quantity=Quantity.OneOrMore)
    description = Property(str)
    cellsize = Property(int)


class Lolilol(Object):
    root = True
