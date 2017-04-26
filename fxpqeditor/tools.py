"""
Useful miscellaneous tools
"""

def partition(iterable, chunksize):
    return [iterable[i:i+chunksize] for i in range(0, len(iterable), chunksize)]
