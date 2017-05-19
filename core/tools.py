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


def ascii_to_xbm(string, black='#', white=' '):
    """Generate a XBM image from an ascii art string"""

    # purify input by removing all empty lines
    # and all lines that contains illegal characters
    lines = []
    for line in string.split('\n'):
        if not line:
            continue
        if not all([c in (black, white) for c in line]):
            continue
        lines.append(line)

    width = len(max(lines, key=len))
    height = len(lines)

    # fill incomplete lines with spaces
    lines = map(lambda l: l.ljust(width, white), lines)
    lines = "".join(lines)

    databytes = []
    for chunk in partition(lines, 8):
        byte = 0x00
        for i, char in enumerate(chunk, start=0):
            if char == black:
                byte += 2 ** i
        databytes.append(format(byte, '#04x'))

    result = """
    #define im_width {0}
    #define im_height {1}
    static char im_bits[] = {{\n{2}\n}};
    """
    return result.format(width, height, ",".join(databytes))
