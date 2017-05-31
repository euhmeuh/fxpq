"""
The solution explorer that reads and display the content of a dimension
"""

from pathlib import Path

import tkinter as tk
from tkinter import ttk

from core.tools import ascii_to_xbm

from editor.events import EventEmitter


class FxpqExplorer(EventEmitter, ttk.Treeview):
    _image_pattern = "{}.xbm"
    _image_default = "object"
    _image_cache = {}

    def __init__(self, package_manager, master=None):
        super().__init__(master)

        self.Object = package_manager.get_class("fxpq.core", "Object")
        self.Reference = package_manager.get_class("fxpq.core", "Reference")

        self.custom_images = package_manager.get_config("images")
        self.icons = package_manager.get_files_in("icons", self.Object)

        self.configure(selectmode='browse', columns=("type", "doc"))
        self.column('#0', width=100)
        self.column('#1', width=100, stretch=False)
        self.column('#2', width=100, stretch=False)
        self.heading('#0', text="Element")
        self.heading('type', text="Type")
        self.heading('doc', text="Document")

        self.bind("<Double-1>", self.on_double_click)

        self.documents = []
        self.tree_items = {}

    def refresh(self, documents):
        self.clear()
        self.documents = documents
        for doc in self._find_orphans(documents):
            self._add(doc)

    def clear(self):
        for item in self.get_children():
            self.delete(item)

    def on_double_click(self, event):
        item = self.identify('item', event.x, event.y)
        filepath = self.tree_items.get(item, None)
        if filepath:
            self.emit('explorer-open', filepath)

    def _find_orphans(self, documents):
        result = []
        for i, doc in enumerate(documents):
            others = documents[i + 1:]
            others.extend(documents[:i])
            if any([other.is_referenced(doc.filepath) for other in others]):
                continue  # this document is not an orphan, skip it
            result.append(doc)

        return result

    def _add(self, doc, parent=None, inline_obj=None):
        """Add a new item in the tree view
        If @parent is specified, add the item as a child of @parent.
        If @inline_obj is specified, use it instead of doc.obj (useful for linking an inline object to an already existing document)
        """

        parent = parent if parent else ""
        obj = inline_obj if inline_obj else doc.obj

        destpath = doc.filepath  # the path this item we lead to

        if obj:
            elt = self.insert(parent, tk.END,
                text=self._get_display_name(obj),
                values=(obj.class_name, doc.title),
                image=self._get_image(obj.class_name.lower()),
                open=True)

            # double-cliking on references will open the referenced file
            if isinstance(obj, self.Reference):
                destpath = doc.full_path(obj.path)

            for refpath in doc.get_reference_paths(obj):
                child_doc = next((d for d in self.documents if d.filepath == refpath), None)
                if child_doc:
                    self._add(child_doc, parent=elt)

            for child in obj.iter_children():
                if isinstance(child, self.Reference):
                    if doc.full_path(child.path) in [d.filepath for d in self.documents]:
                        continue  # skip already resolved references

                self._add(doc, parent=elt, inline_obj=child)
        else:
            elt = self.insert(parent, tk.END,
                text=doc.title,
                values=("???", doc.title),
                open=True)

        self.tree_items[elt] = destpath

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
