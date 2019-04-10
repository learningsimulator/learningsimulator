import matplotlib.pyplot as plt

from .testutil import LsTestCase
from parsing import Script


def run(text):
    script = Script(text)
    script.parse()
    simulation_data = script.run()
    script.postproc(simulation_data, False)
    return script, simulation_data


class TestSmall(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_chain(self):
        text = '''
        n_subjects        : 1
        mechanism         : SR
        behaviors         : b
        stimulus_elements : s1, s2
        start_v           : s1->b:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : default:0
        u                 : s1:2, default:0

        @phase ph stop:S1=4
        S1     s1     | S2
        S2     s2     | S1

        @run ph

        @figure
        xscale: all
        @nplot s1->b

        @figure
        xscale: s1->b
        @nplot s1->b
        '''
        script, simulation_data = run(text)
        history = simulation_data.run_outputs['run1'].output_subjects[0].history
        # print(simulation_data.run_outputs['run1'].output_subjects[0].phase_line_labels)
        expected_history = ['s1', 'b', 's2', 'b', 's1', 'b', 's2', 'b', 's1', 'b', 's2', 'b', 's1', 'b']
        self.assertEqual(history, expected_history)

        # xscale: all
        ax = plt.figure(1).axes
        self.assertEqual(len(ax), 1)
        ax = ax[0]

        lines = ax.get_lines()
        self.assertEqual(len(lines), 1)
        line = lines[0]
        expected_xdata = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        expected_ydata = [0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4]

        self.assertEqual(list(line.get_xdata(True)), expected_xdata)
        self.assertEqual(list(line.get_ydata(True)), expected_ydata)

        # xscale: s1->b
        ax = plt.figure(2).axes
        self.assertEqual(len(ax), 1)
        ax = ax[0]

        lines = ax.get_lines()
        self.assertEqual(len(lines), 1)
        line = lines[0]

        expected_xdata = [0, 1, 2, 3, 4]
        expected_ydata = [0, 1, 2, 3, 4]
        self.assertEqual(list(line.get_xdata(True)), expected_xdata)
        self.assertEqual(list(line.get_ydata(True)), expected_ydata)


class TestDifferentTypes(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_chain(self):
        text = '''
        n_subjects        : 1
        mechanism         : SR
        behaviors         : b
        stimulus_elements : s, reward
        start_v           : -1
        alpha_v           : 0.1
        beta              : 1
        behavior_cost     : 0
        u                 : 0

        @phase world stop:s=5
        XSTIMULUS   s          | REWARD
        REWARD      reward     | XSTIMULUS

        @run world runlabel:myrunlabel

        @figure
        xscale: b->reward ->          b
        runlabel: myrunlabel
        @nplot s->b
        '''
        script, simulation_data = run(text)
        # output = simulation_data.run_outputs["alpha01"].output_subjects[0]
        # print(simulation_data.run_outputs["myrunlabel"].output_subjects[0].history)
        self.assertEqual(len(script.script_parser.postcmds.cmds), 2)

    def test_phase_line_label(self):
        text = '''
        n_subjects        : 1
        mechanism         : SR
        behaviors         : b, b0
        stimulus_elements : s, reward
        start_v           : s->b0:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : default:0
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=60
        XSTIMULUS   s          | b: REWARD  | XSTIMULUS
        REWARD      reward     | XSTIMULUS

        @run instrumental_conditioning runlabel: alpha01

        @figure foo bar   carr
        xscale: s  # XSTIMULUS
        runlabel: alpha01
        @nplot s->b {'linewidth':2}
        '''
        script, simulation_data = run(text)
        output = simulation_data.run_outputs["alpha01"].output_subjects[0]
        history_len = len(output.history)
        self.assertTrue(history_len % 2 == 0)
        n_steps = history_len / 2
        self.assertEqual(len(output.phase_line_labels), n_steps + 1)
        self.assertEqual(output.phase_line_labels[0], "init")
        self.assertEqual(output.phase_line_labels[-1], "last")
        for eb in output.v:
            self.assertEqual(max(output.v[eb].steps), n_steps)
