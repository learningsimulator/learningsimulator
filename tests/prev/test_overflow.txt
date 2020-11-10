import matplotlib.pyplot as plt

import unittest
import LsScript
from tests.LsTestUtil import check_run_output_subject


class TestOverflow(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_bug(self):
        script = '''
            @parameters
            {
            'subjects'          : 100,
            'mechanism'         : 'GA',
            'behaviors'         : ['move_away','stay'],
            'stimulus_elements' : ['new_trial', 'end_stim', 's1','neutral'],
            'start_v'           : {'default':0},
            'alpha_v'           : 0.3,
            'alpha_w'           : 0.3,
            'beta'              : 1,
            'u'                 : {'s1':-2, 'default': 0},
            'omit_learning'     : ['new_trial']
            }

            @phase {'end': 'new_trial=100'}
            NEW_TRIAL 'new_trial' | S1
            S1        's1'        | 'move_away': NEUTRAL  | S1
            NEUTRAL   'neutral'   | END
            END       'end_stim'  | NEW_TRIAL

            @run {'label':'1'}

            @parameters
            {
            'u' : {'s1':-5, 'neutral':0, 'default': 0}
            }

            @run {'label':'2'}

            @parameters
            {
            'u' : {'s1':-20, 'neutral':0, 'default': 0}
            }

            @run {'label':'3'}


            #@figure 'Prob.'
            #@pplot ('s1','move_away') {'steps': 'new_trial'}
            #@pplot ('s1','stay')      {'steps': 'new_trial'}
            #@legend

            @figure 'v'
            @vplot ('s1','stay') {'runlabel':'1'} #{'steps': 'new_trial'}
            @vplot ('s1','stay') {'runlabel':'2'} #{'steps': 'new_trial'}
            @vplot ('s1','stay') {'runlabel':'3'} #{'steps': 'new_trial'}
            @legend ('1','2','3')

            #@figure 'w'
            #@wplot 's1'       {'steps': 'new_trial'}
            #@wplot 'neutral'  {'steps': 'new_trial'}
            #@legend

            #@figure 'Frequencies of behavior'
            #@nplot 'move_away'  {'runlabel':'1', 'steps': 'new_trial'}
            #@nplot ['s1','stay']       {'runlabel':'1','cumulative':'on'}
            #@nplot ['s1','stay']       {'runlabel':'2','cumulative':'on'}
            #@nplot ['s1','stay']       {'runlabel':'3','cumulative':'on'}
            #@legend
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)
        plt.show(block=False)
        _, y1 = self.get_plotdata(1, 0, 0)
        _, y2 = self.get_plotdata(1, 0, 1)
        _, y3 = self.get_plotdata(1, 0, 2)
        shortest_len = min([len(y1), len(y2), len(y3)])
        self.assertGreater(shortest_len, 100)
        y1t = y1[100:shortest_len]
        y2t = y2[100:shortest_len]
        y3t = y3[100:shortest_len]
        for ind, val in enumerate(y1t):
            self.assertGreater(y1t[ind], y2t[ind])
            self.assertGreater(y2t[ind], y3t[ind])

        for subject_ind in range(100):
            out1 = simulation_data.run_outputs["1"].output_subjects[subject_ind]
            check_run_output_subject(self, out1)
            out2 = simulation_data.run_outputs["2"].output_subjects[subject_ind]
            check_run_output_subject(self, out2)
            out3 = simulation_data.run_outputs["3"].output_subjects[subject_ind]
            check_run_output_subject(self, out3)

    def get_plotdata(self, fig_num, ax_num=0, plot_num=0):
        ax = plt.figure(fig_num).axes
        self.assertLess(ax_num, len(ax))
        lines = ax[ax_num].get_lines()
        self.assertLess(plot_num, len(lines))
        x = lines[plot_num].get_xdata(True)
        y = lines[plot_num].get_ydata(True)
        return list(x), list(y)
