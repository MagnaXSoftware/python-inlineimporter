import inspect
import os
from collections import namedtuple
from importlib.util import find_spec

from inline_importer import InlinerException

ModuleDefinition = namedtuple("ModuleDefinition", "name is_package source")
"""A named tuple that represents a module's definition during inlining.
"""


def get_file_source(filename):
    # type: (str) -> str
    """Read the source of a file.

    This convenience function is present to match the interface of get_module_source.

    Args:
        filename (str): the path of the file to read

    Returns:
        str: the contents of the file
    """
    with open(filename, "r") as f:
        return f.read()


def get_module_source(fullname_or_module):
    # type: (Union[str, ModuleType]) -> str
    """Get the source of a module or file.

    This function will invoke python's import machinery to find a module (or package), then read the source.

    Args:
        fullname_or_module (Union[str, `ModuleType`]): Either the fully qualified module name or a module object.

    Returns:
        str: the contents of the module

    Raises:
        `~inline_importer.InlinerException`: If unable to load the source for the given module.
    """
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

    Example:
        >>> extract_module_name('nested/deep/module.py')
        'module'
        >>> extract_module_name('shallow.py')
        'shallow'

    Args:
        path (str): The path of the module file

    Returns:
        str: The name the module

    Raises:
        `~inline_importer.InlinerException`: If unable to determine the name of the module (there is no ``.`` in the
        filename).
    """
    name = os.path.basename(path).rpartition(".")[0]

    if not name:
        raise InlinerException("Unable to determine module name from file {!r}".format(path))

    return name


def extract_package_name(path):
    # type: (str) -> str
    """Convenience method to extract a package name from a path.

    Example:
        >>> extract_package_name('nested/deep/module.py')
        'deep'
        >>> extract_package_name('nested/deep/')
        'deep'
        >>> extract_package_name('nested/deep')
        'deep'

    Args:
        path (str): The path of the package or a module within that package.

    Returns:
        str: The name of the package for the given path.

    Raises:
        `~inline_importer.InlinerException`: If unable to determine the name of the package.
    """

    _o_path = path
    if "." in os.path.basename(path):
        # Because python modules cannot contain dots, if there is a dot in the last component of a path, it's a module,
        # so we get the dirname instead.
        path = os.path.dirname(path)

    if path[-1:] == "/":
        path = path[:-1]

    base = os.path.basename(path)
    if not base:
        raise InlinerException("Unable to determine the name of the package for {}".format(_o_path))

    return base


class Repository(dict):
    """Repository contains the modules being inlined.

    It's a specialized dictionary.

    It is equivalent to a dict(str, `~ModuleDefinition`).
    """

    def insert_module(self, name, source, is_package=False):
        """Convenience method that inserts a module and its source in the repository.

        Args:
            name (str): fully qualified name of the module or package
            source (str): The source code of the module or package
            is_package (bool): is this module is a package

        Raises:
            `~inline_importer.InlinerException`: If the given name is already present in the repository.

        """
        if name in self:
            raise InlinerException("Module {!r} is already present in the repository".format(name))

        self[name] = ModuleDefinition(name, is_package, source)


def build_inlined(modules, packages):
    # type: (List[str], List[str]) -> Repository
    """Builds a `~Repository` of inlined modules and packages.

    Args:
        modules (list(str)): A list of paths to individual modules to inline.
        packages (list(str)): A list of paths to packages to recursively inline.

    Returns:
        `~Repository`: A repository of inlined modules and packages.

    Raises:
        `~inline_importer.InlinerException`: If an entry in `packages` is not a valid python package.
    """

    inlined = Repository()

    for module_file in modules:
        # Technically you can import a module named "__init__", but you probably didn't mean to.
        inlined.insert_module(extract_module_name(module_file), get_file_source(module_file), False)

    for root_package_path in packages:
        _orig_package_path = root_package_path
        if root_package_path.endswith("__init__.py"):
            root_package_path = os.path.dirname(root_package_path)

        dirs = [(extract_package_name(root_package_path), root_package_path)]
        # dirs is a list of tuples, where each tuple contains
        #   (0) the name of the package (unqualified),
        #   (1) the path of the package
        while dirs:
            package_name, package_path = dirs.pop(0)
            if not os.path.exists(os.path.join(package_path, "__init__.py")):
                if package_path == root_package_path:
                    raise InlinerException(
                        "Given package path {!r} does not correspond to a python package".format(_orig_package_path)
                    )
                continue

            for module_file in os.listdir(package_path):
                path = os.path.join(package_path, module_file)
                if os.path.isdir(path):
                    dirs.append((".".join([package_name, module_file]), path))
                    continue

                is_package = module_file == "__init__.py"
                name = package_name
                if not is_package:
                    name = ".".join([name, extract_module_name(module_file)])

                inlined.insert_module(name, get_file_source(path), is_package)

    return inlined
