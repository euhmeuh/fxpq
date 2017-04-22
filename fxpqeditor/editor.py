#/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog
import pygubu

from texteditor import FxpqNotebook


"""
TODO:
- New menu is populated with standard types (zon, npc, item, enemy...)
- Save and Save as menu
- Opening files creates tabs
- Custom tabs with a close button
- Solution tree / Untracked tree
- New files saved inside the dimension folder get tracked
- Right click on untracked file -> Include in dimension

Text editor:
- Line numbers
- Text highlighting
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

        self.notebook = FxpqNotebook()

        self.pane_editor = builder.get_object('Pane_Editor', self.master)
        self.pane_editor.add(self.notebook)

        self.mainmenu = menu = builder.get_object('Menu_Main', self.master)
        self.set_menu(menu)

        builder.connect_callbacks(self)

    def on_open(self):
        filepath = filedialog.askopenfilename(
            filetypes = (
                ("FXPQ file", "*.fxpq"),
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


if __name__ == '__main__':
    root = tk.Tk()
    root.title("FXPQuest Editor")
    app = Application(root)
    app.run()
