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

Ariadne currently uses a programmatic C++ approach to describe a model and analyse it. The full code presented in the following is available [here](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/tutorial/) as a simple self contained example with extensive comments. After following this tutorial, we encourage to play with the example in order to better understand the behavior of the modeled system.

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

Transitions between locations in this automaton are either *internal* or *external*. An internal transition is fired from *opening* to *idle* as soon as $a \geq 1$, since $a$ is not allowed to increase further. Similarly, an internal transition is fired from *closing* to *idle* as soon as $a \leq 0$, since $a$ is not allowed to decrease further. External transitions have associated *event labels*, such as *open* and *close*, which *synchronise* with other automata with the same labels. In this case, since no transition guard is defined, we say that *open* and *close* are *input transitions* for the valve automaton: such transitions will be taken when a corresponding output event is fired by another automaton.

Invariants in the *opening* and *closing* locations are set as the complements of the guards, in order to model the fact that the transitions are *urgent*, i.e., if the trajectory reaches a point that satisfies a guard, then it is required to take the transition immediately.

## 1.3 - Controller model

As discussed previously, the valve is receptive to an *open* and *close* commands. The controller is responsible for issuing such commands. In particular, for simplicity we want to have an *hysteretic* control such that we provide an *open* command when the water level is too low, or a *close* command when the water level is too high.
 
![controller-model](/img/controllermodel.png "The controller model")

Consequently, the automaton is characterised by two states: *rising*, when we are operating under the assumption that the water level is rising, and *falling*, then the assumption is the opposite one. 

We define $h\_{\max} = 7.75$ meters and $h\_{\min} = 5.75$ meters as the acceptable thresholds for the water level. A condition $x \geq h\_{\max}$ would trigger the *close* event, while a condition $x \leq h\_{\min}$ would trigger the *open* event. 
However, in our model, we want to provide non-determinism by introducing *non-urgent* (or *permissive*) transitions. This is obtained by enlarging the intersection between a guard and its corresponding invariant: specifically, we enlarge by $2\, \delta$, with $\delta = 0.1$ meters. The result of such enlargement is that the transition corresponding to the *open* event is both taken and not taken for all $x$ values in the $\[-\delta+h\_{\min},\,h\_{\min}+\delta]$ interval. Similarly, the *close* event is both taken and not taken for all $x$ values in the $\[-\delta+h\_{\max},\,h\_{\max}+\delta]$ interval.

# 2 - System model construction

In Ariadne, the construction of a C++ data structure that represents the described model is performed progressively: we start with an empty automaton and we proceed to "fill it" with locations and transitions.

The formalism used internally by the library is that of Hybrid I/O Automata (see [this article](http://www.sciencedirect.com/science/article/pii/S0890540103000671) for reference). Essentially, in a hybrid I/O automaton variables and events have an I/O specification:

  - *internal* if they are not visible outside the automaton;
  - *output* if their dynamics are specified (variables) or they are fired (events) within the automaton;
  - *input* if they are specified or fired from another automaton.

The additional constraint given by the I/O character is not strictly necessary, yet it is useful to construct complex systems where the roles of each component are explicit. Consequently, this is the preferred syntax used for the specification of automata in Ariadne.

The costruction of an automaton can be summarised in these steps:

  1. An automaton object is created;
  2. Variables and events are added with their I/O character;
  3. Locations are added;
  4. Dynamics and invariants are added, specifying the location;
  5. Transitions are added, specifying the event, the source and target location, the guard and the reset.

In the following we provide the specific implementation for each of the three components of the [tank](#2-1-tank), [valve](#2-2-valve) and [controller](#2-3-controller), followed by a brief discussion on the final [composition](#2-4-composition) of the automata. Please note that the details on each operation will not be repeated for all components.

All the code discussed here can be found in the [system.h](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/tutorial/system.h?at=master) file of the repository.

## 2.1 - Tank

The automaton can be constructed with the following instruction:

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

To add the events to the automaton, we need to provide their I/O character:

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

The construction of the controller for the system start with the usual

```
HybridIOAutomaton controller("controller");
```
after which we can add the involved variables and events: 

```
controller.add_input_var(x);

controller.add_output_event(e_open);
controller.add_output_event(e_close);
```

Therefore, in opposition to the valve automaton, the controller "reads" a variable and "writes" events.

The two locations are created and added in the usual way:

```
DiscreteLocation rising("rising");
DiscreteLocation falling("falling");

controller.new_mode(rising);
controller.new_mode(falling);
```

Since no internal or output variable is present, we do not need to define any dynamics for this automaton.

Moving to transitions, we want to provide two non-urgent transitions, hence we need to define proper guards and invariants. Let's start with defining some parameters:

```
RealParameter hmin("hmin",5.75);
RealParameter hmax("hmax",7.75);
RealParameter delta("delta",0.1);
```
which represent the lower threshold for the water level $h\_{\min}$, the corresponding upper threshold $h\_{\max}$, and the "radius" of non-determinism $\delta$.

Let's define the invariant expressions for the locations:

```
RealExpression x_leq_hmax = x - hmax - delta;
RealExpression x_geq_hmin = hmin - delta - x;
```
where Ariadne works under the assumption that an invariant expression $i$ allows evolution as long as $i \leq 0$; consequently, invariant expressions are complementary in respect to guards, where $g \geq 0$ must hold in order to allow leaving the location. In particular, the two expressions above correspond to $x \leq h\_{\max} + \delta$ and $x \geq h\_{\min} - \delta$, respectively.

In order to add the invariants, we issue:

```
controller.new_invariant(rising, x_leq_hmax);
controller.new_invariant(falling, x_geq_hmin);
```

It must be noted that, while only one guard per transition is allowed, we support multiple invariants per location.

Guards are provided in the usual way:

```
RealExpression x_geq_hmax = x - hmax + delta;
RealExpression x_leq_hmin = hmin + delta - x;
```
which correspond to $x \geq h\_{\max} - \delta$ and $x \leq h\_{\min} + \delta$, respectively.

The transitions then become:

```
controller.new_unforced_transition(e_close, rising, falling, x_geq_hmax);
controller.new_unforced_transition(e_open, falling, rising, x_leq_hmin);		
```
where we clearly need to specify that the transition is *unforced*. In this case, the transition *can* be fired for any point $x$ such that $i(x) \leq 0$ and $g(x) \geq 0$, i.e., for the intersection between the *invariant set* and the *guard set*. If we used a forced transition instead, the transition would be fired only in the intersection between the invariant set and the boundary of the guard set. 

Finally, we note how we necessarily omit the reset when no internal or output variable is present.

## 2.4 - Composition

The Ariadne library currently supports only *horizontal* composition, meaning that two or more automata at the same level of abstraction can be composed to form a more complex automaton. Ariadne does not support vertical modularity in terms of different levels of abstraction and encapsulation. Consequently, we assume that all the automata are represented on a common "horizontal namespace" where all variable and event labels are shared.

Composition is performed between a pair of automata and returns a new automaton which is the product of the original components. When multiple automata must be composed, a progressive sequence of compositions is issued until the product of all the components is performed. Since composition is commutative, the product order is irrelevant.

In order to create the composed automaton of the tank and the valve:

```
HybridIOAutomaton tank_valve = compose("tank,valve",tank,valve,flow,idle);
```

The first argument is the name of the new automaton. The second and third arguments are the components to use, while the fourth and fifth arguments represent the initial locations for each component. Specifying an initial location is required if we want to optimise the resulting system, by creating a product with the actual reachable locations: the choice of the initial location may influence the discrete reachability and consequently the complexity of the system.

The complete system is obtained with:

```
HybridIOAutomaton system = compose("tutorial",tank_valve,controller,
                                   DiscreteLocation("flow,idle"),rising);
```

Here the `tutorial` name ends up overwriting the previous `tank,valve` name, meaning that choosing a specific name for an intermediate automaton is inconsequential.

An important remark on the construction of the initial location for the `tank,valve` component: the product between components implies that location names are combined, meaning that the order of components in the composition is relevant. However, please note that potential errors in the composition due to improper location naming are caught by the library during composition itself.

# 3 - System model analysis

In order to analyse a system in Ariadne, we must prepare an executable. For that reason, all the [examples](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/examples/?at=master) of the library have their own .cc file, usually paired with a .h file used to load the system under analysis.

In this tutorial we follow the convention of having a separate system header file, namely [system.h](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/tutorial/system.h?at=master). In addition, the analysis routines are kept in a dedicated [analysis.h](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/tutorial/analysis.h?at=master) file. These choices can be simply considered best practice and are not part of the Ariadne library itself. Hence they will not be examined in detail: the focus of this section is the content of the analysis functions, which are discussed in the next subsections.

But first of all let us examine the [tutorial.cc](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/tutorial/tutorial.cc?at=master) executable. To work with the Ariadne library it is necessary to start by including the top header for user consumption:

```c++
#include <ariadne.h>
```

followed by adding the system and analysis headers:

```c++
#include "system.h"
#include "analysis.h"
```

The content of the `main` function of the executable revolves around the collection of four items:

  1. The system to analyse;
  2. The initial set to use;
  3. The verbosity for runtime info;
  4. The flag for plotting graphical results.

The system object is loaded with

```c++
HybridIOAutomaton system = Ariadne::getSystem();
```

using a custom function created in the system header. If we want to output the textual description of the system, we can issue:

```c++
cout << system << endl;
```

which provides a compact representation useful for debugging purposes. No graph-based output capabilities are currently available in the library.

The initial set can be provided in different formats. For this tutorial we want to use a generic representation, i.e., a `HybridBoundedConstraintSet`. Such structure allows to specify a set for each location, thus allowing multiple initial sets. Namely:

```c++
HybridBoundedConstraintSet initial_set(system.state_space());
initial_set[DiscreteLocation("flow,idle,rising")] = 
            Box(2, 1.0,1.0, 6.0,7.5);
initial_set[DiscreteLocation("flow,idle,falling")] = 
            Box(2, 0.0,0.0, 6.0,7.5);
```

Here the first line constructs the set as empty, in the hybrid state space of the system. Then, we add sets for two specific locations. Specifically, we construct a `BoundedConstraintSet` from a simple `Box`, which is a coordinate-aligned set. In particular, the first argument of the constructor is the set dimension, while the remaining arguments are the lower and upper bounds for each variable, in alphabetical order. In other words, the continuous set is $\\{a = 1 \, \land \, 6 \leq x \leq 7.5 \\}$ in the *flow,idle,rising* location and $\\{a = 0 \, \land \, 6 \leq x \leq 7.5 \\}$ in the *flow,idle,falling* location.

The verbosity is a non-negative value that allows to show textual runtime information down to a given depth: the higher the value, the lower the depth. In particular, the current depth is prefix to each textual line. Since only a global verbosity variable exists, it is currently not possible to display information exclusively at a specific depth.

Finally, we comment on the ability to turn on or off the graphical output. Graphics are enabled for this tutorial, but for efficiency purposes it is possible to avoid the production of figures; indeed, they are disabled by default in the library. In general, figures are created as .png files under a directory called `<systemname>-png` (`tutorial-png` in this case) from the current working directory. Inside, each analysis produces a specific directory with a timestamp, in order to simplify the identification of the results of multiple runs.

## 3.1 - Evolution

For the routines in this subsection, we are simply interested in computing the reachable set, either for finite time or infinite time evolution.

### 3.1.1 - Finite time evolution

For this subsection, we refer to the `finite_time_upper_evolution` and `finite_time_lower_evolution` functions in the analysis file. Since they essentially differ only by the semantics used, we provide a `_finite_time_evolution` helper function that contains the bulk of the code for the interaction with the Ariadne library.

The first step is the creation of a `HybridEvolver` object, which provides methods for finite time evolution:

```c++
HybridEvolver evolver(system);
```

where the `system` argument is the automaton to evolve. The system is stored before evolution in order to check the consistency of user-provided evolution *settings*. Such settings can be found in the `ImageSetHybridEvolverSettings` class in [hybrid_evolver-image.h](https://bitbucket.org/ariadne-cps/release-1.0/src/HEAD/include/hybrid_evolver-image.h?at=master). For each setting, a default value is provided; also, multiple setter methods are available when useful for a simpler assignment.

The only mandatory setting in practice is the integration step size, which is set in this tutorial with:

```c++
evolver.settings().set_maximum_step_size(0.3);
```

Here the setting is called a *maximum* step size since in general the integration step must be small enough to allow the identification of a bounding box for the flow set. If the provided value does not guarantee such condition, the library internally halves the provided value until the value is acceptable. However, if the step size is reasonably small in respect to the dynamics, it is usually the case that a bounding box is identified with no halving.

Another relevant setting is the `reference_enclosure_widths` which informs the evolver about a particular width value on each dimension of the continuous space; such width should be chosen as proportional to the precision required on the given dimension when discretizing the reachable set. Here an "enclosure" is a name for an evolution set at a given time, which can also be seen as a section of the flow tube. The reference widths are meant to be constant for a given system. The `maximum_enclosure_widths_ratio` setting is then multiplied with the reference widths to decide if an enclosure is too large in respect to a desired numerical accuracy. If `enable_premature_termination_on_enclosure_size` is enabled (enabled by default), then evolution is stopped: this is useful to terminate when the set becomes too large to provide meaningful data for analysis. If `enable_subdivisions` is enabled (disabled by default), evolution continues but the set is split into two enclosures of smaller size.

The assignment of the verbosity is performed with

```
evolver.verbosity = verbosity;
```

where the default verbosity value is zero, i.e., no output is provided.

As soon as the evolver is set up, we can perform finite-time evolution by computing the *orbit* of the automaton. To call the `HybridEvolver::orbit` method we need three arguments:

  1. The initial set expressed as a *localised* enclosure;
  2. The evolution limits in terms of maximum continuous time and maximum number of discrete transitions;
  3. The *semantics* for evolution.

The initial set must be expressed as a localised enclosure, meaning a set paired with a discrete location. If we want to perform evolution for an initial set on two locations, like the one of the tutorial, we actually need to compute two separate orbits. In addition, the initial set that we provided is a hybrid constraint set. For these reasons, we provide the following code snippet for conversion:

```c++
HybridEvolver::EnclosureListType initial_enclosures;
HybridBoxes initial_set_domain = initial_set.domain();
for (HybridBoxes::const_iterator it = 
  initial_set_domain.locations_begin(); 
  it != initial_set_domain.locations_end(); 
  ++it) {
    if (!it->second.empty()) {
      initial_enclosures.adjoin(HybridEvolver::EnclosureType(
        it->first,Box(it->second.centre())));
    }
}
```

We remind here that code such as the above is not required when the initial set is already expressed as a `HybridEvolver::EnclosureType` instead.

The evolution time is provided as a `HybridTime`, which is a pairing of a continuous time and a discrete time:

```c++
HybridTime evol_limits(30.0,8);
```

Here we say that hybrid evolution may progress until 30 seconds of evolution are reached, or until 8 events are fired, whichever condition is met first.

Finally, the semantics in Ariadne is either `UPPER_SEMANTICS` or `LOWER_SEMANTICS`. Such difference essentially amounts to deciding whether a transition should be taken in the presence of approximations. Since Ariadne operates on over-approximated sets, if such a set partially crosses a guard, then it is not always decidable whether the exact set either completely crosses, partially crosses or does not cross at all. If that is the case, we want to provide two semantics of evolution: allow or disallow a spurious transition. In the first case of *upper semantics* we end up with an approximate reachable set which is a (possibly) unbounded over-approximation of the exact reachable set; in the second case of *lower semantics* instead we have a bounded over-approximation, where the bound is essentially the diameter of the flow tube. However, under lower semantics we may terminate evolution earlier, hence the over-approximation may be of a subset of the reachable set. In addition, lower semantics disallows subdivisions of a set, since in that case one of the two splits may not contain any point of the exact reachable set; if such split set then diverges in respect to the other split set, the bound on the over-approximation increases in an uncontrolled way.

Let's call the orbit method for each of the enclosures and each of the semantics, adjoining the reach sets of a given semantics to a common `HybridEvolver::EnclosureListType` data structure:

```c++
HybridEvolver::EnclosureListType reach;
for (HybridEvolver::EnclosureListType::const_iterator it = 
  initial_enclosures.begin();
  it != initial_enclosures.end(); 
  ++it) {
    HybridEvolver::OrbitType orbit = evolver.orbit(*it, 
                    evol_limits, semantics);
    reach.adjoin(upper_orbit.reach());
}
```

If we choose a verbosity value of 1, then for each call to `orbit` we see a long sequence of log lines, where each line provides information on one continuous step of evolution, e.g.:

```
[e:1] #w=6 #r=210 s=2 ps=3.000000e-01 t=15.250000 d=1.954768e-01 ...
```

Let's identify some of these values:

  - \#w: the number of working sets, i.e., of sets to be processed; this number usually increases after a transition, especially if non-urgent, or after a subdivision;
  - \#r: the number of currently reached sets;
  - t: the current time
  - d: the diameter of the set
  - l: the location
  - c: the center of the set
  - w: the width of the set on each dimension
  - e: the list of previously fired events

where the `[e:1]` prefix informs that this logging information is of verbosity level 1 for an evolver. Using a higher verbosity value would provide more detailed information, albeit with less clarity.

Finally we can plot the list of enclosures for each reach set with these commands:

```c++
PlotHelper plotter(system.name());
plotter.plot(upper_reach,"upper_reach");
```

where without lack of generality we focus on the upper reach case.

The `PlotHelper` class is a class able to plot the most relevant graphical outputs used by Ariadne routines. It is constructed with a single argument, which will be used as a prefix for the name of the directory containing the output files. The second argument to the `plot` method instead is a prefix for the filenames.

![upper-reach](/img/upper-reach.png "Finite time upper evolution")

In the figure above, the upper evolution of the system is shown. The horizontal axis is for the valve aperture coordinate $a$, while the vertical axis is for the water level coordinate $x$; the extreme values for each axis are displayed. In the general case of more than two system variables, Ariadne creates a figure for each pair of variables, ordered alphabetically. In this specific case, we see that the behavior of the system is cyclic (counterclockwise), with the following four phases:

  1. The valve is closed, $x$ falls (left part of the figure)
  2. The valve opens with a finite time, $x$ ultimately starts rising (bottom part)
  3. The valve is fully opened, $x$ rises (right part)
  4. The valve closes with a finite time, $x$ ultimately starts falling (top part)

The top and bottom bands are due to non-determinism caused by the non-urgent transitions. 

On this matter, let us compare this figure with the one for lower semantics.

![lower-reach](/img/lower-reach.png "Finite time lower evolution")

In the case of lower semantics, sometimes the activation of a non-urgent transition is not decidable, due to the fact that only a part of the set performs the crossing. For that reason, a significant percentage of the sets is discarded. This situation is apparent from the thinner bands in respect to upper semantics. It can also be detected if we analyse the log output during evolution, where the number of working sets is significantly higher for upper semantics. Ultimately, given the initial set it is still possible to complete a full cycle even for lower semantics, but that result is not always guaranteed based on the numerical settings chosen.

### 3.1.2 - Infinite time evolution

For this subsection, we refer to the `infinite_time_outer_evolution` and `infinite_time_epsilon_lower_evolution` methods, which mostly differ by the semantics used. We will present these methods after discussion of the common part of the analysis procedure.

In infinite time evolution, we perform a sequence of finite time evolutions until *convergence* is obtained, i.e., the reached set does not grow anymore between two evolutions. Since there is no guarantee that convergence is obtained for a given accuracy, or that convergence is possible for the system, we introduce a *bounding domain* expressed as a hybrid box:

```c++
HybridBoxes domain(system.state_space(),Box(2,0.0,1.0,4.5,9.0));
```
which corresponds to $0 \leq a \leq 1$ and $4.5 \leq x \leq 9$ for all locations.

In addition, it is necessary to choose an *accuracy* setting, which is a non-negative number. First of all, the accuracy defines the amount of times we split the domain in order to discretise the space. Discretization is necessary in order to perform an efficient and effective identification of the termination condition for infinite time evolution (both in the outer and lower evolution). Such discretization is also used internally to automatically identify proper settings for the underlying finite time evolutions.

For this reason, infinite time evolution is performed from a `HybridReachabilityAnalyser` class, which masks the internal use of evolver object(s). In order to construct an analyser, we issue:

```c++
HybridReachabilityAnalyser analyser(system,domain,accuracy);
```

where for the purposes of the tutorial we set

```c++
int accuracy = 5;
```

which means that the domain is split $2^5 = 32$ times its nominal amount for each dimension; since for zero accuracy we split the domain once, we end up with discretization "cells" of widths $1/64$ and $4.5/64$, respectively for $a$ and $x$.

As with the evolver, an analyser can be configured with a verbosity. In particular, if the verbosity depth is sufficiently high, then the logging of the internal evolver methods is performed.

In addition, an analyser has a `HybridReachabilityAnalyserSettings` object that can be accessed using `analyser.settings()`, as with the evolver case. However, most of these settings are used internally when performing verification on the system, hence they will not be discussed here. The only setting that has a significant relevance for the user is the `enable_lower_pruning` flag (true by default). For lower semantics only, the flag enables the elimination of overlapping trajectories, increasing the efficiency of the procedure. We remind here that for upper semantics we are not allowed to remove behaviors of the system. Such setting is not offered at the evolver level for a simple reason: the identification of the overlapping condition is more viable when we have a discretization of the continuous space, which is performed only at the analyser level. Finally, we should remark that pruning is performed stochastically, hence results may vary between different runs of the same method.

Let us now present the methods discussed here: the calculation of the *outer reachability* $O$ and the *epsilon-lower reachability* $L\_{\varepsilon}$ approximations of the exact reachable set $Re$:

  - $O$ is an over-approximated set such that $O \supset Re$. Since we want to include any possible behaviors (i.e., trajectories) produced by the evolution of the system, upper semantics is used.
  - $L_{\varepsilon}$ is an over-approximated set such that $\exists\, x \in Re \,\,s.t.\, || x - L\_{\varepsilon}  || \leq \varepsilon $; in other terms, we guarantee that the approximation is within a bounded distance $\varepsilon$ to the reachable set. In order to guarantee such bound, lower semantics is used. Since lower semantics may cause early termination of the evolution, we have that $L\_{\varepsilon}$ is an over-approximation of a *subset* of $Re$, which is different from an inner approximation $I$ such that $I \subset Re$.

In order to compute $O$ in the `infinite_time_outer_evolution` function, we issue

```c++
HybridDenotableSet reach = analyser.outer_chain_reach(initial_set);
```
where a `HybridDenotableSet` is simply a set of cells, where each cell is enriched with the discrete location involved. Denotable sets in Ariadne are currently implemented though Binary Decision Diagrams for efficiency purposes.

As usual, we can plot the resulting set using a `PlotHelper`, namely:

```c++
plotter.plot(reach,"outer",accuracy);
```

Here we show that it is possible to provide an additional argument, given by an integer value, that is used to extend the filename. This option is useful during verification, where a progressive increase of the accuracy is performed until an answer is obtained. In that case, we are able to output several graphical files within the same directory, where each one is named uniquely based the accuracy used.

Additionally, this variant of the plot method provides all the projections of the set on each location. 

![outer-reach](/img/outer-reach.png "Infinite time outer evolution at accuracy 5")

In the figure above we can see the reached set, which can be compared with the one obtained for finite time evolution. The most relevant difference is that discretisations occur after *each transition* and after a given continuous evolution time; after such discretisation, the current set is compared with the set on the previous discretisation in order to identify if no cells are reached. A total of 16 discretisation are performed before this condition is met, as can be seen if we set a verbosity of 2. Discretisations necessarily increase the width of the flow tube, which is apparent on the right side of the figure: this is the section where the dynamics is the slowest, hence more discretisation events occur. The "artifacts" on the top right and bottom left corners of the figure are due to discretisation error; while quite relevant at accuracy 5, it can be shown for accuracy 7 to reduce their overall impact, thus shrinking to zero for infinite accuracy.

![outer-reach-7](/img/outer-reach-7.png "Infinite time outer evolution at accuracy 7")

Both discretised outer reach sets seem quite coarse in respect to the finite time case. While this is the case for flow tubes with very small diameter, for large tubes the opposite holds: just look at the extreme value for $x$ for finite time: even if only one cycle has been performed, it is already coarser than the result obtained for infinite time at accuracy 5. This is due to the fact that discretisation allows to efficiently split the set and work on smaller enclosures, which yield better bounds and consequently a tighter reached set overall. Such splitting without discretisation would be possible, but it would be less effective and more expensive from the computational viewpoint.
Summarizing, discretisations enable manipulations of the flow tube that, while introducing over-approximations, improve the efficiency and effectiveness of the procedure for large flow tubes.

## 3.2 - Verification

### 3.2.1 - Safety verification

### 3.2.2 - Parametric safety verification