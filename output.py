import util
import mechanism
from exceptions import EvalException
import keywords as kw


class ScriptOutput():
    def __init__(self, run_outputs):
        # A dict with RunOutput objects, keys are run-labels
        self.run_outputs = run_outputs

    def write_v(self, run_label, subject_ind, stimulus, response, step, mechanism):
        '''stimulus is a tuple.'''
        self.run_outputs[run_label].write_v(subject_ind, stimulus, response, step, mechanism)

    def write_w(self, run_label, subject_ind, stimulus, step, mechanism):
        '''stimulus is a tuple.'''
        self.run_outputs[run_label].write_w(subject_ind, stimulus, step, mechanism)

    def vwpn_eval(self, vwph, expr, parameters):
        # self._evalparse(parameters)
        run_label = parameters.get(kw.RUNLABEL)
        return self.run_outputs[run_label].vwpn_eval(vwph, expr, parameters)

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
    def __init__(self, n_subjects, stimulus_req):
        # A list of RunOutputSubject objects
        self.output_subjects = list()
        self.n_subjects = n_subjects
        for _ in range(n_subjects):
            self.output_subjects.append(RunOutputSubject(stimulus_req))

    def write_v(self, subject_ind, stimulus, response, step, mechanism):
        '''stimulus is a tuple.'''
        self.output_subjects[subject_ind].write_v(stimulus, response, step, mechanism)

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

    def vwpn_eval(self, vwpn, expr, parameters):
        subject_ind = parameters.get(kw.EVAL_SUBJECT)
        if subject_ind == kw.EVAL_AVERAGE:
            eval_subjects = list()
            for i in range(self.n_subjects):
                eval_subjects.append(self.output_subjects[i].vwpn_eval(vwpn, expr, parameters))
            return util.eval_average(eval_subjects)
        elif subject_ind == kw.EVAL_ALL:
            eval_subjects = list()
            for i in range(self.n_subjects):
                eval_subjects.append(self.output_subjects[i].vwpn_eval(vwpn, expr, parameters))
            return eval_subjects
        else:
            return self.output_subjects[subject_ind].vwpn_eval(vwpn, expr, parameters)

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
        assert(type(stimulus) is tuple)
        if len(stimulus) == 1:
            self.history.append(stimulus[0])
        else:
            self.history.append(stimulus)
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

    def vwpn_eval(self, vwpn, expr, parameters):
        if vwpn == 'n':
            _, history, phase_line_labels, _ = self._phasefilter(None, parameters)
            return RunOutputSubject.n_eval(expr, history, phase_line_labels, parameters)
        else:
            switcher = {
                'v': self.v_eval,
                'w': self.w_eval,
                'p': self.p_eval,
            }
            fun = switcher[vwpn]
            funout = fun(expr, parameters)
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

        run_phases = self.first_step_phase[0]  # List of phases in the order they were run
        assert(len(run_phases) > 0)

        out = list()
        history_out = list()
        phase_line_labels_out = list()
        phase_line_labels_steps_out = list()
        if type(plot_phases) is not list:
            plot_phases = (plot_phases,)
        for phase in plot_phases:
            if phase not in run_phases:
                raise EvalException(f"Invalid phase label {phase}. Must be in {run_phases}.")

        if evalout is not None:
            if plot_phases[0] == run_phases[0]:
                # First value (out[0]) should be inital value (evalout[0]) if the first phase
                # in 'phases' is the first run-phase.
                out.append(evalout[0])
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
            phase_endind = self.first_step_phase[1][fsp_index + 1]
            for j in range(phase_startind - 1, phase_endind - 1):
                history_out.append(self.history[2 * j])
                history_out.append(self.history[2 * j + 1])

            if False:
                for j in range(phase_startind, phase_endind):
                    if evalout is not None:
                        out.append(evalout[j])
                    enum_plls = enumerate(self.phase_line_labels_steps)
                    pll_inds = [i for i, pll in enum_plls if pll == j]  # pll 1-based
                    for pll_ind in pll_inds:
                        phase_line_labels_out.append(self.phase_line_labels[pll_ind])
                        phase_line_labels_steps_out.append(cnt)
                    cnt += 1
            else:

                if evalout is not None:
                    for j in range(phase_startind, phase_endind):
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
                    elif plls_j == phase_endind - 1:
                        plls_endind = j  # We want the last index to phase_endind-1
                    elif plls_j > phase_endind - 1:
                        break  # We need look no further
                assert(plls_startind is not None)
                assert(plls_endind is not None)

                prev_pll = None
                for j in range(plls_startind, plls_endind + 1):
                    curr_pll = self.phase_line_labels[j]
                    phase_line_labels_out.append(curr_pll)
                    phase_line_labels_steps_out.append(cnt)
                    if prev_pll != curr_pll:
                        cnt += 1
                    prev_pll = curr_pll

        return out, history_out, phase_line_labels_out, phase_line_labels_steps_out

    def _xscalefilter(self, evalout, history, phase_line_labels, phase_line_labels_steps,
                      parameters):
        eval_steps = parameters.get(kw.XSCALE)
        if eval_steps == kw.EVAL_ALL:
            return evalout
        else:
            if eval_steps in phase_line_labels:  # xscale is a phase line label
                # Because the first update is done after S->B->S'
                phase_line_labels = phase_line_labels[2:]
                phase_line_labels_steps = [x - 1 for x in phase_line_labels_steps[2:]]

                findind, cumsum = util.find_and_cumsum(phase_line_labels, eval_steps, True)
                out = [evalout[0]]  # evalout[0] must be kept
                for pll_ind, zero_or_one in enumerate(findind):
                    if zero_or_one == 1:
                        evalout_ind = phase_line_labels_steps[pll_ind]  # Zero-based index
                        out.append(evalout[evalout_ind])
                return out
            else:
                pattern = eval_steps
                pattern_len = RunOutputSubject.compute_patternlen(pattern)
                use_exact_match = (parameters.get(kw.XSCALE_MATCH) == 'exact')
                # history[2:] because the first update is done after S->B->S'
                findind, cumsum = util.find_and_cumsum(history[2:], pattern, use_exact_match)
                out = [evalout[0]]  # evalout[0] must be kept
                for history_ind, zero_or_one in enumerate(findind):
                    if zero_or_one == 1 and history_ind >= 2:
                        evalout_ind = RunOutputSubject.historyind2stepind(history_ind, pattern_len)
                        out.append(evalout[evalout_ind])
                return out

    @staticmethod
    def historyind2stepind(history_ind, pattern_len):
        step_ind = (history_ind + pattern_len - 1) // 2 + 1
        return step_ind

    @staticmethod
    def compute_patternlen(pattern):
        if type(pattern) is list:
            pattern_len = len(pattern)
        else:
            pattern_len = 1
        return pattern_len

    def v_eval(self, er, parameters):
        return self.v[er].evaluate(parameters)

    def w_eval(self, element, parameters):
        return self.w[element].evaluate(parameters)

    def p_eval(self, sr, parameters):
        """sr is a tuple (S,R) where S=(E1,E2,...)."""
        v_val = dict()
        for er in self.v:
            if er[0] in sr[0]:  # Only need to evaluate for stimulus elements in sr[0]
                v_val[er] = self.v[er]

        behaviors = list()
        nval = 0
        for er in v_val:
            v_val[er] = self.v_eval(er, parameters)
            if nval == 0:
                nval = len(v_val[er])
            behavior = er[1]
            if behavior not in behaviors:
                behaviors.append(behavior)

        out = [None] * nval
        for i in range(nval):
            v_local = util.dict_of_list_ind(v_val, i)
            out[i] = mechanism.probability_of_response(sr[0], sr[1], behaviors, self.stimulus_req,
                                                       parameters.get(kw.BETA),
                                                       parameters.get(kw.MU), v_local)
        return out

    @staticmethod
    def n_eval(seqs, history, phase_line_labels, parameters):
        seqstype = type(seqs)
        if seqstype is not tuple:
            seqs = (seqs, None)
        seq = seqs[0]
        seqref = seqs[1]
        is_exact_n_match = (parameters.get(kw.MATCH) == kw.EVAL_EXACT)
        is_cumulative = (parameters.get(kw.EVAL_CUMULATIVE) == kw.EVAL_ON)
        findind_seq, cumsum_seq = util.find_and_cumsum(history, seq, is_exact_n_match)

        xscale = parameters.get(kw.XSCALE)
        all_steps = (xscale == kw.EVAL_ALL)
        findind_steps = list()
        if not all_steps:
            if xscale in phase_line_labels:  # xscale is a phase line label
                raise Exception("xscale cannot be a phase line label in @nplot/@nexport.")
                findind_pll, _ = util.find_and_cumsum(phase_line_labels, xscale, True)

                # findind_steps has length (number of visited phase line labels, including help
                # lines) - change to len(history) by adding zeros in the response positions
                findind_steps = [0] * len(history)
                for ind_pll, zero_or_one in enumerate(findind_pll):
                    if zero_or_one == 1:
                        steps_ind = 0  # phase_line_labels_steps[ind_pll]
                        findind_steps[steps_ind] = 1
            else:
                is_exact_xscale_match = (parameters.get(kw.XSCALE_MATCH) == kw.EVAL_EXACT)
                findind_steps, _ = util.find_and_cumsum(history, xscale, is_exact_xscale_match)

        out_seq = RunOutputSubject.n_eval_out(findind_seq, cumsum_seq, findind_steps,
                                              is_cumulative, all_steps)
        if seqref is None:
            out = out_seq
        else:
            findind_seqref, cumsum_seqref = util.find_and_cumsum(history, seqref, is_exact_n_match)
            out_seqref = RunOutputSubject.n_eval_out(findind_seqref, cumsum_seqref, findind_steps,
                                                     is_cumulative, all_steps)
            out = util.arraydivide(out_seq, out_seqref)
        return [0] + out

    @staticmethod
    def n_eval_out(findind_n, cumsum, findind_steps, is_cumulative, all_steps):
        if is_cumulative:
            if all_steps:
                out = cumsum
            else:
                out = util.arrayind(cumsum, findind_steps)
        else:
            if all_steps:
                out = findind_n
            else:
                # out = util.diff(cumsum, findind_steps)
                out = util.arrayind(findind_n, findind_steps)
        return out

    def write_v(self, stimulus, response, step, mechanism):
        for element in stimulus:
            key = (element, response)
            if key not in self.v:
                self.v[key] = Val()
            self.v[key].write(mechanism.v[key], step)

    def write_w(self, stimulus, step, mechanism):
        for element in stimulus:
            key = element
            if key not in self.w:
                self.w[key] = Val()
            self.w[key].write(mechanism.w[key], step)

    def printout(self):
        print("\n")
        for key, val in self.v.items():
            print("v({0}) = {1})".format(key, val))
        for key, val in self.w.items():
            print("w({0}) = {1})".format(key, val))
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

    def evaluate(self, evalprops):
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

        # max_step = self.steps[-1]
        # out = list()
        # curr_ind = 0
        # out.append(self.values[curr_ind])  # Start value
        # for i in range(1, max_step + 1):
        #     if i in self.steps:  # XXX can be optimized
        #         curr_ind += 1
        #     out.append(self.values[curr_ind])
        # return out

    def printout(self):
        print("values: {} floats".format(len(self.values)))
        print("steps: {} ints".format(len(self.steps)))
