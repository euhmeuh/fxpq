"""
Serialize from and to XML
"""

from lxml import etree

from tools import isprimitive


class Serializer:
    """Static serializer"""

    package_manager = None
    _instance = None

    def __init__(self):
        self.base = self.package_manager.get_class("fxpq.core", "Object")
        self.Quantity = self.package_manager.get_class("fxpq.core", "Quantity")

    @classmethod
    def instance(cls):
        if not cls.package_manager:
            raise AssertionError("You must set the Serializer's \"package_manager\" static field before creating instances.")

        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def serialize(self, obj):
        root = etree.Element("fxpq", attrib={'version': "1.0"})

        self._serialize_object(root, obj)

        document = etree.tostring(root, encoding="unicode")
        result = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fxpq>\n{}'
        return result.format(document)

    def deserialize(self, xml_string):
        raise NotImplementedError

    def _serialize_object(self, xml_root, obj):
        name = obj.__class__.__name__.lower()
        attribs, attrib_elts = self._serialize_attributes(obj)
        xml_elt = etree.SubElement(xml_root, name, attrib=attribs)

        for attrib_elt, prop in attrib_elts.items():
            xml_attrib_elt = etree.SubElement(xml_elt, attrib_elt)
            self._serialize_property_value(xml_attrib_elt, prop)

        self._serialize_property_value(xml_elt, obj.children)

    def _serialize_attributes(self, obj):
        inline_attribs = {}
        attribute_elts = {}
        for name, prop in obj.get_properties().items():
            if prop.value == prop.default_value and not prop.required:
                continue

            if isprimitive(prop.type):
                inline_attribs[name] = str(prop.value)
            else:
                elt_name = "{0}.{1}".format(obj.__class__.__name__.lower(), name)
                attribute_elts[elt_name] = prop

        return inline_attribs, attribute_elts

    def _serialize_property_value(self, xml_elt, prop):
        if prop.value is None:
            return

        if isprimitive(prop.type):
            xml_elt.text = str(prop.value)
            return

        if prop.quantity in (self.Quantity.ZeroOrMore, self.Quantity.OneOrMore):
            for value in prop.value:
                self._serialize_object(xml_elt, value)
        else:
            self._serialize_object(xml_elt, prop.value)
