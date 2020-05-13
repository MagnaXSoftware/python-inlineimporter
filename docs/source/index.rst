inline-importer Documentation
#############################

inline-importer is a library for python projects that uses the `PEP 302 <https://www.python.org/dev/peps/pep-0302/>`_ import protocol to inline libraries into a single-file script.

Why build inline-importer?
==========================

Because we can.

But in all seriousness, this came out from spending days managing adhoc scripts that shared a lot of functionality.
For ease of development, it would have been nice to extract the common pieces to a common library, but that would have meant distributing a whole directory and managing import paths on the destination systems versus a single self-contained file.

License
=======

inline-importer is licensed under the MIT license.

Guide
=====

.. toctree::
   :maxdepth: 2

   install
   usage


Advanced Information & Development
==================================

.. toctree::
   :maxdepth: 2

   advanced/how-it-works
   advanced/usage
   advanced/develop
   advanced/api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
