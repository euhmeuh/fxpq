"""
Core FXPQ objects
"""

import uuid

from enum import Enum


class Quantity(Enum):
    ExactlyOne = ""
    OneOrMore = "+"
    ZeroOrMore = "*"
    ZeroOrOne = "?"


class Property:
    def __init__(self, content_type, quantity=Quantity.ZeroOrOne, default_value=None):
        if not isinstance(content_type, type):
            raise ValueError("Property's content_type parameter must be a type.")

        self.name = ""
        self.type = content_type
        self.quantity = quantity

        self._default_value = default_value
        if default_value is None:
            if self.type in [str, int, float, bool]:
                self._default_value = self.type()
            elif self.is_many():
                self._default_value = []

    @property
    def default_value(self):
        if hasattr(self._default_value, 'copy'):
            # avoid passing a reference to the default value
            return self._default_value.copy()
        else:
            return self._default_value

    @property
    def required(self):
        return self.quantity in (Quantity.ExactlyOne, Quantity.OneOrMore)

    def value(self, obj):
        return getattr(obj, self.name)

    def set_value(self, obj, value):
        setattr(obj, self.name, value)

    def is_default(self, obj):
        return (self.value(obj) == self.default_value)

    def is_many(self):
        return (self.quantity in (Quantity.OneOrMore, Quantity.ZeroOrMore))


class MetaObject(type):
    """Metaclass that process Properties"""

    def __new__(cls, clsname, bases, dct):
        properties = {}
        others = {}

        for base in bases:
            if not issubclass(base, Object):
                continue
            properties.update(base.properties)

        for name, value in dct.items():
            if isinstance(value, Property):
                value.name = name
                if name == 'children':
                    continue  # we ignore children
                properties[name] = value
            else:
                others[name] = value

        result_attr = {}

        # we keep the children property in its own field
        result_attr['_children'] = dct.get('children', None)
        result_attr['_properties'] = properties

        others.update(result_attr)
        return super().__new__(cls, clsname, bases, others)

    @property
    def properties(self):
        return self._properties

    @property
    def children_property(self):
        return self._children


class Object(metaclass=MetaObject):
    """Abstract base of all FXPQuest objects"""

    root = False

    def __init__(self):
        self.id = uuid.uuid4()

        if self.children_property:
            self.children = self.children_property.default_value
        else:
            self.children = None

        for name, prop in self.properties.items():
            prop.set_value(self, prop.default_value)

    def has_object_children(self):
        return self.children_property and self.children_property.type not in [str, int, float, bool]

    def iter_children(self):
        """Returns an iterable, even if the object has no children
        """
        if not self.has_object_children():
            return

        if self.children_property.is_many():
            for child in self.children:
                yield child
        else:
            yield self.children

    @property
    def references(self):
        """List of references to other files"""
        return iter(c for c in self.iter_children() if isinstance(c, Reference))

    @property
    def properties(self):
        return self.__class__.properties

    @property
    def children_property(self):
        return self.__class__.children_property

    @property
    def class_name(self):
        return self.__class__.__name__


class Reference(Object):
    """Reference to another fxpq file containing a root object"""

    path = Property(str, quantity=Quantity.ExactlyOne)
