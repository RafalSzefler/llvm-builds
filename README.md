llvm-builds
===========

The main responsibility of this respository is to build LLVM from source code and distribute
built artifacts in the form of zipped binaries.

Building LLVM
=============

To run build scripts you need the following components:

* Python3.9+ (it is necessary for building LLVM anyway)
* git (likely any modern version will do)
* Some valid C++ compiler (likely CMake will cry about it anyway)

The Python scripts will try to install missing dependencies (like CMake) if necessary.
By "install" we mean generate/build/download needed packages locally, without doing any
environment modifications.

Once you have those simply run

> python builder/build_archive.py --llvm-version=22

This will generate and pack a new LLVM build for current host. The entire build will get zipped
and stored inside `/archives` folder by default.

For more information about the script run

> python builder/build_archive.py --help

*Note:* by default this generates `Release` builds. It also excludes all tests, benchmarks
and examples so that compilation process is faster, and final artifacts smaller.

At the moment the repository does not support different build configurations. Of course you
can always manually modify `/builder/scripts/helpers_llvm.py` script to fix that. In particular
the `cmake`/`ninja` calls inside.

Usage
=====

Once you have build an archive you can unpack it and link to existing project.
Note that each archive should have `bin/llvm-config` binary inside to help
you with that task (this is verified at build anyway).
