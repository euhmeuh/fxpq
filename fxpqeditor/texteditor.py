"""
Custom text editor with syntax highlighting and live validations
"""

import tkinter as tk
from tkinter import ttk

from pygubu.builder.widgets.scrollbarhelper import ScrollbarHelper

from generator import Generator
from validator import Validator


class LiveText(tk.Text):
    """Text widget that calls on_modified() when edits are made by the user"""

    def __init__(self):
        super().__init__()

        self._resetting_modified_flag = False
        self.bind('<<Modified>>', self._on_modified)

    def _on_modified(self, event=None):
        if self._resetting_modified_flag:
            self._resetting_modified_flag = False
            return

        self._clear_modified_flag()
        self.on_modified(event)

    def _clear_modified_flag(self):
        self._resetting_modified_flag = True

        # this will trigger the <<Modified>> virtual event
        # as a side effect
        self.edit_modified(False)

    def on_modified(self, event=None):
        raise NotImplementedError


class FxpqText(LiveText):

    def __init__(self):
        super().__init__()

        self.filepath = ""

        self.generator = Generator("./packages", ["fxpq", "fxp2"])
        self.dtd = self.generator.generate()

        self.validator = Validator(self.dtd, "packages/fxpq/fxpq.sch")

        self.bind("<Tab>", self.on_tab)
        self.configure(wrap=tk.NONE)
        self._configure_tags()

    def on_tab(self, event=None):
        self.insert(tk.INSERT, " " * 4)
        return 'break'

    def on_modified(self, event=None):
        text = self.get(1.0, tk.END)
        if not self.validator.validate(text):
            self._highlight_errors(self.validator.errors)

    def _highlight_errors(self, errors):
        print(errors)

class FxpqNotebook(ttk.Notebook):
    """The main document manager of the fxpq editor"""

    def open(self, filepath):
        fxpqtext = FxpqText()
        fxpqtext.filepath = filepath
        with open(filepath) as f:
            text = f.read()
            fxpqtext.insert(tk.END, text)

        scrollbar = ScrollbarHelper(master=self)
        scrollbar.add_child(fxpqtext)

        self.add(scrollbar, text=filepath)
