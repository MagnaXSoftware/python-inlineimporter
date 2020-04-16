# InlineImporter

InlineImporter is a library for python projects that uses the PEP 302 import protocol to inline libraries into a script.

## Why?

Because we can.

But in all seriousness, this came out from spending days managing adhoc scripts that shared a lot of functionality.
For ease of development, it would have been nice to extract the common pieces to a common library, but that would have meant distributing a whole directory and managing import paths on the destination systems versus a single self-contained file.

## How it works

PEP 302 defined a protocol for managing module imports.
The protocol defines two components: `Finder`s and `Loader`s.
The Finder is responsible for, unsurprisingly, finding modules.
If a Finder finds a module, i.e. _knows_ which loader can load a module, it returns a  `ModuleSpec`.
This ModuleSpec gives details on some parameters of the module, such as filename and package, and states which Loader can load the module.
The Loader is, as you've guessed it, responsible for loading modules into the environment.
It does so by first creating a module object, which the python machinery places into the `sys.modules` dictionary, then executing the module code.
An object that can both Find and Load is called an `Importer`.

InlineImporter works by placing the source code of modules in a dictionary, keyed by module name.
The finder searche the dictionary for a key matching the given module name.
If found, it returns a ModuleSpec with itself listed as the loader.
The loader simply compiles the inlined source code to python bytecode, and executes it as the normal python loader does.

## Usage

Include `inline-importer` in your development dependencies.
**`inline-importer` is not a runtime dependency, but a build-time dependency instead.**

Build your final script using _TDB_ and distribute the output of that instead.

Your users will not require `inline-importer`.
However, if you have dependencies on other modules, your users will have to install those.

## What's next

While the importer is built, the rest of the machinery isn't.

* [x] Importer with PoC.
* [ ] Script to collect all the modules to be inlined and build the dictionary.
* [x] Script that can combine the importer and the modules.
* [ ] Support for inlining distributed python libraries.
* [ ] Support for pre-compiled bytecode.
