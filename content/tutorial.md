---
title: "Tutorial"
date: 2017-10-11T19:11:44+02:00
draft: false
---

<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}
});
</script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>

This tutorial has the purpose of providing detailed information for *users* of the library. It is split into three sections:

  1. [Description of a simple system](#the-system) that will be used for the tutorial;
  2. [Construction of a model](#system-model-construction) for the system;
  3. [Analysis of the model](#system-model-analysis), in terms of both evolution and verification.

Ariadne currently uses a programmatic C++ approach to describe a model and analyze it. The full code presented in the following is available [here](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/tutorial/) as a simple self contained example with extensive comments. After following this tutorial, we encourage to play with the example in order to better understand the behavior of the modeled system.

## The system

![watertank](/img/watertank.png "The watertank system")

The system described for this tutorial is a *watertank* system. This example from hydrodynamics revolves around a tank component, which has a controlled input water flow and an output water flow. In particular, the input pressure $p$ is modulated by a valve to obtain the actual input $u$ to the tank. The controller acts in response to a reading $x_s$ of the actual water level $x$. The reading is affected by an uncertainty $\delta$.

![watertank-block](/img/watertank-block.png "The watertank system block diagram")

For our system model, we identify three components: the [tank](#tank-model), the [valve](#valve-model) and the [controller](#controller-model). In order to provide a model of the sensor, instead, we would need to be able to express the relation $x_s(t) = x(t) + \delta$. This amounts to treating $\delta$ as a noise source. However, Ariadne currently does not support noise modeling in the stable release, hence we will provide an alternative system model that achieves a similar result. In addition, algebraic relations are not supported in the automata model of the stable release (while they are available in the development version).

### Tank model

The model of the tank is simple, since it involves only one location, hereby called *flow*, with no transitions. The dynamics of the water level $x$ is the result of the effect of the output flow $\Phi_o = -\alpha\, x $ and the input flow $\Phi_i = \beta\, a$.

![tank-model](/img/tankmodel.png "The tank model")

Here we choose a fixed value $\alpha = 0.02$, which is a function of hydrodynamic quantities including the outlet section area. On the other hand, we want to have $\beta \in [0.3,\, 0.32863]$, with the semantics that the input flow is a *fixed* value in that interval. The motivation behind the interval is that we want to study the behavior of the system for all the values in the interval, under the assumption that $\beta$ has a fixed but unknown value. Let us remark again that Ariadne does not currently support *differential inclusions*, which would allow $\beta$ to vary within the interval.

Please note that a more realistic expression for the output flow would require $\Phi_o \propto \sqrt{x}$. However, this choice would have inherent numerical issues around $x = 0$ in the presence of over-approximations, in particular when discretizing the reachable set onto a grid. In order to allow some tweaking of the model parameters in Ariadne without incurring into numerical issues, we preferred to settle for a simplified expression for the tutorial.

### Valve model

![valve-model](/img/valvemodel.png "The valve model")

### Controller model

![controller-model](/img/controllermodel.png "The controller model")

## System model construction

### Tank

### Valve

### Controller

### Composition

## System model analysis

### Evolution

#### Finite time evolution

#### Infinite time outer evolution

#### Infinite time lower evolution

### Verification

#### Safety verification

#### Parametric safety verification

