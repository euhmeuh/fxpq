"""
The solution explorer that reads and display the content of a dimension
"""

import tkinter as tk
from tkinter import ttk

from serializer import Serializer

class FxpqExplorer(ttk.Treeview):
    def __init__(self, base_type, master=None):
        super().__init__(master)

        self.images = {
            'dimension': tk.BitmapImage(file="icons/dimension.xbm"),
            'zone': tk.BitmapImage(file="icons/zone.xbm"),
            'object': tk.BitmapImage(file="icons/object.xbm"),
        }

        self.configure(selectmode='browse', columns=("type",))
        self.column('#0', width=100)
        self.column('#1', width=100, stretch=False)
        self.heading('#0', text="Element")
        self.heading('type', text="Type")
        manafia = self.insert("", "end", text="Manafia", values=("Dimension",), image=self.images['dimension'])
        golfia = self.insert(manafia, "end", text="Golfia", values=("Zone",), image=self.images['zone'])
        self.insert(golfia, "end", text="Home", values=("Object",), image=self.images['object'])
        self.insert(golfia, "end", text="Tree", values=("Object",), image=self.images['object'])

        # initialize the serializer with the base type
        Serializer.base = base_type

    def update(self, current_file):
        """Update the treeview depending on the currently edited file"""


