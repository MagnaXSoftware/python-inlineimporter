#!/usr/bin/env python3

from setuptools import setup, find_packages


def readme():
    """Read in and return the contents of the project's README.md file."""
    with open("README.md", encoding="utf-8") as f:
        return f.read()


def package_vars(version_file):
    """Read in and return the variables defined by the version_file."""
    pkg_vars = {}
    with open(version_file) as f:
        exec(f.read(), pkg_vars)  # nosec
    return pkg_vars


setup(
    name="inline-importer",
    # Versions should comply with PEP440
    version=package_vars("inline_importer/_version.py")["__version__"],
    description="Python module inlining library",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MagnaXSoftware/python-inlineimporter",
    # Author details
    author="MagnaX Software",
    author_email="info@magnax.ca",
    license="License :: OSI Approved :: MIT License",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires="~=3.4",
    packages=find_packages(exclude=()),
    # py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    entry_points={"console_scripts": ["inline-python = inline_importer.__main__:main"]},
)
