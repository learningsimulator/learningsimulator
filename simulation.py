import keywords as kw
from exceptions import ParseException, InterruptedSimulation
from output import ScriptOutput, RunOutput


class Runs():
    def __init__(self):
        # A dict with Run objects. Keys are run labels.
        self.runs = dict()

        # The run labels respecting the order in which they were added
        self.run_labels = list()

    def add(self, run_obj, label, lineno):  # , world, mechanism_obj, n_subjects):
        if label in self.runs:
            raise ParseException(lineno, f"Run label {label} is duplicated.")
        self.run_labels.append(label)
        self.runs[label] = run_obj  # ScriptRun(label, world, mechanism_obj, n_subjects)

    def get(self, label):
        return self.runs[label]

    def get_n_subjects(self):
        """Return a list containing the number of subjects in each run."""
        return [self.runs[run_label].n_subjects for run_label in self.run_labels]

    def get_n_phases(self):
        """Return a dict containing the number of phases in each run."""
        n_phases_dict = dict()
        for run_label in self.run_labels:
            n_phases_dict[run_label] = len(self.runs[run_label].world.phases)
        return n_phases_dict

    def all_runs_have_length(self, length):
        n_phases_dict = self.get_n_phases()
        for _, n_phases in n_phases_dict.items():
            if n_phases != length:
                return False
        return True

    def run(self, progress=None):
        out = dict()
        for label in self.run_labels:
            run = self.runs[label]
            if progress:
                progress.report1(f"Running {label}")
            out[label] = run.run(progress)

        # for label, run in self.runs.items():
        #     progress.report(1, f"Running {label}")
        #     out[label] = run.run(progress)

        return ScriptOutput(out)


class Run():
    """A class for a script run."""

    def __init__(self, run_label, world, mechanism_obj, n_subjects, bind_trials):
        self.run_label = run_label
        self.world = world
        self.mechanism_obj = mechanism_obj
        self.has_v = mechanism_obj.has_v()
        self.has_w = mechanism_obj.has_w()
        self.has_vss = mechanism_obj.has_vss()
        self.n_subjects = n_subjects
        self.bind_trials = bind_trials

    def run(self, progress=None):
        out = RunOutput(self.n_subjects, self.mechanism_obj)

        stimulus_elements = self.mechanism_obj.parameters.get(kw.STIMULUS_ELEMENTS)
        behaviors = self.mechanism_obj.parameters.get(kw.BEHAVIORS)
        is_bind_off = (self.bind_trials == "off")

        # Initialize output with start values
        for subject_ind in range(self.n_subjects):
            for element in stimulus_elements:
                if self.has_w:
                    out.write_w(subject_ind, {element: 1}, 0, self.mechanism_obj)
                if self.has_v:
                    for behavior in behaviors:
                        out.write_v(subject_ind, {element: 1}, behavior, 0, self.mechanism_obj)
                if self.has_vss:
                    for element2 in stimulus_elements:
                        out.write_vss(subject_ind, {element: 1}, {element2: 1}, 0, self.mechanism_obj)
            # out.write_step(subject_ind, self.world.phases[0].label, 0)

        # The actual simulation
        for subject_ind in range(self.n_subjects):
            prev_phase_label = None  # For phases progress
            if progress:
                if progress.get_n_runs() > 1:
                    progress.report1(f"{self.run_label}: Simulating subject {subject_ind + 1}")
                else:
                    progress.report1(f"Simulating subject {subject_ind + 1}")
                progress.reset2()
                progress.report2("")
            step = 1
            subject_done = False
            response = None
            while not subject_done:
                if progress and progress.stop_clicked:
                    raise InterruptedSimulation()
                stimulus, phase_label, phase_line_label, preceeding_help_lines = self.world.next_stimulus(response)
                if progress:
                    if phase_label != prev_phase_label:  # Update phases progress
                        progress.increment2(self.run_label)
                        progress.report2(f"Phase {phase_label}")
                        prev_phase_label = phase_label

                subject_done = (stimulus is None)
                if not subject_done:
                    is_new_trial = (phase_line_label.lower() == "new_trial")
                    lower_phh = [x.lower() for x in preceeding_help_lines]
                    omit_learn = is_bind_off and (is_new_trial or ("new_trial" in lower_phh))
                    prev_stimulus = self.mechanism_obj.prev_stimulus
                    prev_response = self.mechanism_obj.response
                    response = self.mechanism_obj.learn_and_respond(stimulus, omit_learn)

                    if prev_stimulus is not None:
                        if self.has_w:
                            out.write_w(subject_ind, prev_stimulus, step, self.mechanism_obj)
                        if self.has_v:
                            out.write_v(subject_ind, prev_stimulus, prev_response, step,
                                        self.mechanism_obj)
                        if self.has_vss:
                            # Loop since *all* vss[(prev_stimulus,*)] is set in
                            # OriginalRescorlaWagner.learn_and_respond, not only
                            # vss[(prev_stimulus,stimulus)]
                            for e in stimulus_elements:
                                out.write_vss(subject_ind, prev_stimulus, {e: 1}, step,
                                              self.mechanism_obj)
                        out.write_history(subject_ind, prev_stimulus, prev_response)
                        phase_step = step
                        if step > 1:
                            phase_step = step + 1
                        out.write_step(subject_ind, phase_label, phase_step)
                        step += 1
                    out.write_phase_line_label(subject_ind, phase_line_label, step,
                                               preceeding_help_lines)
                    last_stimulus = dict(stimulus)  # XXX dict ok?
                    last_response = response
                else:
                    step -= 1
                    # Write last step to all variables
                    if self.has_w:
                        for element in stimulus_elements:
                            out.write_w(subject_ind, (element,), step, self.mechanism_obj)
                    if self.has_v:
                        for element in stimulus_elements:
                            for behavior in behaviors:
                                out.write_v(subject_ind, {element: 1}, behavior, step,
                                            self.mechanism_obj)

                    if self.has_vss:
                        for element1 in stimulus_elements:
                            for element2 in stimulus_elements:
                                out.write_vss(subject_ind, {element1: 1}, {element2: 1}, step,
                                              self.mechanism_obj)

                    out.write_history(subject_ind, last_stimulus, last_response)
                    out.write_step(subject_ind, "last", step + 2)

                    # Reset mechanism and world for the next subject
                    self.mechanism_obj.subject_reset()
                    self.world.subject_reset()
            if progress:
                progress.increment1()
        return out
