from math import exp
from random import seed, random

import keywords as kw
from util import dict_inv, ParseUtil

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

        # self.v = dict(parameters.get(kw.START_V))
        # self.w = dict(parameters.get(kw.START_W))
        # self._initialize_v()
        # self._initialize_w()
        self.prev_stimulus = None
        self.response = None

        if self.use_trace:
            for s in self.stimulus_intensities:
                self.stimulus_intensities[s] = 0
            for s in self.prev_stimulus_intensities:
                self.prev_stimulus_intensities[s] = 0

    def _update_stimulus_intensities(self, stimulus):
        for s in self.stimulus_intensities:
            self.stimulus_intensities[s] *= self.trace
        for s in stimulus:
            if self.parameters.get(kw.FILENAME) == '+':  # XXX temporary
                self.stimulus_intensities[s] += 1
            else:
                self.stimulus_intensities[s] = 1

    def learn_and_respond(self, stimulus, omit=False):
        """stimulus is a tuple."""
        # element_in_omit = False
        # for e in stimulus:
        #     if e in self.omit_learning:
        #         element_in_omit = True
        #         break

        if self.use_trace:
            self._update_stimulus_intensities(stimulus)

        if self.prev_stimulus is not None and not omit:  # Do not update if first time or if omit
            if self.use_trace:
                self.learn_i(stimulus)
            else:
                self.learn(stimulus)

        self.response = self._get_response(stimulus)

        self.prev_stimulus = stimulus
        if self.use_trace:
            for s in self.parameters.get(kw.STIMULUS_ELEMENTS):
                self.prev_stimulus_intensities[s] = self.stimulus_intensities[s]

        return self.response

    def learn(self, stimulus):
        # Must be overridden
        raise NotImplementedError

    def learn_i(self, stimulus):
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
        return support_vector_static(stimulus, behaviors, self.stimulus_req, beta, mu, self.v)

    def check_compatibility_with_world(self, world):
        return True, None, None  # To be overridden where necessary

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
    exponents = list()
    for behavior in feasible_behaviors:
        exponent = 0
        for element in stimulus:
            key = (element, behavior)
            exponent += beta[key] * v[key] + mu[key]
        exponents.append(exponent)
    max_exponent = max(exponents)
    if max_exponent > 500:
        shifted_exponents = [x - max_exponent for x in exponents]
        vector = [exp(x) for x in shifted_exponents]
    else:
        vector = [exp(x) for x in exponents]
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

        usum, vsum = 0, 0
        for element in stimulus:
            usum += u[element]
        for element in self.prev_stimulus:
            vsum += self.v[(element, self.response)]
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            self.v[(element, self.response)] += alpha_v_er * (usum - vsum - c[self.response])

    def learn_i(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)

        usum, vsum = 0, 0
        for element in stimulus:  # self.stimulus_intensities:
            # intensity = self.stimulus_intensities[element]
            usum += u[element]  # * intensity
        for element in self.prev_stimulus:
            intensity = self.prev_stimulus_intensities[element]
            vsum += self.v[(element, self.response)] * intensity
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            intensity = self.prev_stimulus_intensities[element]
            delta = alpha_v_er * (usum - vsum - c[self.response]) * intensity
            self.v[(element, self.response)] += delta

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
            x, feasible_behaviors = self._support_vector((element,))
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

    def learn_i(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        usum, vsum_prev = 0, 0
        for element in stimulus:
            intensity = self.stimulus_intensities[element]
            usum += u[element] * intensity
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
            intensity = self.prev_stimulus_intensities[element]
            delta = alpha_v_er * (usum + discount * E - c[self.response] - vsum_prev) * intensity
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

    def learn_i(self, stimulus):
        behaviors = self.parameters.get(kw.BEHAVIORS)
        # stimulus_req = self.parameters.get(kw.STIMULUS_REQUIREMENTS)
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        usum, vsum_prev = 0, 0
        for element in stimulus:
            intensity = self.stimulus_intensities[element]
            usum += u[element] * intensity
        for element in self.prev_stimulus:
            intensity = self.prev_stimulus_intensities[element]
            vsum_prev += self.v[(element, self.response)] * intensity

        maxvsum_future = 0
        for index, element in enumerate(stimulus):
            intensity = self.stimulus_intensities[element]
            feasible_behaviors = get_feasible_behaviors((element,), behaviors, self.stimulus_req)
            vsum_future = 0
            for b in feasible_behaviors:
                vsum_future += self.v[(element, b)] * intensity

            if (index == 0) or (vsum_future > maxvsum_future):
                maxvsum_future = vsum_future

        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            intensity = self.prev_stimulus_intensities[element]
            delta = alpha_v_er * (usum + discount * maxvsum_future - c[self.response] - vsum_prev) * intensity
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

    def learn_i(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        alpha_w = self.parameters.get(kw.ALPHA_W)
        beta = self.parameters.get(kw.BETA)
        discount = self.parameters.get(kw.DISCOUNT)

        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            intensity = self.prev_stimulus_intensities[element]
            vsum_prev += self.v[(element, self.response)] * intensity
            wsum_prev += self.w[element] * intensity
        for element in stimulus:
            intensity = self.stimulus_intensities[element]
            usum += u[element] * intensity
            wsum += self.w[element] * intensity

        # v
        delta = usum + discount * wsum - c[self.response] - wsum_prev
        x, feasible_behaviors = self._support_vector(self.prev_stimulus)
        p = x[feasible_behaviors.index(self.response)] / sum(x)
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            beta_er = beta[(element, self.response)]
            intensity = self.prev_stimulus_intensities[element]
            self.v[(element, self.response)] += alpha_v_er * delta * beta_er * (1 - p) * intensity
        # w
        for element in self.prev_stimulus:
            alpha_w_e = alpha_w[element]
            intensity = self.prev_stimulus_intensities[element]
            self.w[element] += alpha_w_e * delta * intensity

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
        print(f"stimulus={stimulus}")
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_w = self.parameters.get(kw.ALPHA_W)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        discount = self.parameters.get(kw.DISCOUNT)

        vsum_prev, wsum_prev, usum, wsum = 0, 0, 0, 0
        for element in self.prev_stimulus:
            intensity = self.prev_stimulus_intensities[element]
            vsum_prev += self.v[(element, self.response)] * intensity
            wsum_prev += self.w[element] * intensity
        for element in stimulus:
            # intensity = self.stimulus_intensities[element]
            usum += u[element]  # * intensity
            wsum += self.w[element]  # * intensity
        # v
        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            intensity = self.prev_stimulus_intensities[element]
            delta = alpha_v_er * (usum + discount * wsum - c[self.response] - vsum_prev) * intensity
            self.v[(element, self.response)] += delta
        # w
        for element in self.prev_stimulus:
            intensity = self.prev_stimulus_intensities[element]
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
                    if condition_obj.cond_is_behavior:
                        mech_name = self.parameters.get(kw.MECHANISM_NAME)
                        err = f"Phase line logic cannot depend on behavior in mechanism '{mech_name}'."
                        lineno = condition_obj.lineno
                        return False, err, lineno

        return True, None, None

    def has_vss(self):
        return True

    def has_v(self):
        return False
