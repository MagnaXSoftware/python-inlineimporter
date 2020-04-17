import inspect
import sys
from io import StringIO

from inline_importer import InlinerException
from inline_importer import __version__ as inline_importer_version
from inline_importer.inliner import ModuleDefinition, get_module_source


def build_file(
    inlined_modules, entrypoint, importer_module="inline_importer.importer", shebang=None, namespace_packages=None
):
    # type: (Dict[str, ModuleDefinition], str, Union[str, ModuleType], Optional[str], Optional[bool]) -> str
    """Builds an single file script containing the importer module.

    This function returns the inlined script as a string.
    """

    importer_source = get_module_source(importer_module)

    with StringIO() as f:
        if shebang:
            f.write(shebang)
            f.write("\n\n")

        f.write("# InlineImporter\n")
        f.write(importer_source)
        f.write("\n\n")
        f.write("InlineImporter.version = {!r}\n".format(inline_importer_version))
        if namespace_packages is not None:
            f.write("InlineImporter.namespace_packages = {!r}\n".format(bool(namespace_packages)))
        f.write("InlineImporter.inlined_modules = {\n")

        for name, module_def in inlined_modules.items():
            # We loop over each entry in the inlined_modules dictionary because we don't want to use the ModuleDefinition
            # namedtuple in the inlined script.
            f.write("    {!r}: ({!r}, {!r}),\n".format(name, bool(module_def.is_package), module_def.source))

        f.write("}\n")
        f.write("_sys.meta_path.insert(2, InlineImporter)\n\n# Entrypoint\n")
        f.write(entrypoint)

        return f.getvalue()


def write_file(filename, *args, **kwargs):
    """Build a single file script and write it to filename.

    Other than a filename, the rest of the arguments are passed verbatim to build_file.
    """

    with open(filename, "w") as f:
        return f.write(build_file(*args, **kwargs))
