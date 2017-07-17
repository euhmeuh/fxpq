"""
Package manager
"""

import os
from os import path
from pathlib import PurePath
import pkgutil
import importlib

from core.serializer import Serializer
from core.tools import get_subclasses


class PackageManager:
    def __init__(self, packages_dir):
        self.packages_dir = PurePath(packages_dir)
        self.register_packages(packages_dir)

        self.modules = []
        self._find_and_import_modules(self.packages_dir)

        # initialize the serializer
        Serializer.package_manager = self

    def register_packages(self, directory):
        """Allow imports from the specified directory"""
        import sys
        sys.path.insert(0, directory)

    def get_class(self, module, class_name):
        """Get a class from the specified module"""
        if not self.modules:
            self._find_and_import_modules(self.packages_dir)

        for mod in self.modules:
            if mod.__name__ == module:
                if hasattr(mod, class_name):
                    return getattr(mod, class_name)

        raise AttributeError("The class \"{0}\" was not found in module \"{1}\"."
            .format(class_name, module))

    def get_config(self, dict_name):
        """Get the merged dictionary of every config.py files"""
        if not self.modules:
            self._find_and_import_modules(self.packages_dir)

        result = {}

        for module in self.modules:
            if not module.__name__.endswith(".config"):
                continue

            if not hasattr(module, dict_name):
                continue

            variable = getattr(module, dict_name)
            if not isinstance(variable, dict):
                raise AttributeError("The configuration entry \"{0}\" in module \"{1}\" should be a dictionary."
                    .format(dict_name, module.__name__))

            result.update(variable)

        return result

    def get_path(self, path):
        """Get a path relative to the packages directory"""
        return str(self.packages_dir / path)

    def get_files_in(self, common_folder, base_class=None):
        """Find all the files present in every @common_folder of the packages.
        If @base_class is specified, restrict results to packages that defines a subclass of @base_class.

        Example: package_manager.get_files_in("templates") returns all the files in the "templates" folder of every package.
        """
        result = []
        for namespace, location in self.get_packages(base_class):

            folder = path.join(location, common_folder)
            if not path.exists(folder):
                continue

            result.extend([path.abspath(path.join(folder, f))
                for f in os.listdir(folder) if path.isfile(path.join(folder, f))])

        return result

    def get_packages(self, base_class=None):
        """Returns the toplevel packages discovered by the package manager as a tuple (name, path).
        If @base_class is specified, restrict results to packages that defines a subclass of @base_class.
        """
        modules = self.modules
        if base_class:
            modules = [c.__module__ for c in get_subclasses(base_class)]

        namespaces = {module.split(".")[0] for module in modules}

        return [(ns, self.get_path(ns)) for ns in namespaces]

    def _find_and_import_modules(self, pkg_dir):
        self.modules = []
        for importer, modname, ispkg in pkgutil.walk_packages(path=[pkg_dir]):
            print("Found {0} {1}".format("package" if ispkg else "module", modname))
            if not ispkg:
                module = importlib.import_module(modname)
                self.modules.append(module)
