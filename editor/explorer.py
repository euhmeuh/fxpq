"""
The solution explorer that reads and display the content of a dimension
"""

from pathlib import Path

import tkinter as tk
from tkinter import ttk

from core.tools import is_primitive, ascii_to_xbm


class FxpqExplorer(ttk.Treeview):
    _image_pattern = "{}.xbm"
    _image_default = "object"
    _image_cache = {}

    def __init__(self, package_manager, master=None):
        super().__init__(master)

        self.Object = package_manager.get_class("fxpq.core", "Object")
        self.Quantity = package_manager.get_class("fxpq.core", "Quantity")
        self.Zone = package_manager.get_class("fxpq.roots", "Zone")
        self.Dimension = package_manager.get_class("fxpq.roots", "Dimension")

        self.custom_images = package_manager.get_config("images")
        self.icons = package_manager.get_files_in("icons", self.Object)

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
        for item in self.get_children():
            self.delete(item)

    def _add(self, obj, parent=None):
        parent = parent if parent else ""

        display_name = obj.class_name
        if hasattr(obj, 'display_name'):
            display_name = obj.display_name

        elt = self.insert(parent, tk.END,
            text=display_name,
            values=(obj.class_name,),
            image=self._get_image(obj.class_name.lower()),
            open=True)

        if obj.children_property and not is_primitive(obj.children_property.type):
            if obj.children_property.is_many():
                for child in obj.children:
                    self._add(child, parent=elt)
            else:
                self._add(obj.children, parent=elt)

    def _get_image(self, class_name):
        image = self._image_cache.get(class_name, None)
        if image:
            return image

        custom_image = self.custom_images.get(class_name, None)
        if custom_image:
            image = tk.BitmapImage(data=ascii_to_xbm(custom_image))
            self._image_cache[class_name] = image
            return image

        filename = self._image_pattern.format(class_name)
        filepath = self._try_get_icon(filename)
        if not filepath or not filepath.is_file():
            filepath = self._try_get_icon(self._image_pattern.format(self._image_default))

        image = tk.BitmapImage(file=filepath)
        self._image_cache[class_name] = image
        return image

    def _try_get_icon(self, filename):
        return next((Path(i) for i in self.icons if Path(i).name == filename), None)
