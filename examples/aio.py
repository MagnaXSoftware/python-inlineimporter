#!/usr/bin/env python3

import os as _os
import sys as _sys
from functools import lru_cache
from importlib.machinery import ModuleSpec
from importlib.abc import ExecutionLoader, MetaPathFinder


class InlineImporter(ExecutionLoader, MetaPathFinder):

    _inlined_modules = {}

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        """Find a spec for a given module.
        
        Because we only deal with our inlined module, we don't have to care about path or target.
        The import machinery also takes care of fully resolving all names, so we just have to deal with the fullnames.
        """
        if fullname in cls._inlined_modules:
            # We have inlined this module, so return the spec
            ms = ModuleSpec(fullname, cls, origin=cls.get_filename(fullname), is_package=cls.is_package(fullname))
            ms.has_location = True
            if ms.submodule_search_locations is not None:
                for p in _sys.path:
                    ms.submodule_search_locations.append(_os.path.join(p, _os.path.dirname(ms.origin)))

            return ms

        return None

    @staticmethod
    def _call_with_frames_removed(f, *args, **kwds):
        """remove_importlib_frames in import.c will always remove sequences
        of importlib frames that end with a call to this function

        Use it instead of a normal call in places where including the importlib
        frames introduces unwanted noise into the traceback (e.g. when executing
        module code)
        """
        return f(*args, **kwds)

    @classmethod
    def create_module(cls, spec):
        """Create a module using the default machinery."""
        return None

    @classmethod
    def exec_module(cls, module):
        """Execute the module."""
        code = cls.get_code(module.__name__)
        if code is None:
            raise ImportError("cannot load module {!r} when get_code() returns None".format(module.__name__))
        cls._call_with_frames_removed(exec, code, module.__dict__)

    @classmethod
    @lru_cache(maxsize=None)
    def get_filename(cls, fullname):
        """Returns the 

        Raises ImportError if the module cannot be found.
        """
        if fullname not in cls._inlined_modules:
            raise ImportError

        mod = cls._inlined_modules[fullname]
        origin = fullname
        if mod[0]:
            origin = ".".join([origin, "__init__"])
        origin = ".".join([origin.replace(".", "/"), "py"])

        return origin

    @classmethod
    @lru_cache(maxsize=None)
    def is_package(cls, fullname):
        if fullname not in cls._inlined_modules:
            raise ImportError

        return cls._inlined_modules[fullname][0]

    @classmethod
    def get_source(cls, fullname):
        if fullname not in cls._inlined_modules:
            raise ImportError

        return cls._inlined_modules[fullname][1]

    @classmethod
    def get_code(cls, fullname):
        """Method to return the code object for fullname.

        Should return None if not applicable (e.g. built-in module).
        Raise ImportError if the module cannot be found.
        """
        source = cls.get_source(fullname)
        if source is None:
            return None
        try:
            path = cls.get_filename(fullname)
        except ImportError:
            return cls.source_to_code(source)
        else:
            return cls.source_to_code(source, path)


InlineImporter._inlined_modules = {
    "aio_script": (
        False,
        """
import os
import sys
import other.test

def main():
    print(os.path.curdir)
    print("and now on stderr", file=sys.stderr)
    print(other.test.VALUE)
    print(__file__)
""",
    ),
    "other": (True, ""),
    "other.test": (
        False,
        """
from other import me
from . import not_me
VALUE='this was a ' + me.string()

print('Package:', __package__)
""",
    ),
    "other.me": (
        True,
        """
string = lambda: "test"
print('Package:', __package__)
""",
    ),
    "other.me.again": (False, ""),
    "other.not_me": (False, ""),
}
_sys.meta_path.insert(2, InlineImporter)


def run_main():
    import aio_script as script
    import other.them
    import other.me.again

    return script.main()


if __name__ == "__main__":
    run_main()
