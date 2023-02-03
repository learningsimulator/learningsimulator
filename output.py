import util
from mechanism import probability_of_response
from exceptions import EvalException
import keywords as kw


class ScriptOutput():
    def __init__(self, run_outputs):
        # A dict with RunOutput objects, keys are run-labels
        self.run_outputs = run_outputs

    def write_v(self, run_label, subject_ind, stimulus, response, step, mechanism):
        '''stimulus is a dict.'''
        self.run_outputs[run_label].write_v(subject_ind, stimulus, response, step, mechanism)

    def write_vss(self, run_label, subject_ind, stimulus1, stimulus2, step, mechanism):
        '''stimulus is a tuple.'''
        self.run_outputs[run_label].write_vss(subject_ind, stimulus1, stimulus2, step, mechanism)

    def write_w(self, run_label, subject_ind, stimulus, step, mechanism):
        '''stimulus is a tuple.'''
        self.run_outputs[run_label].write_w(subject_ind, stimulus, step, mechanism)

    def vwpn_eval(self, vwph, expr, parameters, run_parameters):
        # self._evalparse(parameters)
        run_label = parameters.get(kw.RUNLABEL)
        return self.run_outputs[run_label].vwpn_eval(vwph, expr, parameters, run_parameters)

    def printout(self):
        for run_label, run_output in self.run_outputs.items():
            print(run_label + '\n')
            run_output.printout()

    # def _evalparse(self, evalprops):
    #     if EVAL_RUNLABEL not in evalprops:
    #         if len(self.run_outputs) == 1:
    #             run_label = list(self.run_outputs.keys())[-1]
    #         else:
    #             raise EvalException("Property '{}' not specified.".format(EVAL_RUNLABEL))
    #         evalprops[EVAL_RUNLABEL] = run_label
    #     else:
    #         run_label = evalprops[EVAL_RUNLABEL]
    #         if run_label not in self.run_outputs:
    #             raise EvalException("Unknown run label '{}'".format(run_label))

    #     n_subjects = len(self.run_outputs[run_label].output_subjects)
    #     if EVAL_SUBJECT not in evalprops:
    #         if n_subjects == 1:
    #             subject_ind = 0
    #         else:
    #             subject_ind = EVAL_AVERAGE
    #         evalprops[EVAL_SUBJECT] = subject_ind
    #     else:
    #         subject_ind = evalprops[EVAL_SUBJECT]
    #         if type(subject_ind) is int:
    #             if subject_ind >= n_subjects or subject_ind < 0:
    #                 raise EvalException("Property '{}' out of range.".format(EVAL_SUBJECT))
    #         elif type(subject_ind) is str:
    #             if subject_ind != EVAL_AVERAGE and subject_ind != EVAL_ALL:
    #                 raise LsEvalException("Property '{0}' must be int or '{1}'".
    #                                       format(EVAL_SUBJECT, EVAL_AVERAGE))

    #     if EVAL_CUMULATIVE not in evalprops:
    #         evalprops[EVAL_CUMULATIVE] = EVAL_OFF
    #     else:
    #         cumulative = evalprops[EVAL_CUMULATIVE]
    #         if (cumulative != EVAL_ON) and (cumulative != EVAL_OFF):
    #             raise EvalException("Property '{0}' must be '{1}' or '{2}'".
    #                                 format(EVAL_CUMULATIVE, EVAL_ON, EVAL_OFF))

    #     if EVAL_EXACTSTEPS not in evalprops:
    #         evalprops[EVAL_EXACTSTEPS] = EVAL_OFF
    #     else:
    #         exact = evalprops[EVAL_EXACTSTEPS]
    #         if (exact != EVAL_ON) and (exact != EVAL_OFF):
    #             raise EvalException("Property '{0}' must be '{1}' or '{2}'".
    #                                 format(EVAL_EXACTSTEPS, EVAL_ON, EVAL_OFF))

    #     if EVAL_EXACTN not in evalprops:
    #         evalprops[EVAL_EXACTN] = EVAL_OFF
    #     else:
    #         exact = evalprops[EVAL_EXACTN]
    #         if (exact != EVAL_ON) and (exact != EVAL_OFF):
    #             raise EvalException("Property '{0}' must be '{1}' or '{2}'".
    #                                 format(EVAL_EXACTN, EVAL_ON, EVAL_OFF))

    #     if EVAL_STEPS not in evalprops:
    #         evalprops[EVAL_STEPS] = EVAL_ALL
    #     else:
    #         steps = evalprops[EVAL_STEPS]
    #         steps_type = type(steps)
    #         if (steps != EVAL_ALL) and (steps_type is not str) and (steps_type is not tuple) and (steps_type is not list):
    #             raise EvalException("Property '{0}' must be '{1}' or a string/tuple/list.".
    #                                 format(EVAL_STEPS, EVAL_ALL))
    #         if steps_type is tuple:
    #             if not util.is_tuple_of_str(steps):
    #                 raise EvalException("When '{0}' is a tuple, it must be a tuple of strings.".
    #                                     format(EVAL_STEPS))
    #         elif steps_type is list:
    #             for s in steps:
    #                 if (not util.is_tuple_of_str(s)) and (type(s) is not str):
    #                     raise EvalException(("When '{0}' is a list, each list item must be a " +
    #                                          "string or a tuple of strings.").format(EVAL_STEPS))

    #     return evalprops


class RunOutput():
    def __init__(self, n_subjects, mechanism_obj):
        # A list of RunOutputSubject objects
        self.output_subjects = list()
        self.n_subjects = n_subjects
        self.mechanism_obj = mechanism_obj
        for _ in range(n_subjects):
            self.output_subjects.append(RunOutputSubject(mechanism_obj.stimulus_req))

    def write_v(self, subject_ind, stimulus, response, step, mechanism):
        '''stimulus is a dict.'''
        self.output_subjects[subject_ind].write_v(stimulus, response, step, mechanism)

    def write_vss(self, subject_ind, stimulus1, stimulus2, step, mechanism):
        '''stimulus is a tuple.'''
        self.output_subjects[subject_ind].write_vss(stimulus1, stimulus2, step, mechanism)

    def write_w(self, subject_ind, stimulus, step, mechanism):
        '''stimulus is a tuple.'''
        self.output_subjects[subject_ind].write_w(stimulus, step, mechanism)

    def write_history(self, subject_ind, stimulus, response):
        self.output_subjects[subject_ind].write_history(stimulus, response)

    def write_step(self, subject_ind, phase_label, step):
        self.output_subjects[subject_ind].write_step(phase_label, step)

    def write_phase_line_label(self, subject_ind, phase_line_label, step, preceeding_help_lines):
        self.output_subjects[subject_ind].write_phase_line_label(phase_line_label, step,
                                                                 preceeding_help_lines)

    def vwpn_eval(self, vwpn, expr, parameters, run_parameters):
        if vwpn in ('v', 'p') and not self.mechanism_obj.has_v():
            raise EvalException("Used mechanism does not have variable 'v'.")
        if vwpn == 'w' and not self.mechanism_obj.has_w():
            raise EvalException("Used mechanism does not have variable 'w'.")
        if vwpn == 'vss' and not self.mechanism_obj.has_vss():
            raise EvalException("Used mechanism does not have variable 'vss'.")

        subject_ind = parameters.get(kw.EVAL_SUBJECT)
        if subject_ind == kw.EVAL_AVERAGE:
            eval_subjects = list()
            for i in range(self.n_subjects):
                eval_subjects.append(self.output_subjects[i].vwpn_eval(vwpn, expr, parameters, run_parameters))
            return util.eval_average(eval_subjects)
        elif subject_ind == kw.EVAL_ALL:
            eval_subjects = list()
            for i in range(self.n_subjects):
                eval_subjects.append(self.output_subjects[i].vwpn_eval(vwpn, expr, parameters, run_parameters))
            return eval_subjects
        else:
            if subject_ind >= len(self.output_subjects):
                raise EvalException(f"The value ({subject_ind + 1}) for the parameter '{kw.EVAL_SUBJECT}' exceeds the number of subjects ({len(self.output_subjects)}).")
            return self.output_subjects[subject_ind].vwpn_eval(vwpn, expr, parameters, run_parameters)

    def printout(self):
        i = 0
        for ros in self.output_subjects:
            print("Subject {}".format(i))
            i += 1
            ros.printout()


class RunOutputSubject():
    def __init__(self, stimulus_req):
        self.stimulus_req = stimulus_req

        # Keys are 2-tuples (stimulus_element,response), values are Val objects
        self.v = dict()

        # Keys are 2-tuples (stimulus_element,stimulus_element), values are Val objects
        self.vss = dict()

        # Keys are stimulus elements (strings), values are Val objects
        self.w = dict()

        # History of stimulus and responses [S1,R1,S2,R2,...]
        self.history = list()

        # Tuple where first index is list of phase labels, second is list of step numbers for
        # first step in each phase
        self.first_step_phase = (list(), list())

        # List of phase line labels, used for evaluating when parameter XSCALE is phase line label
        self.phase_line_labels = list()

        # Step numbers for the phase line labels in self.phase_line_labels. Used to keep track of
        # step numbers for help lines
        self.phase_line_labels_steps = list()

    def write_history(self, stimulus, response):
        stimulus_tuple = tuple([e for e in stimulus if stimulus[e] != 0])
        if len(stimulus_tuple) == 1:
            self.history.append(stimulus_tuple[0])
        else:
            self.history.append(stimulus_tuple)
        self.history.append(response)

    def write_step(self, phase_label, step):
        if phase_label not in self.first_step_phase[0]:
            self.first_step_phase[0].append(phase_label)
            self.first_step_phase[1].append(step)

    def write_phase_line_label(self, phase_line_label, step, preceeding_help_lines):
        if preceeding_help_lines:
            for line_label in preceeding_help_lines:
                self.phase_line_labels.append(line_label)
                self.phase_line_labels_steps.append(step)
        self.phase_line_labels.append(phase_line_label)
        self.phase_line_labels_steps.append(step)

    def write_v(self, stimulus, response, step, mechanism):
        '''stimulus is a dict.'''
        if mechanism.use_trace:
            stimulus_elements = mechanism.parameters.get(kw.STIMULUS_ELEMENTS)
        else:
            stimulus_elements = stimulus
        for element in stimulus_elements:
            key = (element, response)
            if key not in self.v:
                self.v[key] = Val()
            self.v[key].write(mechanism.v[key], step)

    def write_vss(self, stimulus1, stimulus2, step, mechanism):
        # XXX Handle compound stimuli
        assert(len(stimulus1) == 1)
        assert(len(stimulus2) == 1)

        key = (list(stimulus1.keys())[0], list(stimulus2.keys())[0])
        if key not in self.vss:
            self.vss[key] = Val()

        self.vss[key].write(mechanism.vss[key], step)

    def write_w(self, stimulus, step, mechanism):
        for element in stimulus:
            key = element
            if key not in self.w:
                self.w[key] = Val()
            self.w[key].write(mechanism.w[key], step)

    def vwpn_eval(self, vwpn, expr, parameters, run_parameters):
        if vwpn == 'n':
            _, history, phase_line_labels, _ = self._phasefilter(None, parameters)
            return RunOutputSubject.n_eval(expr, history, phase_line_labels, parameters)
        else:
            if vwpn == 'p':
                # expr is a tuple ({'e1':i1, 'e2':i2, ...}, behavior)
                stimulus = expr[0]
                behavior = expr[1]
                funout = self.p_eval(stimulus, behavior, parameters, run_parameters)
            else:
                switcher = {
                    'v': self.v_eval,
                    'vss': self.vss_eval,
                    'w': self.w_eval
                }
                fun = switcher[vwpn]
                funout = fun(expr)
            funout, history, phase_line_labels, phase_line_labels_steps = self._phasefilter(funout, parameters)
            return self._xscalefilter(funout, history, phase_line_labels, phase_line_labels_steps, parameters)

    def _phasefilter(self, evalout, parameters):
        """
        Filter evalout (output from {v,w,p}-eval) as well as self.history,
        self.phase_line_labels and self.phase_line_labels_steps w.r.t. the parameter
        'phases'.
        """
        plot_phases = parameters.get(kw.EVAL_PHASES)
        if plot_phases == kw.EVAL_ALL:
            return evalout, self.history, self.phase_line_labels, self.phase_line_labels_steps

        # List of phases in the order they were run (don't include "last")
        run_phases = self.first_step_phase[0][0:-1]
        assert(len(run_phases) > 0)

        if plot_phases == run_phases:
            return evalout, self.history, self.phase_line_labels, self.phase_line_labels_steps

        out = list()
        history_out = list()
        phase_line_labels_out = list()
        phase_line_labels_steps_out = list()
        if type(plot_phases) is not list:
            plot_phases = (plot_phases,)
        for phase in plot_phases:
            if phase not in run_phases:
                raise EvalException(f"Invalid phase label {phase}. Must be in {run_phases}.")

        wrote_inital_value = False
        if evalout is not None:
            if plot_phases[0] == run_phases[0]:
                # First value (out[0]) should be inital value (evalout[0]) if the first phase
                # in 'phases' is the first run-phase.
                out.append(evalout[0])
                wrote_inital_value = True
            else:
                # First value (out[0]) should be last value of previous phase if the first
                # phase in 'phases' is NOT the first run-phase.
                first_plot_phase_index = run_phases.index(plot_phases[0])
                first_plot_phase_startind = self.first_step_phase[1][first_plot_phase_index]
                first_value_previous_phase = evalout[first_plot_phase_startind - 1]
                out.append(first_value_previous_phase)

        cnt = 1
        for phase in plot_phases:
            fsp_index = run_phases.index(phase)
            phase_startind = self.first_step_phase[1][fsp_index]
            nextphase_startind = self.first_step_phase[1][fsp_index + 1]
            phase_endind = nextphase_startind - 1
            for j in range(phase_startind - 1, phase_endind):  # phase_startind is one-based
                history_out.append(self.history[2 * j])
                history_out.append(self.history[2 * j + 1])

            if evalout is not None:
                for j in range(phase_startind - 1, phase_endind):
                    if j == 0 and wrote_inital_value:
                        pass
                    else:
                        out.append(evalout[j])

            # Index to first occurence of phase_startind in self.phase_line_labels_steps
            plls_startind = None
            # Index to last occurence of phase_endind in self.phase_line_labels_steps
            plls_endind = None
            for j in range(phase_startind - 1, len(self.phase_line_labels_steps)):
                plls_j = self.phase_line_labels_steps[j]
                if plls_j == phase_startind:
                    if plls_startind is None:  # We want the first index to phase_startind
                        plls_startind = j
                elif plls_j == phase_endind:
                    plls_endind = j  # We want the last index to phase_endind-1
                elif plls_j > phase_endind:
                    break  # We need look no further
            assert(plls_startind is not None)
            assert(plls_endind is not None)

            prev_plls = None
            for j in range(plls_startind, plls_endind + 1):
                curr_plls = self.phase_line_labels_steps[j]
                phase_line_labels_out.append(self.phase_line_labels[j])
                phase_line_labels_steps_out.append(cnt)
                if prev_plls != curr_plls:
                    cnt += 1
                prev_plls = curr_plls

        return out, history_out, phase_line_labels_out, phase_line_labels_steps_out

    def _xscalefilter(self, evalout, history, phase_line_labels, phase_line_labels_steps,
                      parameters):
        xscale = parameters.get(kw.XSCALE)
        if xscale == kw.EVAL_ALL:
            return evalout
        else:
            if xscale in phase_line_labels:  # xscale is a phase line label
                findind, _ = util.find_and_cumsum(phase_line_labels, xscale, True)
                out = [evalout[0]]  # evalout[0] must be kept
                for pll_ind, zero_or_one in enumerate(findind):
                    # pll_ind >= 1 because the first update is done after S->B->S'
                    if zero_or_one == 1 and pll_ind >= 1:  # 1 because pll_ind is index to phase_line_labels that contains only phase line labels
                        evalout_ind = phase_line_labels_steps[pll_ind] - 1  # Zero-based index
                        out.append(evalout[evalout_ind])
                return out
            else:
                pattern = xscale
                pattern_len = RunOutputSubject.compute_patternlen(pattern)
                use_exact_match = (parameters.get(kw.XSCALE_MATCH) == 'exact')
                findind, _ = util.find_and_cumsum(history, pattern, use_exact_match)
                out = [evalout[0]]  # evalout[0] must be kept
                for history_ind, zero_or_one in enumerate(findind):
                    # history_ind >= 2 because the first update is done after S->B->S'
                    if zero_or_one == 1 and history_ind >= 2:  # 2 because history_ind is index to history that contains S,B,S,B,S,B,...
                        evalout_ind = RunOutputSubject.historyind2stepind(history_ind, pattern_len)
                        out.append(evalout[evalout_ind])
                return out

    @staticmethod
    def historyind2stepind(history_ind, pattern_len):
        step_ind = (history_ind + pattern_len - 1) // 2
        return step_ind

    @staticmethod
    def compute_patternlen(pattern):
        if type(pattern) is list:
            pattern_len = len(pattern)
        else:
            pattern_len = 1
        return pattern_len

    def v_eval(self, er):
        return self.v[er].evaluate()

    def vss_eval(self, ss):
        return self.vss[ss].evaluate()

    def w_eval(self, element):
        return self.w[element].evaluate()

    def p_eval(self, stimulus, response, parameters, run_parameters):
        """stimulus is a dict with intensities for stimulus elements. response is a string."""
        nonzero_intensity_stimulus = {e: i for e, i in stimulus.items() if i != 0}

        # Only evaluate for stimulus elements with nonzero intensity
        v_val = dict()
        for er in self.v:
            if er[0] in nonzero_intensity_stimulus:
                v_val[er] = self.v[er]

        behaviors = list()
        nval = 0
        for er in v_val:
            v_val[er] = self.v_eval(er)
            if nval == 0:
                nval = len(v_val[er])
            behavior = er[1]
            if behavior not in behaviors:
                behaviors.append(behavior)

        out = [None] * nval
        for i in range(nval):
            v_local = util.dict_of_list_ind(v_val, i)
            out[i] = probability_of_response(nonzero_intensity_stimulus, response, behaviors,
                                             self.stimulus_req, run_parameters.get(kw.BETA),
                                             run_parameters.get(kw.MU), v_local)
        return out

    @staticmethod
    def n_eval(seq, history, phase_line_labels, parameters):
        is_exact = (parameters.get(kw.MATCH) == kw.EVAL_EXACT)
        is_cumulative = (parameters.get(kw.EVAL_CUMULATIVE) == kw.EVAL_ON)
        xscale = parameters.get(kw.XSCALE)
        xscale_exact = (parameters.get(kw.XSCALE_MATCH) == kw.EVAL_EXACT)

        out = None
        # prepend_zero = (xscale == kw.EVAL_ALL)
        if (xscale == kw.EVAL_ALL):
            if is_cumulative:
                _, out = util.find_and_cumsum(history, seq, is_exact)
            else:
                out, _ = util.find_and_cumsum(history, seq, is_exact)
        else:
            if xscale in phase_line_labels:  # xscale is a phase line label
                raise Exception("xscale cannot be a phase line label in @nplot/@nexport.")
            if is_cumulative:
                _, out = util.find_and_cumsum_interval(history, seq, is_exact, xscale, xscale_exact)
            else:
                out, _ = util.find_and_cumsum_interval(history, seq, is_exact, xscale, xscale_exact)
        # if is_cumulative:
        #     out = [0] + out
        return out

    def printout(self):
        print("\n")
        for key, val in self.v.items():
            print(f"v({key}):")
            val.printout()
        for key, val in self.w.items():
            print(f"w({key}):")
            val.printout()
        for key, val in self.vss.items():
            print(f"vss({key}):")
            val.printout()
        print(f"history={self.history}")
        print(f"first_step_phase={self.first_step_phase}")
        print(f"phase_line_labels={self.phase_line_labels}")
        print(f"phase_line_labels_steps={self.phase_line_labels_steps}")


class Val():
    def __init__(self):
        # List of float values
        self.values = list()

        self.steps = list()

        # Phase labels
        # self.phase_labels = list()

    def write(self, value, step):
        self.values.append(value)
        self.steps.append(step)
        # self.phase_labels.append(phase_label)

    def evaluate(self):
        '''Assumes that self.steps is increasing and that self.steps[0]=0.'''
        max_step = self.steps[-1]
        outlen = max_step + 1
        out = [None] * outlen

        nchunks = len(self.steps) - 1
        for chunkind in range(nchunks):
            startind = self.steps[chunkind]
            stopind = self.steps[chunkind + 1]
            v = self.values[chunkind]
            for i in range(startind, stopind):
                out[i] = v
            out[max_step] = self.values[nchunks]  # Last point
        return out


    def printout(self):
        print(f"values: {self.values}")
        print(f"steps: {self.steps}")
