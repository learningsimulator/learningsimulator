import matplotlib.pyplot as plt

from .testutil import LsTestCase, run


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
        self.assertEqual(len(script.script_parser.postcmds.cmds), 16)

    def test_reset_local_variable(self):
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

        @figure Number of no_reward
        @nplot no_reward
        @legend
            '''
        script, script_output = run(text)
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

    def test_count_instead_of_local_variable(self):
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
        new_trial  s_start    | STEP1
        STEP1      s1         | b1: STEP2   |  new_trial
        STEP2      s2         | b2: OUTCOME |  new_trial
        OUTCOME               | count(new_trial)<=50: REWARD | NO_REWARD
        REWARD     reward     | new_trial
        NO_REWARD  no_reward  | new_trial

        @run experiment

        xscale: s_start
        subject: average

        @figure Number of no_reward
        @nplot no_reward
        @legend
            '''
        script, script_output = run(text)
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

    def test_phases_when_xscale_is_help_line_label(self):
        text = '''
        # Pavlovian revaluation
        # Explores acquisition, extinction and reaquisition

        n_subjects             : 50
        mechanism              : GA
        behaviors              : cr,other  # ur = cr
        stimulus_elements      : us,no_us,cs1,cs2,start
        start_v                : cs1->cr:-1, cs2->cr:-1, default: 1
        alpha_v                : cs1->other:0, cs2->other:0, default:0.1
        alpha_w                : 0.1
        beta                   : 1
        behavior_cost          : cr:1, default: 0
        u                      : us:10, default:0
        bind_trials            : off

        @phase acquisition  stop: new_trial= 100
        new_trial             | CS2
        CS2        cs2        | CS1
        CS1        cs1        | US
        US         us           | new_trial

        @phase revaluation stop: new_trial=50
        new_trial             | CS1
        CS1        cs1        | NO_US
        NO_US      no_us      | new_trial

        @phase extinction stop: new_trial=40
        new_trial             | CS2
        CS2        cs2        | NO_US
        NO_US      no_us      | new_trial

        @phase reacquisition(acquisition) stop: new_trial=40

        @run acquisition,revaluation,extinction,reacquisition   runlabel:'exp'
        @run acquisition,extinction,reacquisition   runlabel:'control'

        xscale: new_trial
        subject: average
        phases:extinction,reacquisition
        @figure
        @subplot 121 - {'xlabel':'Trial','ylabel':'Probability', 'title':'Responding to CS2'  }
        runlabel:'exp'
        @pplot cs2->cr {'linewidth':2,'color':'black','label':'Revaluation'}
        runlabel:'control'
        @pplot cs2->cr {'linewidth':1,'linestyle':'--','color':'red','label':'Control'}
        @legend

        @subplot 122 - {'xlabel':'Trial','ylabel':'w', 'title':'w(CS1) '  }
        runlabel:'exp'
        @wplot cs1 {'linewidth':2,'color':'black','label':'Revaluation'}
        runlabel:'control'
        @wplot cs1 {'linewidth':1,'linestyle':'--','color':'red','label':'Control'}
        @legend
        '''
        script, script_output = run(text)

    def test_phases_when_xscale_is_help_line_label_minimal(self):
        text = '''
        # Pavlovian revaluation
        # Explores acquisition, extinction and reaquisition

        n_subjects             : 1
        mechanism              : GA
        behaviors              : cr,other  # ur = cr
        stimulus_elements      : us,no_us,cs1,cs2,start
        start_v                : cs1->cr:-1, cs2->cr:-1, default: 1
        alpha_v                : cs1->other:0, cs2->other:0, default:0.1
        alpha_w                : 0.1
        beta                   : 1
        behavior_cost          : cr:1, default: 0
        u                      : us:10, default:0
        bind_trials            : off

        @phase acquisition  stop: new_trial=5
        new_trial             | CS2
        CS2        cs2        | CS1
        CS1        cs1        | US
        US         us         | new_trial

        @run acquisition

        xscale: new_trial
        phases:acquisition
        @vplot cs2->cr
        '''
        script, script_output = run(text)


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
