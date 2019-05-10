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
        stimulus_elements : S1, S2, reward, reward2 # , new_trial
        start_v           : default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : R1:1, R2:1, default:0
        u                 : reward:10, default: 0
        # omit_learning     : ['new trial']

        ## ------------- SEQUENCE LEARNING -------------
        @phase chaining stop:reward=100
        # NEW_TRIAL   new_trial  | STIMULUS_1
        NEW_TRIAL   S1           | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  S2           | R2: REWARD         | NEW_TRIAL
        REWARD     reward        | NEW_TRIAL

        @run chaining

        xscale: reward
        @figure
        @wplot S1 {'color':'red'}
        @wplot S2 {'color':'green'}
        @legend

        @figure
        @pplot S1,S2->R1
        @pplot S1->R0
        @legend

        @figure
        @vplot S1->R1
        @vplot S1->R0
        @legend

        @figure
        cumulative: on
        @nplot reward
        @nplot S1
        '''
        script_obj = Script(script)
        script_obj.parse()
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)

        axw = plt.figure(1).axes
        self.assertEqual(len(axw), 1)
        axw = axw[0]

        lines = axw.get_lines()
        self.assertEqual(len(lines), 2)
        if lines[0].get_color() == 'red':
            wS1 = lines[0]
            wS2 = lines[1]
        else:
            wS1 = lines[1]
            wS2 = lines[0]
        self.assertEqual(wS1.get_color(), 'red')
        self.assertEqual(wS2.get_color(), 'green')

        # wS1
        xmin = wS1.get_xdata(True).min(0)
        xmax = wS1.get_xdata(True).max(0)
        ymin = wS1.get_ydata(True).min(0)
        ymax = wS1.get_ydata(True).max(0)
        self.assertEqual(xmin, 0)
        self.assertEqual(xmax, 100)
        self.assertLessEqual(ymin, 0)
        self.assertAlmostEqual(ymax, 8, 2)

        # wS2
        xmin = wS2.get_xdata(True).min(0)
        xmax = wS2.get_xdata(True).max(0)
        ymin = wS2.get_ydata(True).min(0)
        ymax = wS2.get_ydata(True).max(0)
        self.assertEqual(xmin, 0)
        self.assertEqual(xmax, 100)
        self.assertAlmostEqual(ymax, 9, 2)

    def test_vplot(self):
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
        # 'omit_learning' : new_trial

        ## ------------- SEQUENCE LEARNING -------------
        @phase chaining stop:reward=100
        # NEW_TRIAL   new_trial  | STIMULUS_1
        NEW_TRIAL   S1         | R1: STIMULUS_2     | NEW_TRIAL
        STIMULUS_2  S2         | R2: REWARD         | NEW_TRIAL
        REWARD      reward     | NEW_TRIAL

        @run chaining

        xscale: reward
        @vplot S1->R1 {'linestyle':'-'}
        @vplot S1->R0 {'linestyle':':'}
        '''
        script_obj = Script(script)
        script_obj.parse()
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)

        axv = plt.figure(1).axes
        self.assertEqual(len(axv), 1)
        axv = axv[0]

        lines = axv.get_lines()
        self.assertEqual(len(lines), 2)
        if lines[0].get_linestyle() == '-':
            vS1R1 = lines[0]
            vS1R0 = lines[1]
        else:
            vS1R1 = lines[1]
            vS1R0 = lines[0]
        self.assertEqual(vS1R1.get_linestyle(), '-')
        self.assertEqual(vS1R0.get_linestyle(), ':')

        # vS1R1
        xmin = vS1R1.get_xdata(True).min(0)
        xmax = vS1R1.get_xdata(True).max(0)
        ymin = vS1R1.get_ydata(True).min(0)
        ymax = vS1R1.get_ydata(True).max(0)
        self.assertEqual(xmin, 0)
        self.assertEqual(xmax, 100)
        self.assertLessEqual(ymin, 0)
        self.assertAlmostEqual(ymax, 8, 2)

        # vS1R0
        xmin = vS1R0.get_xdata(True).min(0)
        xmax = vS1R0.get_xdata(True).max(0)
        ymin = vS1R0.get_ydata(True).min(0)
        ymax = vS1R0.get_ydata(True).max(0)
        self.assertEqual(xmin, 0)
        self.assertEqual(xmax, 100)
        self.assertLessEqual(ymin, 0)
        self.assertAlmostEqual(ymax, -1, 2)

    # def test_pplot(self):
    #     script = '''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     ## ------------- SEQUENCE LEARNING -------------
    #     @phase {'label':'chaining', 'end': 'reward=100'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL

    #     @run {'phases':('chaining',)}

    #     @pplot (('S1','S2'), 'R1') {'steps':'reward'} {'marker':'o', 'markevery':5}
    #     @pplot ('S1', 'R0') {'steps':'reward'} {'marker':'*'}
    #     '''
    #     script_obj = LsScript.LsScript(script)
    #     simulation_data = script_obj.run()
    #     script_obj.postproc(simulation_data, False)
    #     # plt.show(block=False)

    #     ax = plt.figure(1).axes
    #     self.assertEqual(len(ax), 1)
    #     ax = ax[0]

    #     lines = ax.get_lines()
    #     self.assertEqual(len(lines), 2)
    #     if lines[0].get_marker() == 'o':
    #         pS1S2R1 = lines[0]
    #         vS1R0 = lines[1]
    #     else:
    #         pS1S2R1 = lines[1]
    #         vS1R0 = lines[0]
    #     self.assertEqual(pS1S2R1.get_marker(), 'o')
    #     self.assertEqual(vS1R0.get_marker(), '*')

    #     # pS1S2R1
    #     xmin = pS1S2R1.get_xdata(True).min(0)
    #     xmax = pS1S2R1.get_xdata(True).max(0)
    #     xfirst = pS1S2R1.get_xdata(True).tolist()[0]
    #     xlast = pS1S2R1.get_xdata(True).tolist()[-1]
    #     ymin = pS1S2R1.get_ydata(True).min(0)
    #     ymax = pS1S2R1.get_ydata(True).max(0)
    #     yfirst = pS1S2R1.get_ydata(True).tolist()[0]
    #     ylast = pS1S2R1.get_ydata(True).tolist()[-1]
    #     self.assertEqual(xmin, 0)
    #     self.assertEqual(xmax, 99)
    #     self.assertEqual(xfirst, 0)
    #     self.assertEqual(xlast, 99)
    #     self.assertAlmostEqual(ymin, 0.02, 1)
    #     self.assertAlmostEqual(ymax, 0.27, 2)
    #     self.assertAlmostEqual(yfirst, 0.21, 2)
    #     self.assertAlmostEqual(ylast, 0.27, 2)

    #     # vS1R0
    #     xmin = vS1R0.get_xdata(True).min(0)
    #     xmax = vS1R0.get_xdata(True).max(0)
    #     xfirst = vS1R0.get_xdata(True).tolist()[0]
    #     xlast = vS1R0.get_xdata(True).tolist()[-1]
    #     ymin = vS1R0.get_ydata(True).min(0)
    #     ymax = vS1R0.get_ydata(True).max(0)
    #     yfirst = vS1R0.get_ydata(True).tolist()[0]
    #     ylast = vS1R0.get_ydata(True).tolist()[-1]
    #     self.assertEqual(xmin, 0)
    #     self.assertEqual(xmax, 99)
    #     self.assertEqual(xfirst, 0)
    #     self.assertEqual(xlast, 99)
    #     self.assertAlmostEqual(ymin, 0, 1)
    #     self.assertAlmostEqual(ymax, 0.333, 3)
    #     self.assertAlmostEqual(yfirst, 0.333, 3)
    #     self.assertAlmostEqual(ylast, 0, 3)

    # def test_nplot(self):
    #     script = '''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'end': 'reward=100'}
    #     NEW_TRIAL   'new trial'   | STIMULUS_1
    #     STIMULUS_1  'S1'          | R1: STIMULUS_2     | NEW_TRIAL
    #     STIMULUS_2  'S2'          | R2: REWARD         | NEW_TRIAL
    #     REWARD      reward        | NEW_TRIAL

    #     @run

    #     @figure
    #     @nplot 'reward' {'cumulative':'off'}

    #     @figure
    #     @nplot 'reward' {'cumulative':'on'} {'marker':'o', 'markevery':50}

    #     @figure
    #     @nplot ['S1','R1','S2','R2'] {'cumulative':'on'}

    #     @figure
    #     @nplot 'reward' 'new trial' {'cumulative':'on'} {}
    #     '''
    #     script_obj = LsScript.LsScript(script)
    #     simulation_data = script_obj.run()
    #     script_obj.postproc(simulation_data, False)
    #     # plt.show(block=False)

    #     ax = plt.figure(1).axes
    #     self.assertEqual(len(ax), 1)
    #     ax = ax[0]
    #     lines = ax.get_lines()
    #     self.assertEqual(len(lines), 1)
    #     line = lines[0]
    #     xmin = line.get_xdata(True).min(0)
    #     ymin = line.get_ydata(True).min(0)
    #     ymax = line.get_ydata(True).max(0)
    #     self.assertEqual(xmin, 0)
    #     self.assertEqual(ymin, 0)
    #     self.assertEqual(ymax, 1)

    #     ax = plt.figure(2).axes
    #     self.assertEqual(len(ax), 1)
    #     ax = ax[0]
    #     lines = ax.get_lines()
    #     self.assertEqual(len(lines), 1)
    #     line = lines[0]
    #     self.assertEqual(line.get_marker(), 'o')
    #     xmin = line.get_xdata(True).min(0)
    #     # xmax = line.get_xdata(True).max(0)
    #     ymin = line.get_ydata(True).min(0)
    #     ymax = line.get_ydata(True).max(0)
    #     y0 = list(line.get_ydata(True))[0]
    #     yend = list(line.get_ydata(True))[-1]
    #     npts = len(line.get_ydata(True))
    #     midind = npts // 2
    #     ymid = list(line.get_ydata(True))[midind]
    #     self.assertGreater(ymid / ymax, 0)
    #     self.assertLess(ymid / ymax, 0.5)
    #     self.assertGreater(ymid / ymax, 0.3, 1)
    #     self.assertLess(ymid / ymax, 0.5, 1)
    #     self.assertEqual(xmin, 0)
    #     self.assertEqual(ymin, 0)
    #     self.assertEqual(ymax, 100)
    #     self.assertEqual(y0, 0)
    #     self.assertEqual(yend, 100)

    #     ax = plt.figure(3).axes
    #     self.assertEqual(len(ax), 1)
    #     ax = ax[0]
    #     lines = ax.get_lines()
    #     self.assertEqual(len(lines), 1)
    #     line = lines[0]
    #     self.assertEqual(line.get_marker(), 'None')
    #     xmin = line.get_ydata(True).min(0)
    #     ymin = line.get_ydata(True).min(0)
    #     ymax = line.get_ydata(True).max(0)
    #     y0 = list(line.get_ydata(True))[0]
    #     yend = list(line.get_ydata(True))[-1]
    #     npts = len(line.get_ydata(True))
    #     midind = npts // 2
    #     ymid = list(line.get_ydata(True))[midind]
    #     self.assertGreater(ymid / ymax, 0)
    #     self.assertLess(ymid / ymax, 0.5)
    #     self.assertGreater(ymid / ymax, 0.3)
    #     self.assertLess(ymid / ymax, 0.5)
    #     self.assertEqual(xmin, 0)
    #     self.assertEqual(ymin, 0)
    #     self.assertEqual(ymax, 100)
    #     self.assertEqual(y0, 0)
    #     self.assertEqual(yend, 100)

    #     ax = plt.figure(4).axes
    #     self.assertEqual(len(ax), 1)
    #     ax = ax[0]
    #     lines = ax.get_lines()
    #     self.assertEqual(len(lines), 1)
    #     line = lines[0]
    #     self.assertEqual(line.get_marker(), 'None')
    #     xmin = line.get_ydata(True).min(0)
    #     ymin = line.get_ydata(True).min(0)
    #     ymax = line.get_ydata(True).max(0)
    #     y0 = list(line.get_ydata(True))[0]
    #     yend = list(line.get_ydata(True))[-1]
    #     npts = len(line.get_ydata(True))
    #     midind = npts // 2
    #     ymid = list(line.get_ydata(True))[midind]
    #     self.assertGreater(ymid / ymax, 0)
    #     self.assertGreater(ymid / ymax, 0.5)

    #     self.assertGreater(ymid / ymax, 0.6)
    #     self.assertLess(ymid / ymax, 1)

    #     self.assertEqual(xmin, 0)
    #     self.assertEqual(ymin, 0)
    #     self.assertEqual(y0, 0)
    #     self.assertGreater(yend, 0.5)
    #     self.assertLess(yend, 0.99)
    #     self.assertGreater(ymid, 0.4)
    #     self.assertLess(ymid, 0.99)

    # def test_wplot_properties_not_dict(self):
    #     script = '''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @wplot 'S1' {'steps','reward'}
    #     '''
    #     with self.assertRaises(Exception):  # {'steps','reward'} instead of
    #                                         # {'steps:'reward'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj)

    # def test_wplot_plotproperties_not_dict(self):
    #     script='''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @wplot 'S1' {'steps':'reward'} {'linecolor','red'}
    #     '''
    #     with self.assertRaises(Exception):  # {'linecolor','red'} instead of
    #                                         # {'linecolor:'red'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj) 

    # def test_vplot_properties_not_dict(self):
    #     script='''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @vplot ('S1','R1') {'steps','reward'}
    #     '''
    #     with self.assertRaises(Exception):  # {'steps','reward'} instead of
    #                                         # {'steps:'reward'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj)

    # def test_vplot_plotproperties_not_dict(self):
    #     script='''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @vplot ('S1','R1') {'steps':'reward'} {'linecolor','red'}
    #     '''
    #     with self.assertRaises(Exception):  # {'linecolor','red'} instead of
    #                                         # {'linecolor:'red'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj) 

    # def test_pplot_properties_not_dict(self):
    #     script='''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @pplot ('S1','R1') {'steps','reward'}
    #     '''
    #     with self.assertRaises(Exception):  # {'steps','reward'} instead of
    #                                         # {'steps:'reward'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj)

    # def test_pplot_plotproperties_not_dict(self):
    #     script='''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @pplot ('S1','R1') {'steps':'reward'} {'linecolor','red'}
    #     '''
    #     with self.assertRaises(Exception):  # {'linecolor','red'} instead of
    #                                         # {'linecolor:'red'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj) 

    # def test_nplot_properties_not_dict(self):
    #     script='''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @nplot 'S1' {'cumulative','on'} {'linecolor':'red'}
    #     '''
    #     with self.assertRaises(Exception):  # {'steps','reward'} instead of
    #                                         # {'steps:'reward'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj)

    # def test_nplot_plotproperties_not_dict(self):
    #     script='''@parameters
    #     {
    #     'subjects'          : 1,
    #     'mechanism'         : 'GA',
    #     'behaviors'         : ['R0','R1','R2'],
    #     'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
    #     'start_v'           : {'default':-1},
    #     'alpha_v'           : 0.1,
    #     'alpha_w'           : 0.1,
    #     'beta'              : 1,
    #     'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
    #     'u'                 : {'reward':10, 'default': 0},
    #     'omit_learning'     : ['new trial']
    #     }

    #     @phase {'label':'chaining', 'end': 'reward=25'}
    #     NEW_TRIAL   'new trial'     | STIMULUS_1    
    #     STIMULUS_1  'S1'              | R1: STIMULUS_2     | NEW_TRIAL 
    #     STIMULUS_2  'S2'              | R2: REWARD         | NEW_TRIAL
    #     REWARD     reward      | NEW_TRIAL  

    #     @run

    #     @nplot 'S1' {'cumulative':'on'} {'linecolor','red'}
    #     '''
    #     with self.assertRaises(Exception):  # {'linecolor','red'} instead of
    #                                         # {'linecolor:'red'}
    #         script_obj = LsScript.LsScript(script)
    #         self.assertIsNone(script_obj) 
