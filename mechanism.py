from math import exp
from random import seed, random

import keywords as kw
from util import dict_inv, ParseUtil

seed()


class Mechanism():
    '''Base class for mechanisms'''

    def __init__(self, parameters):
        self.parameters = parameters
        self.trace = self.parameters.get(kw.TRACE)
        self.use_trace = (self.trace != 0)

        if self.use_trace:
            self.trace_stimulus = {s: 0 for s in parameters.get(kw.STIMULUS_ELEMENTS)}
            self.prev_trace_stimulus = dict(self.trace_stimulus)
        else:
            self.trace_stimulus = None
            self.prev_trace_stimulus = None

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

    def _reset_trace(self, stimulus=None):
        for e in self.trace_stimulus:
            self.trace_stimulus[e] = 0
        if stimulus is not None:
            for e in stimulus:
                self.trace_stimulus[e] = stimulus[e]

        for e in self.prev_trace_stimulus:
            self.prev_trace_stimulus[e] = 0

    def _decay_trace_stimulus(self, stimulus):
        '''stimulus is a dict.'''
        for e in self.trace_stimulus:
            self.trace_stimulus[e] *= self.trace
        for e in stimulus:
            self.trace_stimulus[e] += stimulus[e]

    def learn_and_respond(self, stimulus, omit=False):
        '''stimulus is a dict.'''
        if self.use_trace:
            self._decay_trace_stimulus(stimulus)

        if (self.prev_stimulus is None) or omit:  # Do not update if first time or if omit
            pass
        else:
            if self.use_trace:
                self.learn(stimulus, self.prev_trace_stimulus)
            else:
                self.learn(stimulus, self.prev_stimulus)

        self.response = self._get_response(stimulus)

        if self.use_trace and omit:
            self._reset_trace(stimulus)

        self.prev_stimulus = dict(stimulus)  # dict ok?
        if self.use_trace:
            # self.prev_trace_stimulus = dict(self.trace_stimulus)
            for s in self.parameters.get(kw.STIMULUS_ELEMENTS):
                self.prev_trace_stimulus[s] = self.trace_stimulus[s]

        return self.response

    def learn(self, stimulus, prev_stimulus):
        # Must be overridden
        raise NotImplementedError

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
        return support_vector_static(stimulus, self.trace_stimulus, behaviors,
                                     self.stimulus_req, beta, mu, self.v)

    def check_compatibility_with_world(self, world):
        if self.has_v():
            if self.parameters.get(kw.ALPHA_V) is None:
                return "Parameter alpha_v not specified.", None
        if self.has_w():
            if self.parameters.get(kw.ALPHA_W) is None:
                return "Parameter alpha_w not specified.", None
        if self.has_vss():
            if self.parameters.get(kw.ALPHA_VSS) is None:
                return "Parameter alpha_vss not specified.", None
        return None, None

    def has_v(self):
        return True

    def has_w(self):
        return False

    def has_vss(self):
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
        raise Exception(f"Error in @pplot: Behavior '{behavior}' is not a possible response to '{csse}'.")
    index = feasible_behaviors.index(behavior)
    p = x[index] / sum(x)
    return p


class StimulusResponse(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus, prev_stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)

        usum, vsum = 0, 0
        for element, intensity in stimulus.items():
            usum += u[element] * intensity
        for element, intensity in prev_stimulus.items():
            vsum += self.v[(element, self.response)] * intensity
        for element, intensity in prev_stimulus.items():
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

    def learn(self, stimulus, prev_stimulus):
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

    def learn(self, stimulus, prev_stimulus):
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

    def learn(self, stimulus, prev_stimulus):
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

    def learn(self, stimulus, prev_stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_w = self.parameters.get(kw.ALPHA_W)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        usum, wsum = 0, 0
        for element, intensity in stimulus.items():
            usum += u[element] * intensity
            wsum += self.w[element] * intensity

        vsum_prev, wsum_prev = 0, 0
        for element, intensity in prev_stimulus.items():
            vsum_prev += self.v[(element, self.response)] * intensity
            wsum_prev += self.w[element] * intensity

        # v
        for element, intensity in prev_stimulus.items():
            alpha_v_er = alpha_v[(element, self.response)]
            delta = alpha_v_er * (usum + discount * wsum - c[self.response] - vsum_prev) * intensity
            self.v[(element, self.response)] += delta
        # w
        for element, intensity in prev_stimulus.items():
            delta = alpha_w[element] * (usum + discount * wsum - c[self.response] - wsum_prev) * intensity
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
        err, lineno = super().check_compatibility_with_world(world)
        if err:
            return err, lineno

        behaviors = self.parameters.get(kw.BEHAVIORS)

        # Check that stop condition does not depend on behavior
        for phase in world.phases:
            expr_vars = ParseUtil.variables_in_expr(phase.stop_condition.cond)
            for behavior in behaviors:
                if behavior in expr_vars:
                    mech_name = self.parameters.get(kw.MECHANISM_NAME)
                    err = f"Stop condition cannot depend on behavior in mechanism '{mech_name}'."
                    lineno = phase.stop_condition.lineno
                    return err, lineno

        # Check that phase line logics do not depend on behavior
        for phase in world.phases:
            for _, phase_line in phase.phase_lines.items():
                for condition_obj in phase_line.conditions.conditions:
                    if condition_obj.condition_is_behavior:
                        mech_name = self.parameters.get(kw.MECHANISM_NAME)
                        err = f"Phase line logic cannot depend on behavior in mechanism '{mech_name}'."
                        lineno = condition_obj.lineno
                        return err, lineno

        return None, None

    def has_vss(self):
        return True

    def has_v(self):
        return False
