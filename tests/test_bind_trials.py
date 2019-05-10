import matplotlib.pyplot as plt

import unittest
from parsing import Script
from .testutil import run, get_plot_data


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
        self.assertEqual(xmax, 100)
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
        self.assertEqual(xmax, 100)
        self.assertLessEqual(ymin, 0)
        self.assertGreater(ymax, 20.0, 1)
        self.assertLess(ymax, 30.0, 1)

    def test_new_trial_is_help_line(self):
        script = '''
        n_subjects             : 25
        mechanism              : GA
        behaviors              : cr,ignore  # ur = cr, cr1=cr2
        stimulus_elements      : us,cs1,cs2,none
        start_v                : default: 0
        alpha_v                : cs1->ignore: 0.0, cs2->ignore: 0.0, default: 0.05
        # alpha_w                : us: 0, none:0, default: 0.05
        alpha_w                : 0.05
        beta                   : 1
        behavior_cost          : cr:1, default: 0
        u                      : us:5, default: 0
        bind_trials            : off
        #start_w                : 1.42

        @phase Both_paired  stop: new_trial=10
        new_trial        | CS1(0.5) | NONE
        CS1      cs1     | CS2
        CS2      cs2        | US
        US       us      | new_trial
        NONE     none    | new_trial

        @phase Only_CS2_US_paired(Both_paired)   stop: new_trial=10
        new_trial        | CS1(0.5),CS2(0.5)
        CS1      cs1     | NONE

        @phase Only_CS1_CS2_paired(Both_paired)   stop: new_trial=10
        new_trial        | CS1(0.5),US(0.5)
        CS2      cs2     | NONE

        @run Both_paired           runlabel: Both_paired
        @run Only_CS2_US_paired    runlabel: Only_CS2_US_paired
        @run Only_CS1_CS2_paired   runlabel: Only_CS1_CS2_paired

        @figure
        xscale: new_trial
        subject: average

        runlabel: Both_paired
        @wplot us {'label':'us_Both_paired'}
        @wplot none {'label':'none_Both_paired'}

        runlabel: Only_CS2_US_paired
        @wplot us {'label':'us_Only_CS2_US_paired'}
        @wplot none {'label':'none_Only_CS2_US_paired'}

        runlabel: Only_CS1_CS2_paired
        @wplot us {'label':'us_Only_CS1_CS2_paired'}
        @wplot none {'label':'none_Only_CS1_CS2_paired'}
        @legend
        '''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()
        zeros = [0] * 9
        self.assertEqual(plot_data['us_Both_paired']['y'], zeros)
        self.assertEqual(plot_data['none_Both_paired']['y'], zeros)
        self.assertEqual(plot_data['us_Only_CS2_US_paired']['y'], zeros)
        self.assertEqual(plot_data['none_Only_CS2_US_paired']['y'], zeros)
        self.assertEqual(plot_data['us_Only_CS1_CS2_paired']['y'], zeros)
        self.assertEqual(plot_data['none_Only_CS1_CS2_paired']['y'], zeros)

        # Minimal example of new_trial being help line and xscale:new_trial
        plt.close('all')
        script = '''
        mechanism              : GA
        behaviors              : cr,ignore
        stimulus_elements      : us,cs1,cs2,none
        start_w                : 1.4

        @phase foo stop: new_trial=4
        new_trial        | NONE
        NONE     none    | new_trial

        @run foo

        @figure
        xscale: new_trial
        @wplot us
        '''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['y'], [1.4] * 3)

        # Minimal example of new_trial being help line and xscale:all
        plt.close('all')
        script = '''
        mechanism              : GA
        behaviors              : cr,ignore
        stimulus_elements      : us,cs1,cs2,none
        start_w: 1.4

        @phase foo stop: new_trial=4
        new_trial        | NONE
        NONE     none    | new_trial

        @run foo

        @figure
        xscale: all
        @wplot us
        '''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['y'], [1.4] * 3)

        # Add a stimulus to new_trial, and plot will contain one more point
        plt.close('all')
        script = '''
        mechanism              : GA
        behaviors              : cr,ignore
        stimulus_elements      : us,cs1,cs2,none
        start_w: 1.4

        @phase foo stop: new_trial=4
        new_trial us      | NONE
        NONE      none    | new_trial

        @run foo

        @figure
        xscale: new_trial
        @wplot us
        '''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['y'], [1.4] * 4)

    def test_home_made_bind_off_with_alpha_w(self):
        script = '''
        n_subjects             : 25
        mechanism              : GA
        behaviors              : cr,ignore  # ur = cr, cr1=cr2
        stimulus_elements      : us,cs1,cs2,none
        start_v                : default: 0
        alpha_v                : cs1->ignore: 0.0, cs2->ignore: 0.0, default: 0.05
        alpha_w                : us: 0, none:0, default: 0.05
        # alpha_w                : 0.05
        beta                   : 1
        behavior_cost          : cr:1, default: 0
        u                      : us:5, default: 0
        bind_trials            : on

        @phase Both_paired  stop: new_trial=10
        new_trial        | CS1(0.5) | NONE
        CS1      cs1     | CS2
        CS2      cs2        | US
        US       us      | new_trial
        NONE     none    | new_trial

        @phase Only_CS2_US_paired(Both_paired)   stop: new_trial=10
        new_trial        | CS1(0.5),CS2(0.5)
        CS1      cs1     | NONE

        @phase Only_CS1_CS2_paired(Both_paired)   stop: new_trial=10
        new_trial        | CS1(0.5),US(0.5)
        CS2      cs2     | NONE

        @run Both_paired           runlabel: Both_paired
        @run Only_CS2_US_paired    runlabel: Only_CS2_US_paired
        @run Only_CS1_CS2_paired   runlabel: Only_CS1_CS2_paired

        @figure
        xscale: new_trial
        subject: average

        runlabel: Both_paired
        @wplot us {'label':'us_Both_paired'}
        @wplot none {'label':'none_Both_paired'}

        runlabel: Only_CS2_US_paired
        @wplot us {'label':'us_Only_CS2_US_paired'}
        @wplot none {'label':'none_Only_CS2_US_paired'}

        runlabel: Only_CS1_CS2_paired
        @wplot us {'label':'us_Only_CS1_CS2_paired'}
        @wplot none {'label':'none_Only_CS1_CS2_paired'}
        @legend
        '''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()
        zeros = [0] * 9
        self.assertEqual(plot_data['us_Both_paired']['y'], zeros)
        self.assertEqual(plot_data['none_Both_paired']['y'], zeros)
        self.assertEqual(plot_data['us_Only_CS2_US_paired']['y'], zeros)
        self.assertEqual(plot_data['none_Only_CS2_US_paired']['y'], zeros)
        self.assertEqual(plot_data['us_Only_CS1_CS2_paired']['y'], zeros)
        self.assertEqual(plot_data['none_Only_CS1_CS2_paired']['y'], zeros)
