import copy
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import keywords as kw
from exceptions import InterruptedSimulation
from output import ScriptOutput, RunOutput, RunOutputSubject
import compute


def _run_one_subject(subject_ind, world, mechanism_obj, run_label, bind_trials,
                     has_v, has_w, has_vss, progress_queue, stop_event):
    """Simulate a single subject.

    Each call receives its own deep-copied world and mechanism_obj so
    threads do not share mutable simulation state.
    """

    def _omit_learn_using_new_trial(phase_line_label, preceeding_help_lines, is_bind_off):
        is_new_trial = (phase_line_label.lower() == "new_trial")
        lower_phh = [x.lower() for x in preceeding_help_lines]
        return is_bind_off and (is_new_trial or ("new_trial" in lower_phh))

    # Set random seed
    seed = mechanism_obj.parameters.get(kw.RANDOM_SEED)
    if seed is not None:
        random.seed(int(seed) + subject_ind)

    # Reset mechanism and world for this subject
    mechanism_obj.subject_reset()
    world.subject_reset()

    prev_phase_label = None
    out = RunOutputSubject(mechanism_obj.stimulus_req)

    stimulus_elements = mechanism_obj.parameters.get(kw.STIMULUS_ELEMENTS)
    behaviors = mechanism_obj.parameters.get(kw.BEHAVIORS)
    is_bind_off = (bind_trials == "off")

    # Initialize output with start values
    for element in stimulus_elements:
        if has_w:
            out.write_w({element: 1}, 0, mechanism_obj)
        if has_v:
            for behavior in behaviors:
                out.write_v({element: 1}, behavior, 0, mechanism_obj)
        if has_vss:
            for element2 in stimulus_elements:
                out.write_vss({element: 1}, {element2: 1}, 0, mechanism_obj)

    if progress_queue is not None:
        progress_queue.put(("report1", f"{run_label}: Simulating subject {subject_ind + 1}"))
        progress_queue.put(("reset2",))
        progress_queue.put(("report2", ""))

    step = 1
    subject_done = False
    response = None
    while not subject_done:
        if stop_event is not None and stop_event.is_set():
            raise InterruptedSimulation()

        next_stimulus_out = world.next_stimulus(response)
        stimulus, phase_label, phase_line_label, preceeding_help_lines, omit_learn, variables, preceding_help_line_variables = next_stimulus_out

        if phase_label != prev_phase_label:
            if progress_queue is not None:
                progress_queue.put(("increment2", run_label))
                progress_queue.put(("report2", f"Phase {phase_label}"))
            prev_phase_label = phase_label

        subject_done = (stimulus is None)

        if not subject_done:
            omit_learn_using_new_trial = _omit_learn_using_new_trial(
                phase_line_label, preceeding_help_lines, is_bind_off)
            omit_learn = (omit_learn or omit_learn_using_new_trial)

            prev_stimulus = mechanism_obj.prev_stimulus
            prev_response = mechanism_obj.response
            response = mechanism_obj.learn_and_respond(stimulus, omit_learn)

            if prev_stimulus is not None:
                if has_w:
                    out.write_w(prev_stimulus, step, mechanism_obj)
                if has_v:
                    out.write_v(prev_stimulus, prev_response, step, mechanism_obj)
                if has_vss:
                    for e in stimulus_elements:
                        out.write_vss(prev_stimulus, {e: 1}, step, mechanism_obj)
                out.write_history(prev_stimulus, prev_response)
                phase_step = step
                if step > 1:
                    phase_step = step + 1
                out.write_step(phase_label, phase_step)
                step += 1
            out.write_phase_line_label(phase_line_label, step, preceeding_help_lines)
            out.write_variables(variables, step, preceding_help_line_variables)
            last_stimulus = dict(stimulus)
            last_response = response
        else:
            step -= 1
            if has_w:
                for element in stimulus_elements:
                    out.write_w((element,), step, mechanism_obj)
            if has_v:
                for element in stimulus_elements:
                    for behavior in behaviors:
                        out.write_v({element: 1}, behavior, step, mechanism_obj)
            if has_vss:
                for element1 in stimulus_elements:
                    for element2 in stimulus_elements:
                        out.write_vss({element1: 1}, {element2: 1}, step, mechanism_obj)

            out.write_history(last_stimulus, last_response)
            out.write_step("last", step + 2)

    if progress_queue is not None:
        progress_queue.put(("increment1",))
    return out


class Runs():
    def __init__(self):
        self.runs = dict()
        self.run_labels = list()

    def add(self, run_obj, label):
        self.run_labels.append(label)
        self.runs[label] = run_obj

    def get(self, label):
        return self.runs[label]

    def get_last_run_obj(self):
        last_run_label = self.run_labels[-1]
        return self.runs[last_run_label]

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

    def run(self):
        out = dict()
        for label in self.run_labels:
            run = self.runs[label]
            compute.progress_queue.put(("report1", f"Running {label}"))
            out[label] = run.run()
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

    def _submit_subject(self, subject_ind):
        """Run a single subject with its own deep-copied state."""
        return _run_one_subject(
            subject_ind,
            copy.deepcopy(self.world),
            copy.deepcopy(self.mechanism_obj),
            self.run_label,
            self.bind_trials,
            self.has_v,
            self.has_w,
            self.has_vss,
            compute.progress_queue,
            compute.stop,
        )

    def run(self):
        out = RunOutput(self.n_subjects, self.mechanism_obj)

        # When a random_seed is set, subjects must run sequentially so
        # that each subject's random.seed(seed + i) produces reproducible
        # results (threads share the global random state).
        has_seed = self.mechanism_obj.parameters.get(kw.RANDOM_SEED) is not None
        use_threads = self.n_subjects > 1 and not has_seed

        if not use_threads:
            for i in range(self.n_subjects):
                out.output_subjects[i] = self._submit_subject(i)
        else:
            max_workers = min(self.n_subjects, 8)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._submit_subject, i): i
                    for i in range(self.n_subjects)
                }
                for future in as_completed(futures):
                    i = futures[future]
                    out.output_subjects[i] = future.result()

        # Drain any leftover progress messages
        while not compute.progress_queue.empty():
            try:
                compute.progress_queue.get_nowait()
            except Exception:
                break

        return out
