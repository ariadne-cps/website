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

# The system

![watertank](/img/watertank.png "The watertank system")

The system described for this tutorial is a *watertank* system. This example from hydrodynamics revolves around a tank component, which has a controlled input water flow and an output water flow. In particular, the input pressure $p$ is modulated by a valve to obtain the actual input $u$ to the tank. The controller acts in response to a reading $x_s$ of the actual water level $x$. The reading is affected by an uncertainty $\delta$.

![watertank-block](/img/watertank-block.png "The watertank system block diagram")

For our system model, we identify three components: the [tank](#tank-model), the [valve](#valve-model) and the [controller](#controller-model). In order to provide a model of the sensor, instead, we would need to be able to express the relation $x\_s(t) = x(t) + \delta$. This amounts to treating $\delta$ as a noise source. However, Ariadne currently does not support noise modeling in the stable release, hence we will provide an alternative system model that achieves a similar result. In addition, algebraic relations are not supported in the automata model of the stable release (while they are available in the development version).

## Tank model

The model of the tank is simple, since it involves only one location, hereby called *flow*, with no transitions. The dynamics of the water level $x$ is the result of the effect of the output flow $\Phi\_o = -\alpha\, x $ and the input flow $\Phi\_i = \beta\, a$.

![tank-model](/img/tankmodel.png "The tank model")

Here we choose a fixed value $\alpha = 0.02$, which is a function of hydrodynamic quantities including the outlet section area. On the other hand, we want to have $\beta \in [0.3,\, 0.32863]$, with the semantics that the input flow is a *fixed* value in that interval. The motivation behind the interval is that we want to study the behavior of the system for all the values in the interval, under the assumption that $\beta$ has a fixed but unknown value. Let us remark again that Ariadne does not currently support *differential inclusions*, which would allow $\beta$ to vary within the interval.

Please note that a more realistic expression for the output flow would require $\Phi\_o \propto \sqrt{x}$. However, this choice would have inherent numerical issues around $x = 0$ in the presence of over-approximations, in particular when discretizing the reachable set onto a grid. In order to allow some tweaking of the model parameters in Ariadne without incurring into numerical issues, we preferred to settle for a simplified expression for the tutorial.

## Valve model

The model of the valve assumes that the valve opens or closes in a finite time $T = 4\, s$, with a linear opening or closing. Consequently we define two locations *opening* and *closing* in which the dynamics for the aperture $a$ is increasing or decreasing, respectively, with a rate equal to $\frac{1}{T}$. A third location *idle* instead models the valve being fully opened or fully closed, i.e., when $a$ is not allowed to vary.

![valve-model](/img/valvemodel.png "The valve model")

Transitions between locations in this automaton are either *internal* or *external*. An internal transition is fired from *opening* to *idle* as soon as $a \geq 1$, since $a$ is not allowed to increase further. Similarly, an internal transition is fired from *closing* to *idle* as soon as $a \leq 0$, since $a$ is not allowed to decrease further. External transitions have associated *event labels*, such as *open* and *close*, which *synchronize* with other automata with the same labels. In this case, since no transition guard is defined, we say that *open* and *close* are *input transitions* for the valve automaton: such transitions will be taken when a corresponding output event is fired by another automaton.

Invariants in the *opening* and *closing* locations are set as the complements of the guards, in order to model the fact that the transitions are *urgent*, i.e., if the trajectory reaches a point that satisfies a guard, then it is required to take the transition immediately.

## Controller model

As discussed previously, the valve is receptive to an *open* and *close* commands. The controller is responsible for issuing such commands. In particular, for simplicity we want to have an *hysteretic* control such that we provide an *open* command when the water level is too low, or a *close* command when the water level is too high.
 
![controller-model](/img/controllermodel.png "The controller model")

Consequently, the automaton is characterized by two states: *rising*, when we are operating under the assumption that the water level is rising, and *falling*, then the assumption is the opposite one. 

We define $h\_{\max} = 7.75$ meters and $h\_{\min} = 5.75$ meters as the acceptable thresholds for the water level. A condition $x \geq h\_{\max}$ would trigger the *close* event, while a condition $x \leq h\_{\min}$ would trigger the *open* event. 
However, in our model, we want to provide non-determinism by introducing *non-urgent* (or *permissive*) transitions. This is obtained by enlarging the intersection between a guard and its corresponding invariant: specifically, we enlarge by $2\, \delta$, with $\delta = 0.1$ meters. The result of such enlargement is that the transition corresponding to the *open* event is both taken and not taken for all $x$ values in the $\[-\delta+h\_{\min},\,h\_{\min}+\delta]$ interval. Similarly, the *close* event is both taken and not taken for all $x$ values in the $\[-\delta+h\_{\max},\,h\_{\max}+\delta]$ interval.

# System model construction

In Ariadne, the construction of a C++ data structure that represents the described model is performed progressively: we start with an empty automaton and we proceed to "fill it" with locations and transitions.

The formalism used internally by the library is that of Hybrid I/O Automata (see [this article](http://www.sciencedirect.com/science/article/pii/S0890540103000671) for reference). Essentially, in a hybrid I/O automaton variables and events have an I/O specification:

  - *internal* if they are not visible outside the automaton;
  - *output* if their dynamics are specified (variables) or they are fired (events) within the automaton;
  - *input* if they are specified or fired from another automaton.

The additional constraint given by the I/O character is not stricly necessary, yet it is useful to construct complex systems where the roles of each component are explicit. Consequently, this is the preferred syntax used for the specification of automata in Ariadne.

The costruction of an automaton can be summarized in these steps:

  1. An automaton object is created;
  2. Variables and events are added with their I/O character;
  3. Locations are added;
  4. Dynamics and invariants are added, specifying the location;
  5. Transitions are added, specifying the event, the source and target location, the guard and the reset.

In the following we provide the specific implementation for each of the three components of the [tank](#tank), [valve](#valve) and [controller](#controller), followed by a brief discussion on the final [composition](#composition) of the automata.

## Tank



## Valve

## Controller

## Composition

# System model analysis

## Evolution

### Finite time evolution

### Infinite time outer evolution

### Infinite time lower evolution

## Verification

### Safety verification

### Parametric safety verification

