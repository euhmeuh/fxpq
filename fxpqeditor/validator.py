#!/usr/bin/env python3

import re
from io import StringIO

from lxml import etree
from lxml import isoschematron

class Validator:
    def __init__(self, dtd_string, schematron_path):
        self.dtd = etree.DTD(StringIO(dtd_string))

        schematron_doc = etree.parse(schematron_path)
        self.schematron = isoschematron.Schematron(schematron_doc, store_report = True)

        self.errors = []

    def validate(self, xml_string):
        self.errors = []

        xml_string = self._remove_encoding_tag(xml_string)

        try:
            root = etree.fromstring(xml_string)
        except etree.XMLSyntaxError as e:
            self.errors.append(str(e))
            return

        if not self.dtd.validate(root):
            self.errors.append(self.dtd.error_log.filter_from_errors())

        if not self.schematron.validate(root):
            self.errors.append(str(self.schematron.validation_report))

        return (not self.errors)

    def _remove_encoding_tag(self, string):
        # remove encoding tag because lxml won't accept it for unicode objects
        if string.startswith('<?'):
            string = re.sub(r'^\<\?.*?\?\>', '', string, flags=re.DOTALL)

        return string
