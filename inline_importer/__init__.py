"""
The inliner package assembles the various components of the InlineImporter library.

The inline_importer.inline_importer module should be kept clean, as it will be inlined with any script produced by this.
"""

from inline_importer._version import __version__

__all__ = ["__version__", "InlinerException"]


class InlinerException(Exception):
    pass
