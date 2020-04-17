import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, ArgumentTypeError, SUPPRESS

from inline_importer import __version__, builder, inliner


def _ternary_type(value):
    """Convert a string to a ternary value (None, True, False).
    """
    val = value.lower()

    if val in ("true", "yes", "on", "1"):
        return True

    if val in ("false", "no", "off", 0):
        return False

    if val in ("none"):
        return None

    raise ArgumentTypeError("{!r} is not a valid ternary value (None, True, False)".format(value))


def parse_args(name):
    parser = ArgumentParser(name, description="", add_help=True, allow_abbrev=True)

    parser.add_argument(
        "-V", "--version", action="version", version="InlineImporter version {}".format(__version__),
    )

    entrypoints = parser.add_mutually_exclusive_group(required=True)
    entrypoints.add_argument("-e", "--entrypoint-file", help="Path to the entrypoint file")
    entrypoints.add_argument("--entrypoint-module", help="Fully qualified name of the entrypoint module")
    entrypoints.add_argument("--entrypoint-script", help="Inline entrypoint script (e.g.: 'print(\"The entrypoint\")')")

    shebangs = parser.add_mutually_exclusive_group()
    shebangs.add_argument(
        "--shebang", help="Specify the shebang line to use in the script", default="#!/usr/bin/env python3"
    )
    shebangs.add_argument("--no-shebang", help="Disable the generation of a shebang line", action="store_true")

    parser.add_argument(
        "-n",
        "--namespace-inlined-packages",
        help="Whether inlined packages be marked as PEP 420 namespace packages. None uses the libary default, currently False.",
        default=None,
        choices=(None, True, False),
        type=_ternary_type,
    )

    parser.add_argument(
        "-i",
        "--importer-module",
        help="Fully qualified name of the importer module. Must contain a class named InlineImporter, matching the interface of inline_importer.importer:InlineImporter",
        default="inline_importer.importer",
    )

    inputs = parser.add_argument_group()
    inputs.add_argument(
        "-f",
        "--input-file",
        help="Path to a file to inline. This file will not be placed in a package.",
        dest="input_files",
        default=[],
        nargs="*",
    )

    parser.add_argument(
        "-o", "--output-file", help="Name of the output file. Use - to output to stdout instead.", required=True
    )

    args = parser.parse_args()

    if args.no_shebang:
        args.shebang = None

    if not args.entrypoint_script:
        args.entrypoint_script = ""

    return args


def main():
    name = os.path.basename(sys.argv[0])
    if name == "__main__.py":
        name = "{} -m {}".format(os.path.basename(sys.executable), __package__)
    args = parse_args(name)

    # Collect and inline the modules
    # Because of the mutually exclusive group, we only have one type of
    entrypoint = args.entrypoint_script
    if args.entrypoint_file:
        entrypoint = inliner.get_file_source(args.entrypoint_file)
    if args.entrypoint_module:
        entrypoint = inliner.get_module_source(args.entrypoint_module)

    inlined = inliner.build_inlined(files=args.input_files)

    # Build the inlined script
    builder_args = dict(
        inlined_modules=inlined, entrypoint=entrypoint, importer_module=args.importer_module, shebang=args.shebang
    )

    if args.output_file == "-":
        print(builder.build_file(**builder_args), file=sys.stdout)
    else:
        builder.write_file(args.output_file, **builder_args)


if __name__ == "__main__":
    main()
