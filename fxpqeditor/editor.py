#/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog
import pygubu

from packagemanager import PackageManager
from generator import Generator
from templator import Templator
from validator import Validator
from texteditor import FxpqNotebook
from explorer import FxpqExplorer


"""
TODO:
- Custom tabs with a close button
- Solution tree / Untracked tree
- Right click on untracked file -> Include in dimension
- Disable the create button in the "new file" dialog until validations are satisfied
- Move the templates folder so that there is one in each package
- Move the icons folder so that there is one in each package
- New files saved inside the dimension folder get tracked

Text editor:
- Line numbers
- Display validation errors
- Show matching tags
- Autocomplete class and properties
- Right click copy/cut/paste
- Search & replace
"""


class Form:
    """Generates a user form from an input configuration"""

    def __init__(self, master, button, inputs, base_input_type):
        """
        master: the tk.Frame in which the form should generate inputs
        button: the tk.Button that sends the form (will be disabled by validations)
        inputs: the dictionary of inputs
        base_input_type: the base class to look for in the inputs dictionary

        The keys in the inputs dictionary will be used as the input's labels.
        The values can be either a simple string, in which case they will be considered as hidden fields,
        or any subclass of the given base_input_type, in which case the corresponding input widget will be created.
        """
        self.inputs = inputs
        self.base = base_input_type

        for widget in master.winfo_children():
            widget.destroy()

        for index, kv in enumerate(inputs.items()):
            name, value = kv
            if isinstance(value, base_input_type):
                label = tk.Label(master, text=name).grid(row=index, column=0)

                stringvar = tk.StringVar()
                on_modified = lambda name,index,mode,widget=stringvar,value=value: value.update(widget.get())
                stringvar.trace('w', on_modified)

                widget = tk.Entry(master, textvariable=stringvar)
                widget.grid(row=index, column=1)

    def get_values(self):
        try:
            values = {}
            for name, value in self.inputs.items():
                if isinstance(value, self.base):
                    values[name] = value.validate()
                else:
                    values[name] = str(value)
        except ValueError:
            return {}

        return values


class Application(pygubu.TkApplication):
    filetypes = (
        ("FXPQ file", "*.fxpq"),
        ("FXPQ file", "*.dim"),
        ("All files", "*.*"))

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

        self.explorer = FxpqExplorer(base_type, self.master)
        self.pane_explorer = builder.get_object('Pane_Explorer', self.master)
        self.pane_explorer.add(self.explorer)

        dtd = self.generator.generate()
        self.validator = Validator(dtd, "packages/fxpq/fxpq.sch")
        self.notebook = FxpqNotebook(self.generator, self.validator)

        self.pane_editor = builder.get_object('Pane_Editor', self.master)
        self.pane_editor.add(self.notebook)

        self.mainmenu = menu = builder.get_object('Menu_Main', self.master)
        self.set_menu(menu)

        builder.connect_callbacks(self)
        self.mainwindow.bind_all("<Control-o>", self.on_open)
        self.mainwindow.bind_all("<Control-s>", self.on_save)

        self._configure_menu()
        self._update_menu()

    def on_new(self, obj_type):
        dialog = self.builder.get_object('Dialog_NewFile', self.master)
        frame_newfile = self.builder.get_object('Frame_NewFile', self.master)
        button_cancel = self.builder.get_object('Button_NewFile_Cancel', self.master)
        button_create = self.builder.get_object('Button_NewFile_Create', self.master)

        def on_cancel():
            dialog.close()

        def on_create(obj_type, input_values):
            typename = obj_type.__name__.lower()
            title, text = self.templator.new(obj_type, input_values)
            self.notebook.new(title=title, text=text)
            self._update_menu()
            dialog.close()

        inputs = self.packagemanager.get_config("inputs")
        inputs = inputs.get(obj_type.__name__.lower(), None)
        if not inputs:
            on_create(obj_type, {})
            return

        base_input_type = self.packagemanager.get_class("fxpq.config", "Input")
        dialog.form = Form(frame_newfile, button_create, inputs, base_input_type)

        button_cancel.config(command=on_cancel)
        button_create.config(command=lambda: on_create(obj_type, dialog.form.get_values()))

        dialog.set_title("New {}".format(obj_type.__name__))
        dialog.run()

    def on_open(self, event=None):
        filepath = filedialog.askopenfilename(filetypes=self.filetypes)
        if not filepath:
            return

        self.notebook.open(filepath)
        self._update_menu()

    def on_save(self, event=None):
        fxpqtext = self.notebook.current()
        if fxpqtext.filepath:
            with open(fxpqtext.filepath, 'w') as f:
                f.write(fxpqtext.get_text())
                fxpqtext.dirty = False
        else:
            self.on_save_as()

    def on_save_as(self):
        fxpqtext = self.notebook.current()

        initialfile = fxpqtext.title.replace("*", "").replace(" ", "")

        filepath = filedialog.asksaveasfilename(filetypes=self.filetypes,
            initialfile=initialfile, defaultextension=".fxpq")
        if not filepath:
            return

        with open(filepath, 'w') as f:
            f.write(fxpqtext.get_text())
            fxpqtext.filepath = filepath
            fxpqtext.dirty = False

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

    def _update_menu(self):
        filemenu = self.builder.get_object('Submenu_File', self.master)
        state = tk.NORMAL if self.notebook.current() else tk.DISABLED
        filemenu.entryconfig("Save", state=state)
        filemenu.entryconfig("Save as...", state=state)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("FXPQuest Editor")
    app = Application(root)
    app.run()
