"""
Useful miscellaneous tools
"""

import re


def partition(iterable, chunksize):
    """Partition an iterable into chunks of the given size"""
    return [iterable[i:i + chunksize] for i in range(0, len(iterable), chunksize)]


def is_primitive(mytype):
    """Check if a type is primitive"""
    return mytype in [str, int, float, bool]


def remove_encoding_tag(string):
    """Remove the encoding tag from an xml file content"""
    if string.startswith('<?'):
        string = re.sub(r'^<\?.*?\?>', '', string, flags=re.DOTALL)

    return string


def bool_from_string(string):
    false_values = ["false", "0"]
    return False if string.lower() in false_values else bool(string)
