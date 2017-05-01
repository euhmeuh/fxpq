"""
Package configuration

Every variable declared here is a configuration entry.
This fxpq module also defines the base classes you can use in your configuration files.
"""

import uuid
from datetime import datetime


class Input:
    def __init__(self):
        self.value = ""

    def validate(self):
        raise NotImplementedError

    def __unicode__(self):
        return self.value


class StringEntry(Input):
    pass


class DropdownChoice(Input):
    pass


class DropdownCheckboxes(Input):
    pass


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
