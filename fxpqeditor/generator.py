"""
Generates DTD rules from python packages
"""

from os import path
import pkgutil


class Generator:
    def __init__(self, packages_dir, package_list):

        self.packages_dir = packages_dir
        # allow local imports from the specified directory
        import sys
        sys.path.insert(0, packages_dir)

        # TODO: replace with a string parameter "Object"?
        from fxpq.core import Object
        self.base = Object

        self.packages = package_list
        self.objects = {}

    def generate(self):
        for package in self.packages:
            self._find_and_import_modules(self.packages_dir, package)

        self.objects = self.base.__subclasses__()

        result = []

        # the root fxpq element is the only python namespace to have its own element definition
        fxpq_element = "<!ELEMENT fxpq ({0})>".format(" | ".join(
            [c.__name__.lower() for c in self.rootobjects()]))
        result.append(fxpq_element)

        # it also have an attribute list with a version and all the xmlns definitions of other packages
        attributes = ["version\tCDATA\t#REQUIRED"]
        namespaces = {c.__module__.split(".")[0] for c in self.objects}
        attributes.extend(["xmlns:{0}\tCDATA\t#FIXED\t\"python-namespace:{0}\"".format(ns)
            for ns in namespaces if ns != "fxpq"])
        fxpq_attlist = "<!ATTLIST fxpq\n\t{0}\n>".format("\n\t".join(attributes))
        result.append(fxpq_attlist)

        for c in self.objects:
            result.extend(self._generate_element(c))

        return "\n".join(result)

    def rootobjects(self):
        return [o for o in self.objects if o.root]

    def _find_and_import_modules(self, pkg_dir, package, parent=""):
        pkgpath = path.join(pkg_dir, package)
        prefix = package + "."
        if parent:
            prefix = parent + "." + prefix

        for importer, modname, ispkg in pkgutil.walk_packages(path=[pkgpath], prefix=prefix):
            print("Found {0} {1}".format("package" if ispkg else "module", modname))
            if ispkg:
                self._find_and_import_modules(importer.path, modname, package)
            else:
                __import__(modname)

    def _generate_element(self, klass):
        result = []
        element_name = self._format_name(klass)

        children = self._generate_children(klass.children, klass)
        element = "<!ELEMENT {0} {1}>".format(element_name, children)
        result.append(element)

        attributes = self._generate_attributes(klass)
        result.extend(attributes)

        return result

    def _generate_children(self, prop, klass=None):
        """Generate allowed children based on a Property
           If you specify the @klass attribute, it'll also allow attribute elements first:
           ((attribute_elements)*, (prop.type)prop.quantity)
        """
        primitive_type = "#PCDATA"

        children_type = None
        attribute_elements = []

        if prop:
            if prop.type == self.base:
                return "ANY"

            if prop.type in [type(""), type(1), type(1.0), type(True)]:
                children_type = primitive_type
            else:
                children_type = self._format_name(prop.type)

                # every root element can be replaced by a Reference element
                if prop.type.root:
                    children_type = children_type + " | reference"

        if klass:
            element_name = self._format_name(klass)
            for name in klass.properties().keys():
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

    def _generate_attributes(self, klass):
        result = []
        element_name = self._format_name(klass)
        properties = klass.properties()
        if not properties:
            return result

        rules = self._generate_attribute_rules(klass)
        attlist = "<!ATTLIST {0}\n\t{1}\n>".format(element_name, "\n\t".join(rules))
        result.append(attlist)

        for name, prop in properties.items():
            att_element = self._generate_attribute_element(klass, name, prop)
            result.append(att_element)

        return result

    def _generate_attribute_rules(self, klass):
        for name in klass.properties().keys():
            yield "{0}\tCDATA\t#IMPLIED".format(name)

    def _generate_attribute_element(self, klass, name, prop):
        element_name = self._format_name(klass)
        children = self._generate_children(prop)
        return "<!ELEMENT {0}.{1} {2}>".format(element_name, name, children)

    def _format_name(self, klass):
        namespace = klass.__module__.split(".")[0]
        element_name = klass.__name__.lower()

        # elements that are not part of the fxpq namespace
        # must be prefixed with their respective namespace
        if namespace != "fxpq":
            element_name = namespace + ":" + element_name

        return element_name
