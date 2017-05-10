"""
Serialize from and to XML
"""

from lxml import etree

from generator import Generator
from validator import Validator, Error
from tools import is_primitive, remove_encoding_tag, bool_from_string


class Serializer:
    """Static serializer"""

    package_manager = None
    _instance = None

    def __init__(self):
        self.Object = self.package_manager.get_class("fxpq.core", "Object")
        self.Quantity = self.package_manager.get_class("fxpq.core", "Quantity")
        self.Reference = self.package_manager.get_class("fxpq.entities", "Reference")

        self.objects = self.Object.__subclasses__()
        self.errors = []

        self.generator = Generator(self.package_manager)
        dtd = self.generator.generate()
        self.validator = Validator(dtd, self.package_manager.get_path("fxpq/fxpq.sch"))

    @classmethod
    def instance(cls):
        if not cls.package_manager:
            raise AssertionError("You must instantiate a PackageManager before calling the Serializer.")

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
        self.errors = []

        # Most of the potential errors that the serializer would have faced are
        # already handled by the validator. Hence, the serializer's code
        # assumes most of the data to be correct after this point.
        if not self.validator.validate(xml_string):
            self.errors.extend(self.validator.errors)
            raise ValueError("The given xml string is not a valid FXPQ file.")

        root = etree.fromstring(remove_encoding_tag(xml_string),
            parser=etree.XMLParser(remove_comments=True))

        # fxpq files always have one child in the root
        return self._deserialize_object(root[0])

    def _serialize_object(self, xml_root, obj):
        name = obj.class_name().lower()
        attribs, attrib_elts = self._serialize_attributes(obj)
        xml_elt = etree.SubElement(xml_root, name, attrib=attribs)

        for attrib_elt, prop in attrib_elts.items():
            xml_attrib_elt = etree.SubElement(xml_elt, attrib_elt)
            self._serialize_property_value(xml_attrib_elt, prop)
        if obj.children:
            self._serialize_property_value(xml_elt, obj.children)

    def _serialize_attributes(self, obj):
        inline_attribs = {}
        attribute_elts = {}
        for name, prop in obj.get_properties().items():
            if prop.is_default() and not prop.required:
                continue

            if is_primitive(prop.type):
                inline_attribs[name] = str(prop.value)
            else:
                elt_name = "{0}.{1}".format(obj.class_name().lower(), name)
                attribute_elts[elt_name] = prop

        return inline_attribs, attribute_elts

    def _serialize_property_value(self, xml_elt, prop):
        if prop.value is None:
            return

        if is_primitive(prop.type):
            xml_elt.text = str(prop.value)
            return

        if prop.is_many():
            for value in prop.value:
                self._serialize_object(xml_elt, value)
        else:
            self._serialize_object(xml_elt, prop.value)

    def _deserialize_object(self, xml_elt):
        tag = etree.QName(xml_elt.tag)
        class_name = tag.localname.title().replace("_", "")
        class_ = next((o for o in self.objects if o.__name__ == class_name), None)
        if not class_:
            raise ValueError("There is no class with name \"{0}\" corresponding to the object \"{1}\"."
                .format(class_name, tag.localname))

        obj = class_()
        self._deserialize_attributes(xml_elt.attrib, obj)

        if obj.children and is_primitive(obj.children.type):
            self._parse_primitive_value(obj.children, self._get_text(xml_elt))

        for xml_child in xml_elt:
            if "." in xml_child.tag:
                self._deserialize_attribute_element(xml_child, obj)
            else:
                if not obj.children:
                    raise ValueError("The class \"{0}\" does not allow children."
                        .format(class_name))

                obj_child = self._deserialize_object(xml_child)
                if not isinstance(obj_child, obj.children.type):
                    if isinstance(obj_child, self.Reference):
                        with open("../data/Manafia/" + obj_child.path.value) as f:
                            obj_child = self.deserialize(f.read())
                    else:
                        raise ValueError("The class \"{0}\" does not allow children of type \"{1}\"."
                            .format(class_name, obj_child.class_name()))

                if not obj.children.value:
                    obj.children.value = []
                obj.children.value.append(obj_child)

        return obj

    def _deserialize_attributes(self, attrib, obj):
        for name, value in attrib.items():
            prop = getattr(obj, name)  # will always work, thanks to the validator
            self._parse_primitive_value(prop, value)

    def _deserialize_attribute_element(self, xml_elt, obj):
        class_name, attr_name = xml_elt.tag.split(".")
        prop = getattr(obj, attr_name)  # will always work, thanks to the validator

        if is_primitive(prop.type):
            self._parse_primitive_value(prop, self._get_text(xml_elt))
            return

        if prop.is_many():
            for xml_child in xml_elt:
                obj_child = self._deserialize_object(xml_child)
                if not prop.value:
                    prop.value = []
                prop.value.append(obj_child)
        else:
            try:
                xml_child = xml_elt[0]
            except IndexError:
                if prop.quantity == self.Quantity.ExactlyOne:
                    raise ValueError("There should be at least one value for the attribute \"{0}\"."
                        .format(attr_name))
                else:
                    return

            prop.value = self._deserialize_object(xml_child)

    def _parse_primitive_value(self, prop, string):
        if prop.type == bool:
            prop.value = bool_from_string(string)
        else:
            prop.value = prop.type(string)

    def _get_text(self, xml_elt):
        """Get the full text data from a xml element"""
        string = ""
        if xml_elt.text:
            string += xml_elt.text
        if xml_elt.tail:
            string += xml_elt.tail

        return string
