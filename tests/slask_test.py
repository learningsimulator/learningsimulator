import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestPlotProperties(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

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
        #output.printout()
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
