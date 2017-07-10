---
title: "Installation"
date: 2017-07-09T19:11:44+02:00
draft: false
---

These installation instructions have been tested on Ubuntu 16.04 and macOS 10.12. 

### Preparing for the installation

First let's download the source distribution from https://bitbucket.org/ariadne-cps/release-1.0. To do that, we need to install the *git* version control software. 

#### Ubuntu

Issue the command
```
$ sudo apt-get install git
```
to obtain the software.

#### macOS

The easiest way is to install the Command Line Developer Tools from the Apple Store. The tools are also required to obtain dependencies through the Brew package manager and to build the sources.

### Installing the dependencies

For the Ubuntu installation, we will refer to packages available on Aptitude. The macOS installation instead will assume you are using the Brew package manager.

The library dependencies of Ariadne are the following:

#### Ubuntu
Aptitude packages required: `cmake libboost-system-dev libboost-serialization-dev libboost-thread-dev libgtk2.0-dev libcairo2-dev libbdd-dev`

#### macOS

First, install Homebrew from http://brew.sh/.

The Homebrew packages required are: `cmake boost gtk cairo`, therefore issue

```
$ brew install cmake boost gtk cairo
```

No Buddy package is offered, hence you need to compile the library from https://sourceforge.net/projects/buddy/ :

1. Download and extract the Buddy package
2. From the extracted directory:

```
$ ./configure
$ make
$ make install
```

Optionally, if you want to build the documentation, you need Doxygen and a working Latex distribution (including the Math packages).

### Building the library

The build system is CMake. The compiler we tested the library under Ubuntu is g++, while for macOS is clang. To build the library in a clean way, it is preferable that you set up a build subdirectory from the root of the Ariadne directory:

```
$ mkdir build
$ cd build
```

Then you can prepare the build environment:

```
$ cmake ..
```

At this point, if no error arises, you can build the library itself:

```
$ make
```

Optionally, you can also run the test suite for the library:

```
$ make test
```

where no error should appear.

If you have correctly installed Doxygen and a Latex distribution and you want to build the documentation, you have to issue the following:

```
$ make doc
```

### Installing globally

To install the library globally, you must do
```
$ make install
```

To find the installed library under Ubuntu, you may need to set the `LD_LIBRARY_PATH` variable in the .bashrc file:
```
export LD_LIBRARY_PATH=/usr/local/lib
```

To test the correctness of the global installation, you may copy the `tutorial/` example into any location of your file system and build it. The tutorial relies on Ariadne being present within system library and include directories.
