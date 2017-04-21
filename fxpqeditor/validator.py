#!/usr/bin/env python3

from lxml import etree
from lxml import isoschematron

class Validator:
    def __init__(self, dtd_path, schematron_path):
        self.dtd = etree.DTD(dtd_path)

        schematron_doc = etree.parse(schematron_path)
        self.schematron = isoschematron.Schematron(schematron_doc, store_report = True)

        self.errors = []

    def validate(self, file_path):
        self.errors = []
        doc = etree.parse(file_path)
        root = doc.getroot()

        if not self.dtd.validate(root):
            self.errors.append(self.dtd.error_log.filter_from_errors())

        if not self.schematron.validate(doc):
            self.errors.append(str(self.schematron.validation_report))

        return (not self.errors)


if __name__ == '__main__':
    validator = Validator("generated.dtd", "packages/fxpq/fxpq.sch")
    files = ["../data/Manafia/golfia.fxpq", "../data/Manafia/manafia.dim"]
    for f in files:
        if validator.validate(f):
            print("File \"{0}\" is valid.".format(f))
        else:
            print("Error! File \"{0}\" is invalid.".format(f))
            print(validator.errors)
