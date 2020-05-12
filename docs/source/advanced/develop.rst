Develop inline-importer
#######################

While inline-importer is listed on `github.com <https://github.com/MagnaXSoftware/python-inlinepython>`_, development happens on MagnaX's `gitlab server <https://git.magnax.ca/magnax/python-inlineimporter>`_.

We welcome issues, discussions, and PRs on GitHub, but mainline development will occur on our internal gitlab.

Environment
===========

You can develop using any supported version of python (``>= 3.4``), but we recommend using python ``>= 3.6`` as black, the code formatter we use, requires that as a minimum.

Guide
=====

While we do not have a formal guide for contributions, we try to follow a few principles.

* The ``Importer`` component should be as small as possible, without sacrificing maintainability.
* The ``Importer`` component should have as few dependencies as possible, so that ``inline-importer`` is not required at runtime.
* There should be an easy and simple path for typical usecases.
* Advanced or complex functionality should be exposed through additional parameters or options in the inliner.
* The "public" API should not be broken without good reason.
* Generally, follow the Zen of Python.