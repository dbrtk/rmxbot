""" Making a class that behaves like a dict (dictionary). As a matter of fact, 
it is a wrapper around a dict object that is extended with methods provided by 
collections MutableMapping.

https://hg.python.org/cpython/file/3.4/Lib/collections/appconf.py
"""

import collections


class RmxDict(collections.UserDict):
    """
    """

    def __init__(self, _dict=None, *args, **kwds):
        """
        """
        self.dict = {}
        if _dict is not None:
            self.update(_dict)
        if len(kwds):
            self.update(kwds)

    def __repr__(self): return repr(self.dict)

    def __setitem__(self, key, value): self.dict[key] = value

    def __getitem__(self, key):
        """
        """
        if key in self.dict:
            return self.dict[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __delitem__(self, key): del self.dict[key]

    def __iter__(self): return iter(self.dict)

    def __len__(self): return len(self.dict)

    def __contains__(self, key): return key in self.dict


if __name__ == '__main__':
    _d = RmxDict(a=1, b=2, c=3, d=4)
    import pdb
    pdb.set_trace()
