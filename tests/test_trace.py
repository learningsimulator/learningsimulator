import matplotlib.pyplot as plt

import unittest
from .testutil import run, get_plot_data


class TestBasic(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_sr(self):
        pass
#         script = '''
# n_subjects            : 200
# mechanism             : sr
# behaviors             : approach,eat,other
# stimulus_elements     : plant,berry,sugar,no_reward
# response_requirements : approach:plant, eat:berry
# start_v               : plant->other:0, berry->other:0, default:-1
# alpha_v               : 0.1
# alpha_w               : 0.1
# beta                  : 1
# behavior_cost         : approach:1, default: 0
# u                     : sugar:10, default:0
# bind_trials           : off

# @phase acquisition stop: plant=200
# new_trial                 | PLANT
# PLANT          plant      | approach: BERRY    |  new_trial
# BERRY          berry      | eat: REWARD        |  NO_REWARD
# REWARD         sugar      | new_trial
# NO_REWARD      no_reward  | new_trial

# @run acquisition runlabel:notrace

# trace: 0
# @run acquisition runlabel:trace=0

# trace: 0.2
# @run acquisition runlabel:trace=0.2

# trace: 0.4
# @run acquisition runlabel:trace=0.4

# trace: 0.6
# @run acquisition runlabel:trace=0.6

# trace: 0.8
# @run acquisition runlabel:trace=0.8

# trace: 1
# @run acquisition runlabel:trace=1

# xscale: plant
# subject: average

# runlabel: notrace
# @pplot plant->approach {'label':'notrace'}

# runlabel: trace=0
# @pplot plant->approach {'label':'trace=0'}

# runlabel: trace=0.2
# @pplot plant->approach {'label':'trace=0.2'}

# runlabel: trace=0.4
# @pplot plant->approach {'label':'trace=0.4'}

# runlabel: trace=0.6
# @pplot plant->approach {'label':'trace=0.6'}

# runlabel: trace=0.8
# @pplot plant->approach {'label':'trace=0.8'}

# runlabel: trace=1
# @pplot plant->approach {'label':'trace=1'}

# @legend
# '''
#         script_obj, script_output = run(script)
#         plot_data = get_plot_data()

#         # Check that the plot for notrace and trace=0 are the same
#         self.assertEqual(plot_data['notrace']['x'], plot_data['trace=0']['x'])
#         self.assertEqual(len(plot_data['notrace']['y']), len(plot_data['trace=0']['y']))
#         for yno, y0 in zip(plot_data['notrace']['y'], plot_data['trace=0']['y']):
#             self.assertAlmostEqual(yno, y0, places=4)

#         # Store all pplot end-values in end_value
#         end_value = dict()
#         for lbl in plot_data:
#             end_value[lbl] = plot_data[lbl]['y'][-1]
#             self.assertLessEqual(end_value[lbl], 1)
#             self.assertGreaterEqual(end_value[lbl], 0)

#         # Check that the start values (x=0) are all the same


#         # Check that the end-values increase with trace
#         self.assertLess(end_value['trace=0'], end_value['trace=0.2'])
#         self.assertLess(end_value['trace=0.2'], end_value['trace=0.4'])
#         self.assertLess(end_value['trace=0.4'], end_value['trace=0.6'])
#         self.assertLess(end_value['trace=0.6'], end_value['trace=0.8'])
#         self.assertLess(end_value['trace=0.8'], end_value['trace=1'])
