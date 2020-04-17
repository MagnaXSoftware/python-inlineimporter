import inspect
import os
from collections import namedtuple
from importlib.util import find_spec

from inline_importer import InlinerException

ModuleDefinition = namedtuple("ModuleDefinition", "is_package source")


def get_file_source(filename):
    # type: (str) -> str
    """Read the source of a file.

    This convenience function is present to match the interface of get_module_source.
    """
    with open(filename, "r") as f:
        return f.read()


def get_module_source(fullname_or_module):
    # type: (Union[str, ModuleType]) -> str
    module = fullname_or_module
    if isinstance(fullname_or_module, str):
        spec = find_spec(fullname_or_module)

        # The following behaviour is based on inspect.getsource and linecache behaviour.

        if spec.has_location and getattr(spec, "origin", None) is not None:
            try:
                return get_file_source(spec.origin)
            except OSError:
                pass

        if getattr(spec, "loader", None) is not None:
            loader = spec.loader
            get_source = getattr(loader, "get_source", None)

            if get_source:
                return get_source(spec.name)

        raise InlinerException("Unable to load the source for module {!r}".format(fullname_or_module))

    return inspect.getsource(module)


def extract_module_name(filename):
    """Convenience method to extract a module name from a filename.
    """
    name = os.path.basename(filename).rpartition(".")[0]

    if not name:
        raise InlinerException("Unable to determine module name from file {!r}".format(filename))

    return name


def build_inlined(files):
    # type: (List[str]) -> Dict[str, ModuleDefinition]

    inlined = {}

    for f in files:
        name = extract_module_name(f)

        if name in inlined:
            raise InlinerException("Module {!r} is already present in the inlining dictionary".format(name))

        inlined[name] = ModuleDefinition(False, get_file_source(f))

    return inlined
