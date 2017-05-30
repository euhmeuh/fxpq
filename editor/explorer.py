"""
The solution explorer that reads and display the content of a dimension
"""

from pathlib import Path

import tkinter as tk
from tkinter import ttk

from core.tools import ascii_to_xbm

from editor.document import FxpqDocument


class FxpqExplorer(ttk.Treeview):
    _image_pattern = "{}.xbm"
    _image_default = "object"
    _image_cache = {}

    def __init__(self, package_manager, master=None):
        super().__init__(master)

        self.Object = package_manager.get_class("fxpq.core", "Object")
        self.Quantity = package_manager.get_class("fxpq.core", "Quantity")
        self.Reference = package_manager.get_class("fxpq.core", "Reference")
        self.Zone = package_manager.get_class("fxpq.roots", "Zone")
        self.Dimension = package_manager.get_class("fxpq.roots", "Dimension")

        self.custom_images = package_manager.get_config("images")
        self.icons = package_manager.get_files_in("icons", self.Object)

        self.configure(selectmode='browse', columns=("type",))
        self.column('#0', width=100)
        self.column('#1', width=100, stretch=False)
        self.heading('#0', text="Element")
        self.heading('type', text="Type")

        self.documents = []

    def refresh(self, documents):
        self.clear()
        self.documents = documents
        for doc in self._find_orphans(documents):
            self._add(doc)

    def clear(self):
        for item in self.get_children():
            self.delete(item)

    def _find_orphans(self, documents):
        result = []
        for i, doc in enumerate(documents):
            others = documents[i + 1:]
            others.extend(documents[:i])
            if any([doc.filepath in other.reference_paths for other in others]):
                continue  # this document is not an orphan, skip it
            result.append(doc)

        return result

    def _add(self, doc, parent=None):
        parent = parent if parent else ""

        if doc.obj:
            elt = self.insert(parent, tk.END,
                text=self._get_display_name(doc.obj),
                values=(doc.obj.class_name,),
                image=self._get_image(doc.obj.class_name.lower()),
                open=True)

            for refpath in doc.reference_paths:
                child_doc = next((d for d in self.documents if d.filepath == refpath), None)
                if child_doc:
                    self._add(child_doc, parent=elt)

            for child in doc.obj.iter_children():
                if isinstance(child, self.Reference):
                    if doc.full_path(child.path) in [d.filepath for d in self.documents]:
                        continue  # skip already resolved references

                self._add_link(doc, child, elt)

        else:
            elt = self.insert(parent, tk.END,
                text=doc.title,
                values=("???",),
                open=True)

    def _add_link(self, doc, obj, parent):
        """Add a link to an inline object so that clicking on it will redirect to the file that contains it"""
        self.insert(parent, tk.END,
            text=self._get_display_name(obj),
            values=(obj.class_name,),
            image=self._get_image(obj.class_name.lower()),
            open=True)

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

    def _get_display_name(self, obj):
        display_name = obj.class_name
        if hasattr(obj, 'display_name'):
            display_name = obj.display_name
        if isinstance(obj, self.Reference):
            display_name = obj.path
        return display_name
