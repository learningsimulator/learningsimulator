from math import exp
from random import seed, random, choice

import keywords as kw
from util import dict_inv, ParseUtil

import math

seed()


class Mechanism():
    '''Base class for mechanisms'''

    def __init__(self, parameters):
        self.parameters = parameters
        # parameters.scalar_expand()
        self.trace = self.parameters.get(kw.TRACE)
        self.use_trace = (self.trace != 0)

        if self.use_trace:
            self.stimulus_intensities = {s: 0 for s in parameters.get(kw.STIMULUS_ELEMENTS)}
            self.prev_stimulus_intensities = dict(self.stimulus_intensities)
        else:
            self.stimulus_intensities = None
            self.prev_stimulus_intensities = None

        self.v = None
        self.w = None
        self.prev_stimulus = None
        self.response = None

        # Make self.stimulus_req
        self.stimulus_req = dict_inv(parameters.get(kw.RESPONSE_REQUIREMENTS))

        self.subject_reset()

    def subject_reset(self):
        self.v = dict(self.parameters.get(kw.START_V))
        self.w = dict(self.parameters.get(kw.START_W))
        self.prev_stimulus = None
        self.response = None

        if self.use_trace:
            self._reset_trace()

    def foo_reset_trace(self, stimulus=None):
        for s in self.stimulus_intensities:
            if (stimulus is not None) and (s in stimulus):  # Keep intensities for the elements in stimulus
                self.stimulus_intensities[s] = stimulus[s]
            else:
                self.stimulus_intensities[s] = 0
        for s in self.prev_stimulus_intensities:
            self.prev_stimulus_intensities[s] = 0

    def _reset_trace(self, stimulus=None):
        for s in self.stimulus_intensities:
            self.stimulus_intensities[s] = 0
        for s in self.prev_stimulus_intensities:
            self.prev_stimulus_intensities[s] = 0

    def _decay_stimulus_intensities(self, stimulus):
        '''stimulus is a dict.'''
        for e in self.stimulus_intensities:
            self.stimulus_intensities[e] *= self.trace
        for e in stimulus:
            self.stimulus_intensities[e] += stimulus[e]

    def learn_and_respond(self, stimulus, omit=False):
        '''stimulus is a dict.'''
        if self.use_trace:
            self._decay_stimulus_intensities(stimulus)

        if (self.prev_stimulus is None) or omit:  # Do not update if first time or if omit
            pass
        else:
            if self.use_trace:
                self.learn_i(stimulus)
            else:
                self.learn(stimulus)

        self.response = self._get_response(stimulus)

        # if self.use_trace and omit:
        #     # XXX Should be a separate @cleartrace or something that triggers
        #     # this reset (separate from "omit learning")
        #     self._reset_trace(stimulus)

        self.prev_stimulus = dict(stimulus)  # dict ok?
        if self.use_trace:
            for s in self.parameters.get(kw.STIMULUS_ELEMENTS):
                self.prev_stimulus_intensities[s] = self.stimulus_intensities[s]

        return self.response

    def learn(self, stimulus):
        # Must be overridden
        raise NotImplementedError

    def learn_i(self, stimulus):
        mechanism_name = self.parameters.get(kw.MECHANISM_NAME)
        raise NotImplementedError(f"Trace not implemented in mechanism '{mechanism_name}'.")

    def _get_response(self, stimulus):
        x, feasible_behaviors = self._support_vector(stimulus)
        q = random() * sum(x)
        index = 0
        while q > sum(x[0:index + 1]):
            index += 1
        return feasible_behaviors[index]

    def _support_vector(self, stimulus):
        behaviors = self.parameters.get(kw.BEHAVIORS)
        beta = self.parameters.get(kw.BETA)
        mu = self.parameters.get(kw.MU)
        return support_vector_static(stimulus, self.stimulus_intensities, behaviors,
                                     self.stimulus_req, beta, mu, self.v)

    def check_compatibility_with_world(self, world):
        return True, None, None  # To be overridden where necessary

    def has_v(self):
        return True

    def has_w(self):
        return False

    def has_vss(self):
        return False

    def has_x(self):
        return False

    def has_y(self):
        return False

    def has_z(self):
        return False


# This cache doesn't seem to speed things up.
# feasible_behaviors_cache = dict()
def get_feasible_behaviors(stimulus, behaviors, stimulus_req):
    if not stimulus_req:  # If stimulus_req is empty
        return list(behaviors)  # XXX conversion to list expensive?

    # if stimulus in feasible_behaviors_cache:
    #     return feasible_behaviors_cache[stimulus]

    feasible_behaviors = list()
    for element in stimulus:
        for b in stimulus_req[element]:
            if b not in feasible_behaviors:
                feasible_behaviors.append(b)
    # feasible_behaviors_cache[stimulus] = feasible_behaviors
    return feasible_behaviors


def support_vector_static(stimulus, internal_intensities, behaviors, stimulus_req, beta, mu, v):
    if internal_intensities is None:
        internal_intensities = stimulus
    feasible_behaviors = get_feasible_behaviors(stimulus, behaviors, stimulus_req)
    exponents = list()
    for behavior in feasible_behaviors:
        exponent = 0
        for element, intensity in internal_intensities.items():
            key = (element, behavior)
            exponent += beta[key] * v[key] * intensity + mu[key]
        exponents.append(exponent)
    max_exponent = max(exponents)
    if max_exponent > 500:
        shifted_exponents = [x - max_exponent for x in exponents]
        vector = [exp(x) for x in shifted_exponents]
    else:
        vector = [exp(x) for x in exponents]
    return vector, feasible_behaviors


# For postprocessing (pplot) only
def probability_of_response(stimulus, behavior, behaviors,
                            stimulus_req, beta, mu, v):
    x, feasible_behaviors = support_vector_static(stimulus, None, behaviors,
                                                  stimulus_req, beta, mu, v)
    if behavior not in feasible_behaviors:
        stimulus = [e for e in stimulus if e != 0]
        csse = ','.join(stimulus)  # Comma-separated stimulus elements
        raise Exception(f"Behavior '{behavior}' is not a possible response to '{csse}'.")
    index = feasible_behaviors.index(behavior)
    p = x[index] / sum(x)
    return p


class StimulusResponse(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)

        usum, vsum = 0, 0
        for element, intensity in stimulus.items():
            usum += u[element] * intensity
        for element, intensity in self.prev_stimulus.items():
            vsum += self.v[(element, self.response)] * intensity
        for element, intensity in self.prev_stimulus.items():
            alpha_v_er = alpha_v[(element, self.response)]
            self.v[(element, self.response)] += alpha_v_er * (usum - vsum - c[self.response]) * intensity

    def learn_i(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)

        usum, vsum = 0, 0
        for element, intensity in stimulus.items():
            usum += u[element] * intensity
        for element, intensity in self.prev_stimulus_intensities.items():
            vsum += self.v[(element, self.response)] * intensity
        for element, intensity in self.prev_stimulus_intensities.items():
            alpha_v_er = alpha_v[(element, self.response)]
            self.v[(element, self.response)] += alpha_v_er * (usum - vsum - c[self.response]) * intensity

# class SARSA(Mechanism):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def learn(self, stimulus):
#         usum, vsum1, vsum2 = 0, 0, 0
#         for element in stimulus:
#             usum += self.u[element]
#         for element in self.prev_stimulus:
#             vsum1 += self.v[(element, self.response)]
#         for element in self.stimulus:
#             vsum2 += self.v[(element, self.response)]   # XXX ???
#         for element in self.prev_stimulus:
#             self.v[(element, self.response)] += self.alpha_v * \
#                 (usum + vsum2 - vsum1 - self.c[self.response])


class EXP_SARSA(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        usum, vsum_prev = 0, 0
        for element in stimulus:
            usum += u[element]
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]

        E = 0
        for element in stimulus:
            x, feasible_behaviors = self._support_vector({element: 1})
            sum_x = sum(x)

            expected_value = 0
            for index, b in enumerate(feasible_behaviors):
                p = x[index] / sum_x
                expected_value += p * self.v[(element, b)]
            E += expected_value

        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            delta = alpha_v_er * (usum + discount * E - c[self.response] - vsum_prev)
            self.v[(element, self.response)] += delta


class Qlearning(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus):
        behaviors = self.parameters.get(kw.BEHAVIORS)
        # stimulus_req = self.parameters.get(kw.STIMULUS_REQUIREMENTS)
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        usum, vsum_prev = 0, 0
        for element in stimulus:
            usum += u[element]
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]

        maxvsum_future = 0
        for index, element in enumerate(stimulus):
            feasible_behaviors = get_feasible_behaviors((element,), behaviors, self.stimulus_req)
            vsum_future = 0
            for b in feasible_behaviors:
                vsum_future += self.v[(element, b)]

            if (index == 0) or (vsum_future > maxvsum_future):
                maxvsum_future = vsum_future

        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            delta = alpha_v_er * (usum + discount * maxvsum_future - c[self.response] - vsum_prev)
            self.v[(element, self.response)] += delta


class ActorCritic(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        alpha_w = self.parameters.get(kw.ALPHA_W)
        beta = self.parameters.get(kw.BETA)
        discount = self.parameters.get(kw.DISCOUNT)

        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]
            wsum_prev += self.w[element]
        for element in stimulus:
            usum += u[element]
            wsum += self.w[element]

        # v
        delta = usum + discount * wsum - c[self.response] - wsum_prev
        x, feasible_behaviors = self._support_vector(self.prev_stimulus)
        p = x[feasible_behaviors.index(self.response)] / sum(x)
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            beta_er = beta[(element, self.response)]
            self.v[(element, self.response)] += alpha_v_er * delta * beta_er * (1 - p)
        # w
        for element in self.prev_stimulus:
            alpha_w_e = alpha_w[element]
            self.w[element] += alpha_w_e * delta

    def has_w(self):
        return True


class Enquist(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_w = self.parameters.get(kw.ALPHA_W)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]
            wsum_prev += self.w[element]
        for element in stimulus:
            usum += u[element]
            wsum += self.w[element]
        # v
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            delta = alpha_v_er * (usum + discount * wsum - c[self.response] - vsum_prev)
            self.v[(element, self.response)] += delta
        # w
        for element in self.prev_stimulus:
            delta = alpha_w[element] * (usum + discount * wsum - c[self.response] - wsum_prev)
            self.w[element] += delta

    def learn_i(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_w = self.parameters.get(kw.ALPHA_W)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        usum, wsum = 0, 0
        for element in stimulus:
            usum += u[element]
            wsum += self.w[element]
        wsum *= discount

        vsum_i, wsum_i = 0, 0
        for element, intensity in self.prev_stimulus_intensities.items():
            vsum_i += self.v[(element, self.response)] * intensity
            wsum_i += self.w[element] * intensity

        # v
        for element, intensity in self.prev_stimulus_intensities.items():
            alpha_v_er = alpha_v[(element, self.response)]
            delta = alpha_v_er * (usum + wsum - c[self.response] - vsum_i) * intensity
            self.v[(element, self.response)] += delta
        # w
        for element, intensity in self.prev_stimulus_intensities.items():
            alpha_w_e = alpha_w[element]
            delta = alpha_w_e * (usum + wsum - c[self.response] - wsum_i) * intensity
            self.w[element] += delta

    def has_w(self):
        return True


class OriginalRescorlaWagner(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def subject_reset(self):
        super().subject_reset()
        self.vss = dict(self.parameters.get(kw.START_VSS))

    def learn_and_respond(self, stimulus, omit=False):
        if self.prev_stimulus is not None:  # and not omit: # Never omit in this mechanism
            # Do not update if first time or if omit
            self.learn(stimulus)

        # self.response = self._get_response(stimulus)
        self.prev_stimulus = stimulus
        return None  # Dummy response

    def learn(self, stimulus):
        _lambda = self.parameters.get(kw.LAMBDA)
        alpha_vss = self.parameters.get(kw.ALPHA_VSS)

        # XXX Handle compound stimuli
        assert(len(self.prev_stimulus) == 1)
        assert(len(stimulus) == 1)

        s1 = list(self.prev_stimulus.keys())[0]
        s2 = list(stimulus.keys())[0]
        # ss = (self.prev_stimulus[0], stimulus[0])
        ss = (s1, s2)
        self.vss[ss] += alpha_vss[ss] * (_lambda[s2] - self.vss[ss])

        for s in self.parameters.get(kw.STIMULUS_ELEMENTS):
            if s != s2:
                key = (s1, s)
                self.vss[key] += -alpha_vss[key] * self.vss[key]

    def check_compatibility_with_world(self, world):
        behaviors = self.parameters.get(kw.BEHAVIORS)

        # Check that stop condition does not depend on behavior
        for phase in world.phases:
            expr_vars = ParseUtil.variables_in_expr(phase.stop_condition.cond)
            for behavior in behaviors:
                if behavior in expr_vars:
                    mech_name = self.parameters.get(kw.MECHANISM_NAME)
                    err = f"Stop condition cannot depend on behavior in mechanism '{mech_name}'."
                    lineno = phase.stop_condition.lineno
                    return False, err, lineno

        # Check that phase line logics do not depend on behavior
        for phase in world.phases:
            for _, phase_line in phase.phase_lines.items():
                for condition_obj in phase_line.conditions.conditions:
                    if condition_obj.condition_is_behavior:
                        mech_name = self.parameters.get(kw.MECHANISM_NAME)
                        err = f"Phase line logic cannot depend on behavior in mechanism '{mech_name}'."
                        lineno = condition_obj.lineno
                        return False, err, lineno

        return True, None, None

    def has_vss(self):
        return True

    def has_v(self):
        return False


class MapLearner(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.seen_stimuli = list()
        
    def subject_reset(self):
        super().subject_reset()
        self.z = dict(self.parameters.get(kw.START_Z))  # Indexed by element-behavior-element triples
        self.seen_stimuli = list()
    
    def learn(self, stimulus):
        # shortcuts:
        alpha_z = self.parameters.get(kw.ALPHA_Z)
        print( "alpha_z:", alpha_z )
        b = self.response

        # loop over all stimulus elements to update their prediction
        # based on elements in pre_stimulus:
        for e2 in self.parameters.get(kw.STIMULUS_ELEMENTS):
            # the correct z is 1 if e2 is present, 0 otherwise:
            if e2 in stimulus.keys(): zcorrect = 1
            else:                     zcorrect = 0
            # set intensity of e2 for learning rate purposes, which
            # means i2=1 if e2 is absent:
            if e2 in stimulus.keys(): i2 = stimulus[ e2 ]
            else:                     i2 = 1
            # calculate prediction for this element
            zsum = 0
            for e1, i1 in self.prev_stimulus.items():
                zsum += self.z[ (e1,b,e2) ] * i1
            # now we can update the prediction of e2 for all elements
            # in prev_stimulus:
            for e1, i1 in self.prev_stimulus.items():
                self.z[ (e1,b,e2) ] += alpha_z[ (e1,b,e2) ] * ( zcorrect - zsum ) * i1 * i2
        
    def has_v(self):
        return True

    def has_w(self):
        return False

    def has_vss(self):
        return False

    def has_z(self):
        return True


class TolmanMechanism(MapLearner):
        
    def learn_and_respond(self, stimulus, omit=False):        

        #print( "stimulus is", stimulus )
        
        # learn if we are told to and have enough experience:
        if self.prev_stimulus and self.response and not omit:
            self.learn(stimulus)

        # possibly add stimulus to seen_stimuli:
        if stimulus not in self.seen_stimuli:
            self.seen_stimuli.append( stimulus )
            
        # reset v values
        self.v = self.parameters.get(kw.START_V)
            
        # shortcuts
        u = self.parameters.get(kw.U)
        behaviors = self.parameters.get(kw.BEHAVIORS)
        behavior_cost = self.parameters.get(kw.BEHAVIOR_COST)

        # set goal to highest valued stimulus in seen_stimuli
        # (XXX finds only one even if there are more)
        usums = list()
        for s in self.seen_stimuli:
            usums.append( sum( u[e] for e in s.keys() ) )
        goal = format( self.seen_stimuli[ usums.index( max(usums) ) ] )

        # if we are already at goal or no goal is found, return random
        # behavior
        if format(stimulus) == goal or max(usums)==0:
            #print( "stimulus:", stimulus, "max usums:", max(usums) ) 
            self.response = self._get_response(stimulus)
            self.prev_stimulus = dict(stimulus)  # dict ok?
            return self.response

        #print( "setting goal to", goal )
        
        # build transition graph between seen_stimuli. probabilities
        # are transformed into distances for Dijkstra's algorithm:
        # dist = -log( prob ). the graph is just a list of
        # connections, which requires some looping later on when we
        # need to find a specific connection
        graph = list()
        for b in behaviors:
            for s1 in self.seen_stimuli:
                for s2 in self.seen_stimuli:
                    zsum = 0
                    for e1 in s1.keys():
                        for e2 in s2.keys():
                            zsum += self.z.get( (e1,b,e2), 0 )
                    zsum = min( zsum, 1 ) # XXX overprediction
                    if zsum>0: # possible transition: add
                        graph.append({ 'from':format(s1),'to':format(s2),'with':b,'prob':zsum })
                        
        #print( "graph:", graph )
        
        # use Dijkstra's algorithm to find a shortest path from
        # stimulus to goal, if one exists

        # data setup:

        # string representation of unvisited nodes, used both for
        # accounting and for indexing:
        unv = [format(s) for s in self.seen_stimuli]
        # dis[s] = distance between node and goal: 
        dis = dict.fromkeys( unv, math.inf )
        # previous node on the shortest path
        pre = dict.fromkeys( unv, None )
        # act[s] = response to s to follow shortest path  
        act = dict.fromkeys( unv, None )
        # start from current stimulus:
        cur = format(stimulus)
        dis[ cur ] = 0

        # algorithm loops while there are unvisited nodes:
        while len(unv):
            # loop over all connections in graph:
            for con in graph: 
                # con must lead from cur to an unv node:
                if con['from'] != cur or con['to'] not in unv:
                    continue
                # new estimate for distance:
                guess = -math.log( con['prob'] ) + dis[cur]
                # update if better than existing estimate:
                k = con['to']
                if guess < dis[k]:
                    dis[k] = guess
                    act[k] = con['with']
                    pre[k] = con['from']
            unv.remove( cur )
            # stop if path found:
            if goal not in unv: 
                break
            ## set closest (estimated) unv node as cur: 
            mindis = math.inf
            for u in unv:
                if dis[format(u)] < mindis:
                    mindis = dis[format(u)]
                    cur = u
            if mindis == math.inf: # no path
                break

        # if no path to the goal is found, return random behavior
        if goal in unv:
            #print( "no path to goal" )
            self.response = self._get_response(stimulus)
            self.prev_stimulus = dict(stimulus)  # dict ok?
            return self.response

        #print( "dis:", dis )
        #print( "act:", act )
        #print( "pre:", pre )
        
        # build shortest path to goal
        shortest_path = list()
        response_path = list()
        distance_path = list()
        x = goal
        #print( "building path" )
        while x != format(stimulus):
            #print( "x:", x )
            shortest_path.insert( 0, x )
            response_path.insert( 0, act[x] )
            distance_path.insert( 0, dis[x] )
            x = pre[x]
            #print( "shortest path:", shortest_path )
            #print( "response path:", response_path )
            #print( "distance path:", distance_path )
        
        ## path value = ( goal value - cost ) * success prob
        path = { 'value':0, 'cost':0, 'prob':0 }
        path['cost'] = sum( [behavior_cost[b] for b in response_path] )
        path['prob'] = exp( - sum( distance_path ) )
        path['value'] = ( max(usums) - path['cost'] ) * path['prob']
        
        # to choose a response, we still use softmax, with the value
        # of the goal as the v for self.response. the value is spread
        # equally across elements of 'stimulus'
        n = len( stimulus.keys() )
        for e in stimulus.keys():
            self.v[ (e,response_path[0]) ] = path['value'] / n
        self.response = self._get_response(stimulus)
        self.prev_stimulus = dict(stimulus)
        #print( self.v )

        # print( "sti:", stimulus )
        # print( "bes:", best_response )
        # print( "res:", self.response )
        # print( "dis:", dis )
        # print( "act:", act )
        
        return self.response


class MentalSimulator(MapLearner):

    def learn_and_respond(self, stimulus, omit=False):        

        if self.prev_stimulus and self.response and not omit:
            self.learn(stimulus)

        if stimulus not in self.seen_stimuli:
            self.seen_stimuli.append( stimulus )

        # shortcuts
        u = self.parameters.get(kw.U)
        behaviors = self.parameters.get(kw.BEHAVIORS)
        s_elements = self.parameters.get(kw.STIMULUS_ELEMENTS)

        # reset v's for responding to current stimulus
        for e in stimulus.keys():
            for b in behaviors:
                self.v[ (e,b) ] = 0 
            
        # do a number of simulations and assign v values to behaviors
        # according to what the simulations find
        n_simulations = 10
        n_steps = 10
        sims = list()
        current = stimulus
        for n in range(n_simulations):
            path = list()
            for i in range(n_steps):
                # find out which stimuli can be reached from the current one
                zsum = dict.fromkeys( behaviors, 0 )
                b = choice( behaviors )
                path.append( b )
                for e1 in current.keys():
                    for maybe_next in self.seen_stimuli:
                        for e2 in maybe_next.keys():
                            zsum[b] += self.z[ (e1,b,e2) ]
                
                
