---
title: "About"
date: 2017-07-11T10:01:34+02:00
draft: false
---

Ariadne is a library for [formal verification](https://en.wikipedia.org/wiki/Formal_verification) of [cyber physical systems](https://en.wikipedia.org/wiki/Cyber-physical_system). In particular, it allows to model such systems as [hybrid systems](https://en.wikipedia.org/wiki/Hybrid_system), focusing on nonlinear behavior.

Since the evolution of a nonlinear hybrid system cannot be calculated exactly, Ariadne uses [numerical analysis](https://en.wikipedia.org/wiki/Numerical_analysis) to compute such evolution in an approximate way. The library uses a conservative rounding approach along with rigorous semantics to guarantee the correctness of the results, independently of the numerical precision of the processing machine. In particular, it is able to calculate approximations of the trajectory *from above* or *from below*, which allows to prove or disprove properties of the system, respectively.

The library is written in C++ and it is [distributed](https://bitbucket.org/ariadne-cps) using Git on BitBucket under the GPLv3 license. The *release-1.0* repository currently holds the stable version of the library. This is the repository referenced by this site in terms of documentation, tutorial and installation. The *development* repository introduces a lot of improvements to the code base, it is usable but it is still considered not stable. In addition, verification routines are not currently implemented in the development version. The user interface of the library currently relies on using C++ code directly. Python bindings are available in the development version, but they are mainly focused on low-level routines for numerical analysis. Ariadne is actively supported on both Ubuntu derivatives and macOS.

Ariadne is mainly developed as a collaboration between the [University of Verona, Italy](http://www.di.univr.it/?lang=en) and the [University of Maastricht, The Netherlands](https://www.maastrichtuniversity.nl/research/department-data-science-and-knowledge-engineering). Given the open nature of the library, we encourage anyone interested in contributing to [contact us](mailto:developers@ariadne-cps.org).

While this website represents the main resource for the documentation of the library, we also maintain a ResearchGate [project](https://www.researchgate.net/project/Ariadne-2) where the news from this site are backlinked.

