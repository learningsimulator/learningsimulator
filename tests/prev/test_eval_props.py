import unittest
import LsScript


class TestEvalProps(unittest.TestCase):

    def setUp(self):
        script = '''
        @parameters
        {
        'mechanism' :         'Rescorla_Wagner',
        'behaviors' :         ['R1','R2'],
        'stimulus_elements' : ['E','rew'],
        'u'                 : {'rew':1, 'E':0}
        }

        @phase {'label':'foo', 'end':'B=3'}
        A 'E'   | 5:B | A
        B 'rew' | A

        @run {'label':'B=3'}

        @phase {'label':'foo', 'end':'rew=5'}
        @run {'label':'rew=5'}

        # @nplot 'E' {'runlabel':'B=3', 'cumulative':'off', 'steps':'rew'}
        # @nplot 'E' {'runlabel':'rew=5', 'cumulative':'off', 'steps':'rew'}

        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        self.run_B3 = simulation_data.run_outputs["B=3"].output_subjects[0]
        self.run_rew5 = simulation_data.run_outputs["rew=5"].output_subjects[0]

    # @unittest.skip("Reason skipped")  # FIXME
    def test_phase_end_condition(self):
        cnt_rew1 = 0
        for h in self.run_B3.history:
            if h == 'rew':
                cnt_rew1 += 1
        self.assertEqual(cnt_rew1, 3)

        cnt_rew2 = 0
        for h in self.run_rew5.history:
            if h == 'rew':
                cnt_rew2 += 1

        self.assertEqual(cnt_rew2, 5)

    def footest_phase(self):
        script = '''
        @parameters
        {
        'mechanism' :         'Rescorla_Wagner',
        'behaviors' :         ['R','RR'],
        'stimulus_elements' : ['E1','rew1','E2','rew2'],
        'u'                 : {'rew1':1, 'rew2':1, 'E1':0, 'E2':0}
        }

        @phase {'label':'phase1', 'end':'B=3'}
        A 'E1'   | 5:B | A
        B 'rew1' | A

        @phase {'label':'phase2', 'end':'B=6'}
        A 'E2'   | 5:B | A
        B 'rew2' | A

        @run

        '''
        script_obj = LsScript.LsScript(script)
        s = script_obj.run()
        # s = simulation_data  # .run_outputs["run1"].output_subjects[0]

        eval_phase1 = s.vwpn_eval('n', 'E1', {'phase': 'phase1'})
        eval_phase2 = s.vwpn_eval('n', 'E1', {'phase': 'phase2'})
        eval_phase12 = s.vwpn_eval('n', 'E1', {'phase': ('phase1', 'phase2')})
        self.assertEqual(eval_phase1[0], 0)
        self.assertEqual(eval_phase2[0], 0)
        self.assertEqual(eval_phase12[0], 0)

        len_eval_phase1 = len(eval_phase1)
        len_eval_phase2 = len(eval_phase2)
        len_eval_phase12 = len(eval_phase12)
        history = s.run_outputs['run1'].output_subjects[0].history
        len_history = len(history)
        self.assertEqual(len_eval_phase12, 1 + len_history)
        self.assertEqual(len_eval_phase1 + len_eval_phase2, 2 + len_history)
