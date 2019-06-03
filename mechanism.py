from math import exp
from random import seed, random

import keywords as kw
import util

seed()


class Mechanism():
    '''Base class for mechanisms'''

    def __init__(self, parameters):
        self.parameters = parameters
        # parameters.scalar_expand()

        self.v = None
        self.w = None
        self.prev_stimulus = None
        self.response = None

        # Make self.stimulus_req
        self.stimulus_req = util.dict_inv(parameters.get(kw.RESPONSE_REQUIREMENTS))

        self.subject_reset()

    def subject_reset(self):
        self.v = dict(self.parameters.get(kw.START_V))
        self.w = dict(self.parameters.get(kw.START_W))

        # self.v = dict(parameters.get(kw.START_V))
        # self.w = dict(parameters.get(kw.START_W))
        # self._initialize_v()
        # self._initialize_w()
        self.prev_stimulus = None
        self.response = None

    def learn_and_respond(self, stimulus, omit=False):
        """stimulus is a tuple."""
        # element_in_omit = False
        # for e in stimulus:
        #     if e in self.omit_learning:
        #         element_in_omit = True
        #         break
        if self.prev_stimulus is not None and not omit:
            # Do not update if first time or if omit
            self.learn(stimulus)

        self.response = self._get_response(stimulus)
        self.prev_stimulus = stimulus
        return self.response

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
        return support_vector_static(stimulus, behaviors, self.stimulus_req, beta, mu, self.v)

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


def support_vector_static(stimulus, behaviors, stimulus_req, beta, mu, v):
    feasible_behaviors = get_feasible_behaviors(stimulus, behaviors, stimulus_req)
    vector = list()
    for behavior in feasible_behaviors:
        exponent = 0
        for element in stimulus:
            key = (element, behavior)
            exponent += beta[key] * v[key] + mu[key]
        value = exp(exponent)
        vector.append(value)
    return vector, feasible_behaviors


# For postprocessing only
def probability_of_response(stimulus, behavior, behaviors, stimulus_req, beta, mu, v):
    x, feasible_behaviors = support_vector_static(stimulus, behaviors, stimulus_req, beta, mu, v)
    if behavior not in feasible_behaviors:
        csse = ','.join(stimulus)  # Comma-separated stimulus elements
        raise Exception(f"Behavior '{behavior}' is not a possible response to '{csse}'.")
    index = feasible_behaviors.index(behavior)
    p = x[index] / sum(x)
    return p


class RescorlaWagner(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)

        if self.prev_stimulus is None:
            return
        usum, vsum = 0, 0
        for element in stimulus:
            usum += u[element]
        for element in self.prev_stimulus:
            vsum += self.v[(element, self.response)]
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            self.v[(element, self.response)] += alpha_v_er * (usum - vsum - c[self.response])


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

        usum, vsum_prev = 0, 0, 0
        for element in stimulus:
            usum += u[element]
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]

        E = 0
        for element in stimulus:
            x, feasible_behaviors = self._support_vector((element,))
            sum_x = sum(x)

            expected_value = 0
            for index, b in enumerate(feasible_behaviors):
                p = x[index] / sum_x
                expected_value += p * self.v[(element, b)]
            E += expected_value

        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            delta = alpha_v_er * (usum + E - c[self.response] - vsum_prev)
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

        usum, vsum_prev = 0, 0, 0
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
            delta = alpha_v_er * (usum + maxvsum_future - c[self.response] - vsum_prev)
            self.v[(element, self.response)] += delta


'''class ActorCritic(Mechanism):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def learn(self, stimulus):
        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]
            wsum_prev += self.w[element]
        for element in stimulus:
            usum += self.u[element]
            wsum += self.w[element]

        delta = usum + wsum - wsum_prev - self.c[self.response]
        deltav = self.alpha_v * delta
        deltaw = self.alpha_w * delta

        # v
        for element in self.prev_stimulus:
            self.v[(element, self.response)] += deltav
        # w
        for element in self.prev_stimulus:
            self.w[element] += deltaw'''


class ActorCritic(Mechanism):
    def __init__(self, parameters):
        super().__init__(parameters)

    def learn(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        alpha_w = self.parameters.get(kw.ALPHA_W)

        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            vsum_prev += self.v[(element, self.response)]
            wsum_prev += self.w[element]
        for element in stimulus:
            usum += u[element]
            wsum += self.w[element]

        # v
        delta = usum + wsum - c[self.response] - wsum_prev
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            self.v[(element, self.response)] += alpha_v_er * delta
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
            delta = alpha_v_er * (usum + wsum - c[self.response] - vsum_prev)
            self.v[(element, self.response)] += delta
        # w
        for element in self.prev_stimulus:
            delta = alpha_w[element] * (usum + wsum - c[self.response] - wsum_prev)
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

        ss = (self.prev_stimulus[0], stimulus[0])
        self.vss[ss] += alpha_vss[ss] * (_lambda[stimulus[0]] - self.vss[ss])

        for s in self.parameters.get(kw.STIMULUS_ELEMENTS):
            if s != stimulus[0]:
                key = (self.prev_stimulus[0], s)
                self.vss[key] += -alpha_vss[key] * self.vss[key]

    def has_vss(self):
        return True

    def has_v(self):
        return False
