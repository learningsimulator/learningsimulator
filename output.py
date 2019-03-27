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

    def vwpn_eval(self, vwpn, expr, parameters):
        if vwpn == 'n':
            _, history = self._phasefilter(None, parameters)
            return RunOutputSubject.n_eval(expr, history, parameters)
        else:
            switcher = {
                'v': self.v_eval,
                'w': self.w_eval,
                'p': self.p_eval,
            }
            fun = switcher[vwpn]
            funout = fun(expr, parameters)
            funout, history = self._phasefilter(funout, parameters)
            return self.stepsfilter(funout, history, parameters)

    def _phasefilter(self, evalout, parameters):
        """
        Filter evalout (output from {v,w,p}-eval) as well as self.history w.r.t. the parameter
        'phase'.
        """
        phases = parameters.get(kw.EVAL_PHASES)
        if phases == kw.EVAL_ALL:
            return evalout, self.history
        else:
            out = list()
            history_out = list()
            if type(phases) is not list:
                phases = (phases,)
            for phase in phases:
                if phase not in self.first_step_phase[0]:
                    raise EvalException(f"Invalid phase label {phase}.")
            for phase in phases:
                fsp_index = self.first_step_phase[0].index(phase)
                phase_startind = self.first_step_phase[1][fsp_index]
                phase_endind = self.first_step_phase[1][fsp_index + 1]  # - 1
                for j in range(phase_startind, phase_endind):
                    history_out.append(self.history[2 * j])
                    history_out.append(self.history[2 * j + 1])
                    if evalout is not None:
                        out.append(evalout[j])
            return out, history_out

    def stepsfilter(self, evalout, history, parameters):
        eval_steps = parameters.get(kw.XSCALE)
        if eval_steps == kw.EVAL_ALL:
            return evalout
        else:
            pattern = eval_steps
            pattern_len = RunOutputSubject.compute_patternlen(pattern)
            use_exact_match = (parameters.get(kw.XSCALE_MATCH) == 'exact')
            findind, cumsum = util.find_and_cumsum(history, pattern, use_exact_match)
            n_matches = cumsum[-1]
            out = [None] * n_matches
            out_ind = 0
            for history_ind, zero_or_one in enumerate(findind):
                if zero_or_one == 1:
                    evalout_ind = RunOutputSubject.historyind2stepind(history_ind, pattern_len)
                    out[out_ind] = evalout[evalout_ind]
                    out_ind += 1
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

    def v_eval(self, er, parameters):
        return self.v[er].evaluate(parameters)

    def w_eval(self, element, parameters):
        return self.w[element].evaluate(parameters)

    def p_eval(self, sr, parameters):
        '''sr is a tuple (S,R) where S=(E1,E2,...).'''
        v_val = dict(self.v)
        behaviors = list()
        nval = 0
        for er, _ in v_val.items():
            v_val[er] = self.v_eval(er, parameters)
            if nval == 0:
                nval = len(v_val[er])
            behavior = er[1]
            if behavior not in behaviors:
                behaviors.append(behavior)

        out = [None] * nval
        for i in range(nval):
            v_local = util.dict_of_list_ind(v_val, i)
            out[i] = mechanism.probability_of_response(sr[0], sr[1], behaviors,
                                                       self.stimulus_req, parameters.get(kw.BETA),
                                                       v_local)
        return out

    @staticmethod
    def n_eval(seqs, history, parameters):
        seqstype = type(seqs)
        if seqstype is not tuple:
            seqs = (seqs, None)
        seq = seqs[0]
        seqref = seqs[1]
        exact_n = (parameters.get(kw.MATCH) == kw.EVAL_EXACT)
        cumulative = (parameters.get(kw.EVAL_CUMULATIVE) == kw.EVAL_ON)
        findind_seq, cumsum_seq = util.find_and_cumsum(history, seq, exact_n)

        steps = parameters.get(kw.XSCALE)
        all_steps = (steps == kw.EVAL_ALL)
        findind_steps = None
        if not all_steps:
            exact_steps = (parameters.get(kw.XSCALE_MATCH) == kw.EVAL_EXACT)
            findind_steps, _ = util.find_and_cumsum(history, steps, exact_steps)

        args = [findind_steps, cumulative, all_steps]
        out_seq = RunOutputSubject.n_eval_out(findind_seq, cumsum_seq, *args)
        if seqref is None:
            out = out_seq
        else:
            findind_seqref, cumsum_seqref = util.find_and_cumsum(history, seqref, exact_n)
            out_seqref = RunOutputSubject.n_eval_out(findind_seqref, cumsum_seqref, *args)
            out = util.arraydivide(out_seq, out_seqref)
        return [0] + out

    @staticmethod
    def n_eval_out(findind, cumsum, findind_steps, cumulative, all_steps):
        if cumulative:
            if all_steps:
                out = cumsum
            else:
                out = util.arrayind(cumsum, findind_steps)
        else:
            if all_steps:
                out = findind
            else:
                out = util.diff(cumsum, findind_steps)
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
        for key, val in self.v.items():
            print("v({0}) = {1})".format(key, val))
        for key, val in self.w.items():
            print("w({0}) = {1})".format(key, val))
        print("history=")
        print(self.history)


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
