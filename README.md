# Learning Simulator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Build status

![Build](https://github.com/markusrobertjonsson/lesim2/workflows/Learning%20Simulator/badge.svg)
[![Read the Docs](https://readthedocs.org/projects/learningsimulator/badge/?version=latest)](https://learningsimulator.readthedocs.io/en/latest/?badge=latest)

# Summary

*Learning Simulator* is a software for simulating learning phenomena governed by
associative learning. It is written in Python and can be run either in a graphical
user interface, or from a system command prompt. The input to the program is a
text-based script in a simple scripting language.
Our software is primarily targeted to computational and behavior biologists, ethologists,
and psychologists, however students/teachers who learn/teach learning phenomena may also
find it useful.

# Introduction

Associative learning (AL) is the process by which a subject learns contingency
relations, either between pairs of stimuli (classical or Pavlovian conditioning),
or between stimulus-behavior pairs (operant or instrumental conditioning).

The formalization of AL that is used in Learning Simulator and
that captures both classical and operant conditioning
comprises a subject that interacts with an environment.
The environment presents a stimulus to the subject, and the subject responds
with a behavior. As a result, the environment presents the next stimulus
that the subject responds to, and so on. See Figure 1.

<!---
![The subject and the world can be seen as two interacting dynamical systems,
where the state variables in the subject determines the probabilities for
its behaviors (the subject's output), and each behavior from the subject puts the environment
in a state that determines its output stimulus. It is this system that is
simulated in Learning Simulator.
\label{fig:system-fig}](system-fig.png)
-->
<img src="system-fig.png" width="505" height="339" />

**Figure 1: The subject and the world can be seen as two interacting dynamical systems,
where the state variables in the subject determines the probabilities for
its behaviors (the subject's output), and each behavior from the subject puts the environment
in a state that determines its output stimulus. It is this system that is
simulated in Learning Simulator.**

Each stimulus has a reinforcement value (which is genetically determined for
biological subjects). A rewarding stimulus (e.g. food) would typically have
positive value, while a stimulus representing harm to the body ("punishment")
would have a negative value.

As per Figure 1, after the response *B* to a stimulus *S*, the subject is presented with the next stimulus *S'*:

*S* -> *B* -> *S'*.

Thus, as a consequence of responding with behavior *B* to *S*, the subject meets
the stimulus *S'*.
The reinforcement value of *S'* gives the subject an indication of the quality of the response *B* to *S*. 
Specifically, this is accomplished by the learning mechanism updating one or more of
the subject's memory state
variables. In the case of operant conditioning, these include the associative strength between the stimulus *S*
and its response *B*. 
The values of these state variables control the
probabilities of future responses. For example, if the response *B* to stimulus *S*
leads to a reward (a stimulus with high reinforcement value), the subject will be more likely to respond with *B* the next
time it faces *S*.

The user of Learning Simulator specifies in a text-based script how the output
stimulus from the environment depends on the subject's response to the previous stimulus.
This script also specifies the values of all parameters used
in the learning process.
The simulation script, written in a simple and well-documented scripting language,
is the only input to Learning Simulator. In this language,
the user also specifies how to visualize the simulation data,
for example how a memory state variable changes over time during the simulation.
Learning Simulator also includes a functionality to export the results to a
data processor spreadsheet.
