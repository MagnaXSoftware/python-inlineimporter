Usage
#####

inline-importer installs a script, ``inline-python``.
This script is the main interface that you should interact with inline-importer.

.. note:: If you can't run inline-python, the same functionality can be achieved by running ``python -m inline_importer`` instead of ``inline-python``.

A full list of the options, along with small documentation, can be obtained by adding the ``-h`` option to the ``inline-python`` command.

Simple Usage
============

For simple scripts, only a few of ``inline-python``'s options are required.

* If there are packages to inline, add a ``--input-package`` option with the paths to the package folder (containing the ``__init__.py``) or to the ``__init__.py`` itself.
  inline-importer will recursively find all subpackages and submodules and inline them.
* If there are modules to inline, add a ``--input-module`` option with the paths to the modules.
* The entrypoint file should be specified using the ``--entrypoint-file`` option.
* The output file should be specified using the ``--output-file`` option.

.. caution:: inline-importer does not process the inputs (entrypoint, module, package). It will read the source code and inline it as is, without executing it. It also won't try to automatically inline any dependencies that are imported by the inlined code.

.. warning:: inline-importer does not support importing namespace packages (`PEP 420 <https://www.python.org/dev/peps/pep-0420/>`_).

Simple Example
==============

In this simple example, we will use the following project structure. Our goal will be to generate a single file, containing the entire project.

.. code-block::

    project/
    |- src/
    | |- moduleA.py
    | |- pkgB/
    |   |- __init__.py
    |   |- submodC.py
    |- scripts/
      |- entrypoint.py
  

* ``scripts/entrypoint.py`` is the entrypoint of the script, the "``if __name__ == "__main__":``" chunk.
* ``src/`` contains a number of modules and packages that are imported, both directly and indirectly by the entrypoint.

In this case, in order to inline module ``moduleA``, package ``pkgB``, along with ``entrypoint.py``, into ``final-script.py``, one would issue the following command:

.. code-block:: bash

    inline-python -m src/moduleA.py -p src/pkgB -e scripts/entrypoint.py -o final-script.py

The output file, ``final-script.py`` will contain the ``Importer`` component, the inlined modules and packages, and the entrypoint.
This output file is now self-contained, and can be distributed far and wide.

