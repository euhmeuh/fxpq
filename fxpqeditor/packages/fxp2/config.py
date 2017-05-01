"""
Package configuration

Every variable declared here is a configuration entry.
"""

from fxpq.config import DropdownChoice


inputs = {
    'home': {
        'model': DropdownChoice()
    }
}
