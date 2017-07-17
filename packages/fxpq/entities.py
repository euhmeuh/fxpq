"""
Basic entities used in all fxpq files
"""

from fxpq.core import Object, Property, Quantity as Q


class Rectangle(Object):
    """Boundaries of a Zone"""
    x = Property(int)
    y = Property(int)
    w = Property(int)
    h = Property(int)


class Key(Object):
    """A condition for a Door to open"""
    pass


class Door(Object):
    """A door that leads to another zone"""
    rectangles = Property(Rectangle, quantity=Q.OneOrMore)
    keys = Property(Key, quantity=Q.ZeroOrMore)
    event = Property(str, quantity=Q.ExactlyOne)
    target = Property(str, quantity=Q.ExactlyOne)


class Change(Object):
    """Changes that happened to a dimension"""
    children = Property(str, quantity=Q.ZeroOrMore)

    version = Property(str, quantity=Q.ExactlyOne)
    date = Property(str)
    breaking = Property(bool)


class Author(Object):
    """Author of a dimension"""
    children = Property(str, quantity=Q.ExactlyOne)

    section = Property(str)
