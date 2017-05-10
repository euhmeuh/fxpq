"""
The solution explorer that reads and display the content of a dimension
"""

from pathlib import Path

import tkinter as tk
from tkinter import ttk

from serializer import Serializer
from tools import is_primitive, ascii_to_xbm


class FxpqExplorer(ttk.Treeview):
    _image_pattern = "icons/{}.xbm"
    _image_default = "object"
    _image_cache = {}

    def __init__(self, package_manager, master=None):
        super().__init__(master)

        self.Object = package_manager.get_class("fxpq.core", "Object")
        self.Quantity = package_manager.get_class("fxpq.core", "Quantity")
        self.Zone = package_manager.get_class("fxpq.roots", "Zone")
        self.Dimension = package_manager.get_class("fxpq.roots", "Dimension")

        self.objects = []

        self.configure(selectmode='browse', columns=("type",))
        self.column('#0', width=100)
        self.column('#1', width=100, stretch=False)
        self.heading('#0', text="Element")
        self.heading('type', text="Type")

        with open("../data/Manafia/manafia.dim") as f:
            text = f.read()
            print(text)
            self.update(text)

    def update(self, current_fxpqtext):
        """Update the treeview depending on the currently edited file"""
        try:
            obj = Serializer.instance().deserialize(current_fxpqtext)
        except ValueError:
            raise
            return

        parent = self._try_to_find_parent(obj)
        self.add(obj, parent=parent)

    def add(self, obj, parent=None):
        parent = parent if parent else ""

        display_name = obj.class_name()
        if hasattr(obj, 'display_name'):
            display_name = obj.display_name.value

        elt = self.insert(parent, "end",
            text=display_name,
            values=(obj.class_name(),),
            image=self._get_image(obj.class_name().lower()))

        if obj.children and not is_primitive(obj.children.type):
            if obj.children.quantity in (self.Quantity.ZeroOrMore, self.Quantity.OneOrMore):
                for child in obj.children.value:
                    self.add(child, parent=elt)
            else:
                self.add(obj.children.value, parent=elt)

    def _try_to_find_parent(self, obj):
        return None

    def _get_image(self, class_name):
        image = self._image_cache.get(class_name, None)
        if image:
            return image

        path = Path(self._image_pattern.format(class_name))
        if not path.is_file():
            path = self._image_pattern.format(self._image_default)

        image = tk.BitmapImage(file=path)
        self._image_cache[class_name] = image
        return image
