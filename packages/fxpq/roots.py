"""
Root entities allowed once in every fxpq file
"""

from fxpq.core import Object, Property, Quantity as Q
from fxpq.entities import Rectangle, Door, Change, Author


class Zone(Object):
    root = True
    children = Property(Object, quantity=Q.ZeroOrMore)

    map = Property(str)
    display_name = Property(str, quantity=Q.ExactlyOne)
    rectangles = Property(Rectangle, quantity=Q.OneOrMore)
    doors = Property(Door, quantity=Q.ZeroOrMore)


class Dimension(Object):
    root = True
    children = Property(Zone, quantity=Q.ZeroOrMore)

    guid = Property(str, quantity=Q.ExactlyOne)
    display_name = Property(str, quantity=Q.ExactlyOne)
    cellsize = Property(int, quantity=Q.ExactlyOne)

    version = Property(str)
    description = Property(str)

    authors = Property(Author, quantity=Q.OneOrMore)
    changelog = Property(Change, quantity=Q.ZeroOrMore)


class Factory(Object):
    root = True
    children = Property(Object, quantity=Q.ExactlyOne)

    resource = Property(str, quantity=Q.ExactlyOne)
