import matplotlib.pyplot as plt

import unittest
import LsScript
from LsExceptions import LsEvalException, LsParseException

# import time
# time.sleep(40)

# Suppress warning "RuntimeWarning: More than 20 figures have been opened. Figures created through
# the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may
# consume too much memory. (To control this warning, see the rcParam `figure.max_open_warning`)."
plt.rcParams.update({'figure.max_open_warning': 0})


class TestPlotProperties(unittest.TestCase):

    def setUp(self):
        self.base_script = """
            @parameters
            {
            'subjects'          : 10, # number of individuals
            'mechanism'         : 'ga',
            'behaviors'         : ['response','no_response'],
            'stimulus_elements' : ['new_trail', 'context', 'us', 'cs', 'reward'],
            'start_v'           : {'default':-1},
            'alpha_v'           : 0.1,
            'alpha_w'           : 0.1,
            'beta'              : 1.5,
            'behavior_cost'     : {'response':4,'default':0},
            'u'                 : {'reward':10, 'default': 0},
            'omit_learning'     : ['new_trail']
            }

            @phase {'label':'pretraining', 'end':'us=10'}
            NEW_TRIAL   'new_trail'               | CONTEXT
            CONTEXT     'context'                 | 5:SHOW_US            | CONTEXT
            SHOW_US     ('us','context')          | 'response': REWARD   | NEW_TRIAL
            REWARD      ('reward','context')      | NEW_TRIAL

            @phase {'label':'conditioning', 'end':'cs=10'}
            NEW_TRIAL   'new_trail'               | 1:CONTEXT            | NEW_TRIAL
            CONTEXT     'context'                 | 5:SHOW_CS            | CONTEXT
            SHOW_CS     ('cs','context')          | 1:SHOW_US            | SHOW_CS
            SHOW_US     ('us','context')          | response: REWARD     | NEW_TRIAL
            REWARD      ('reward','context')      | NEW_TRIAL
        """

    def tearDown(self):
        # pass
        plt.close('all')

    def get_plotdata(self, fig_num):
        ax = plt.figure(fig_num).axes
        self.assertEqual(len(ax), 1)
        lines = ax[0].get_lines()
        self.assertEqual(len(lines), 1)
        x = lines[0].get_xdata(True)
        y = lines[0].get_ydata(True)
        return list(x), list(y)

    # @staticmethod
    def run_script(self, script):
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_runlabel(self):
        script = self.base_script + '''
            @run {'label':'pretraining_only', 'phases':'pretraining'}
            @run {'label':'conditioning_only', 'phases':'conditioning'}
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @wplot 'us' {'runlabel':'pretraining'}  # Should be 'pretraining_only'
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_runlabel(self):
        script = self.base_script + '''
            @run {'label':'pretraining_only', 'phases':'pretraining'}
            @run {'label':'conditioning_only', 'phases':'conditioning'}
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'runlabel':'pretraining_only'}
            @figure
            @pplot ('us','response') {'runlabel':'conditioning_only'}
            @figure
            @pplot ('us','response') {'runlabel':'both'}

            @figure
            @vplot ('cs','response') {'runlabel':'pretraining_only'}
            @figure
            @vplot ('cs','response') {'runlabel':'conditioning_only'}
            @figure
            @vplot ('cs','response') {'runlabel':'both'}

            @figure
            @wplot 'context' {'runlabel':'pretraining_only'}
            @figure
            @wplot 'context' {'runlabel':'conditioning_only'}
            @figure
            @wplot 'context' {'runlabel':'both'}

            @figure
            @nplot 'cs' {'runlabel':'pretraining_only', 'cumulative':'on'}
            @figure
            @nplot 'cs' {'runlabel':'conditioning_only', 'cumulative':'on'}
            @figure
            @nplot 'cs' {'runlabel':'both', 'cumulative':'on'}

            @figure
            @nplot 'us' {'runlabel':'pretraining_only', 'cumulative':'on'}
            @figure
            @nplot 'us' {'runlabel':'conditioning_only', 'cumulative':'on'}
            @figure
            @nplot 'us' {'runlabel':'both', 'cumulative':'on'}
        '''
        self.run_script(script)

        # pplot
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        x3, y3 = self.get_plotdata(3)
        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        # vplot
        x1, y1 = self.get_plotdata(4)
        x2, y2 = self.get_plotdata(5)
        x3, y3 = self.get_plotdata(6)
        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        self.assertEqual(x1[0], 0)
        for pt in y1:
            self.assertEqual(pt, -1)

        self.assertEqual(x2[0], 0)
        self.assertEqual(y2[0], -1)

        self.assertEqual(x3[0], 0)
        self.assertEqual(y3[0], -1)

        # wplot
        x1, y1 = self.get_plotdata(7)
        x2, y2 = self.get_plotdata(8)
        x3, y3 = self.get_plotdata(9)
        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))
        self.assertEqual(x1[0], 0)
        self.assertEqual(x2[0], 0)
        self.assertEqual(x3[0], 0)
        self.assertEqual(y1[0], 0)
        self.assertEqual(y2[0], 0)
        self.assertEqual(y3[0], 0)

        # nplot cs
        x1, y1 = self.get_plotdata(10)
        x2, y2 = self.get_plotdata(11)
        x3, y3 = self.get_plotdata(12)

        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        self.assertEqual(y1[-1], 0)
        self.assertEqual(y2[-1], 10)
        self.assertEqual(y3[-1], 10)

        # nplot us
        x1, y1 = self.get_plotdata(13)
        x2, y2 = self.get_plotdata(14)
        x3, y3 = self.get_plotdata(15)

        self.assertTrue(len(x1) < len(x3))
        self.assertTrue(len(x2) < len(x3))

        self.assertEqual(y1[-1], 10)
        self.assertEqual(y2[-1], 9)
        self.assertEqual(y3[-1], 19)

    def test_invalid_subject1(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'subject':'qwqw'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_subject2(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'subject':10}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_subject(self):
        # pplot
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @pplot ('us','response') {'subject':0}
            @figure
            @pplot ('us','response') {'subject':9}
            @figure
            @pplot ('us','response') {'subject':'average'}
            @figure
            @pplot ('us','response') {'subject':'all'}
        '''
        self.run_script(script)
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        self.assertTrue(x1[0] == x2[0])
        self.assertTrue(y1 != y2)

        x3, y3 = self.get_plotdata(3)
        self.assertTrue(x1[0] == x3[0])

        ax = plt.figure(4).axes
        self.assertEqual(len(ax), 1)
        lines = ax[0].get_lines()
        self.assertEqual(len(lines), 10)

        # vplot
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @vplot ('us','response') {'subject':0}
            @figure
            @vplot ('us','response') {'subject':9}
            @figure
            @vplot ('us','response') {'subject':'average'}
            @figure
            @vplot ('us','response') {'subject':'all'}
        '''
        self.run_script(script)
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        self.assertTrue(x1[0] == x2[0])
        self.assertTrue(y1 != y2)

        x3, y3 = self.get_plotdata(3)
        self.assertTrue(x1[0] == x3[0])

        ax = plt.figure(4).axes
        self.assertEqual(len(ax), 1)
        lines = ax[0].get_lines()
        self.assertEqual(len(lines), 10)

        # wplot
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @wplot 'us' {'subject':0}
            @figure
            @wplot 'us' {'subject':9}
            @figure
            @wplot 'us' {'subject':'average'}
            @figure
            @wplot 'us' {'subject':'all'}
        '''
        self.run_script(script)
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        self.assertTrue(x1[0] == x2[0])
        self.assertTrue(y1 != y2)

        x3, y3 = self.get_plotdata(3)
        self.assertTrue(x1[0] == x3[0])

        ax = plt.figure(4).axes
        self.assertEqual(len(ax), 1)
        lines = ax[0].get_lines()
        self.assertEqual(len(lines), 10)

        # nplot
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}

            @figure
            @nplot 'us' {'subject':0, 'cumulative':'on'}
            @figure
            @nplot 'us' {'subject':9, 'cumulative':'on'}
            @figure
            @nplot 'us' {'subject':'average', 'cumulative':'on'}
            @figure
            @nplot 'us' {'subject':'all', 'cumulative':'on'}
        '''
        self.run_script(script)
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        self.assertTrue(x1[0] == x2[0])
        self.assertTrue(y1 != y2)

        x3, y3 = self.get_plotdata(3)
        self.assertTrue(x1[0] == x3[0])

        ax = plt.figure(4).axes
        self.assertEqual(len(ax), 1)
        lines = ax[0].get_lines()
        self.assertEqual(len(lines), 10)

    def test_invalid_steps1(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}
            @pplot ('us','response') {'steps': {'foo',1, 'bar',2} }
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_steps2(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}
            @pplot ('us','response') {'steps': {'foo':1, 'bar':2} }
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_steps3(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}
            @pplot ('us','response') {'steps': ('foo', 42, 'bar') }
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_steps4(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}
            @pplot ('us','response') {'steps': ['foo', 42, 'bar'] }
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_steps5(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}
            @pplot ('us','response') {'steps': ['foo', ('baz',42), 'bar'] }
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_steps6(self):
        script = self.base_script + '''
            @run {'label':'both', 'phases':('pretraining','conditioning')}
            @figure '19'
            @pplot ('us','response') {'steps':['us','response']), 'exact_steps':'on', 'phase':('pretraining','conditioning')}
        '''
        with self.assertRaises(LsParseException):
            LsScript.LsScript(script)
        plt.show(block=False)

    def test_steps_phase_exactsteps(self):
        # pplot
        script = self.base_script + '''
            @run {'label':'test_steps', 'phases':('pretraining','conditioning')}

            @figure '1'
            @pplot ('us','response')
            @figure '2'
            @pplot ('us','response') {'steps':'all'}

            @figure '3'
            @pplot ('us','response') {'steps':'foobar'}

            @figure '4'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'off'}
            @figure '5'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'on'}

            @figure '6'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'off', 'phase':'pretraining'}
            @figure '7'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'off', 'phase':'conditioning'}
            @figure '8'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'off', 'phase':('pretraining','conditioning')}

            @figure '9'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'on', 'phase':'pretraining'}
            @figure '10'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'on', 'phase':'conditioning'}
            @figure '11'
            @pplot ('us','response') {'steps':'us', 'exact_steps':'on', 'phase':('pretraining','conditioning')}

            @figure '12'
            @pplot ('us','response') {'steps':('us','context'), 'exact_steps':'off', 'phase':'pretraining'}
            @figure '13'
            @pplot ('us','response') {'steps':('us','context','foo'), 'exact_steps':'off', 'phase':'pretraining'}

            @figure '14'
            @pplot ('us','response') {'steps':('us','context'), 'exact_steps':'off', 'phase':'conditioning'}
            @figure '15'
            @pplot ('us','response') {'steps':('us','context'), 'exact_steps':'off', 'phase':('pretraining','conditioning')}

            @figure '16'
            @pplot ('us','response') {'steps':('us','context'), 'exact_steps':'on', 'phase':'pretraining'}
            @figure '17'
            @pplot ('us','response') {'steps':('us','context'), 'exact_steps':'on', 'phase':'conditioning'}
            @figure '18'
            @pplot ('us','response') {'steps':('us','context'), 'exact_steps':'on', 'phase':('pretraining','conditioning')}

            @figure '19'
            @pplot ('us','response') {'steps':['us','response'], 'exact_steps':'on', 'phase':('pretraining','conditioning')}
            @figure '20'
            @pplot ('us','response') {'steps':['us','response'], 'subject':0}

            @figure '21'
            @pplot ('us','response') {'steps':[('us','context'),'response'], 'subject':0}
            @figure '22'
            @pplot ('us','response') {'steps':[('us','context'),'response'], 'exact_steps':'on', 'subject':0}
        '''
        self.run_script(script)
        x1, y1 = self.get_plotdata(1)
        x2, y2 = self.get_plotdata(2)
        self.assertTrue(x1 == x2)
        self.assertTrue(y1 == y2)
        plt.close(1)
        plt.close(2)

        x1, y1 = self.get_plotdata(3)
        self.assertEqual(len(x1), 0)
        self.assertEqual(len(y1), 0)
        plt.close(3)

        x1, y1 = self.get_plotdata(4)
        self.assertEqual(len(x1), 19)
        self.assertEqual(len(y1), 19)
        x2, y2 = self.get_plotdata(5)
        self.assertEqual(len(x2), 0)
        self.assertEqual(len(y2), 0)
        plt.close(4)
        plt.close(5)

        x1, y1 = self.get_plotdata(6)
        self.assertEqual(len(x1), 10)
        self.assertEqual(len(y1), 10)
        x2, y2 = self.get_plotdata(7)
        self.assertEqual(len(x2), 9)
        self.assertEqual(len(y2), 9)
        x3, y3 = self.get_plotdata(8)
        self.assertEqual(len(x3), 19)
        self.assertEqual(len(y3), 19)
        plt.close(6)
        plt.close(7)
        plt.close(8)

        x1, y1 = self.get_plotdata(9)
        self.assertEqual(len(x1), 0)
        self.assertEqual(len(y1), 0)
        x2, y2 = self.get_plotdata(10)
        self.assertEqual(len(x2), 0)
        self.assertEqual(len(y2), 0)
        x3, y3 = self.get_plotdata(11)
        self.assertEqual(len(x3), 0)
        self.assertEqual(len(y3), 0)
        plt.close(9)
        plt.close(10)
        plt.close(11)

        x1, y1 = self.get_plotdata(12)
        self.assertEqual(len(x1), 10)
        self.assertEqual(len(y1), 10)
        x2, y2 = self.get_plotdata(13)
        self.assertEqual(len(x2), 0)
        self.assertEqual(len(y2), 0)
        plt.close(12)
        plt.close(13)
        x3, y3 = self.get_plotdata(14)
        self.assertEqual(len(x3), 9)
        self.assertEqual(len(y3), 9)
        x4, y4 = self.get_plotdata(15)
        self.assertEqual(len(x4), 19)
        self.assertEqual(len(y4), 19)
        plt.close(14)
        plt.close(15)

        x1, y1 = self.get_plotdata(16)
        self.assertEqual(len(x1), 10)
        self.assertEqual(len(y1), 10)
        x2, y2 = self.get_plotdata(17)
        self.assertEqual(len(x2), 9)
        self.assertEqual(len(y2), 9)
        x3, y3 = self.get_plotdata(18)
        self.assertEqual(len(x3), 19)
        self.assertEqual(len(y3), 19)
        plt.close(16)
        plt.close(17)
        plt.close(18)

        x1, y1 = self.get_plotdata(19)
        self.assertEqual(len(x1), 0)
        self.assertEqual(len(y1), 0)
        x2, y2 = self.get_plotdata(20)
        self.assertGreater(len(x2), 0)
        self.assertGreater(len(y2), 0)
        if len(x2) > 5:
            self.assertGreater(y2[-1], 0.95)

        x3, y3 = self.get_plotdata(21)
        self.assertEqual(x2, x3)
        self.assertEqual(y2, y3)

        x4, y4 = self.get_plotdata(22)
        self.assertEqual(x2, x4)
        self.assertEqual(y2, y4)
        plt.close(19)
        plt.close(20)
        plt.close(21)
        plt.close(22)

    def test_invalid_exact_steps(self):
        script = self.base_script + '''
            @run
            @pplot ('us','response') {'steps':['us','response'], 'exact_steps':'foo'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_phase1(self):
        script = self.base_script + '''
            @run
            @pplot ('us','response') {'steps':['us','response'], 'exact_steps':'off', 'phase':1}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

    def test_invalid_phase2(self):
        script = self.base_script + '''
            @run
            @pplot ('us','response') {'steps':['us','response'], 'exact_steps':'off', 'phase':'foo'}
        '''
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        with self.assertRaises(LsEvalException):
            script_obj.postproc(simulation_data, False)
        plt.show(block=False)

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

                @{}plot
                '''.format(vwnp)
            with self.assertRaises(LsParseException):
                LsScript.LsScript(script)