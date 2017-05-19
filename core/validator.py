"""
Validates XML files against DTD and schematron rules
"""

from io import StringIO

from lxml import etree
from lxml import isoschematron

from core.tools import remove_encoding_tag


class Error:
    def __init__(self, error):
        self.line = 0
        self.message = ""

        if isinstance(error, etree.XMLSyntaxError):
            self.line = error.lineno
            self.message = error.msg

        elif isinstance(error, etree._LogEntry):
            self.line = error.line
            self.message = error.message

        elif isinstance(error, str):
            self.message = error

    def __repr__(self):
        return "ERROR (line {0}): {1}".format(self.line, self.message)


class Validator:
    def __init__(self, dtd_string, schematron_path):
        self.dtd = etree.DTD(StringIO(dtd_string))

        schematron_doc = etree.parse(schematron_path)
        self.schematron = isoschematron.Schematron(schematron_doc, store_report=True)

        self.errors = []

    def validate(self, xml_string):
        self.errors = []

        # remove encoding tag because lxml won't accept it for unicode objects
        xml_string = remove_encoding_tag(xml_string)

        try:
            root = etree.fromstring(xml_string)
        except etree.XMLSyntaxError as e:
            self.errors.append(Error(e))
            return

        if not self.dtd.validate(root):
            dtd_errors = [Error(e) for e in self.dtd.error_log.filter_from_errors()]
            self.errors.extend(dtd_errors)

        if not self.schematron.validate(root):
            schema_errors = self._parse_schematron_errors(root)
            self.errors.extend(schema_errors)

        return (not self.errors)

    def _parse_schematron_errors(self, root):
        errors = []
        report = self.schematron.validation_report
        namespaces = {"svrl": "http://purl.oclc.org/dsdl/svrl"}
        for fail in report.findall("svrl:failed-assert/svrl:text", namespaces=namespaces):
            location = fail.getparent().attrib.get("location")
            error = Error(fail.text.strip())
            error.line = root.xpath(location)[0].sourceline
            errors.append(error)

        return errors
