"""
Custom text editor with syntax highlighting and live validations
"""

import regex as re

import tkinter as tk
from tkinter import ttk

from pygubu.builder.widgets.scrollbarhelper import ScrollbarHelper

from tools import partition


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
        'error': {'background': '#f92672'},
        'tag_name': {'foreground': '#f92672'},
        'attr_name': {'foreground': '#a6e22a'},
        'attr_value': {'foreground': '#e6db5a'},
        'focused_tag': {'underline': 'true'},
        'comment': {'foreground': '#75715e'},
        'cdata': {'foreground': '#e6db5a'},
        'disabled': {'foreground': 'darkgrey', 'background': 'grey', 'bgstipple': 'gray12'},
    }

    qualified_name = r'(?:[a-zA-Z_][\w_.-]*:)?[a-zA-Z_][\w_.-]*'
    syntax = {
        'disabled': r'(^<\?.*?\?>\s*<!DOCTYPE\s+.*?>\n?)',
        'tag_name': r'</?\s*({{qualified_name}})\s*.*?>',
        'attr_name': r'</?\s*{{qualified_name}}(?:\s*({{qualified_name}})=\".*?\"\s*)+/?>',
        'attr_value': r'</?\s*{{qualified_name}}(?:\s*{{qualified_name}}=(\".*?\")\s*)+/?>',
        'comment': r'(<!--.+?-->)',
        'cdata': r'(<!\[CDATA\[.*?\]\]>)',
    }

    def __init__(self, generator, validator, master=None):
        super().__init__(master)

        self.filepath = ""
        self.generator = generator
        self.validator = validator

        self.bind('<Key>', self.on_key)
        self.bind("<Tab>", self.on_tab)
        self.configure(wrap=tk.NONE,
            foreground='white',
            background='#272822',
            insertbackground='white',
            selectbackground='#49483e')
        self._configure_tags()

    def on_key(self, key):

        # make the ranges easier to compare
        def comparable(range):
            return float(str(range))

        disabled_ranges = list(map(comparable, self.tag_ranges('disabled')))
        if key.keysym in ['Left', 'Right', 'Down', 'Up']:
            return

        for start, end in partition(disabled_ranges, 2):
            if start <= comparable(self.index(tk.INSERT)) <= end:
                return 'break'

            try:
                sel_first = comparable(self.index(tk.SEL_FIRST))
                sel_last = comparable(self.index(tk.SEL_LAST))
            except tk.TclError:
                pass  # no selection
            else:
                if((start <= sel_first <= end)
                or (start <= sel_last <= end)):
                    return 'break'

    def on_tab(self, event=None):
        self.insert(tk.INSERT, " " * 4)
        return 'break'

    def on_modified(self, event=None):
        text = self.get(1.0, tk.END)
        self._remove_tags()
        self._highlight(text)
        if not self.validator.validate(text):
            self._highlight_errors(self.validator.errors)

    def set_text(self, text):
        self.delete(1.0, tk.END)
        self.insert(tk.END, text)

    def open(self, filepath):
        self.filepath = filepath
        with open(filepath) as f:
            text = f.read()
            self.insert(tk.END, text)

    def _configure_tags(self):
        for tag, val in self.tags.items():
            self.tag_config(tag, **val)

    def _remove_tags(self):
        for tag in self.tags.keys():
            self.tag_remove(tag, "1.0", "end")

    def _highlight(self, text):
        for tag, rule in self.syntax.items():
            regex = rule.replace(r'{{qualified_name}}', self.qualified_name)
            for match in re.finditer(regex, text, flags=re.DOTALL):
                for start, end in match.spans(1):
                    self.tag_add(tag,
                        "1.0 + {} chars".format(start),
                        "1.0 + {} chars".format(end))

    def _highlight_errors(self, errors):
        print(errors)
        for error in errors:
            self.tag_add('error',
                "{}.0 linestart".format(error.line),
                "{}.0 lineend + 1 chars".format(error.line))


class FxpqNotebook(ttk.Notebook):
    """The main document manager of the fxpq editor"""

    def __init__(self, generator, validator, master=None):
        super().__init__(master)
        self.generator = generator
        self.validator = validator

    def new(self, title="untitled", text=""):
        fxpqtext = FxpqText(self.generator, self.validator)
        fxpqtext.set_text(text)
        self._new_tab(title, fxpqtext)

    def open(self, filepath):
        fxpqtext = FxpqText(self.generator, self.validator)
        fxpqtext.open(filepath)
        self._new_tab(filepath, fxpqtext)

    def _new_tab(self, name, element):
        scrollbar = ScrollbarHelper(master=self, scrolltype='both')
        scrollbar.add_child(element)
        element.master = scrollbar
        self.add(scrollbar, text=name)
        self.select(scrollbar)
