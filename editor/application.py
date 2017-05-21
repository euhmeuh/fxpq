import tkinter as tk
from tkinter import filedialog
import pygubu

from core.package_manager import PackageManager
from core.templator import Templator
from core.serializer import Serializer

from editor.texteditor import FxpqDocumentManager
from editor.explorer import FxpqExplorer


"""
TODO:
- Custom tabs with a close button
- Solution tree / Untracked tree
- Right click on untracked file -> Include in dimension
- Disable the create button in the "new file" dialog until validations are satisfied
- New files saved inside the dimension folder get tracked
- Better test coverage
- Remove some exceptions from the serializer that might never raise
- Replace on_key binding in the texteditor with on_insert and on_delete to better handle disabled areas

Text editor:
- Line numbers
- Show matching tags
- Autocomplete class and properties
- Right click copy/cut/paste
- Search & replace
- Smart tabs

Bugs:
- Form values are kept when creating from template
- Saving adds an extra linefeed
"""


class Form:
    """Generates a user form from an input configuration"""

    def __init__(self, package_manager, master, button, inputs):
        """
        master: the tk.Frame in which the form should generate inputs
        button: the tk.Button that sends the form (will be disabled by validations)
        inputs: the dictionary of inputs

        The keys in the inputs dictionary will be used as the input's labels.
        The values can be either a simple string, in which case they will be considered as hidden fields,
        or any subclass of Input, in which case the corresponding input widget will be created.
        """
        self.Input = package_manager.get_class("fxpq.config", "Input")
        self.inputs = inputs

        for widget in master.winfo_children():
            widget.destroy()

        for index, kv in enumerate(inputs.items()):
            name, value = kv
            if isinstance(value, self.Input):
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
                if isinstance(value, self.Input):
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

    ui_file = "./editor/editor.ui"
    packages_dir = "./packages"

    def _create_ui(self):
        self.builder = builder = pygubu.Builder()

        builder.add_from_file(self.ui_file)

        self.mainwindow = builder.get_object('Frame_Main', self.master)
        self.mainwindow.pack(fill=tk.BOTH, expand=1)
        self.panedwindow = builder.get_object('Panedwindow_Main', self.master)
        self.panedwindow.pack(fill=tk.BOTH, expand=1)

        self.package_manager = PackageManager(self.packages_dir)
        self.templator = Templator(self.package_manager)

        self.explorer = FxpqExplorer(self.package_manager, self.master)
        self.pane_explorer = builder.get_object('Pane_Explorer', self.master)
        self.pane_explorer.add(self.explorer)

        self.doc_manager = FxpqDocumentManager(self.master)

        self.pane_editor = builder.get_object('Pane_Editor', self.master)
        self.pane_editor.add(self.doc_manager)

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
            title, text = self.templator.new(obj_type, input_values)
            self.doc_manager.new(title=title, text=text)
            self._update_menu()
            dialog.close()

        inputs = self.package_manager.get_config("inputs")
        inputs = inputs.get(obj_type.__name__.lower(), None)
        if not inputs:
            on_create(obj_type, {})
            return

        dialog.form = Form(self.package_manager, frame_newfile, button_create, inputs)

        button_cancel.config(command=on_cancel)
        button_create.config(command=lambda: on_create(obj_type, dialog.form.get_values()))

        dialog.set_title("New {}".format(obj_type.__name__))
        dialog.run()

    def on_open(self, event=None):
        filepath = filedialog.askopenfilename(filetypes=self.filetypes)
        if not filepath:
            return

        self.doc_manager.open(filepath)
        self._update_menu()
        self._update_explorer()

    def on_save(self, event=None):
        fxpqtext = self.doc_manager.current()
        if fxpqtext.filepath:
            with open(fxpqtext.filepath, 'w') as f:
                f.write(fxpqtext.text)
                fxpqtext.dirty = False
        else:
            self.on_save_as()

        self._update_explorer()

    def on_save_as(self):
        fxpqtext = self.doc_manager.current()

        initialfile = fxpqtext.title.replace("*", "").replace(" ", "")

        filepath = filedialog.asksaveasfilename(filetypes=self.filetypes,
            initialfile=initialfile, defaultextension=".fxpq")
        if not filepath:
            return

        with open(filepath, 'w') as f:
            f.write(fxpqtext.text)
            fxpqtext.filepath = filepath
            fxpqtext.dirty = False

        self._update_explorer()

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

        for root in Serializer.instance().generator.root_objects():
            # we capture root in the lambda closure by using default parameters
            command = lambda root=root: self.on_new(root)
            menu.add_command(label=root.__name__, command=command)

    def _update_menu(self):
        filemenu = self.builder.get_object('Submenu_File', self.master)
        state = tk.NORMAL if self.doc_manager.current() else tk.DISABLED
        filemenu.entryconfig("Save", state=state)
        filemenu.entryconfig("Save as...", state=state)

    def _update_explorer(self):
        self.explorer.refresh(self.doc_manager.get_objects())


class Editor:
    def run(self):
        root = tk.Tk()
        root.title("FXPQuest Editor")
        app = Application(root)
        app.run()
