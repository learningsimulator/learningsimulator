from .testutil import LsTestCase, run, remove_files


class TestPlots(LsTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        filenames = ['test_wexport1.csv',
                     'test_wexport2.csv',
                     'test_vexport1.csv',
                     'test_vexport2.csv',
                     'test_pexport1.csv',
                     'test_pexport2.csv',
                     'test_nexport1.txt',
                     'test_nexport2.txt',
                     'test_hexport1.csv',
                     'test_hexport2.csv']
        remove_files(filenames)
        self.assert_files_are_removed(filenames)

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
        remove_files(filenames)
        self.assert_files_are_removed(filenames)

    def test_singlesubject(self):
        filenames = ['test_wexport1.csv',
                     'test_wexport2.csv',
                     'test_vexport1.csv',
                     'test_vexport2.csv',
                     'test_pexport1.csv',
                     'test_pexport2.csv',
                     'test_nexport1.txt',
                     'test_nexport2.txt',
                     'test_hexport1.csv',
                     'test_hexport2.csv']
        remove_files(filenames)
        self.assert_files_are_removed(filenames)

        script = '''
        n_subjects          : 1
        mechanism         : GA
        behaviors         : R0,R1,R2
        stimulus_elements : S1,S2,reward,reward2,new_trial
        start_v           : default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : R1:1, R2:1, default:0
        u                 : reward:10, default: 0

        ## ------------- SEQUENCE LEARNING -------------
        @phase chaining stop: reward=25
        NEW_TRIAL   new_trial  | STIMULUS_1
        STIMULUS_1  S1         | R1: STIMULUS_2  | NEW_TRIAL
        STIMULUS_2  S2         | R2: REWARD      | NEW_TRIAL
        REWARD     reward      | NEW_TRIAL

        @phase test_A  stop: S1=100
        NEW_TRIAL   new_trial    | STIMULUS_1
        STIMULUS_1  S1           | REWARD
        REWARD      reward2      | NEW_TRIAL

        @phase test_B   stop: S1=100
        NEW_TRIAL   new_trial   | STIMULUS_1
        STIMULUS_1  S1          | R1: STIMULUS_2  | NEW_TRIAL
        STIMULUS_2  S2          | NEW_TRIAL

        @run chaining,test_A   runlabel:A
        @run chaining,test_B   runlabel:B

        runlabel:A
        @wexport S1 ./tests/exported_files/test_wexport1.csv
        runlabel:B
        @wexport S1 ./tests/exported_files/test_wexport1.csv
        runlabel:A
        @wexport S2 ./tests/exported_files/test_wexport2.csv
        runlabel:B
        @wexport S2 ./tests/exported_files/test_wexport2.csv

        @pexport S1,S2->R1 ./tests/exported_files/test_pexport1.csv
        @pexport S1->R0    ./tests/exported_files/test_pexport2.csv

        @vexport S1->R1 ./tests/exported_files/test_vexport1.csv
        @vexport S1->R0 ./tests/exported_files/test_vexport2.csv

        cumulative:on
        @nexport reward ./tests/exported_files/test_nexport1.txt  # Test without csv-suffix
        @nexport S1 ./tests/exported_files/test_nexport2.txt      # Test without csv-suffix

        runlabel:A
        @hexport ./tests/exported_files/test_hexport1.csv
        @hexport ./tests/exported_files/test_hexport2.csv
        '''
        run(script)
        self.assert_files_exist(filenames)

    def test_multisubject(self):
        filenames = ['test_wexportMS1.csv',
                     'test_wexportMS2.csv',
                     'test_vexportMS1.csv',
                     'test_vexportMS2.csv',
                     'test_pexportMS1.csv',
                     'test_pexportMS2.csv',
                     'test_nexportMS1.csv',
                     'test_nexportMS2.csv']
        remove_files(filenames)
        self.assert_files_are_removed(filenames)

        script = '''
        n_subjects        : 10
        mechanism         : GA
        behaviors         : R0,R1,R2
        stimulus_elements : S1,S2,reward,reward2,new_trial
        start_v           : default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : R1:1, R2:1, default:0
        u                 : reward:10,default: 0

        ## ------------- SEQUENCE LEARNING -------------
        @phase chaining stop:reward=25
        NEW_TRIAL   new_trial   | STIMULUS_1
        STIMULUS_1  S1          | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  S2          | R2: REWARD         | NEW_TRIAL
        REWARD      reward      | NEW_TRIAL

        @phase test_A stop: S1=100
        NEW_TRIAL   new_trial       | STIMULUS_1
        STIMULUS_1  S1              | REWARD
        REWARD      reward2         | NEW_TRIAL

        @phase test_B stop: S1=100
        NEW_TRIAL   new_trial   | STIMULUS_1
        STIMULUS_1  S1          | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  S2          | NEW_TRIAL

        @run chaining,test_B

        subject:all
        @wexport S1 ./tests/exported_files/test_wexportMS1.csv
        @wexport S2 ./tests/exported_files/test_wexportMS2.csv

        @pexport S1,S2->R1 ./tests/exported_files/test_pexportMS1.csv
        @pexport S1->R0 ./tests/exported_files/test_pexportMS2.csv

        @vexport S1->R1 ./tests/exported_files/test_vexportMS1.csv
        @vexport S1->R0 ./tests/exported_files/test_vexportMS2.csv

        cumulative:on
        @nexport reward ./tests/exported_files/test_nexportMS1.csv
        @nexport S1 ./tests/exported_files/test_nexportMS2.csv

        @hexport ./tests/exported_files/test_hexportMS1.csv
        @hexport ./tests/exported_files/test_hexportMS2.csv
        '''
        run(script)
        self.assert_files_exist(filenames)

    def test_wrong_arguments(self):
        for vwnp in 'vwnp':
            script = f'''
            mechanism         : GA
            behaviors         : R
            stimulus_elements : S

            @phase foo stop: S=100
            FOO    S   | FOO

            @{vwnp}export
            '''
            msg = f"Invalid @{vwnp}export command."
            with self.assertRaisesX(Exception, msg):
                run(script)

    def test_vssexport(self):
        filenames = ['foobar_csus.txt', 'foobar_uscs.txt', 'foobar_usus.txt', 'foobar_cscs.txt']
        remove_files(filenames)
        self.assert_files_are_removed(filenames)

        script = """
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        filename:./tests/exported_files/foobar_csus.txt
        @vssexport cs->us

        @vssexport us->cs ./tests/exported_files/foobar_uscs.txt

        filename:./tests/exported_files/foobar_usus.txt
        @vssexport us->us

        @vssexport cs->cs ./tests/exported_files/foobar_cscs.txt
        """
        run(script)
        self.assert_files_exist(filenames)

    def test_compare_to_plots(self):
        pass  # XXX
