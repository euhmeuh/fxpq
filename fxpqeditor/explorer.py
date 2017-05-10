"""
The solution explorer that reads and display the content of a dimension
"""

from pathlib import Path

import tkinter as tk
from tkinter import ttk

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

        self.custom_images = package_manager.get_config("images")

        self.configure(selectmode='browse', columns=("type",))
        self.column('#0', width=100)
        self.column('#1', width=100, stretch=False)
        self.heading('#0', text="Element")
        self.heading('type', text="Type")

    def refresh(self, objects):
        self.clear()
        for obj in objects:
            self._add(obj)

    def clear(self):
        print(self.get_children())
        for item in self.get_children():
            self.delete(item)

    def _add(self, obj, parent=None):
        parent = parent if parent else ""

        display_name = obj.class_name()
        if hasattr(obj, 'display_name'):
            display_name = obj.display_name.value

        elt = self.insert(parent, "end",
            text=display_name,
            values=(obj.class_name(),),
            image=self._get_image(obj.class_name().lower()))

        if obj.children and not is_primitive(obj.children.type):
            if obj.children.is_many():
                for child in obj.children.value:
                    self._add(child, parent=elt)
            else:
                self._add(obj.children.value, parent=elt)

    def _get_image(self, class_name):
        image = self._image_cache.get(class_name, None)
        if image:
            return image

        custom_image = self.custom_images.get(class_name, None)
        if custom_image:
            image = tk.BitmapImage(data=ascii_to_xbm(custom_image))
            self._image_cache[class_name] = image
            return image

        path = Path(self._image_pattern.format(class_name))
        if not path.is_file():
            path = self._image_pattern.format(self._image_default)

        image = tk.BitmapImage(file=path)
        self._image_cache[class_name] = image
        return image
