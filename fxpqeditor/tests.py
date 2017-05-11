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
        cls.Zone = pm.get_class("fxpq.roots", "Zone")
        cls.Dimension = pm.get_class("fxpq.roots", "Dimension")
        cls.Change = pm.get_class("fxpq.entities", "Change")
        cls.Author = pm.get_class("fxpq.entities", "Author")
        cls.Rectangle = pm.get_class("fxpq.entities", "Rectangle")

        cls.xmldimension = '<?xml version="1.0" encoding="UTF-8"?>\n'\
            '<!DOCTYPE fxpq>\n'\
            '<fxpq version="1.0">'\
            '<dimension cellsize="16" display_name="My Favorite Dimension">'\
            '<dimension.changelog><change version="0.1">We did some stuff, I think..</change>'\
            '<change breaking="True" version="0.2">We did some stuff, I think..</change>'\
            '<change version="0.3">We did some stuff, I think..</change>'\
            '</dimension.changelog><dimension.authors><author>Jean Rochefort</author>'\
            '<author>Jean Rochefort</author></dimension.authors><zone><zone.rectangles>'\
            '<rectangle h="1" w="1"/></zone.rectangles></zone></dimension></fxpq>'
        cls.maxDiff = None

    def test_serialize_dimension(self):
        obj = SerializerTests.Dimension()
        obj.display_name = "My Favorite Dimension"
        obj.cellsize = 16
        obj.changelog = list(SerializerTests._sample_changes(3))
        obj.authors = list(SerializerTests._sample_authors(2))
        obj.children = list(SerializerTests._sample_zones(1))

        self.assertEqual(Serializer.instance().serialize(obj), SerializerTests.xmldimension)

    def test_deserialize_dimension(self):
        dimension = Serializer.instance().deserialize(SerializerTests.xmldimension)

        self.assertEqual(dimension.display_name, "My Favorite Dimension")
        self.assertEqual(dimension.cellsize, 16)

        sample_changes = list(SerializerTests._sample_changes(3))
        sample_authors = list(SerializerTests._sample_authors(2))
        sample_zones = list(SerializerTests._sample_zones(1))

        self.assertListEqual(
            [c.children for c in dimension.changelog],
            [c.children for c in sample_changes])
        self.assertListEqual(
            [a.children for a in dimension.authors],
            [a.children for a in sample_authors])
        self.assertListEqual(
            [z.rectangles[0].w for z in dimension.children],
            [z.rectangles[0].w for z in sample_zones])

        for i, change in enumerate(dimension.changelog):
            self.assertListEqual(
                [p.value(change) for p in change.properties.values()],
                [p.value(sample_changes[i]) for p in sample_changes[i].properties.values()])

        for i, author in enumerate(dimension.authors):
            self.assertListEqual(
                [p.value(author) for p in author.properties.values()],
                [p.value(sample_authors[i]) for p in sample_authors[i].properties.values()])

    def test_raises_if_no_package_manager(self):
        pm = Serializer.package_manager
        Serializer.package_manager = None

        with self.assertRaises(AssertionError):
            Serializer.instance()

        Serializer.package_manager = pm

    @classmethod
    def _sample_changes(cls, amount):
        for i in range(1, amount + 1):
            change = cls.Change()
            change.version = "0.{}".format(i)
            change.children = "We did some stuff, I think.."
            change.breaking = (i % 2 == 0)
            yield change

    @classmethod
    def _sample_authors(cls, amount):
        for i in range(1, amount + 1):
            author = cls.Author()
            author.children = "Jean Rochefort"
            yield author

    @classmethod
    def _sample_zones(cls, amount):
        for i in range(1, amount + 1):
            zone = cls.Zone()
            rect = cls.Rectangle()
            rect.w, rect.h = 1, 1
            zone.rectangles = [rect]
            yield zone


if __name__ == "__main__":
    unittest.main()
