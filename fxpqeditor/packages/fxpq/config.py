"""
Package configuration

Every dictionary declared here is a configuration entry.
This fxpq module also defines the base classes you can use in your configuration files.
"""

import uuid
from datetime import datetime


class Input:
    def __init__(self):
        self.value = ""

    def update(self, value):
        self.value = value

    def validate(self):
        raise NotImplementedError


class StringEntry(Input):
    def validate(self):
        return self.value


class DropdownChoice(Input):
    def validate(self):
        return self.value


class DropdownCheckboxes(Input):
    def validate(self):
        return self.value


inputs = {
    'dimension': {
        'name': StringEntry(),
        'display_name': StringEntry(),
        'guid': uuid.uuid4(),
        'datetime': datetime.utcnow().replace(microsecond=0).isoformat(),
    },

    'zone': {
        'name': StringEntry(),
        'display_name': StringEntry(),
        'namespaces': DropdownCheckboxes()
    }
}
