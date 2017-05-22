"""
Custom text editor with syntax highlighting and live validations
"""

import regex as re

import tkinter as tk
from tkinter import ttk

from pygubu.builder.widgets.scrollbarhelper import ScrollbarHelper

from core.tools import partition

from editor.document import FxpqDocument


class FxpqErrorList(tk.Listbox):

    def update(self, errors):
        self.delete(0, tk.END)
        for error in errors:
            self.insert(tk.END, str(error))


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

    # we use a list of tuple to keep the priority order
    tags = [
        ('attr_value', {'foreground': '#e6db5a'}),
        ('attr_name', {'foreground': '#a6e22a'}),
        ('tag_name', {'foreground': '#f92672'}),
        ('focused_tag', {'underline': 'true'}),
        ('comment', {'foreground': '#75715e'}),
        ('cdata', {'foreground': '#e6db5a'}),
        ('error', {'background': '#f92672', 'foreground': 'black'}),
        ('disabled', {'foreground': 'darkgrey', 'background': 'grey', 'bgstipple': 'gray12'}),
    ]

    qualified_name = r'(?:[a-zA-Z_][\w_.-]*:)?[a-zA-Z_][\w_.-]*'
    syntax = {
        'disabled': r'(^<\?.*?\?>\s*<!DOCTYPE\s+.*?>\n?)',
        'tag_name': r'</?\s*({{qualified_name}})\s*.*?>',
        'attr_name': r'</?\s*{{qualified_name}}(?:\s*({{qualified_name}})=\".*?\"\s*)+/?>',
        'attr_value': r'</?\s*{{qualified_name}}(?:\s*{{qualified_name}}=(\".*?\")\s*)+/?>',
        'comment': r'(<!--.+?-->)',
        'cdata': r'(<!\[CDATA\[.*?\]\]>)',
    }

    def __init__(self, doc, master=None):
        super().__init__(master)

        self.doc = doc
        self.text = doc.text
        self._ignore_next_dirty = False

        self.errors = []

        self.bind('<Key>', self.on_key)
        self.bind("<Tab>", self.on_tab)
        self.configure(wrap=tk.NONE,
            foreground='white',
            background='#272822',
            insertbackground='white',
            selectbackground='#49483e')
        self._configure_tags()
        self._configure_line_numbers()

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
        if self._ignore_next_dirty:
            self._ignore_next_dirty = False
        else:
            self.doc.dirty = True

        self._remove_tags()

        self.errors = self.doc.try_serialize(self.text)
        if self.errors:
            self._highlight_errors()

        self._highlight()

        self.event_generate('<<DocumentsChanged>>')

    @property
    def text(self):
        return self.get(1.0, tk.END)

    @text.setter
    def text(self, text):
        # we don't want to trigger on_modified
        self._ignore_next_dirty = True

        self.delete(1.0, tk.END)
        self.insert(tk.END, text)
        self.dirty = False

    def _configure_tags(self):
        for tag, val in self.tags:
            self.tag_config(tag, **val)

    def _remove_tags(self):
        for tag, val in self.tags:
            self.tag_remove(tag, "1.0", "end")

    def _highlight(self):
        for tag, rule in self.syntax.items():
            regex = rule.replace(r'{{qualified_name}}', self.qualified_name)
            for match in re.finditer(regex, self.text, flags=re.DOTALL):
                for start, end in match.spans(1):
                    self.tag_add(tag,
                        "1.0 + {} chars".format(start),
                        "1.0 + {} chars".format(end))

    def _highlight_errors(self):
        for error in self.errors:
            self.tag_add('error',
                "{}.0 linestart".format(error.line),
                "{}.0 lineend + 1 chars".format(error.line))

    def _configure_line_numbers(self):
        pass  # TODO


class FxpqEditor(tk.PanedWindow):

    def __init__(self, doc, master=None):
        super().__init__(master)

        self.doc = doc

        self.fxpqtext = FxpqText(doc)
        self.error_list = None
        self._create_ui()

        self.doc.on('validation-passed', self.on_validation_passed)
        self.doc.on('validation-failed', self.on_validation_failed)

    def on_validation_passed(self, doc):
        if self.error_list:
            self.remove(self.error_list)
            self.error_list = None

    def on_validation_failed(self, doc, errors):
        if not self.error_list:
            self.error_list = FxpqErrorList(self)
            self.add(self.error_list, minsize=50, height=200, sticky=tk.W + tk.S + tk.E)

        self.error_list.update(errors)

    def _create_ui(self):
        self.config(orient=tk.VERTICAL)
        self.pack(fill=tk.BOTH, expand=1)

        scrollbar = ScrollbarHelper(master=self, scrolltype='both')
        scrollbar.add_child(self.fxpqtext)
        self.fxpqtext.master = scrollbar
        self.add(scrollbar, height=1000, minsize=300)


class FxpqNotebook(ttk.Notebook):
    """Custom notebook"""

    def __init__(self, master=None):
        super().__init__(master)

        self.fxpqeditors = []

    def current(self):
        """Get the currently focused tab"""

        if not self.index("end"):
            return None
        return self.winfo_children()[self.index("current")].doc

    def on_document_opened(self, doc):
        fxpqeditor = FxpqEditor(doc, self)
        self._new_tab(doc.title, fxpqeditor)

    def on_title_changed(self, doc):
        fxpqeditor = next((ed for ed in self.fxpqeditors if ed.doc == doc), None)
        if fxpqeditor:
            self.tab(fxpqeditor, text=doc.title)

    def _new_tab(self, name, fxpqeditor):
        self.add(fxpqeditor, text=name)
        self.select(fxpqeditor)
        self.fxpqeditors.append(fxpqeditor)


class FxpqDocumentManager(tk.Frame):
    """The main document manager of the fxpq editor"""

    def __init__(self, master=None):
        super().__init__(master)

        self.documents = []

        self.notebook = FxpqNotebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=1)

    def current(self):
        return self.notebook.current()

    def new(self, title=None, text=""):
        doc = FxpqDocument(title=title, text=text)
        self._register_doc(doc)

    def open(self, filepath):
        doc = FxpqDocument(filepath=filepath)
        self._register_doc(doc)

    def _register_doc(self, doc):
        self.documents.append(doc)
        doc.on('document-opened', self.notebook.on_document_opened)
        doc.on('title-changed', self.notebook.on_title_changed)
        doc.open()
