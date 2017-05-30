"""
Document models
"""

from pathlib import Path

from core.serializer import Serializer

from editor.events import EventEmitter


class FxpqDocument(EventEmitter):
    """Holds unique document informations"""

    def __init__(self, filepath=None, title=None, text=None):
        super().__init__()

        self._filepath = filepath
        self._title = title
        self._dirty = (filepath is None)

        self.text = text
        self.obj = None  # everytime the serialization works, obj is populated

        self.opened = False

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, value):
        self._filepath = value
        self.emit('title-changed')

    @property
    def title(self):
        title = "untitled" if self._title is None else self._title

        if self.filepath:
            title = self.filepath.split('/')[-1]

        if self.dirty:
            title += "*"

        return title

    @title.setter
    def title(self, value):
        self._title = value
        self.emit('title-changed')

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value
        self.emit('title-changed')

    @property
    def reference_paths(self):
        if not self.obj:
            return []

        return [self.full_path(r.path) for r in self.obj.references]

    def full_path(self, relative_path):
        return str(Path(self.filepath).parent / relative_path)

    def open(self):
        """Open the document in a new tab of the notebook"""
        if not self.opened:
            self.opened = True

            if self.filepath:
                with open(self.filepath) as f:
                    self.text = f.read()

            self.emit('document-opened')

    def try_serialize(self, text):
        self.text = text
        try:
            self.obj = Serializer.instance().deserialize(self.text)
        except ValueError:
            self.obj = None

        errors = Serializer.instance().errors

        if errors:
            self.emit("validation-failed", errors)
        else:
            self.emit('validation-passed')

        return errors
