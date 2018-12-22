class Phases:
    def __init__(self):
        # Keys are phase labels, values are Phase objects
        self.phases = dict()

    def contains(self, script_label):
        return script_label in self.phases

    def all_labels(self):
        """Return all phase labels as a set."""
        return set(self.phases.keys())

    def add_phase(self, phase_label, phase):
        self.script_phases[phase_label] = phase

    def append_row(self, phase_label, row, lineno):
        self.phases[phase_label].append_row(row, lineno)

    def parse_phase(self, phase_label):
        self.phases[phase_label].parse()


class Phase:
    def __init__(self, line, lineno):
        self.rows = list()
        self.linenos = list()
        self.append_row(line, lineno)

    def append_row(self, row, lineno):
        self.rows.append(row)
        self.linenos.append(lineno)

    def nrows(self):
        return len(self.rows)

    def parse(self):
        pass  # XXX
