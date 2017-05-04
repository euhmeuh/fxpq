"""
Unit tests for fxpqeditor
"""

import unittest

from package_manager import PackageManager
from serializer import Serializer


class SerializerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pm = PackageManager("./packages")
        Serializer.package_manager = pm
        cls.Dimension = pm.get_class("fxpq.roots", "Dimension")
        cls.Change = pm.get_class("fxpq.entities", "Change")
        cls.Author = pm.get_class("fxpq.entities", "Author")

        cls.xmldimension = '<?xml version="1.0" encoding="UTF-8"?>\n'\
            '<!DOCTYPE fxpq>\n'\
            '<fxpq version="1.0">'\
            '<dimension cellsize="16" display_name="My Favorite Dimension">'\
            '<dimension.changelog><change version="0.1">We did some stuff, I think..</change>'\
            '<change version="0.2">We did some stuff, I think..</change>'\
            '<change version="0.3">We did some stuff, I think..</change>'\
            '</dimension.changelog><dimension.authors><author>Jean Rochefort</author>'\
            '<author>Jean Rochefort</author></dimension.authors></dimension></fxpq>'

    def test_serialize_dimension(self):
        obj = SerializerTests.Dimension()
        obj.display_name.value = "My Favorite Dimension"
        obj.cellsize.value = 16
        obj.changelog.value = list(SerializerTests._sample_changes(3))
        obj.authors.value = list(SerializerTests._sample_authors(2))

        self.assertEqual(Serializer.instance().serialize(obj), SerializerTests.xmldimension)

    def test_deserialize_dimension(self):
        dimension = Serializer.instance().deserialize(SerializerTests.xmldimension)

        self.assertEqual(dimension.display_name.value, "My Favorite Dimension")
        self.assertEqual(dimension.cellsize.value, 16)
        self.assertEqual(dimension.changelog.value, list(SerializerTests._sample_changes(3)))
        self.assertEqual(dimension.authors.value, list(SerializerTests._sample_authors(2)))

    def test_raises_if_no_packagemanager(self):
        pm = Serializer.package_manager
        Serializer.package_manager = None

        with self.assertRaises(AssertionError):
            Serializer.instance()

        Serializer.package_manager = pm

    @classmethod
    def _sample_changes(cls, amount):
        for i in range(1, amount + 1):
            change = cls.Change()
            change.version.value = "0.{}".format(i)
            change.children.value = "We did some stuff, I think.."
            yield change

    @classmethod
    def _sample_authors(cls, amount):
        for i in range(1, amount + 1):
            author = cls.Author()
            author.children.value = "Jean Rochefort"
            yield author


if __name__ == "__main__":
    unittest.main()
