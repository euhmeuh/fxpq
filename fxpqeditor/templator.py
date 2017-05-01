"""
Creates new files from templates with {{moustache}} syntax
"""

import os
from os import path
import regex as re


class Templator:
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir
        self.templates = [f for f in os.listdir(templates_dir) if path.isfile(path.join(templates_dir, f))]

    def new(self, obj_type, input_values={}):
        typename = obj_type.__name__.lower()
        filename = next((f for f in self.templates if typename in self._find_moustaches(f)), None)
        if not filename:
            filename = path.join(self.templates_dir, r"{{object}}.fxpq")
            input_values['object'] = typename
        else:
            filename = path.join(self.templates_dir, filename)

        with open(filename) as f:
            text = f.read()
            return self._replace_moustaches(text, input_values)

    def _find_moustaches(self, string):
        return re.findall(r'{{([a-zA-Z_][\w_.-]*)}}', string)

    def _replace_moustaches(self, string, dictionary):
        for moustache in self._find_moustaches(string):
            string = string.replace(r'{{' + moustache + r'}}', dictionary.get(moustache, ""))
        return string

