"""
Useful miscellaneous tools
"""

def partition(iterable, chunksize):
    """Partition an iterable into chunks of the given size"""
    return [iterable[i:i+chunksize] for i in range(0, len(iterable), chunksize)]

def isprimitive(mytype):
    """Check if a type is primitive"""
    return mytype in [str, int, float, bool]
