import matplotlib.pyplot as plt

import unittest
from parsing import Script


class TestPlots(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_wplot(self):
        script = '''
        n_subjects        : 1
        mechanism         : GA
        behaviors         : R0, R1, R2
        stimulus_elements : S1, S2, reward, reward2
        start_v           : default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : R1:1, R2:1, default:0
        u                 : reward:10, default: 0
        bind_trials       : off

        @phase chaining stop:reward=100
        NEW_TRIAL   S1         | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  S2         | R2: REWARD         | NEW_TRIAL
        REWARD     reward      | NEW_TRIAL

        @run chaining
        xscale: reward
        @wplot S1

        bind_trials: on
        @run chaining
        @figure
        @wplot S1
        '''
        script_obj = Script(script)
        script_obj.parse()
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)

        axw = plt.figure(1).axes
        self.assertEqual(len(axw), 1)
        axw = axw[0]
        lines = axw.get_lines()
        self.assertEqual(len(lines), 1)

        w_S1_off = lines[0]
        xmin = w_S1_off.get_xdata(True).min(0)
        xmax = w_S1_off.get_xdata(True).max(0)
        ymin = w_S1_off.get_ydata(True).min(0)
        ymax = w_S1_off.get_ydata(True).max(0)
        self.assertEqual(xmin, 0)
        self.assertEqual(xmax, 99)
        self.assertLessEqual(ymin, 0)
        self.assertAlmostEqual(ymax, 8, 2)

        axw = plt.figure(2).axes
        self.assertEqual(len(axw), 1)
        axw = axw[0]
        lines = axw.get_lines()
        self.assertEqual(len(lines), 1)

        w_S1_on = lines[0]
        xmin = w_S1_on.get_xdata(True).min(0)
        xmax = w_S1_on.get_xdata(True).max(0)
        ymin = w_S1_on.get_ydata(True).min(0)
        ymax = w_S1_on.get_ydata(True).max(0)
        self.assertEqual(xmin, 0)
        self.assertEqual(xmax, 99)
        self.assertLessEqual(ymin, 0)
        self.assertGreater(ymax, 20.0, 1)
        self.assertLess(ymax, 30.0, 1)
