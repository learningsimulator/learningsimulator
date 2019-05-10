import matplotlib.pyplot as plt

from .testutil import LsTestCase, get_plot_data
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
        self.assertEqual(len(script.script_parser.postcmds.cmds), 2)

    def test_phase_line_label_ref1(self):
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
        XSTIMULUS   s          | REWARD
        REWARD      reward     | XSTIMULUS

        @run instrumental_conditioning runlabel: alpha01

        @figure
        runlabel: alpha01

        xscale: s
        @pplot s->b

        xscale: XSTIMULUS
        @pplot s->b
        '''
        script, simulation_data = run(text)
        output = simulation_data.run_outputs["alpha01"].output_subjects[0]
        history_len = len(output.history)
        self.assertEqual(history_len, 4 * 59 + 2)
        n_steps = history_len / 2
        self.assertEqual(len(output.phase_line_labels), n_steps)
        for eb in output.v:
            self.assertEqual(max(output.v[eb].steps), n_steps - 1)

        ax = plt.figure(1).axes
        self.assertEqual(len(ax), 1)
        ax = ax[0]

        lines = ax.get_lines()
        self.assertEqual(len(lines), 2)
        line1 = lines[0]
        line2 = lines[1]
        self.assertEqual(list(line1.get_xdata(True)), list(line2.get_xdata(True)))
        self.assertEqual(list(line1.get_ydata(True)), list(line2.get_ydata(True)))

    def test_phase_line_label_ref2(self):
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
        XSTIMULUS   s          | REWARD
        REWARD      reward     | XSTIMULUS

        @run instrumental_conditioning runlabel: alpha01

        @figure
        runlabel: alpha01

        xscale: reward
        @pplot s->b

        xscale: REWARD
        @pplot s->b
        '''
        script, simulation_data = run(text)
        output = simulation_data.run_outputs["alpha01"].output_subjects[0]
        history_len = len(output.history)
        self.assertEqual(history_len, 4 * 59 + 2)
        n_steps = history_len / 2
        self.assertEqual(len(output.phase_line_labels), n_steps)
        for eb in output.v:
            # n_steps-1 since no update is done after first exposure to s
            self.assertEqual(max(output.v[eb].steps), n_steps - 1)

        ax = plt.figure(1).axes
        self.assertEqual(len(ax), 1)
        ax = ax[0]

        lines = ax.get_lines()
        self.assertEqual(len(lines), 2)
        line1 = lines[0]
        line2 = lines[1]
        self.assertEqual(list(line1.get_xdata(True)), list(line2.get_xdata(True)))
        self.assertEqual(list(line1.get_ydata(True)), list(line2.get_ydata(True)))

    def test_phase_line_label_ref3(self):
        text = '''
        n_subjects        : 1
        mechanism         : GA
        behaviors         : b, b0
        stimulus_elements : s, reward
        start_v           : s->b0:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : default:0
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=6
        XSTIMULUS   s          | REWARD
        REWARD      reward     | XSTIMULUS

        @run instrumental_conditioning runlabel: alpha01
        runlabel: alpha01

        @figure
        xscale: reward
        @pplot s->b {'label':'p_reward'}
        xscale: REWARD
        @pplot s->b {'label':'p_REWARD'}

        @figure
        xscale: reward
        @vplot s->b {'label':'v_reward'}
        xscale: REWARD
        @vplot s->b {'label':'v_REWARD'}

        @figure
        xscale: reward
        @wplot s {'label':'w_reward'}
        xscale: REWARD
        @wplot s {'label':'w_REWARD'}

        # Issue #32
        # @figure
        # xscale: reward
        # @nplot b0 {'label':'n_reward'}
        # xscale: REWARD
        # @nplot b0 {'label':'n_REWARD'}
        '''
        run(text)

        plot_data = get_plot_data(1, 1)
        self.assertEqual(len(plot_data), 2)
        self.assertEqual(plot_data['p_reward']['x'], plot_data['p_REWARD']['x'])
        self.assertEqual(plot_data['p_reward']['y'], plot_data['p_REWARD']['y'])

        plot_data = get_plot_data(2, 1)
        self.assertEqual(len(plot_data), 2)
        self.assertEqual(plot_data['v_reward']['x'], plot_data['v_REWARD']['x'])
        self.assertEqual(plot_data['v_reward']['y'], plot_data['v_REWARD']['y'])

        plot_data = get_plot_data(3, 1)
        self.assertEqual(len(plot_data), 2)
        self.assertEqual(plot_data['w_reward']['x'], plot_data['w_REWARD']['x'])
        self.assertEqual(plot_data['w_reward']['y'], plot_data['w_REWARD']['y'])

        # Issue #32
        # plot_data = get_plot_data(4, 1)
        # self.assertEqual(len(plot_data), 2)
        # self.assertEqual(plot_data['n_reward']['x'], plot_data['n_REWARD']['x'])
        # self.assertEqual(plot_data['n_reward']['y'], plot_data['n_REWARD']['y'])
