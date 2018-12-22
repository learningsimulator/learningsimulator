# import matplotlib.pyplot as plt

import os.path
import unittest
import LsScript
from LsExceptions import LsParseException

from tests.LsTestUtil import check_run_output_subject


class TestPlots(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        filenames = ['test_wexport1.csv',
                     'test_wexport2.csv',
                     'test_vexport1.csv',
                     'test_vexport2.csv',
                     'test_pexport1.csv',
                     'test_pexport2.csv',
                     'test_nexport1.csv',
                     'test_nexport2.csv',
                     'test_hexport1.csv',
                     'test_hexport2.csv']
        self.remove_files(filenames)
        self.check_that_files_are_removed(filenames)

        filenames = ['test_wexportMS1.csv',
                     'test_wexportMS2.csv',
                     'test_vexportMS1.csv',
                     'test_vexportMS2.csv',
                     'test_pexportMS1.csv',
                     'test_pexportMS2.csv',
                     'test_nexportMS1.csv',
                     'test_nexportMS2.csv',
                     'test_hexportMS1.csv',
                     'test_hexportMS2.csv']
        self.remove_files(filenames)
        self.check_that_files_are_removed(filenames)

    @staticmethod
    def remove_files(filenames):
        for filename in filenames:
            fullpath = "./tests/exported_files/{}".format(filename)
            if os.path.isfile(fullpath):
                os.remove(fullpath)

    def check_that_files_are_removed(self, filenames):
        for filename in filenames:
            fullpath = "./tests/exported_files/{}".format(filename)
            self.assertFalse(os.path.isfile(fullpath))

    def check_that_files_exist(self, filenames):
        for filename in filenames:
            fullpath = "./tests/exported_files/{}".format(filename)
            self.assertTrue(os.path.isfile(fullpath))

    def test_singlesubject(self):
        filenames = ['test_wexport1.csv',
                     'test_wexport2.csv',
                     'test_vexport1.csv',
                     'test_vexport2.csv',
                     'test_pexport1.csv',
                     'test_pexport2.csv',
                     'test_nexport1.csv',
                     'test_nexport2.csv',
                     'test_hexport1.csv',
                     'test_hexport2.csv']
        self.remove_files(filenames)
        self.check_that_files_are_removed(filenames)

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
        NEW_TRIAL   'new trial'     | STIMULUS_1
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
        REWARD     reward      | NEW_TRIAL

        @phase {'label':'test_A', 'end': 'S1=100'}
        NEW_TRIAL    'new trial'       | STIMULUS_1
        STIMULUS_1  'S1'           | REWARD
        REWARD     'reward2'        | NEW_TRIAL

        @phase {'label':'test_B', 'end': 'S1=100'}
        NEW_TRIAL   'new trial'   | STIMULUS_1
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'              | NEW_TRIAL

        @run {'phases':('chaining','test_A'), 'label':'A'}
        @run {'phases':('chaining','test_B'), 'label':'B'}

        @wexport 'S1' {'filename':'./tests/exported_files/test_wexport1.csv','runlabel':'A'}
        @wexport 'S1' {'filename':'./tests/exported_files/test_wexport1.csv','runlabel':'B'}
        @wexport 'S2' {'filename':'./tests/exported_files/test_wexport2.csv','runlabel':'A'}
        @wexport 'S2' {'filename':'./tests/exported_files/test_wexport2.csv','runlabel':'B'}

        @pexport (('S1','S2'), 'R1') {'filename':'./tests/exported_files/test_pexport1.csv', 'runlabel':'B'}
        @pexport ('S1', 'R0') {'filename':'./tests/exported_files/test_pexport2.csv', 'runlabel':'B'}

        @vexport ('S1', 'R1') {'filename':'./tests/exported_files/test_vexport1.csv', 'runlabel':'B'}
        @vexport ('S1', 'R0') {'filename':'./tests/exported_files/test_vexport2.csv', 'runlabel':'B'}

        @nexport 'reward' {'cumulative':'on', 'filename':'./tests/exported_files/test_nexport1', 'runlabel':'B'}  # Test without csv-suffix
        @nexport 'S1' {'cumulative':'on', 'filename':'./tests/exported_files/test_nexport2', 'runlabel':'B'}  # Test without csv-suffix

        @hexport {'filename': './tests/exported_files/test_hexport1', 'runlabel':'A'}
        @hexport {'filename': './tests/exported_files/test_hexport2', 'runlabel':'B'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)

        self.check_that_files_exist(filenames)

    def test_multisubject(self):
        filenames = ['test_wexportMS1.csv',
                     'test_wexportMS2.csv',
                     'test_vexportMS1.csv',
                     'test_vexportMS2.csv',
                     'test_pexportMS1.csv',
                     'test_pexportMS2.csv',
                     'test_nexportMS1.csv',
                     'test_nexportMS2.csv']
        self.remove_files(filenames)
        self.check_that_files_are_removed(filenames)

        script = '''@parameters
        {
        'subjects'          : 10,
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
        NEW_TRIAL   'new trial'     | STIMULUS_1
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
        REWARD     reward      | NEW_TRIAL

        @phase {'label':'test_A', 'end': 'S1=100'}
        NEW_TRIAL    'new trial'       | STIMULUS_1
        STIMULUS_1  'S1'           | REWARD
        REWARD     'reward2'        | NEW_TRIAL

        @phase {'label':'test_B', 'end': 'S1=100'}
        NEW_TRIAL   'new trial'   | STIMULUS_1
        STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  'S2'              | NEW_TRIAL

        @run {'phases':('chaining','test_B')}

        @wexport 'S1' {'subject':'all', 'filename':'./tests/exported_files/test_wexportMS1'}  # Test without csv-suffix
        @wexport 'S2' {'filename':'./tests/exported_files/test_wexportMS2.csv'}

        @pexport (('S1','S2'), 'R1') {'filename':'./tests/exported_files/test_pexportMS1.csv'}
        @pexport ('S1', 'R0') {'filename':'./tests/exported_files/test_pexportMS2.csv'}

        @vexport ('S1', 'R1') {'filename':'./tests/exported_files/test_vexportMS1.csv'}
        @vexport ('S1', 'R0') {'filename':'./tests/exported_files/test_vexportMS2.csv'}

        @nexport 'reward' {'cumulative':'on', 'filename':'./tests/exported_files/test_nexportMS1'}  # Test without csv-suffix
        @nexport 'S1' {'cumulative':'on', 'filename':'./tests/exported_files/test_nexportMS2.csv'}

        @hexport {'filename':'./tests/exported_files/test_hexportMS1.csv'}
        @hexport {'filename':'./tests/exported_files/test_hexportMS2.csv'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)

        for subject_ind in range(10):
            out = simulation_data.run_outputs["run1"].output_subjects[subject_ind]
            check_run_output_subject(self, out)

        self.check_that_files_exist(filenames)

    def test_wrong_arguments(self):
        for vwnp in 'vwnp':
            script = '''@parameters
                {{
                'mechanism'         : 'GA',
                'behaviors'         : ['R'],
                'stimulus_elements' : ['S']
                }}

                @phase {{'end':'S=100'}}
                FOO    'S'   | FOO

                @{}export
                '''.format(vwnp)
            with self.assertRaises(LsParseException):
                LsScript.LsScript(script)

        def test_compare_to_plots(self):
            pass  # XXX
