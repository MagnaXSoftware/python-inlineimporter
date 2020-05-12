How it Works
############

PEP 302 defines a protocol for managing module imports.
The protocol boils down to this:

* There are two components: ``Finders`` and ``Loaders``.
* ``Finders`` are responsible for, unsurprisingly, finding modules.
* If a ``Finder`` locates a module, i.e. *knows* which loader can load a module, it returns a  ``ModuleSpec``.
* This ``ModuleSpec`` contains information on the module, such as filename and package, and identifies which ``Loader`` can execute the load.
* The ``Loader`` is, as you've guessed it, responsible for loading modules into the environment.
* It does so by first creating a module object, which the python machinery places into the ``sys.modules`` dictionary, then compiling and executing the module code.
* An object that can both Find and Load is called an ``Importer``.

inline-importer works by placing the source code of modules in a dictionary, keyed by module name.
The finder searches this dictionary for an entry whose key matches the given module name.
If found, it returns a ``ModuleSpec`` with itself listed as the ``Loader``.
Then, when python calles the ``Loader``, inline-importer simply compiles the inlined source code to python bytecode and executes it as the normal python loader would.
