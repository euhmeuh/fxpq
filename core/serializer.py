"""
Serialize from and to XML
"""

from lxml import etree
from pathlib import Path

from core.generator import Generator
from core.validator import Validator, Error
from core.tools import is_primitive, remove_encoding_tag, bool_from_string


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
        self.validator = Validator(dtd, "core/fxpq.sch")

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

    def deserialize(self, xml_string, reference_path=None):
        """Deserialize an xml fxpq file into an fxpq object
        Specifying the @reference_path argument enables following references recursively.
        Otherwise references will just be serialized as Reference instances.
        """

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
        first_elt = root[0]
        return self._deserialize_object(first_elt, reference_path)

    def _serialize_object(self, xml_root, obj):
        name = obj.class_name.lower()
        attribs, attrib_elts = self._serialize_attributes(obj)
        xml_elt = etree.SubElement(xml_root, name, attrib=attribs)

        for attrib_elt, prop in attrib_elts.items():
            xml_attrib_elt = etree.SubElement(xml_elt, attrib_elt)
            self._serialize_property_value(xml_attrib_elt, prop, obj)
        if obj.children_property:
            self._serialize_property_value(xml_elt, obj.children_property, obj)

    def _serialize_attributes(self, obj):
        inline_attribs = {}
        attribute_elts = {}
        for name, prop in obj.properties.items():
            if prop.is_default(obj) and not prop.required:
                continue

            if is_primitive(prop.type):
                inline_attribs[name] = str(prop.value(obj))
            else:
                elt_name = "{0}.{1}".format(obj.class_name.lower(), name)
                attribute_elts[elt_name] = prop

        return inline_attribs, attribute_elts

    def _serialize_property_value(self, xml_elt, prop, obj):
        prop_value = prop.value(obj)

        if prop_value is None:
            return

        if is_primitive(prop.type):
            xml_elt.text = str(prop_value)
            return

        if prop.is_many():
            for value in prop_value:
                self._serialize_object(xml_elt, value)
        else:
            self._serialize_object(xml_elt, prop_value)

    def _deserialize_object(self, xml_elt, reference_path=None):
        tag = etree.QName(xml_elt.tag)
        class_name = tag.localname.title().replace("_", "")
        class_ = next((o for o in self.objects if o.__name__ == class_name), None)
        if not class_:
            raise ValueError("There is no class with name \"{0}\" corresponding to the object \"{1}\"."
                .format(class_name, tag.localname))

        obj = class_()
        self._deserialize_attributes(xml_elt.attrib, obj)

        if isinstance(obj, self.Reference) and reference_path:
            try:
                return self._follow_reference(obj, reference_path)
            except FileNotFoundError as e:
                self._raise_error("Cannot find referenced file \"{0}\".".format(e.filename), xml_elt.sourceline)

        if obj.children_property and is_primitive(class_.children_property.type):
            self._parse_primitive_value(obj, obj.children_property, self._get_text(xml_elt))

        for xml_child in xml_elt:
            if "." in xml_child.tag:
                self._deserialize_attribute_element(xml_child, obj, reference_path)
            else:
                if not obj.children_property:
                    self._raise_error("The class \"{0}\" does not allow children.".format(class_name), xml_child.sourceline)

                obj_child = self._deserialize_object(xml_child, reference_path)

                # we don't check type if the child has been
                # deserialized as an unfollowed Reference
                if not isinstance(obj_child, self.Reference):
                    if not isinstance(obj_child, obj.children_property.type):
                        self._raise_error("The class \"{0}\" does not allow children of type \"{1}\"."
                            .format(class_name, obj_child.class_name), xml_child.sourceline)

                obj.children.append(obj_child)

        return obj

    def _deserialize_attributes(self, attrib, obj):
        for name, value in attrib.items():
            prop = obj.properties.get(name)  # will always work, thanks to the validator
            self._parse_primitive_value(obj, prop, value)

    def _deserialize_attribute_element(self, xml_elt, obj, reference_path=None):
        class_name, attr_name = xml_elt.tag.split(".")
        prop = obj.properties.get(attr_name)  # will always work, thanks to the validator

        if is_primitive(prop.type):
            self._parse_primitive_value(obj, prop, self._get_text(xml_elt))
            return

        if prop.is_many():
            for xml_child in xml_elt:
                obj_child = self._deserialize_object(xml_child, reference_path)
                prop.value(obj).append(obj_child)
        else:
            try:
                xml_child = xml_elt[0]
            except IndexError:
                if prop.quantity == self.Quantity.ExactlyOne:
                    self._raise_error("There should be at least one value for the attribute \"{0}\"."
                        .format(attr_name), xml_elt.sourceline)
                else:
                    return

            prop.set_value(obj, self._deserialize_object(xml_child, reference_path))

    def _follow_reference(self, reference, reference_path):
        path = Path(reference_path).parent / reference.path
        if not path.is_file():
            exception = FileNotFoundError()
            exception.filename = path
            raise exception

        with open(path) as f:
            return self.deserialize(f.read(), reference_path=path)

    def _parse_primitive_value(self, obj, prop, string):
        if prop.type == bool:
            prop.set_value(obj, bool_from_string(string))
        else:
            prop.set_value(obj, prop.type(string))

    def _get_text(self, xml_elt):
        """Get the full text data from a xml element"""
        string = ""
        if xml_elt.text:
            string += xml_elt.text
        if xml_elt.tail:
            string += xml_elt.tail

        return string

    def _raise_error(self, message, sourceline=0):
        error = Error(message)
        error.line = sourceline
        self.errors.append(error)
        raise ValueError(message)
