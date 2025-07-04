---
title: "Installation"
date: 2017-07-22T19:11:44+02:00
draft: false
---

## Installation ##

The command-line installation instructions are presented for Debian Linux systems and derivatives (using apt) and macOS systems (using Homebrew). However, openSUSE and Fedora are known to be working when using their own package managers. Windows installations are not supported yet.

Official packages are available for Ubuntu LTS (currently 24.04) and derivatives and macOS 15, but if your architecture or particular setup necessarily requires compilation from sources, instructions are provided. The build system used is CMake. The library is tested for compilation on Ubuntu using gcc (minimum required: 12) and clang (minimum required: 16), under AppleClang latest on macOS.

### Official packages

Supplied packages are published using the official Launchpad platform for Ubuntu, and a custom Homebrew tap repository for macOS. Packages simply require all the dependencies, namely: MPFR, Cairo, Gnuplot and Python 3.

#### Ubuntu

In order to install the apt package, first you need to import the ppa repository to the ppa list:

```
sudo add-apt-repository ppa:ariadne-cps/ariadne
```

Then you can install Ariadne (along with any missing dependencies):

```
sudo apt-get install ariadne
```

which will be updated with the latest release as with other apt packages.

#### macOS

In order to install the Homebrew package, you just need to

```
brew install ariadne-cps/tap/ariadne
```

which in one line both sets up the "tap" for Ariadne and installs the package along with any missing dependencies. The package will be upgraded with any new versions after a `brew upgrade` is issued. The package currently supports x86-64 architectures on macOS Big Sur. Other configurations trigger an automatic build, therefore you should not need to deal with sources any time.

### Dependencies for installation from sources

If installed from sources, the only required library dependency is MPFR. To enable the graphical output you will require either Cairo or Gnuplot in order to save into png files. Finally, the Python bindings require the Python headers (version 3 is only supported, since version 2 is discontinued). In particular for Python, there is an internal Git submodule dependency on the header-only [pybind11](https://github.com/pybind/pybind11) library. In order to build all the submodules of the library, Git must be installed even if Ariadne has been downloaded as an archive. Download of the dependencies is automatic though.

Finally, if you want to build the documentation, you need Doxygen and a working Latex distribution (including the Math packages).

Please note that adding new dependencies after preparing the build environment requires to re-run the CMake command.

Specific instructions for Ubuntu and macOS follow, starting from installation from pre-compiled packages.

#### Ubuntu

apt packages: `cmake pkg-config git libmpfr-dev libcairo2-dev gnuplot` and either `clang-16` or `g++-12` for the compiler toolchain.

Additional package required for the Python interface: `python3-dev`.

Additional packages required for documentation: `doxygen doxygen-latex`

#### macOS

Homebrew packages: `cmake git mpfr cairo gnuplot`.

For Cairo support, you may need to set up a permanent variable for the path of pkgconfig by adding the following line in your `~\.bash_profile`:

```
export PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig
```

To allow building the documentation: `brew install --cask mactex-no-gui` and `brew install doxygen`.

### Downloading the sources

A pre-packaged source zip/tar.gz archive is always available in the [releases](https://github.com/ariadne-cps/ariadne/releases) section of Ariadne's GitHub space.
Still, it is usually preferable to *clone* the repository using Git, in order to keep the distribution updated as soon as a new release is available. 
To do that, you shall issue

```
git clone https://github.com/ariadne-cps/ariadne 
```

which creates an *ariadne* directory under the present working directory. Let's switch into that directory. 

### Building

To build the library from sources in a clean way, it is preferable that you set up a build subdirectory, say:

```
$ mkdir build && cd build
```

Then you can prepare the build environment, choosing a Release build for maximum performance:

```
$ cmake .. -DCMAKE_BUILD_TYPE=Release
```

At this point, if no error arises, you can build the C++ library and its Python bindings with:

```
$ cmake --build .
```

This build does not include the `examples`, `tutorials` and `tests` targets. You can build those by supplying targets with the following:

```
$ cmake --build . --target <TARGET>
```

or by using the `everything` target to include all code targets.

To build the `doc` target for documentation, explicitly use:

```
$ cmake --build . --target doc
```

then you can access the built documentation from the `docs/html/index.html` file in the build directory.


### Installing globally

To install the library globally from built sources, you must do

```
$ cmake --build . --target install
```

using `sudo` if you require administrator privileges for a Linux installation. Please note that the installation will build the whole distribution beforehand, hence it is preferable that you first build the other targets without administrator privileges, build the install target.

To find the installed library under Ubuntu, assuming you use the Bash interpreter you may need to set the library path variable:

```
export LD_LIBRARY_PATH=/usr/local/lib
```

while for macOS:

```
export DYLD_LIBRARY_PATH=/usr/local/lib
```

which can be stored in the .bashrc (Ubuntu) or .bash_profile (macOS) files of your home directory for use in any terminal instance.

### Building executables using Ariadne

The tutorials directory contains two CMake projects that rely on a correct installation of Ariadne, either by using a package or by building the sources. You can copy a project directory in any place on your file system and follow the instructions on the README file inside to check that your installation was successful.
