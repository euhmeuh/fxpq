"""
FXP2 base entities
"""

from fxpq.core import Object, Property, Quantity


class Key(Object):
    """A condition for a Door to open"""

    pass


class Door(Object):
    """A door that leads to another level"""

    model = Property(str)
    target = Property(str)
    keys = Property(Key, quantity=Quantity.ZeroOrMore)


class Home(Object):
    """A simple outside home with a variable number of doors"""

    model = Property(str)
    doors = Property(Door, quantity=Quantity.OneOrMore)
