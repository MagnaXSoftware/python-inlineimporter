import sys
import inspect
from io import StringIO
from inline_importer import __version__ as inline_importer_version, InlinerException
from inline_importer.inliner import ModuleDefinition


def _boolean_repr(val):
    """Returns a python source string representing the given boolean.
    """
    return "True" if val else "False"


def build_file(
    inlined_modules, entrypoint, importer_module="inline_importer.importer", shebang=None, namespace_packages=None
):
    # type: (Dict[str, ModuleDefinition], str, Union[str, module], Optional[str]) -> str
    """Builds an single file script containing the importer module.

    This function returns the inlined script as a string.
    """

    if isinstance(importer_module, str):
        __import__(importer_module)
        importer_module = sys.modules[importer_module]

    if not isinstance(importer_module, type(sys)):
        raise InlinerException(
            "Expected importer_module to be a {}, but got a {} instead".format(type(sys), type(importer_module))
        )

    importer_source = inspect.getsource(importer_module)

    with StringIO() as f:
        if shebang:
            f.write(shebang)
            f.write("\n\n")

        f.write("# InlineImporter\n")
        f.write(importer_source)
        f.write("\n\n")
        f.write("InlineImporter.version = {}\n".format(repr(inline_importer_version)))
        if namespace_packages is not None:
            f.write("InlineImporter.namespace_packages = {}\n".format(_boolean_repr(namespace_packages)))
        f.write("InlineImporter.inlined_modules = {\n")

        for name, module_def in inlined_modules.items():
            f.write("'{}': ({}, {}),\n".format(name, _boolean_repr(module_def.is_package), repr(module_def.source)))

        f.write("}\n")
        f.write("_sys.meta_path.insert(2, InlineImporter)\n\n# Entrypoint\n")
        f.write(entrypoint)

        return f.getvalue()


def write_file(filename, *args, **kwargs):
    """Build a single file script and write it to filename.
    """

    with open(filename, "w") as f:
        return f.write(build_file(*args, **kwargs))
