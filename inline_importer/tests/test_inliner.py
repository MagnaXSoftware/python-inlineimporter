import random
from unittest import TestCase

from inline_importer import inliner, InlinerException


class TestHelpers(TestCase):
    def test_extract_module_name(self):
        self.assertEqual(inliner.extract_module_name("nested/deep/module.py"), "module")
        self.assertEqual(inliner.extract_module_name("shallow.py"), "shallow")

    def test_extract_module_name_invalid(self):
        with self.assertRaises(InlinerException):
            inliner.extract_module_name("nested/deep/module")

        with self.assertRaises(InlinerException):
            inliner.extract_module_name("shallow")

        with self.assertRaises(InlinerException):
            inliner.extract_module_name("")

    def test_extract_package_name(self):
        self.assertEqual(inliner.extract_package_name("nested/deep/module.py"), "deep")
        self.assertEqual(inliner.extract_package_name("nested/deep/"), "deep")
        self.assertEqual(inliner.extract_package_name("nested/deep"), "deep")

    def test_extract_package_name_invalid(self):
        with self.assertRaises(InlinerException):
            inliner.extract_package_name("shallow.py")

        with self.assertRaises(InlinerException):
            inliner.extract_package_name("")


class TestRepository(TestCase):
    def setUp(self) -> None:
        self.repository = inliner.Repository()

    def test_insert_module(self):
        md = inliner.ModuleDefinition("test", False, hex(random.getrandbits(128)))
        try:
            self.repository.insert_module(md.name, md.source, md.is_package)
        except InlinerException:
            self.fail("first insert should succeed")

        self.assertIn(md.name, self.repository)
        self.assertEqual(self.repository[md.name], md)

        with self.assertRaises(InlinerException):
            self.repository.insert_module(md.name, md.source, md.is_package)
