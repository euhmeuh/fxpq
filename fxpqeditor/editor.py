#/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog
import pygubu

from packagemanager import PackageManager
from generator import Generator
from templator import Templator, Form
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

        self.packagemanager = PackageManager("./packages")

        # define Object as the base class for all elements
        base_type = self.packagemanager.get_class("fxpq.core", "Object")
        self.generator = Generator(base_type)
        self.templator = Templator("./templates")

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
        dialog = self.builder.get_object('Dialog_NewFile', self.master)
        frame_newfile = self.builder.get_object('Frame_NewFile', self.master)
        button_cancel = self.builder.get_object('Button_NewFile_Cancel', self.master)
        button_create = self.builder.get_object('Button_NewFile_Create', self.master)

        def on_cancel():
            dialog.close()

        def on_create(obj_type, input_values):
            typename = obj_type.__name__.lower()
            text = self.templator.new(obj_type, input_values)
            self.notebook.new(title="untitled {}".format(typename), text=text)
            dialog.close()

        inputs = self.packagemanager.get_config("inputs")
        inputs = inputs.get(obj_type.__name__.lower(), None)
        if not inputs:
            on_create(obj_type, {})
            return

        dialog.form = Form(frame_newfile, button_create, inputs)

        button_cancel.config(command=on_cancel)
        button_create.config(command=lambda: on_create(obj_type, dialog.form.get_values()))

        dialog.run()

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
        button_close = self.builder.get_object('Button_AboutClose', self.master)

        def on_close_about():
            about.close()

        button_close.config(command=on_close_about)
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
