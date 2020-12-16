

# Rationale

-   The Tolman mechanism implements a learning mechanism that formalizes
    &ldquo;latent-learning&rdquo; and &ldquo;cognitive map&rdquo; models in animal cognition.
-   The animal is assumed to build a mental model of its environment.
-   The model is then used to plan how to reach states with high value.
-   There are major computational challenges in such a mechanism and it
    is unlikely that animals (or even people) can apply this strategy
    in cases beyond a certain complexity.
-   We restrict the mechanism to work in worlds with a single goal, and
    that &ldquo;restart&rdquo; after the goal is obtained.


# Variables

-   The Tolman mechanism learns \(S\to B\to S'\) transition
    probabilities.
-   These estimates are called \(z(S,B,S')\).
-   Everything else is decided when responding.


# Learning

-   There is a single learning rate, \(\alpha_z\).

-   Imagine first that all stimuli are made of a single element. When
    \(S\to\ B\to S'\) is observed, \(z(S,B,X)\) is updated for all
    \(X\) as follows:
    
    where \(\lambda_{X}=1\) when \(X=S'\) (the state that actually
    occurred), and 0 for all other states.

-   With sufficient experience and sufficiently small \(\alpha_z\),
    <eq:sbs-update> will converge to the actual transition
    probabilities.

-   How to extend to stimuli with more elements? Let&rsquo;s first consider
    that all intensities are \(=1\). We can use
    
    where the \(S_i\) are the elements of \(S\) and the \(S_j'\) the elements
    of \(S'\). According to <eq:sbs-multi>, different elements of \(S\)
    compete for predicting each element of \(S'\) in the same way as they
    would compete for accruing \(v\) or \(w\) values in A-learning (and
    other mechanisms).

-   Using <eq:sbs-multi> to calculate \(z(S_i\ldots S_n,B,S_i')\) we can
    update each \(S_i\) as follows:
    
    where \(\lambda=1\) if \(X\in S'\) and \(\lambda=0\) otherwise.

-   With intensities written as \(x\) we can use:


## Trial implementation <span class="timestamp-wrapper"><span class="timestamp">&lt;2020-12-07 Mon&gt;</span></span>

-   The equations above have been implemented in the `github` branch
    `tolman-mechanism`

-   I have made a super simple test where there is only behavior \(B\) and
    two stimuli \(S_1\) and \(S_2\)), and the only thing that happens is the
    sequence:

-   In this case, the Tolman mechanism should learn:

-   Printing this values throughout the simulation shows that they are
    in fact learned, but the graphs do not come out well. I think this
    is because the current plotting code only updates the plot for
    stimulus elements that are actually presented, but the Tolman
    mechanism also updates \(z(S,B,S')\) for \(S'\) elements that are not
    present. For example, this is a graph I get:

<./first-try.pdf>

-   The initial values of all \(z\) is 0.1 for testing purposes. The blue
    line goes to 1 as it should. The orange is plotted at the initial
    0.1 throughout the simulation, but for the last point, which is the
    correct value of 0. As I mentioned above, however, if I print the
    values during learning I do see that they are decreasing toward 0
    all the time.

-   (Element intensities and multiple elements are implemented but not
    tested yet.)


# Responding

-   Responding assumes that the world model in \(z\) is true.

-   Responding should then make the &ldquo;best plan&rdquo; given this
    knowledge.

-   What we need to decide is actually the first step of the plan. We do
    this assigning a \(v\) value to each behavior so that we can keep the
    same decision-making mechanimsm.

-   Evaluating all possible plans is tricky in general. Let&rsquo;s work with
    a particular kind of world to begin with:
    1.  There is only one valued stimulus, called the goal.
    2.  When the goal is reached, the next state is determined by the
        world using a fixed rule (deterministic or stochastic).

-   The second condition means that we need to consider just how to
    reach the goal once, since after that the world &ldquo;resets&rdquo; to a
    statistically equivalent state.

-   The first step is to find all paths to the goal. We start from the
    goal and we go backwards along possible transitions, that is, all
    transitions with \(z>0\) for some \(B\). If we eventually reach the
    current state, we store the sequence of transitions and call it a
    &ldquo;path.&rdquo;

-   We calculate the expected *rate* of return for all paths to the
    goal, that is the expected value divided the path length (number of
    actions):

-   In <eq:path-value>, the sum is over all behaviors in the path,
    \(l_\mathrm{path}\) is path length, and the product is over all
    transition probabilities in the path. (This is the probability that
    the plan will succeed.)

-   We then give a value to each behavior that is feasible in response
    to the current stimulus. If the behavior is the first step on a path
    to the goal, its value is the \(v\) value of the goal. If it is not,
    its value is `start_v`.

-   If a behavior is the first on more than one path, we can average the
    \(v\)&rsquo;s using the success probability of each path, so we should store
    these somewhere.

-   We then use softmax to choose a behavior.

