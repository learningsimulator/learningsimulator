import unittest

import LsScript
import LsUtil
from LsMechanism import RR, STIMULUS_ELEMENTS, BEHAVIORS
from LsExceptions import LsParseException


def make_script_parameters(paramblock):
    script = paramblock + "\n" + "@run"
    script_obj = LsScript.LsScript(script)
    return script_obj.parameters.parameters


class TestUnknownParameter(unittest.TestCase):
    def setUp(self):
        pass

    def test_unknown_parameter(self):
        paramblock = """
        @parameters
        {
            'subjects'          : 100, # number of individuals
            'mechanism'         : 'GA',
            'behaviors'         : ['left','right'],
            'stimulus_elements' : ['new_trail','choice','goal_0','goal_1'],
            'start_v'           : {'default':1},
            'alpha_v'           : 0.1,
            'alpha_w'           : 0.1,
            'beta'              : 0.5,
            'u'                 : {'goal_1':10,'default':1},
            'cost'              : {'left':1},
            'omit_learning'     : ['new_trail']
        }
        """
        with self.assertRaises(LsParseException):
            make_script_parameters(paramblock)


class TestUCDefaults(unittest.TestCase):
    def setUp(self):
        pass

    def test_uc_default_fillin(self):
        script = """
        @parameters
        {
            'mechanism'         : 'GA',
            'behaviors'         : ['left','right'],
            'stimulus_elements' : ['new_trail','choice','goal_0','goal_1'],
            'start_v'           : {'default':1},
            'u'                 : {'goal_1':7},
            'behavior_cost'     : {'left':2},
            'omit_learning'     : ['new_trail']
        }

        @phase {'label':'reward', 'end':'goal_0=50'}
        NEW_TRIAL   'new_trail'      | T_MAZE
        T_MAZE      'choice'         | left: LEFT_ARM | right: RIGHT_ARM
        LEFT_ARM    'goal_0'         | NEW_TRIAL
        RIGHT_ARM   'goal_1'         | NEW_TRIAL

        @run
        """
        script_obj = LsScript.LsScript(script)
        mechanism_obj = script_obj.runs.runs["run1"].mechanism_obj
        self.assertEqual(mechanism_obj.c, {'left': 2, 'right': 0})
        self.assertEqual(mechanism_obj.u, {'new_trail': 0, 'choice': 0, 'goal_0': 0, 'goal_1': 7})


class TestRequired(unittest.TestCase):
    def setUp(self):
        pass

    def test_required(self):
        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0'],
            'stimulus_elements': ['E0']
        }
        """
        p = make_script_parameters(paramblock)
        self.assertEqual(p['mechanism'], 'GA')
        self.assertEqual(p[BEHAVIORS], ['R0'])
        self.assertEqual(p[STIMULUS_ELEMENTS], ['E0'])

    def test_incomplete(self):
        paramblock = """
        @parameters
        {
            'behaviors': ['R0'],
            'stimulus_elements': ['E0']
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

        paramblock = """
        @parameters
        {
            'stimulus_elements': ['E0']
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

        paramblock = """
        @parameters
        {
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)


class TestResponseRequirements(unittest.TestCase):
    def setUp(self):
        pass

    def test_syntax(self):
        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22']
        }
        """
        p = make_script_parameters(paramblock)
        self.assertTrue(RR not in p)

        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {}
        }
        """
        p = make_script_parameters(paramblock)
        self.assertEqual(p[RR], {})

        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {
                                      'R0': ['E00', 'E01'],
                                      'R1': 'E10',
                                      'R2': ['E20', 'E21', 'E22']
                                      }
        }
        """
        p = make_script_parameters(paramblock)
        self.assertEqual(p[RR], {'R0': ['E00', 'E01'],
                                 'R1': 'E10',
                                 'R2': ['E20', 'E21', 'E22']})

    def test_not_dict(self):
        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': 'foo'
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': ['f','o','o']
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

    def test_unknown_behavior(self):
        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {
                                      'R0blaj': ['E00', 'E01'],
                                      'R1': 'E10',
                                      'R2': ['E20', 'E21', 'E22']
                                      }
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {
                                      1234: ['E00', 'E01'],
                                      'R1': 'E10',
                                      'R2': ['E20', 'E21', 'E22']
                                      }
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

    def test_unknown_stimulus_element(self):
        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {
                                      'R0': ['E00', 'E01'],
                                      'R1': 'E10',
                                      'R2': ['E20', 'E21blaj', 'E22']
                                      }
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {
                                      'R0': ['E00', 'E01'],
                                      'R1': 'blaj',
                                      'R2': ['E20', 'E21', 'E22']
                                      }
        }
        """
        with self.assertRaises(LsParseException):
            p = make_script_parameters(paramblock)
            self.assertIsNotNone(p)

    def test_disjunct(self):
        script = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {
                                      'R0': ['E00', 'E01'],
                                      'R1': 'E10',
                                      'R2': ['E20', 'E21', 'E22']
                                      }
        }

        @phase {'label':'foo', 'end':'E00=100'}
        PL00    'E00'  |  PL01
        PL01    'E01'  |  PL10
        PL10    'E10'  |  PL20
        PL20    'E20'  |  PL21
        PL21    'E21'  |  PL22
        PL22    'E22'  |  PL00

        @run
        """
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        _, cumsum_E00 = LsUtil.find_and_cumsum(history, 'E00', True)
        _, cumsum_E00_R0 = LsUtil.find_and_cumsum(history, ['E00', 'R0'], True)
        self.assertEqual(cumsum_E00[-1], cumsum_E00_R0[-1])

        _, cumsum_E01 = LsUtil.find_and_cumsum(history, 'E01', True)
        _, cumsum_E01_R0 = LsUtil.find_and_cumsum(history, ['E01', 'R0'], True)
        self.assertEqual(cumsum_E01[-1], cumsum_E01_R0[-1])

        _, cumsum_E10 = LsUtil.find_and_cumsum(history, 'E10', True)
        _, cumsum_E10_R1 = LsUtil.find_and_cumsum(history, ['E10', 'R1'], True)
        self.assertEqual(cumsum_E10[-1], cumsum_E10_R1[-1])

        _, cumsum_E20 = LsUtil.find_and_cumsum(history, 'E20', True)
        _, cumsum_E20_R2 = LsUtil.find_and_cumsum(history, ['E20', 'R2'], True)
        self.assertEqual(cumsum_E20[-1], cumsum_E20_R2[-1])

        _, cumsum_E21 = LsUtil.find_and_cumsum(history, 'E21', True)
        _, cumsum_E21_R2 = LsUtil.find_and_cumsum(history, ['E21', 'R2'], True)
        self.assertEqual(cumsum_E21[-1], cumsum_E21_R2[-1])

        _, cumsum_E22 = LsUtil.find_and_cumsum(history, 'E22', True)
        _, cumsum_E22_R2 = LsUtil.find_and_cumsum(history, ['E22', 'R2'], True)
        self.assertEqual(cumsum_E22[-1], cumsum_E22_R2[-1])

    def test_disjunct_with_default(self):
        script = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2', 'R3','R4'],
            'stimulus_elements': ['E00', 'E01', 'E10', 'E20', 'E21', 'E22'],
            'response_requirements': {
                                      'R0': ['E00', 'E01'],
                                      'R1': 'E10',
                                      'R2': ['E20', 'E21', 'E22']
                                      }
        }

        @phase {'label':'foo', 'end':'E00=100'}
        PL00    'E00'  |  PL01
        PL01    'E01'  |  PL10
        PL10    'E10'  |  PL20
        PL20    'E20'  |  PL21
        PL21    'E21'  |  PL22
        PL22    'E22'  |  PL00

        @run
        """
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        _, cumsum_E00 = LsUtil.find_and_cumsum(history, 'E00', True)
        _, cumsum_E00_R0 = LsUtil.find_and_cumsum(history, ['E00', 'R0'], True)
        _, cumsum_E00_R3 = LsUtil.find_and_cumsum(history, ['E00', 'R3'], True)
        _, cumsum_E00_R4 = LsUtil.find_and_cumsum(history, ['E00', 'R4'], True)
        self.assertEqual(cumsum_E00[-1], cumsum_E00_R0[-1] + cumsum_E00_R3[-1] + cumsum_E00_R4[-1])
        self.assertGreater(cumsum_E00_R0[-1], 0)
        self.assertGreater(cumsum_E00_R3[-1], 0)
        self.assertGreater(cumsum_E00_R4[-1], 0)

        _, cumsum_E01 = LsUtil.find_and_cumsum(history, 'E01', True)
        _, cumsum_E01_R0 = LsUtil.find_and_cumsum(history, ['E01', 'R0'], True)
        _, cumsum_E01_R3 = LsUtil.find_and_cumsum(history, ['E01', 'R3'], True)
        _, cumsum_E01_R4 = LsUtil.find_and_cumsum(history, ['E01', 'R4'], True)
        self.assertEqual(cumsum_E01[-1], cumsum_E01_R0[-1] + cumsum_E01_R3[-1] + cumsum_E01_R4[-1])
        self.assertGreater(cumsum_E01_R0[-1], 0)
        self.assertGreater(cumsum_E01_R3[-1], 0)
        self.assertGreater(cumsum_E01_R4[-1], 0)

        _, cumsum_E10 = LsUtil.find_and_cumsum(history, 'E10', True)
        _, cumsum_E10_R1 = LsUtil.find_and_cumsum(history, ['E10', 'R1'], True)
        _, cumsum_E10_R3 = LsUtil.find_and_cumsum(history, ['E10', 'R3'], True)
        _, cumsum_E10_R4 = LsUtil.find_and_cumsum(history, ['E10', 'R4'], True)
        self.assertEqual(cumsum_E10[-1], cumsum_E10_R1[-1] + cumsum_E10_R3[-1] + cumsum_E10_R4[-1])
        self.assertGreater(cumsum_E10_R1[-1], 0)
        self.assertGreater(cumsum_E10_R3[-1], 0)
        self.assertGreater(cumsum_E10_R4[-1], 0)

        _, cumsum_E20 = LsUtil.find_and_cumsum(history, 'E20', True)
        _, cumsum_E20_R2 = LsUtil.find_and_cumsum(history, ['E20', 'R2'], True)
        _, cumsum_E20_R3 = LsUtil.find_and_cumsum(history, ['E20', 'R3'], True)
        _, cumsum_E20_R4 = LsUtil.find_and_cumsum(history, ['E20', 'R4'], True)
        self.assertEqual(cumsum_E20[-1], cumsum_E20_R2[-1] + cumsum_E20_R3[-1] + cumsum_E20_R4[-1])
        self.assertGreater(cumsum_E20_R2[-1], 0)
        self.assertGreater(cumsum_E20_R3[-1], 0)
        self.assertGreater(cumsum_E20_R4[-1], 0)

        _, cumsum_E21 = LsUtil.find_and_cumsum(history, 'E21', True)
        _, cumsum_E21_R2 = LsUtil.find_and_cumsum(history, ['E21', 'R2'], True)
        _, cumsum_E21_R3 = LsUtil.find_and_cumsum(history, ['E21', 'R3'], True)
        _, cumsum_E21_R4 = LsUtil.find_and_cumsum(history, ['E21', 'R4'], True)
        self.assertEqual(cumsum_E21[-1], cumsum_E21_R2[-1] + cumsum_E21_R3[-1] + cumsum_E21_R4[-1])
        self.assertGreater(cumsum_E21_R2[-1], 0)
        self.assertGreater(cumsum_E21_R3[-1], 0)
        self.assertGreater(cumsum_E21_R4[-1], 0)

        _, cumsum_E22 = LsUtil.find_and_cumsum(history, 'E22', True)
        _, cumsum_E22_R2 = LsUtil.find_and_cumsum(history, ['E22', 'R2'], True)
        _, cumsum_E22_R3 = LsUtil.find_and_cumsum(history, ['E22', 'R3'], True)
        _, cumsum_E22_R4 = LsUtil.find_and_cumsum(history, ['E22', 'R4'], True)
        self.assertEqual(cumsum_E22[-1], cumsum_E22_R2[-1] + cumsum_E22_R3[-1] + cumsum_E22_R4[-1])
        self.assertGreater(cumsum_E22_R2[-1], 0)
        self.assertGreater(cumsum_E22_R3[-1], 0)
        self.assertGreater(cumsum_E22_R4[-1], 0)

    def test_nondisjunct(self):
        script = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E0', 'E1', 'E2'],
            'response_requirements': {
                                      'R0': ['E0', 'E1'],
                                      'R1': 'E1',
                                      'R2': ['E0', 'E1', 'E2']
                                      }
        }

        @phase {'label':'foo', 'end':'E0=100'}
        PL0    'E0'  |  PL1
        PL1    'E1'  |  PL2
        PL2    'E2'  |  PL0

        @run
        """
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        _, cumsum_E0 = LsUtil.find_and_cumsum(history, 'E0', True)
        _, cumsum_E0_R0 = LsUtil.find_and_cumsum(history, ['E0', 'R0'], True)
        _, cumsum_E0_R2 = LsUtil.find_and_cumsum(history, ['E0', 'R2'], True)
        self.assertEqual(cumsum_E0[-1], cumsum_E0_R0[-1] + cumsum_E0_R2[-1])

    def test_nondisjunct_with_default(self):
        # Same as test_nondisjunct but omitting 'R2':['E0', 'E1', 'E2'] which is default

        script = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E0', 'E1', 'E2'],
            'response_requirements': {
                                      'R0': ['E0', 'E1'],
                                      'R1': 'E1'
                                      }
        }

        @phase {'label':'foo', 'end':'E0=100'}
        PL0    'E0'  |  PL1
        PL1    'E1'  |  PL2
        PL2    'E2'  |  PL0

        @run
        """
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        _, cumsum_E0 = LsUtil.find_and_cumsum(history, 'E0', True)
        _, cumsum_E0_R0 = LsUtil.find_and_cumsum(history, ['E0', 'R0'], True)
        _, cumsum_E0_R2 = LsUtil.find_and_cumsum(history, ['E0', 'R2'], True)
        self.assertEqual(cumsum_E0[-1], cumsum_E0_R0[-1] + cumsum_E0_R2[-1])
        self.assertGreater(cumsum_E0_R0[-1], 0)
        self.assertGreater(cumsum_E0_R2[-1], 0)

    def test_no_feasible_response(self):

        paramblock = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E0', 'E1', 'E2','E3'],
            'response_requirements': {
                                      'R0': 'E0',
                                      'R1': 'E1',
                                      'R2': 'E2'
                                      }
        }
        """
        with self.assertRaises(LsParseException):
            make_script_parameters(paramblock)
