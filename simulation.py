import keywords as kw
from exceptions import ParseException
from output import ScriptOutput, RunOutput


class Runs():
    def __init__(self):
        # A dict with Run objects. Keys are run labels.
        self.runs = dict()

    def add(self, run_obj, label, lineno):  # , world, mechanism_obj, n_subjects):
        if label in self.runs:
            raise ParseException(lineno, f"Run label {label} is duplicated.")
        self.runs[label] = run_obj  # ScriptRun(label, world, mechanism_obj, n_subjects)

    def get(self, label):
        return self.runs[label]

    def run(self):
        out = dict()
        for label, run in self.runs.items():
            out[label] = run.run()
        return ScriptOutput(out)


class Run():
    """A class for a script run."""

    def __init__(self, world, mechanism_obj, n_subjects, bind_trials):
        # self.runlabel = runlabel
        self.world = world
        self.mechanism_obj = mechanism_obj
        self.has_w = mechanism_obj.has_w()
        self.n_subjects = n_subjects
        self.bind_trials = bind_trials

    def run(self):
        out = RunOutput(self.n_subjects, self.mechanism_obj.stimulus_req)

        stimulus_elements = self.mechanism_obj.parameters.get(kw.STIMULUS_ELEMENTS)
        behaviors = self.mechanism_obj.parameters.get(kw.BEHAVIORS)

        # Initialize output with start values
        # first_phase_label = self.world.phases[0].label
        for subject_ind in range(self.n_subjects):
            for element in stimulus_elements:
                if self.has_w:
                    out.write_w(subject_ind, (element,), 0, self.mechanism_obj)
                for behavior in behaviors:
                    out.write_v(subject_ind, (element,), behavior, 0, self.mechanism_obj)
            out.write_step(subject_ind, self.world.phases[0].label, "init", 0)

        # The actual simulation
        for subject_ind in range(self.n_subjects):
            step = 1
            subject_done = False
            response = None
            while not subject_done:
                stimulus, phase_label, phase_line_label = self.world.next_stimulus(response)
                subject_done = (stimulus is None)
                if not subject_done:
                    omit_learn = (phase_line_label.lower() == "new_trial" and self.bind_trials == "off")
                    prev_stimulus = self.mechanism_obj.prev_stimulus
                    prev_response = self.mechanism_obj.response
                    response = self.mechanism_obj.learn_and_respond(stimulus, omit_learn)

                    if prev_stimulus is not None:
                        if self.has_w:
                            out.write_w(subject_ind, prev_stimulus, step, self.mechanism_obj)
                        out.write_v(subject_ind, prev_stimulus, prev_response, step,
                                    self.mechanism_obj)
                        out.write_history(subject_ind, prev_stimulus, prev_response)
                        out.write_step(subject_ind, phase_label, phase_line_label, step)
                        step += 1
                    last_stimulus = stimulus
                    last_response = response
                else:
                    # Write last step to all variables (except the ones that were written in
                    # the last step)
                    if self.has_w:
                        for element in stimulus_elements:
                            if True:  # element not in last_stimulus:
                                out.write_w(subject_ind, (element,), step, self.mechanism_obj)
                    for element in stimulus_elements:
                        for behavior in behaviors:
                            if True:  #(element not in last_stimulus) or (behavior!=last_response):
                                out.write_v(subject_ind, (element,), behavior, step,
                                            self.mechanism_obj)
                    out.write_history(subject_ind, last_stimulus, last_response)
                    out.write_step(subject_ind, "last", "last", step)

                    # Reset mechanism and world for the next subject
                    self.mechanism_obj.subject_reset()
                    self.world.subject_reset()

        return out
