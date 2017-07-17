"""
FXP2 base entities
"""

from fxpq.core import Object, Property, Quantity as Q
from fxpq.entities import Door as FxpqDoor


class Door(FxpqDoor):
    model = Property(str)


class Home(Object):
    """A simple outside home with a variable number of doors"""

    model = Property(str)
    doors = Property(Door, quantity=Q.ZeroOrMore)
