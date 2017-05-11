"""
Basic entities used in all fxpq files
"""

from fxpq.core import Object, Property


class Reference(Object):
    """Reference to another fxpq file containing a root object"""

    path = Property(str)


class Rectangle(Object):
    """Boundaries of a Zone"""

    x = Property(int)
    y = Property(int)
    w = Property(int)
    h = Property(int)


class Change(Object):
    """Changes that happened to a dimension"""

    children = Property(str)

    version = Property(str)
    date = Property(str)
    breaking = Property(bool)


class Author(Object):
    """Author of a dimension"""

    children = Property(str)

    section = Property(str)
