import unittest
import LsScript
import LsUtil


class TestEvalSteps(unittest.TestCase):

    def setUp(self):
        script = '''@parameters
        {
        'subjects'          : 1,
        'mechanism'         : 'GA',
        'behaviors'         : ['R0','R1','R2'],
        'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
        'start_v'           : {'default':-1},
        'alpha_v'           : 0.1,
        'alpha_w'           : 0.1,
        'beta'              : 1,
        'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
        'u'                 : {'reward':10, 'default': 0},
        'omit_learning'     : ['new trial']
        }
        ## ------------- SEQUENCE LEARNING -------------
        @phase {'label':'chaining', 'end': 'reward=25'}
        NEW_TRIAL  'new trial'      | STIMULUS_1
        STIMULUS_1  'S1'            | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'            | R2: REWARD         | NEW_TRIAL
        REWARD     reward      | NEW_TRIAL
        @phase {'label':'test_A', 'end': 'S1=100'}
        NEW_TRIAL   'new trial'    | STIMULUS_1
        STIMULUS_1  'S1'           | REWARD
        REWARD      'reward2'      | NEW_TRIAL
        @phase {'label':'test_B', 'end': 'S1=100'}
        NEW_TRIAL  'new trial'    | STIMULUS_1
        STIMULUS_1  'S1'            | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'            | NEW_TRIAL
        @run {'phases':('chaining','test_B')}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        self.subject_output = simulation_data.run_outputs["run1"].output_subjects[0]

    def test1(self):
        findind, cumsum = LsUtil.find_and_cumsum(self.subject_output.history, 'new trial', False)
        evalprops = {"steps": "blajblaj", "exact_steps": False}
        e = self.subject_output.vwpn_eval('w', 'new trial', evalprops)
        self.assertEqual(len(e), 0)

        evalprops = {"steps": "new trial", "exact_steps": False}
        e = self.subject_output.vwpn_eval('w', 'new trial', evalprops)
        self.assertEqual(len(e), cumsum[-1])

        evalprops = {"steps": "new trial", "exact_steps": True}
        e = self.subject_output.vwpn_eval('w', 'new trial', evalprops)
        self.assertEqual(len(e), cumsum[-1])

    def test2(self):
        histind_S1, cumsum_S1 = LsUtil.find_and_cumsum(self.subject_output.history, 'S1', False)
        steps = self.subject_output.w['S1'].steps
        # All variables are written at start and at end, so difference must be <= 2
        self.assertLessEqual(abs(len(steps) - cumsum_S1[-1]), 2)

        histind_S2, cumsum_S2 = LsUtil.find_and_cumsum(self.subject_output.history, 'S2', False)
        steps = self.subject_output.w['S2'].steps
        # All variables are written at start and at end, so difference must be <= 2
        self.assertLessEqual(abs(len(steps) - cumsum_S2[-1]), 2)

    def test3(self):
        histind, cumsum = LsUtil.find_and_cumsum(self.subject_output.history, ['S1', 'R2'], False)
        steps_S1R2 = self.subject_output.v[('S1', 'R2')].steps
        for ind, zero_or_one in enumerate(histind):
            if zero_or_one == 1:
                self.assertEqual(ind % 2, 0)
                self.assertIn(1 + ind // 2, steps_S1R2)

#    def test_heval(self):
#        history = self.subject_output.history
