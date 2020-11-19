---
title: 'Learning Simulator: A simulation software for animal and human learning'
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
  - name: Vera Vinken
    affiliation: 3
  - name: Magnus Enquist
    affiliation: "1, 4"

affiliations:
  - name: Centre for Cultural Evolution, Stockholm University, Stockholm, Sweden
    index: 1
  - name: Department of Psychology, Brooklyn College and Graduate Center, CUNY, New York, NY, USA
    index: 2
  - name: Biosciences Institute, Newcastle University, Newcastle upon Tyne, United Kingdom
    index: 3    
  - name: Department of Zoology, Stockholm University, Sweden
    index: 4
date: 4 November 2020
bibliography: paper.bib
---

<!---  - name: Center for Behaviour and Evolution, Newcastle University -->

# Summary

Learning Simulator is a software for simulating learning in animals
and humans, as studied for example in experimental psychology and
animal cognition research.  It is primarily intended for computational
and behavioral biologists, ethologists, and psychologists, and it can
also be useful to students and teachers in these fields.

<!--
  The input to the program is a text-based script in a simple scripting language.
. It is written in Python and can be run either in a graphical
user interface, or from a system command prompt. 
-->

# Introduction

<!---
Associative learning is the ability of organisms to acquire knowledge about environmental contingencies between stimuli, responses, and outcomes
-->

Learning Simulator was developed to study learning in animals and humans. The current version implements associative learning (AL) and reinforcement learning (RL) algorithms, apt to study instrumental (operant) learning and Pavlovian (classical) learning [@Pearce:2013; @Bouton:2016], including in complex situations such as social learning or maze learning. A plugin system to add more learning mechanisms is planned for a future version.

<!--- Here we formalize associative learning experiments.-->
The simulator uses a commonly used framing of learning that
<!---that captures both classical and operant conditioning-->
comprises a subject interacting with an environment.
The environment presents a stimulus to the subject, and the subject responds
with a behavior. As a result, the environment presents the next stimulus
that the subject responds to, and so on. See \autoref{fig:system-fig}.

<!---
![The subject and the environment are two interacting dynamical systems.\label{fig:system-fig}](system-fig.png)
-->

![The subject and the world can be seen as two interacting dynamical systems,
where the state variables in the subject determine the probabilities for
its behaviors (the subject's output), and each behavior from the subject puts the environment
in a state that determines (probabilistically) its output stimulus.
<!---It is this system that is
simulated in Learning Simulator.-->
\label{fig:system-fig}](system-fig.pdf)

The stimuli that the environment presents and the behaviors that the subject
can exhibit are pre-defined by the user of the program.
Each stimulus is given a reinforcement value (corresponding to genetically determined values in
biological organisms). A stimulus such as food would typically have a
positive value, while the perception of harm to the body
would have a negative value.

As seen in \autoref{fig:system-fig}, 
the consequence of responding with a behavior (say $B$) to a stimulus (say $S$) is that the subject meets
the next stimulus (say $S')$:
<!---
after a response (say $B$) to a stimulus (say $S$), the subject is presented with the next stimulus (say $S')$:
-->
\begin{equation}
    S \to B \to S'. \nonumber
\end{equation}
Learning algorithms can then use the reinforcement value of $S'$ as an indication of the quality of the response $B$ to $S$. 
Specifically, this can be accomplished by 
<!--- the learning mechanism --> 
updating one or more of the subject's memory state
variables.
<!---
For example, in operant conditioning these may include the associative strength between the stimulus $S$
and the response $B$. 
-->
These state variables control the
probabilities of future responses: if the response $B$ to stimulus $S$
leads to a reward (a stimulus with high reinforcement value), the subject will be more likely to respond with $B$ the next time it faces $S$.

The user of Learning Simulator specifies in a text script how the output
stimulus from the environment depends on the subject's response to the previous stimulus.
<!---
Conversely, `Learning Simulator` also implements the stochastic decision
function that determines how the subject's response depends on the presented
stimulus.
-->
This script also specifies the values of all parameters used
in the learning process.
The simulation script, written in a simple and well-documented scripting language,
is the only input to Learning Simulator, facilitating reproducible workflows. The script also specifies how to visualize the simulation data,
for example how a memory state variable changes during the simulation.
Learning Simulator can also export results to CSV files.

More information is available at https://www.learningsimulator.org.

# Applications of associative learning

Associative learning theory has a rich tradition of computational modeling, which has recently converged with RL learning models from machine learning [@Sutton:2018].
During the last decade or so, AL and RL algorithms have proven increasingly powerful.
<!-- ,
as a fair amount of research in
the field has been directed toward the development
of different mathematical models, *learning mechanisms*.
-->

Firstly, when applied to deep neural networks, 
<!---Firstly, RL mechanisms have been used in artificial intelligence (where the subject is
a virtual computer agent),
-->
RL has been used 
to teach computers to find optimal play and achieve human-level
skills in chess [@Silver:2017] and the Chinese board game Go [@Silver:2016].

Secondly, behaving optimally (or near-optimally) is central to animals' adaptation
to their environment. AL and RL can provide explanations for a wide range of
learning phenomena in 
<!---biological systems, 
-->
both humans and 
animals [@Niv:2009; @Dayan:2008; @Enquist:2016; @Ghirlanda:2020].
<!---
, for example tool use, social learning, 
misbehavior, and
social learning [@Enquist:2016], and the learning of behavior sequences
[@Ghirlanda:2017].
-->
Indeed, investigating predictions about animal and human behavior is the main motivation behind Learning Simulator,
with the goal to understand biological learning and its numerous applications to animal welfare and training
[@Mcgreevy:2011], and to human health [@Bernstein:1999; @Haselgrove:2013; @Schachtman:2011].

<!-- STEFANO: I would take this out because it is not clear that Learning Simulator is relevant to these applications

Lastly, the ability of AL algorithms to search for optimal policies using
low-variance gradient estimates has made them useful in several other real-life
applications, such as robotics, power control, and finance [@Grondman:2012].

-->

# Statement of need

As a result of a strong theoretical tradition, and of the many
application areas, there are now many AL and RL models with varying
properties and varying predictive power in different environments.

<!---The wide range of application areas and the various mechanisms-->

This situation has created a need
for a general simulation software offering a convenient way to investigate different learning models.
The first aim of our software is to fulfil this need.

The second aim is to provide a generic, flexible
way to describe unambiguously the design of learning experiments or, more generally, the features of any learning scenario.

<!---The fast development of computing power has drastically improved the possibility
for this type of simulations.
-->

<!---The main advantage of our software lies in its flexibility. It is designed with \autoref{fig:system-fig}
in mind, seeing the system being simulated as two interacting dynamical systems,
making it generally applicable to the different areas where associative learning plays a role.
-->

The main advantage of Learning Simulator is its simple scripting language that
provides a way to explore and understand learning mechanisms in a multitude of learning scenarios, and investigate
the effects of varying their underlying parameters.

<!---properties, bysuch as
exploration, learning rate coefficients, initial values of state variables, etc. -->

A further strength is the simplicity with which even complex learning
environments can be specified, such as psychological experiments with complex dependencies between stimuli and behaviors.
The scripting language has been developed to be useful to any researcher of learning phenomena -- not necessarily
computer programmers. 

<!--This turns it into a useful research tool for biologists and
psychologists.
-->

<!---
, which enables scientific exploration of learning phenomena by students
and experts alike.
-->

<!---
With the simulator, opportunities for simulation
and assessment of associative learning mechanisms are easily available,
in this
way, we hope that Learning Simulator will facilitate evaluating and
comparing different associative learning theories, 
thereby
helping gain a deeper understanding of the processes and
representations involved.
-->
Our software has been
used in scientific publications [@Lind:2018; @Lind:2019; @Ghirlanda:2020]
as well as in teaching at the Ethology Master's Programme at Stockholm University, 
at the Veterinary Programme at the Swedish University of Agricultural Sciences, and at the Department of Psychology of Brooklyn College, City University of New York.

<!---
Our software can also potentially be applied to animal welfare in terms of experiment planning,
and understanding/avoiding stereotypic behavior,
as well as in clinical psychology in terms of planning of treatments for phobias, for example.

An open source license as well as its accessibility recommend `Learning Simulator` as a practical tool for biology, ethology, and
psychology students
enables scientific exploration of learning phenomena by students
and experts alike.
-->

An open source license and an accessible scripting language enable further scientific exploration of learning phenomena by students and experts alike within the fields of biology, ethology, psychology, and neuroscience.


# State of the field

Other simulating software either specialize in one specific
mechanism [@Schultheis:2008_1; <!--- Harris model -->
@Alonso:2012; <!---  (Rescorla-Wagner),-->
@Schultheis:2008_2]  <!---  (only Rescorla-Wagner with compound stimuli),  -->
or only include models of classical conditioning [@Harris:2010; @learnSim; @Thorwart:2009],
<!---(where the latter is not maintained),-->
or provide only one learning algorithm or environment [@QLSim].

Learning Simulator provides a common interface to several AL and RL algorithms:

- *Stimulus-response learning* [@Bush:1951],
- *Rescorla-Wagner* [@Rescorla:1972],
- *Actor-critic* [@Witten:1977; @Sutton:2018],
- *Q-learning* [@Watkins:1989; @Watkins:1992],
- *Expected SARSA* [@vanSeijen:2009], and
- *A-learning* [@Ghirlanda:2020]

facilitating direct comparison of these mechanisms. <!-- STEFANO: I think we said this in the previous section Moreover, the flexible environment definition allows the generation of meaningful
experiment designs and discrimination tasks. -->

# Repository

The program is written in Python and its source code repository is hosted on GitHub. 
<!---
It uses the standard Python package `Tkinter` for its graphical user interface, and `Matplotlib` [@Hunter:2007]
for plotting simulation results. 
-->
Its documentation is
<!---generated using `Sphinx` and-->
hosted on Read the Docs.
<!---In terms of quality assurance, 
test-driven development has been employed, and-->
The repository incorporates 
<!---Travis CI alongside Coveralls code coverage measurement of the program's test suite.-->
continuous integration with automatic build of the documentation, linting, 
<!---with `Flake8`-->and
execution of a test suite along with code coverage measurement.
<!---with `Coverage.py`. (https://coverage.readthedocs.io). -->

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

<!---
# Road map

Making the software ever more readily available with a web interface.

Adding an alternative, even more easy-to-use (however less flexible) graphical user interface (GUI) to the scripting language.

Make it easier to add custom learning mechanisms.
-->

# Acknowledgements

Research and development was supported by the Knut and Alice Wallenberg Foundation (2015.0005).

<!---
  We acknowledge valuable contributions from Vera Vinken during the development of this project.
-->

# References
