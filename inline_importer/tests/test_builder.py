import os
import random
import tempfile
from unittest import TestCase

from inline_importer import builder
from inline_importer.inliner import ModuleDefinition


class FakeFile:
    def __init__(self):
        self.wrote = False
        self.written = -1

    def write(self, data):
        self.wrote = True
        self.written = len(data)
        return self.written


class TestWriteFile(TestCase):
    def test_write_file_obj(self):
        f = FakeFile()
        written = builder.write_file(f, {}, "")

        self.assertTrue(f.wrote, "write_file should have called the 'write' method")
        self.assertEqual(f.written, written)

    def test_write_file_str(self):
        with tempfile.NamedTemporaryFile(suffix=".py") as f:
            self.assertEqual(os.stat(f.name).st_size, 0, "temporary file should be empty")
            written = builder.write_file(f.name, {}, "")

            f_size = os.stat(f.name).st_size
            self.assertGreater(f_size, 0, "temporary file should have some content")
            self.assertEqual(f_size, written)


# noinspection PyBroadException
class TestBuildFile(TestCase):
    def test_build_file(self):
        s = builder.build_file({}, "")

        try:
            compile(s, "inlined.py", "exec", dont_inherit=True)
        except Exception:
            self.fail("compilation should be valid")

    def test_build_file_shebang(self):
        s = builder.build_file({}, "", shebang="#!/usr/bin/env python3")

        try:
            compile(s, "inlined.py", "exec", dont_inherit=True)
        except Exception:
            self.fail("compilation should be valid")

    def test_build_file_namespace(self):
        s = builder.build_file({}, "", namespace_packages=True)

        try:
            compile(s, "inlined.py", "exec", dont_inherit=True)
        except Exception:
            self.fail("compilation should be valid")

    def test_build_file_modules(self):
        hex_val = hex(random.getrandbits(128))[2:]
        s = builder.build_file(
            {"test": ModuleDefinition("test", False, "IS_TEST=True\nTEST_VALUE={!r}".format(hex_val))}, ""
        )

        self.assertIn(hex_val, s)

        try:
            compile(s, "inlined.py", "exec", dont_inherit=True)
        except Exception:
            self.fail("compilation should be valid")

    def test_build_file_entrypoint(self):
        s = builder.build_file({}, "print('valid!')")

        try:
            compile(s, "inlined.py", "exec", dont_inherit=True)
        except Exception:
            self.fail("compilation should be valid")

    def test_build_file_entrypoint_invalid(self):
        s = builder.build_file({}, "print('invalid!")

        with self.assertRaises(SyntaxError):
            compile(s, "inlined.py", "exec", dont_inherit=True)
