---
title: 'Learning Simulator: A simulation software for associative learning'
tags:
  - Python
  - associative learning
  - reinforcement learning
  - behavior
  - mathematical model
  - simulation
  - gui
authors:
  - name: Markus Jonsson
    orcid: 0000-0003-1242-3599
    affiliation: 1  # (Multiple affiliations must be quoted)
  - name: Stefano Ghirlanda
    orcid: 0000-0002-7270-9612
    affiliation: "1, 2"
  - name: Johan Lind
    orcid: 0000-0002-4159-6926
    affiliation: 1
  - name: Magnus Enquist
    orcid: ????-????-????-????
    affiliation: 1
affiliations:
 - name: Centre for Cultural Evolution, Stockholm University, Stockholm, Sweden
   index: 1
 - name: Department of Psychology, Brooklyn College and Graduate Center, CUNY, New York, NY, USA
   index: 2
date: 4 November 2020
bibliography: paper.bib
---

# Summary

Learning Simulator is a software for simulating learning phenomena governed by
associative learning. It is written in Python and can be run either in a graphical
user interface, or from a system command prompt. 
Our software is primarily targeted to computational and behavior biologists, ethologists,
and psychologists, however students/teachers who learn/teach learning phenomena may also
find it useful.

# Introduction

In associative learning (AL) theory, a subject interacts with an environment.
The environment present a stimulus to the subject, and the subject responds
with a behavior. As a result, the environment presents the next stimulus
that the subject responds to, and so on.

The subject and the world can be seen as two interacting dynamical systems,
where the state variables in the subject determines the probabilities for
its responses (output), and each response from the subject puts the environment
in a state that determines its output stimulus. It is this system that is
simulated in Learning Simulator. See \autoref{fig:system-fig}.

![The subject and the environment are two interacting dynamical systems.\label{fig:system-fig}](system-fig.png)

After each response, the subject is presented with the next stimulus. This stimulus has a 
reinforcement value (typically a "reward" or "punishment") that the subject receives
which gives it an indication of the quality of that response. 
This is accomplished by the learning mechanism updating one or more of
the subject's memory state
variables, for example the associative strength between a stimulus
and its response. 
<!---
the behavior with which the subject responded.
-->
The values of these state variables control the
probabilities of future responses.

The user of Learning Simulator specifies in a text-based script how the next
stimulus depends on the subject's response to the previous stimulus.
<!---
Conversely, `Learning Simulator` also implements the stochastic decision
function that determines how the subject's response depends on the presented
stimulus.
-->
This script also specifies the values of all parameters used
in the learning process.
The simultion script, written in a well-documented scripting language,
is the only input to Learning Simulator. In this language,
the user also specifies how to visualize or export the simulation data,
for example how a memory state variable changes over time during the simulation.

# Associative learning mechanisms

During the last decade or so, AL has proven to be more powerful than earlier thought.
Firstly, AL mechanisms have been used in artificial intelligence,
for example to teach computers to find optimal play and achieve human
level skills in chess [@Silver:2017] and the Chinese board game Go [@Silver:2016].

Secondly, behaving optimally (or near-optimally) is central to animals' adaptation
to their environment. Thus, AL can also provide explanations for a wide range of
learning phenomena in biological systems (both human and non-human
animals), for example Pavlovian (classical) and operant (instrumental) conditioning,
misbehavior and genetic predispositions, and social learning [@Enquist:2016].

Moreover, AL theory underpins some of the most successful applications
of psychology to animal welfare and training [@Mcgreevy:2011], and to
human health [@Bernstein:1999; @Haselgrove:2013; @Schachtman:2011].

The ability of AL algorithms to be able to search for optimal policies using
low-variance gradient estimates has made them useful in several real-life
applications, such as robotics, power control, and finance [@Grondman:2012].

# Statement of need

The wide range of application areas of AL has given rise to a need
for a general simulation software for simulating different AL mechanisms.
The aim of our software is to fulfil this need.
The fast development of computing power has drastically improved the possibility
for this type of simulations.

The main advantage of our software lies in its flexibility. It is designed with \autoref{fig:system-fig}
in mind, seeing the system being simulated as two interacting dynamical systems,
making it generally applicable to the different areas where associative learning plays a role.

Apart from its flexibility, Learning Simulator's simple scripting language provides a way to easily investigate
the properties of different learning mechanisms and the effects of varying their properties, such as
exploration, learning rate coefficients, initial state variable values, etc. 

Another strength of Learning Simulator lies in the simplicity to specify even complex
environments with which the subject interacts. The scripting language has been
developed to be available to any researcher of learning phenomena -- not necessarily
computer programmers. This turns it into a useful research tool for biologists and
psychologists.

<!---
, which enables scientific exploration of learning phenomena by students
and experts alike.
-->

Our software has been
used in scientific publications [@Enquist:2016; @Lind:2018; @Lind:2019]
as well as in teaching, 
both at the Ethology Master's Programme at Stockholm University, and
at the Veterinary Programme at the Swedish University of Agricultural Sciences.

<!---
Our software can also potentially be applied to animal welfare in terms of experiment planning,
and understanding/avoiding stereotypic behavior,
as well as in clinical psychology in terms of planning of treatments for phobias, for example.

An open source license as well as its accessibility recommend `Learning Simulator` as a practical tool for biology, ethology, and
psychology students
enables scientific exploration of learning phenomena by students
and experts alike.
-->

An open source license as well as its accessibility enables further scientific exploration of learning phenomena by students
and experts alike within the fields of biology, ethology, and psychology.

The program is written in Python, using the standard Python package `Tkinter` for its graphical user iterface, and `Matplotlib` [@Hunter:2007]
for plotting simulation results.
In terms of quality assurance, test-driven development has been employed, and
our repository incorporates Travis CI alongside Coveralls code coverage measurement of the program's test suite.

<!---
 finding the balance between exploration and exploitation, time to convergence,
 been used in animal learning studies
 to explain flexible behavior in non-human animals.
 A wide range of learning phenomena
-->

<!---
# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"
-->

# Acknowledgements

We acknowledge valuable contributions from Vera Vinken during the development of this project.


# References
