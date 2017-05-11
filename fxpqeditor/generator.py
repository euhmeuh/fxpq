"""
Generates DTD rules from python packages
"""

from tools import is_primitive


class Generator:
    def __init__(self, package_manager):
        self.Object = package_manager.get_class("fxpq.core", "Object")
        self.objects = self.Object.__subclasses__()

    def generate(self):
        result = []

        # the root fxpq element is the only python namespace to have its own element definition
        fxpq_element = "<!ELEMENT fxpq ({0})>".format(" | ".join(
            [c.__name__.lower() for c in self.root_objects()]))
        result.append(fxpq_element)

        # it also have an attribute list with a version and all the xmlns definitions of other packages
        attributes = ["version\tCDATA\t#REQUIRED"]
        namespaces = {self._get_namespace(c) for c in self.objects}
        attributes.extend(["xmlns:{0}\tCDATA\t#FIXED\t\"python-namespace:{0}\"".format(ns)
            for ns in namespaces if ns != "fxpq"])
        fxpq_attlist = "<!ATTLIST fxpq\n\t{0}\n>".format("\n\t".join(attributes))
        result.append(fxpq_attlist)

        for c in self.objects:
            result.extend(self._generate_element(c))

        return "\n".join(result)

    def root_objects(self):
        return [o for o in self.objects if o.root]

    def _generate_element(self, class_):
        result = []
        element_name = self._format_name(class_)

        children = self._generate_children(class_.children_property, class_)
        element = "<!ELEMENT {0} {1}>".format(element_name, children)
        result.append(element)

        attributes = self._generate_attributes(class_)
        result.extend(attributes)

        return result

    def _generate_children(self, prop, class_=None):
        """Generate allowed children based on a Property
           If you specify the @class_ attribute, it'll also allow attribute elements first:
           ((attribute_elements)*, (prop.type)prop.quantity)
        """
        primitive_type = "#PCDATA"

        children_type = None
        attribute_elements = []

        if prop:
            if prop.type == self.Object:
                return "ANY"

            if is_primitive(prop.type):
                children_type = primitive_type
            else:
                children_type = self._format_name(prop.type)

                # every root element can be replaced by a Reference element
                if prop.type.root:
                    children_type = children_type + " | reference"

        if class_:
            element_name = self._format_name(class_)
            for name in class_.properties.keys():
                attribute_elements.append("{0}.{1}".format(element_name, name))

        if not children_type and not attribute_elements:
            return "EMPTY"

        if not attribute_elements:
            if children_type == primitive_type:
                # only primitive content
                return "({0})".format(children_type)
            else:
                # only specific type content
                return "({0}){1}".format(children_type, prop.quantity.value)

        if not children_type:
            # only properties
            return "({0})*".format(" | ".join(attribute_elements))

        if children_type == primitive_type:
            # mixed content
            return "({0} | {1})*".format(children_type, " | ".join(attribute_elements))

        # both properties and children are specific types
        return "(({0})*, ({1}){2})".format(" | ".join(attribute_elements), children_type, prop.quantity.value)

    def _generate_attributes(self, class_):
        result = []
        element_name = self._format_name(class_)
        properties = class_.properties
        if not properties:
            return result

        rules = self._generate_attribute_rules(class_)
        attlist = "<!ATTLIST {0}\n\t{1}\n>".format(element_name, "\n\t".join(rules))
        result.append(attlist)

        for name, prop in properties.items():
            att_element = self._generate_attribute_element(class_, name, prop)
            result.append(att_element)

        return result

    def _generate_attribute_rules(self, class_):
        for name in class_.properties.keys():
            yield "{0}\tCDATA\t#IMPLIED".format(name)

    def _generate_attribute_element(self, class_, name, prop):
        element_name = self._format_name(class_)
        children = self._generate_children(prop)
        return "<!ELEMENT {0}.{1} {2}>".format(element_name, name, children)

    def _format_name(self, class_):
        namespace = self._get_namespace(class_)
        element_name = class_.__name__.lower()

        # elements that are not part of the fxpq namespace
        # must be prefixed with their respective namespace
        if namespace != "fxpq":
            element_name = namespace + ":" + element_name

        return element_name

    def _get_namespace(self, class_):
        return class_.__module__.split(".")[0]
