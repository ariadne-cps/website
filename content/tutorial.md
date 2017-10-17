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

  1. [Description of a simple system](#1-the-system) that will be used for the tutorial;
  2. [Construction of a model](#2-system-model-construction) for the system;
  3. [Analysis of the model](#3-system-model-analysis), in terms of both evolution and verification.

Ariadne currently uses a programmatic C++ approach to describe a model and analyze it. The full code presented in the following is available [here](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/tutorial/) as a simple self contained example with extensive comments. After following this tutorial, we encourage to play with the example in order to better understand the behavior of the modeled system.

# 1 - The system

![watertank](/img/watertank.png "The watertank system")

The system described for this tutorial is a *watertank* system. This example from hydrodynamics revolves around a tank component, which has a controlled input water flow and an output water flow. In particular, the input pressure $p$ is modulated by a valve to obtain the actual input $u$ to the tank. The controller acts in response to a reading $x_s$ of the actual water level $x$. The reading is affected by an uncertainty $\delta$.

![watertank-block](/img/watertank-block.png "The watertank system block diagram")

For our system model, we identify three components: the [tank](#1-1-tank-model), the [valve](#1-2-valve-model) and the [controller](#1-3-controller-model). In order to provide a model of the sensor, instead, we would need to be able to express the relation $x\_s(t) = x(t) + \delta$. This amounts to treating $\delta$ as a noise source. However, Ariadne currently does not support noise modeling in the stable release, hence we will provide an alternative system model that achieves a similar result. In addition, algebraic relations are not supported in the automata model of the stable release (while they are available in the development version).

## 1.1 - Tank model

The model of the tank is simple, since it involves only one location, hereby called *flow*, with no transitions. The dynamics of the water level $x$ is the result of the effect of the output flow $\Phi\_o = -\alpha\, x $ and the input flow $\Phi\_i = \beta\, a$.

![tank-model](/img/tankmodel.png "The tank model")

Here we choose a fixed value $\alpha = 0.02$, which is a function of hydrodynamic quantities including the outlet section area. On the other hand, we want to have $\beta \in [0.3,\, 0.32863]$, with the semantics that the input flow is a *fixed* value in that interval. The motivation behind the interval is that we want to study the behavior of the system for all the values in the interval, under the assumption that $\beta$ has a fixed but unknown value. Let us remark again that Ariadne does not currently support *differential inclusions*, which would allow $\beta$ to vary within the interval.

Please note that a more realistic expression for the output flow would require $\Phi\_o \propto \sqrt{x}$. However, this choice would have inherent numerical issues around $x = 0$ in the presence of over-approximations, in particular when discretizing the reachable set onto a grid. In order to allow some tweaking of the model parameters in Ariadne without incurring into numerical issues, we preferred to settle for a simplified expression for the tutorial.

## 1.2 - Valve model

The model of the valve assumes that the valve opens or closes in a finite time $T = 4\, s$, with a linear opening or closing. Consequently we define two locations *opening* and *closing* in which the dynamics for the aperture $a$ is increasing or decreasing, respectively, with a rate equal to $\frac{1}{T}$. A third location *idle* instead models the valve being fully opened or fully closed, i.e., when $a$ is not allowed to vary.

![valve-model](/img/valvemodel.png "The valve model")

Transitions between locations in this automaton are either *internal* or *external*. An internal transition is fired from *opening* to *idle* as soon as $a \geq 1$, since $a$ is not allowed to increase further. Similarly, an internal transition is fired from *closing* to *idle* as soon as $a \leq 0$, since $a$ is not allowed to decrease further. External transitions have associated *event labels*, such as *open* and *close*, which *synchronize* with other automata with the same labels. In this case, since no transition guard is defined, we say that *open* and *close* are *input transitions* for the valve automaton: such transitions will be taken when a corresponding output event is fired by another automaton.

Invariants in the *opening* and *closing* locations are set as the complements of the guards, in order to model the fact that the transitions are *urgent*, i.e., if the trajectory reaches a point that satisfies a guard, then it is required to take the transition immediately.

## 1.3 - Controller model

As discussed previously, the valve is receptive to an *open* and *close* commands. The controller is responsible for issuing such commands. In particular, for simplicity we want to have an *hysteretic* control such that we provide an *open* command when the water level is too low, or a *close* command when the water level is too high.
 
![controller-model](/img/controllermodel.png "The controller model")

Consequently, the automaton is characterized by two states: *rising*, when we are operating under the assumption that the water level is rising, and *falling*, then the assumption is the opposite one. 

We define $h\_{\max} = 7.75$ meters and $h\_{\min} = 5.75$ meters as the acceptable thresholds for the water level. A condition $x \geq h\_{\max}$ would trigger the *close* event, while a condition $x \leq h\_{\min}$ would trigger the *open* event. 
However, in our model, we want to provide non-determinism by introducing *non-urgent* (or *permissive*) transitions. This is obtained by enlarging the intersection between a guard and its corresponding invariant: specifically, we enlarge by $2\, \delta$, with $\delta = 0.1$ meters. The result of such enlargement is that the transition corresponding to the *open* event is both taken and not taken for all $x$ values in the $\[-\delta+h\_{\min},\,h\_{\min}+\delta]$ interval. Similarly, the *close* event is both taken and not taken for all $x$ values in the $\[-\delta+h\_{\max},\,h\_{\max}+\delta]$ interval.

# 2 - System model construction

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

In the following we provide the specific implementation for each of the three components of the [tank](#2-1-tank), [valve](#2-2-valve) and [controller](#2-3-controller), followed by a brief discussion on the final [composition](#2-4-composition) of the automata. Please note that the details on each operation will not be repeated for all components.

## 2.1 - Tank

First, it is necessary to include the top header of the library for user consumption:

```c++
#include "ariadne.h"
```

The automaton itself is constructed with the following instruction:

```c++
HybridIOAutomaton tank("tank");
```
where the argument string is useful for logging purposes. This is already a legal automaton, while still empty.

Let us fill it with some behavior. First, we want to define the variables to use:

```c++
RealVariable a("a");
RealVariable x("x");
```

Please note that, since variables are shared within the system, their definition may be provided only once for all components, at the top of the definition file. Still, sharing is performed based on the string label, not on the C++ variable name. Consequently, there may exist multiple variable objects with different names but same label.

Variables need to be added to the automaton, specifying their I/O character:

```c++
tank.add_input_var(a);
tank.add_output_var(x);
```

Now we want to define the location of the automaton:

```c++
DiscreteLocation flow("flow");
```

which is added to the automaton with

```c++
tank.new_mode(flow);
```

Now we can add dynamics for the location in respect to the automaton. But first, let us define some parameters:

```c++
RealParameter alpha("alpha",0.02);
RealParameter beta("beta",Interval(0.3,0.32863));
```

where we use the `Interval` class to define an interval instead of a singleton value.

Then, we add the dynamics with

```c++
tank.set_dynamics(flow, x, - alpha * x + beta * a);
```

An expression in Ariadne allows any nonlinear combination of variables, constants and parameters, along with the exp, log, sin, cos, tan and sqrt functions.

## 2.2 - Valve

We start construction of the valve automaton with

```
HybridIOAutomaton valve("valve");
```

and add the only involved variable:

```
valve.add_output_var(a);
```

The three locations are then introduced and added using:

```
DiscreteLocation idle("idle");
DiscreteLocation opening("opening");
DiscreteLocation closing("closing");

valve.new_mode(idle);
valve.new_mode(opening);
valve.new_mode(closing);
```

Before adding the corresponding dynamics, we set the parameter $T$:

```
RealParameter T("T",4.0);
```

after which we define:

```
valve.set_dynamics(idle, a, 0.0);
valve.set_dynamics(opening, a, 1.0/T);
valve.set_dynamics(closing, a, -1.0/T);
```

Now we move to events, by starting from the introduction of the labels:

```
DiscreteEvent e_open("open");
DiscreteEvent e_close("close");
DiscreteEvent e_idle("idle");
```

We remind here that events, like variables, are shared between automata using their string labels, not their C++ variable names. 

To add the events to the automaton, we need to provide the I/O character:

```
valve.add_input_event(e_open);
valve.add_input_event(e_close);
valve.add_internal_event(e_idle);
```

While the *open* and *close* events must necessarily be specified as input, since they are not issued by the valve automaton, the *idle* event may be internal or output equivalently. Choosing an internal event is preferable for incapsulation purposes, when we do not need an event to be read by other components.

For transitions, let's start with the simplest case: transitions without a guard or a reset. Such case arises from the presence of an input event, where the guard and reset for the transition are set by the automaton that fires the event itself.

The syntax required becomes:

```
valve.new_unforced_transition(e_open, idle, opening);
valve.new_unforced_transition(e_close, idle, closing);
```

For such situation, we always consider the transition as *unforced* (i.e., non-urgent) for generality, in order to allow non-determinism depending on the actual guards and invariants. The first argument is the (input) event, the second is the *source* location and the third is the *target* location. In the case of self-loops, the target location can be equal to the source location.

Let us now consider the case of internal/output transitions. First, we need to set the guards for the transitions:

```
RealExpression a_geq_one = a - 1.0;
RealExpression a_leq_zero = - a;
```

Here we provide `RealExpression` variables for clarity, instead of directly using the expressions inline within the corresponding transitions. A guard expression $g$ is defined under a $g \geq 0$ assumption. Consequently, it may be necessary to rearrange terms to comply to the required convention. In our case, the two lines correspond to defining the guard expressions $a \geq 1$ and $a \leq 0$ respectively.

To provide a reset, we need to define a variable-expression map instead:

```
std::map<RealVariable,RealExpression> rst_a_one;
rst_a_one[a] = 1.0;
std::map<RealVariable,RealExpression> rst_a_zero;
rst_a_zero[a] = 0.0;
```

We are providing two separate reset maps, applying to the only variable $a$. If there are multiple variables and one of them is reset, then for safe specification a reset for each variable is required: in that case, an identity expression such as `rst[x] = x;` can be used.

Now we can finally provide the transitions themselves:

```
valve.new_forced_transition(e_idle, opening, idle, rst_a_one, a_geq_one);
valve.new_forced_transition(e_idle, closing, idle, rst_a_zero, a_leq_zero);
```

In this case, the transition is defined as *forced*, i.e., urgent. Using this specification, we are not required to provide invariants for the automaton: the invariant in a location is implicitly set as the complement of the union of the guard sets of outgoing transitions.

## 2.3 - Controller

## 2.4 - Composition

# 3 - System model analysis

## 3.1 - Evolution

### 3.1.1 - Finite time evolution

### 3.1.2 - Infinite time outer evolution

### 3.1.3 - Infinite time lower evolution

## 3.2 - Verification

### 3.2.1 - Safety verification

### 3.2.2 - Parametric safety verification

