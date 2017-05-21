"""
Custom text editor with syntax highlighting and live validations
"""

import regex as re

import tkinter as tk
from tkinter import ttk

from pygubu.builder.widgets.scrollbarhelper import ScrollbarHelper

from core.serializer import Serializer
from core.tools import partition


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

    def __init__(self, master=None):
        super().__init__(master)

        self.serializer = Serializer.instance()
        self.obj = None

        self._filepath = ""
        self._dirty = False
        self._ignore_next_dirty = False

        self.title = ""
        self.temptitle = "untitled"

        self.error_list = FxpqErrorList()

        self.bind('<Key>', self.on_key)
        self.bind("<Tab>", self.on_tab)
        self.configure(wrap=tk.NONE,
            foreground='white',
            background='#272822',
            insertbackground='white',
            selectbackground='#49483e')
        self._configure_tags()
        self._configure_line_numbers()

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, value):
        self._filepath = value
        self.update_title()

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value
        self.update_title()

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
            self.dirty = True

        self._remove_tags()

        try:
            self.obj = self.serializer.deserialize(self.text, reference_path=self.filepath)
        except ValueError:
            self.obj = None
            self.event_generate("<<ValidationError>>")
            self._highlight_errors(self.serializer.errors)

        self.error_list.update(self.serializer.errors)

        self._highlight()

    def update_title(self):
        title = self.temptitle

        if self.filepath:
            title = self.filepath.split('/')[-1]

        if self.dirty:
            title += "*"

        self.title = title
        self.master.master.tab(self.master, text=self.title)

    @property
    def text(self):
        return self.get(1.0, tk.END)

    @text.setter
    def text(self, text):
        self.ignore_next_dirty()
        self.delete(1.0, tk.END)
        self.insert(tk.END, text)
        self.dirty = False

    def ignore_next_dirty(self):
        self._ignore_next_dirty = True

    def open(self, filepath):
        self.filepath = filepath
        with open(filepath) as f:
            text = f.read()
            self.text = text

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

    def _highlight_errors(self, errors):
        for error in errors:
            self.tag_add('error',
                "{}.0 linestart".format(error.line),
                "{}.0 lineend + 1 chars".format(error.line))

    def _configure_line_numbers(self):
        pass  # TODO


class FxpqNotebook(ttk.Notebook):
    """Custom notebook"""

    def current(self):
        """Get the currently focused tab"""

        if not self.index("end"):
            return None
        # tab content is in a scrollbarhelper, so we get its child
        return self.winfo_children()[self.index("current")].cwidget

    def new(self, filepath=None, title=None, text=""):
        """Create a new tab"""

        fxpqtext = FxpqText()
        if filepath:
            self._new_tab(filepath, fxpqtext)
            fxpqtext.open(filepath)
        else:
            title = "untitled" if title is None else title
            self._new_tab(title, fxpqtext)
            fxpqtext.temptitle = title
            fxpqtext.text = text
            fxpqtext.dirty = True

        return fxpqtext

    def _new_tab(self, name, element):
        scrollbar = ScrollbarHelper(master=self, scrolltype='both')
        scrollbar.add_child(element)
        element.master = scrollbar
        self.add(scrollbar, text=name)
        self.select(scrollbar)


class FxpqDocumentManager(tk.Frame):
    """The main document manager of the fxpq editor"""

    def __init__(self, master=None):
        super().__init__(master)

        self.documents = []

        self.current_error_list = None

        self.bind_all("<<ValidationError>>", self._on_validation_error)
        self._create_ui()

    def get_objects(self):
        return [doc.obj for doc in self.documents if doc.obj]

    def current(self):
        return self.notebook.current()

    def new(self, title=None, text=""):
        doc = self.notebook.new(title=title, text=text)
        self.documents.append(doc)

    def open(self, filepath):
        doc = self.notebook.new(filepath=filepath)
        self.documents.append(doc)

    def _create_ui(self):
        self.panedwindow = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=1)
        self.notebook = FxpqNotebook(self.panedwindow)
        self.panedwindow.add(self.notebook, height=1000, minsize=300)

    def _on_validation_error(self, event=None):
        sender = event.widget
        error_list = sender.error_list

        if self.current_error_list:
            self.panedwindow.remove(self.current_error_list)

        error_list.master = self.panedwindow
        self.panedwindow.add(error_list, minsize=50, sticky=tk.W + tk.S + tk.E)

        if not self.current_error_list:
            # this is the first time we display the error list
            # so we need to set up a default height
            self.panedwindow.paneconfig(error_list, height=200)

        self.current_error_list = error_list
