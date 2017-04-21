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
        self.default_value = default_value

        if isinstance(content_type, type):
            self.value = default_value
        else:
            # the default value for a primitive type is the given value
            self.value = content_type


class Object:
    """Abstract base of all FXPQuest objects"""

    children = None

    def move(self, delta_time):
        raise NotImplementedError

    def display(self, delta_time):
        raise NotImplementedError

    def act(self, delta_time):
        raise NotImplementedError

    @classmethod
    def properties(cls):
        return {k: v for k, v in vars(cls()).items() if isinstance(v, Property)}

