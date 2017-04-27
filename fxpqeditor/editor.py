#/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog
import pygubu

from templator import Templator
from generator import Generator
from validator import Validator
from texteditor import FxpqNotebook


"""
TODO:
- Save and Save as menu
- Custom tabs with a close button
- Solution tree / Untracked tree
- New files saved inside the dimension folder get tracked
- Right click on untracked file -> Include in dimension

Text editor:
- Line numbers
- Right click copy/cut/paste
- Search & replace
- Display validation errors
- Show matching tags
- Autocomplete class and properties
"""


class Application(pygubu.TkApplication):
    def _create_ui(self):
        self.builder = builder = pygubu.Builder()

        builder.add_from_file('editor.ui')

        self.mainwindow = builder.get_object('Frame_Main', self.master)
        self.mainwindow.pack(fill=tk.BOTH, expand=1)
        self.panedwindow = builder.get_object('Panedwindow_Main', self.master)
        self.panedwindow.pack(fill=tk.BOTH, expand=1)

        self.templator = Templator("./templates")
        self.generator = Generator("./packages", ["fxpq", "fxp2"])
        dtd = self.generator.generate()
        self.validator = Validator(dtd, "packages/fxpq/fxpq.sch")
        self.notebook = FxpqNotebook(self.generator, self.validator)

        self.pane_editor = builder.get_object('Pane_Editor', self.master)
        self.pane_editor.add(self.notebook)

        self.mainmenu = menu = builder.get_object('Menu_Main', self.master)
        self.set_menu(menu)

        builder.connect_callbacks(self)
        self._configure_menu()

    def on_new(self, obj_type):
        typename = obj_type.__name__.lower()
        text = self.templator.new(obj_type)
        self.notebook.new(title="untitled {}".format(typename), text=text)

    def on_open(self):
        filepath = filedialog.askopenfilename(
            filetypes = (
                ("FXPQ file", "*.fxpq"),
                ("FXPQ file", "*.dim"),
                ("All files", "*.*")))
        if not filepath:
            return

        self.notebook.open(filepath)

    def on_quit(self):
        self.quit()

    def on_about(self):
        about = self.builder.get_object('Dialog_About', self.master)
        buttonclose = self.builder.get_object('Button_AboutClose', self.master)

        def on_close_about():
            about.close()

        buttonclose.config(command=on_close_about)
        about.run()

    def _configure_menu(self):
        menu = self.builder.get_object('Submenu_New', self.master)

        for root in self.generator.rootobjects():
            # we capture root in the lambda closure by using default parameters
            command = lambda root=root: self.on_new(root)
            menu.add_command(label=root.__name__, command=command)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("FXPQuest Editor")
    app = Application(root)
    app.run()
