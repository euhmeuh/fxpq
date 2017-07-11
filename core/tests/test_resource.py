"""
Unit tests for the resources
"""

import unittest

from core.connection import Resource


class Pokemon(Resource):
    def __init__(self, id_, name):
        self.id = id_
        self.name = name

    def key(self):
        return self.id

    def __repr__(self):
        return "{}({}, \"{}\")".format(self.__class__.__name__, self.id, self.name)


class ResourceTests(unittest.TestCase):

    def setUp(self):
        self.server1_res = [Pokemon(1, "Bulbasaur"), Pokemon(4, "Charmander"), Pokemon(7, "Squirtle")]
        self.server2_res = [Pokemon(1, "Bulbasaur"), Pokemon(19, "Rattata")]
        self.local_res = [Pokemon(25, "Pikachu")]
        self.total_res = [Pokemon(1, "Bulbasaur"), Pokemon(4, "Charmander"), Pokemon(7, "Squirtle"), Pokemon(25, "Pikachu"), Pokemon(19, "Rattata")]
        self.starters = [Pokemon(1, "Bulbasaur"), Pokemon(4, "Charmander"), Pokemon(7, "Squirtle"), Pokemon(25, "Pikachu")]

    def test_merge_authorized_iterables(self):
        total_res = Resource.merge([list(self.server1_res), tuple(self.local_res), set(self.server2_res)])
        self.assertCountEqual(total_res, self.total_res)

    def test_merge_other_types(self):
        res = Resource.merge(self.total_res)
        self.assertEqual(res, Pokemon(25, "Pikachu"))

    def test_merge_disparate(self):
        """Try to merge a resource list that contains objects and iterables at the same time"""
        result = Resource.merge([Pokemon(25, "Pikachu"), self.server1_res])
        self.assertCountEqual(result, self.starters)

    def test_merge_unsupported_types(self):
        result = Resource.merge(["Ditto", Pokemon(25, "Pikachu"), "Pidgey", 1234, 2.0, lambda x: x * x, dict()])
        # the last comparable resource is used
        # here it is Pidgey because "Pidgey" > "Ditto" alphabetically
        self.assertEqual(result, "Pidgey")
