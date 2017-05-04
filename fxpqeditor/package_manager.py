"""
Package manager
"""

from pathlib import PurePath
import pkgutil
import importlib


class PackageManager:
    def __init__(self, packages_dir):
        self.packages_dir = PurePath(packages_dir)
        self.register_packages(packages_dir)

        self.modules = []
        self._find_and_import_modules(self.packages_dir)

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

    def _find_and_import_modules(self, pkg_dir):
        self.modules = []
        for importer, modname, ispkg in pkgutil.walk_packages(path=[pkg_dir]):
            print("Found {0} {1}".format("package" if ispkg else "module", modname))
            if not ispkg:
                module = importlib.import_module(modname)
                self.modules.append(module)
