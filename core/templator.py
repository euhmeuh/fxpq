"""
Creates new files from templates with {{moustache}} syntax
"""

from os import path
import regex as re


class Templator:
    _default_template = r"fxpq/templates/{{object}}.fxpq"

    def __init__(self, package_manager):
        self.package_manager = package_manager
        self.Object = package_manager.get_class("fxpq.core", "Object")
        self.objects = self.Object.__subclasses__()

        self.templates = package_manager.get_files_in("templates", self.Object)

    def new(self, obj_type, input_values=None):
        if not input_values:
            input_values = {}

        typename = obj_type.__name__.lower()
        filename = next((f for f in self.templates if typename in self._find_moustaches(path.basename(f))), None)
        if not filename:
            filename = self.package_manager.get_path(self._default_template)
            input_values['object'] = typename

        with open(filename) as f:
            text = f.read()
            result_text = self._replace_moustaches(text, input_values)
            result_title = self._format_title(filename, typename, input_values)
            return result_title, result_text

    def _format_title(self, filename, typename, input_values):
        if not input_values.get("name", ""):
            return "untitled {}".format(typename)

        replacement = {}
        replacement[typename] = input_values["name"]
        return self._replace_moustaches(path.basename(filename), replacement)

    def _find_moustaches(self, string):
        return re.findall(r'{{([a-zA-Z_][\w_.-]*)}}', string)

    def _replace_moustaches(self, string, dictionary):
        for moustache in self._find_moustaches(string):
            string = string.replace(r'{{' + moustache + r'}}', dictionary.get(moustache, ""))
        return string
