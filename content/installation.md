---
title: "Installation"
date: 2017-07-09T19:11:44+02:00
draft: false
---

These installation instructions have been tested on recent releases of Ubuntu and macOS, up to Ubuntu 18.04 and macOS 10.13. They specifically refer to the stable *release-1.0* version of the library. In order to install the development version instead, you should download the code from https://github.com/ariadne-cps/ariadne and follow the instructions from the corresponding README.md file.

### Downloading the distribution

First let's download the source distribution from https://github.com/ariadne-cps/release-1.0. It is possible to *clone* the repository using the *git* version control software, or simply to [download](https://github.com/ariadne-cps/release-1.0/downloads/) the repository as a package.

### Installing the dependencies

For the Ubuntu installation, we will refer to packages available on Aptitude. The macOS installation instead will assume you are using the Brew package manager.

The library dependencies of Ariadne are the following:

#### Ubuntu
Aptitude packages required: `cmake libboost-system-dev libboost-serialization-dev libboost-thread-dev libgtk2.0-dev libcairo2-dev libbdd-dev`

#### macOS

First, install Homebrew from http://brew.sh/. This operation will also ask to install the Command Line Developer Tools from the Apple Store. Such tools are also required to build the sources.

The Homebrew packages required are: `cmake boost gtk cairo`, therefore issue

    $ brew install cmake boost gtk cairo

No Buddy package is offered, hence you need to compile the library from https://sourceforge.net/projects/buddy/ :

1. Download and extract the Buddy package
2. From the extracted directory:

    ```
    $ ./configure
    $ make
    $ make install
    ```

Optionally, if you want to build the documentation, you need Doxygen and a working Latex distribution (including the Math packages).

### Building the distribution

The build system used is CMake. The compiler we tested the library under Ubuntu is g++, while for macOS is clang. To build the distribution in a clean way, it is preferable that you set up a build subdirectory from the root of the Ariadne director. For example:

    $ mkdir build
    $ cd build

Then you can prepare the build environment:

    $ cmake ..

At this point, if no error arises, you can build the distribution itself:

    $ make
    
In particular, if you need to build the library only, you can issue

    $ make ariadne
    
or if you want to build the tests along with the library, do

    $ make tests

If the tests have been built, you can run the test suite for the library:

    $ make test

where no error should appear.

If you have correctly installed Doxygen and a Latex distribution and you want to build the documentation, you have to issue the following:

    $ make doc

### Installing the library globally

To install the library globally, you must issue

    $ make install

Depending on your machine, it may be necessary to use `sudo make install` instead, if you do not have privileges for writing into the corresponding include/ and lib/ directories.

To find the installed library under Ubuntu, you may need to set the `LD_LIBRARY_PATH` variable in the .bashrc file:

    export LD_LIBRARY_PATH=/usr/local/lib

To test the correctness of the global installation, you may copy the `tutorial/` example into any location of your file system and build it. The tutorial relies on Ariadne being present within system library and include directories.
