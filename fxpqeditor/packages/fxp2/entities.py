"""
FXP2 base entities
"""

from fxpq.core import Object, Property, Quantity


class Door(Object):
    """A door that leads to another level"""
    def __init__(self):
        self.model = Property("")
        self.target = Property("")


class Home(Object):
    """A simple outside home with a variable number of doors"""
    def __init__(self):
        self.model = Property("")
        self.doors = Property(Door, quantity=Quantity.OneOrMore)
