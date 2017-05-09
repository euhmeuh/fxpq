"""
Basic entities used in all fxpq files
"""

from fxpq.core import Object, Property


class Reference(Object):
    """Reference to another fxpq file containing a root object"""

    def __init__(self):
        self.path = Property("")


class Rectangle(Object):
    """Boundaries of a Zone"""

    def __init__(self):
        self.x = Property(0)
        self.y = Property(0)
        self.w = Property(0)
        self.h = Property(0)


class Change(Object):
    """Changes that happened to a dimension"""

    children = Property("")

    def __init__(self):
        self.version = Property("")
        self.date = Property("")
        self.breaking = Property(False)


class Author(Object):
    """Author of a dimension"""

    children = Property("")

    def __init__(self):
        self.section = Property("")
