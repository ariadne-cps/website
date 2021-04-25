---
title: "Release 2.0"
date: 2020-04-17T18:03:10+02:00
draft: false
---

We are happy to announce the release of version 2.0 of Ariadne!

This release introduces a significant number of changes with respect to the previous major version, mainly:

  1. A more general and robust way of constructing hybrid automata;
  2. On-the-fly composition of systems;
  3. A hybrid simulator based on the classic Runge-Kutta method;
  4. Use of constraints in the evolution of hybrid systems;
  5. Algebraic-differential equations;
  6. Differential inclusions in the continuous space;
  7. Wider use of named variables and symbolic manipulation;
  8. Python bindings for most of the library.

In the process of transitioning from version 1.0 some functionality has not been migrated yet though:

  1. Verification routines;
  2. Parametric analysis;
  3. Use of BDDs for discretisation of reachable sets.

These will be targets for a next release, along with the completion of some functionality such as differential inclusions in the hybrid space and Python bindings for the dynamics module. From now on, the release cycle of Ariadne will be more frequent, in order to reflect API changes and new features.

The installation instructions and the tutorial have been updated accordingly.

