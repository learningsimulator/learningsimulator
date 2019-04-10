from .testutil import LsTestCase
from parsing import Script
import matplotlib.pyplot as plt


def run(text):
    script = Script(text)
    script.parse()
    script_output = script.run()
    script.postproc(script_output, False)
    return script, script_output


class TestFoundBugs(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_response_requirements(self):
        text = '''
        # Simulation of Thrailkill & Bouton (2015)

        n_subjects            : 10
        mechanism             : GA
        behaviors             : b1,b2,ignore
        stimulus_elements     : s_start,s1,s2,m1,m2,reward
        start_v               : s1->ignore:0, s2->ignore:0, default:-1
        alpha_v               : 0.1
        alpha_w               : 0.1
        beta                  : 1
        behavior_cost         : ignore:0, default:1
        response_requirements : b1:[s1,s2], b2:[s1,s2]
        u                     : reward:5, default:0

        @phase acquisition stop: new_trial=50
        new_trial   s_start  | STEP1
        STEP1       s1,m1,m2 | b1: STEP2   |  new_trial
        STEP2       s2,m1,m2 | b2: REWARD  |  new_trial
        REWARD      reward   | new_trial

        @phase extinction stop: new_trial=500
        new_trial   s_start  | STEP1
        STEP1       s1       | b1: STEP2   | NEXT
        STEP2       s2       | NEXT
        NEXT                 | new_trial

        bind_trials: on
        @run acquisition, extinction

        xscale: s_start
        subject: average

        @figure Probability
        @pplot s1->b1 {'linewidth':3}
        @pplot s2->b2 {'linewidth':3}
        @legend

        @figure Response to s1
        @pplot s1->ignore {'linewidth':3}
        @pplot s1->b1 {'linewidth':3}
        @pplot s1->b2 {'linewidth':3}
        @legend

        @figure v-values
        @vplot s1->b1 {'linewidth':3}
        @vplot s2->b2 {'linewidth':3}
        @legend

        @figure w-value
        @wplot s2 {'linewidth':3}
        @legend
        '''
        script, script_output = run(text)
        history = script_output.run_outputs['run1'].output_subjects[0].history
        self.assertEqual(len(script.script_parser.postcmds.cmds), 16)

    def test_reset_local_variables(self):
        text = '''
        # Basic chaining with GA mechanism and start entry
        # Markus and Magnus - March 2019
        n_subjects        : 100
        mechanism         : GA
        behaviors         : b1,b2,ignore
        stimulus_elements : s_start,s1,s2,reward,no_reward
        start_v           : s1->ignore:0, s2->ignore:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : ignore:0, default: 1
        u                 : reward:5, default:0


        @phase experiment stop: new_trial=100
        new_trial  s_start    | FOO
        FOO        foo:foo+1  | STEP1
        STEP1      s1         | b1: STEP2   |  new_trial
        STEP2      s2         | b2: OUTCOME |  new_trial
        OUTCOME               | foo<=50: REWARD | NO_REWARD
        REWARD     reward     | new_trial
        NO_REWARD  no_reward  | new_trial


        @run experiment

        xscale: s_start
        subject: average

        @figure Number of no_reward and b2
        @nplot no_reward
        @legend
            '''
        script, script_output = run(text)
        history = script_output.run_outputs['run1'].output_subjects[0].history
        ax = plt.figure(1).axes
        self.assertEqual(len(ax), 1)
        ax = ax[0]

        lines = ax.get_lines()
        self.assertEqual(len(lines), 1)
        line = lines[0]
        plotted_xdata = list(line.get_xdata(True))
        plotted_ydata = list(line.get_ydata(True))
        self.assertEqual(plotted_xdata, list(range(0, 101)))
        self.assertEqual(plotted_ydata[0:51], [0] * 51)


class TestErrors(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_invalid_pplot_due_to_response_requirements(self):
        text = '''
        # Simulation of Thrailkill & Bouton (2015)

        n_subjects            : 10
        mechanism             : GA
        behaviors             : b1,b2,ignore
        stimulus_elements     : s_start,s1,s2,m1,m2,reward
        start_v               : s1->ignore:0, s2->ignore:0, default:-1
        alpha_v               : 0.1
        alpha_w               : 0.1
        beta                  : 1
        behavior_cost         : ignore:0, default:1
        response_requirements : b1:m1, b2:m2
        u                     : reward:5, default:0

        @phase acquisition stop: new_trial=50
        new_trial   s_start  | STEP1
        STEP1       s1,m1,m2 | b1: STEP2   |  new_trial
        STEP2       s2,m1,m2 | b2: REWARD  |  new_trial
        REWARD      reward   | new_trial

        @phase extinction stop: new_trial=500
        new_trial   s_start  | STEP1
        STEP1       s1       | b1: STEP2   | NEXT
        STEP2       s2       | NEXT
        NEXT                 | new_trial

        bind_trials: on
        @run acquisition, extinction

        xscale: s_start
        subject: average

        @figure Probability
        @pplot s1->b1
        '''
        msg = "Behavior 'b1' is not a possible response to 's1'."
        with self.assertRaisesX(Exception, msg):
            run(text)
