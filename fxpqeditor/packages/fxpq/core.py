"""
Core FXPQ objects
"""

from enum import Enum


class Quantity(Enum):
    ExactlyOne = ""
    OneOrMore = "+"
    ZeroOrMore = "*"
    ZeroOrOne = "?"


class Property:
    def __init__(self, content_type, quantity=Quantity.ExactlyOne, required=False, default_value=None):
        self.type = content_type if isinstance(content_type, type) else type(content_type)
        self.quantity = quantity
        self.required = required

        if isinstance(content_type, type):
            self.value = default_value
            self.default_value = default_value
        else:
            # the default value for a primitive type is the given value
            self.value = content_type
            self.default_value = content_type


class Object:
    """Abstract base of all FXPQuest objects"""

    root = False
    children = None

    def move(self, delta_time):
        raise NotImplementedError

    def display(self, delta_time):
        raise NotImplementedError

    def act(self, delta_time):
        raise NotImplementedError

    def get_properties(self):
        """Get the properties of the current instance"""
        return {k: v for k, v in vars(self).items() if isinstance(v, Property)}

    @classmethod
    def properties(cls):
        """Get a dictionary of all the Property variables defined in this class"""
        return {k: v for k, v in vars(cls()).items() if isinstance(v, Property)}

