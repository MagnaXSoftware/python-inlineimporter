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


def extract_module_name(path):
    # type: (str) -> str
    """Convenience method to extract a module name from a path.
    """
    name = os.path.basename(path).rpartition(".")[0]

    if not name:
        raise InlinerException("Unable to determine module name from file {!r}".format(path))

    return name


def extract_package_name(path):
    # type: (str) -> str
    """Convenience method to extract a package name from a path.
    """

    if "." in os.path.basename(path):
        # Because python modules cannot contain dots, if there is a dot in the last component of a path, it's a module,
        # so we get the dirname instead.
        path = os.path.dirname(path)

    if path[-1:] == "/":
        path = path[:-1]

    return os.path.basename(path)


class Repository(dict):
    def insert_module(self, name, source, is_package=False):
        if name in self:
            raise InlinerException("Module {!r} is already present in the repository".format(name))

        self[name] = ModuleDefinition(is_package, source)


def build_inlined(files, packages):
    # type: (List[str], List[str]) -> Dict[str, ModuleDefinition]

    inlined = Repository()

    for f in files:
        # Technically you can import a module named "__init__", but you probably didn't mean to.
        inlined.insert_module(extract_module_name(f), get_file_source(f), False)

    for p in packages:
        _orig_p = p
        if p.endswith("__init__.py"):
            p = os.path.dirname(p)

        dirs = [(extract_package_name(p), p)]
        while dirs:
            pkg, d = dirs.pop(0)
            if not os.path.exists(os.path.join(d, "__init__.py")):
                if d == p:
                    raise InlinerException(
                        "Given package path {!r} does not correspond to a python package".format(_orig_p)
                    )
                continue

            for f in os.listdir(d):
                path = os.path.join(d, f)
                if os.path.isdir(path):
                    dirs.append((".".join([pkg, f]), path))
                    continue

                is_package = f == "__init__.py"
                name = pkg
                if not is_package:
                    name = ".".join([name, extract_module_name(f)])

                inlined.insert_module(name, get_file_source(path), is_package)

    return inlined
