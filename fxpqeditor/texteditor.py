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

    def __init__(self, master=None):
        super().__init__(master)

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

    tags = {
        'error': 'orange',
        'focused_tag': 'purple'
    }

    def __init__(self, master=None):
        super().__init__(master)

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
        self.tag_remove('error', "1.0", "end")
        if not self.validator.validate(text):
            self._highlight_errors(self.validator.errors)

    def open(self, filepath):
        self.filepath = filepath
        with open(filepath) as f:
            text = f.read()
            self.insert(tk.END, text)

    def _configure_tags(self):
        for tag, val in self.tags.items():
            self.tag_config(tag, background=val)

    def _highlight_errors(self, errors):
        print(errors)
        for error in errors:
            self.tag_add('error',
                "{0}.0 linestart".format(error.line),
                "{0}.0 lineend".format(error.line))


class FxpqNotebook(ttk.Notebook):
    """The main document manager of the fxpq editor"""

    def open(self, filepath):
        scrollbar = ScrollbarHelper(master=self)
        fxpqtext = FxpqText(master=scrollbar)
        scrollbar.add_child(fxpqtext)

        fxpqtext.open(filepath)

        self.add(scrollbar, text=filepath)
