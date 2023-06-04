import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestGitHubIssues(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_issue83(self):
        text = '''
        mechanism             : SR
        behaviors             : b1, b2
        stimulus_elements     : s1, s2
        alpha_v               : 1

        @phase phase_name stop: LINE0=1000
        LINE0 p:0.5 | LINE1
        LINE1 s1    | LINE2(p) | LINE0
        LINE2 s2    | LINE0

        @run phase_name
        @nplot s2
        '''
        run(text)
        plot_data = get_plot_data()
        y = plot_data['y']
        self.assertLess(y[-1], 550)
        self.assertGreater(y[-1], 450)

        plt.close('all')

        text = '''
        mechanism             = SR
        behaviors             = b1, b2
        stimulus_elements     = s0, s1, s2
        alpha_v               = 1

        @phase phase_name stop: LINE0=1000
        START       | p=0.5, LINE0
        LINE0 s0    | LINE1(p) | LINE0
        LINE1 s1    | LINE2(p) | LINE0
        LINE2 s2    | LINE0

        xscale = s0
        @run phase_name
        @nplot s2        '''
        script, script_output = run(text)
        plot_data = get_plot_data()
        x = plot_data['x']
        y = plot_data['y']
        assert(x[-1] == 999)
        assert(y[-1] < 300)
        assert(y[-1] > 200)

        # mechanism             : SR
        # behaviors             : b1, b2
        # stimulus_elements     : s1, s2

        # @phase phase_name stop: LINE0=p
        # LINE0 p:5 | LINE1
        # LINE1 s1    | LINE2(0.5) | LINE0
        # LINE2 s2    | LINE0

        # @run phase_name

        # @nplot s2

    def test_issue112_big(self):
        text = '''
        n_subjects        : 10
        mechanism         : sr
        behaviors         : response, no_response
        stimulus_elements : background, stimulus, reward
        start_v           = default:-1
        alpha_v           = 0.1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus=100
        new_trial  stimulus   | response=n: REWARD | NO_REWARD
        REWARD     reward     | new_trial
        NO_REWARD  background | new_trial

        @variables n:1
        @run training runlabel:1

        @variables n:2
        @run training runlabel:2

        @figure n=1
        runlabel:1
        @nplot background
        @nplot reward
        @legend

        @figure n=2
        runlabel:2
        @nplot background
        @nplot reward
        @legend

        xscale: stimulus
        @figure
        runlabel:1
        @vplot stimulus->response {'label':'n=1'}

        runlabel:2
        @vplot stimulus->response {'label':'n=2'}

        @legend
        '''
        script, script_output = run(text)

        # Figure 1
        plot_data = get_plot_data(figure_number=1)
        for y in plot_data['n(background)']['y'][-100:]:
            self.assertLess(y, 4)
            self.assertGreater(y, 0)
        for y in plot_data['n(reward)']['y'][-100:]:
            self.assertLess(y, 100)
            self.assertGreater(y, 60)

        # Figure 2
        plot_data = get_plot_data(figure_number=2)
        expected_value = 0
        for x, y in zip(plot_data['n(background)']['x'], plot_data['n(background)']['y']):
            if x <= 1:
                expected_value = 0
            else:
                expected_value = (x + 2) // 4
            self.assertEqual(y, expected_value)
        for y in plot_data['n(reward)']['y']:
            self.assertEqual(y, 0)

        # Figure 3
        plot_data = get_plot_data(figure_number=3)
        for x, y1, y2 in zip(plot_data['n=1']['x'], plot_data['n=1']['y'], plot_data['n=2']['y']):
            if x > 40:
                self.assertGreater(y1 - y2, 9)
                self.assertGreater(y2, -0.21)
                self.assertLess(y2, 0)
                self.assertGreater(y1, 9.5)
                self.assertLess(y1, 10)
        for val in plot_data['n=2']['y']:
            self.assertLess(val, 0)
            self.assertGreaterEqual(val, -1)

    def test_issue112_small(self):
        text = '''
        n_subjects        = 1
        mechanism         = sr
        behaviors         = b
        stimulus_elements = e1, e2
        start_v           = 0
        alpha_v           = 0.1
        u                 = e1:10, e2:0

        @PHASE foo stop:e1=10
        A e1   | count_line(e1)=n: B | A
        B e2   | A

        @variables x:0, n:1
        @run foo runlabel:n=1

        @variables x:1, n:2, y:3
        @run foo runlabel:n=2

        @figure
        @nplot e1
        @nplot e2
        '''
        script, script_output = run(text)
        history = script_output.run_outputs["n=1"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e2'] * 9 + ['e1'])

        history = script_output.run_outputs["n=2"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e1', 'e2'] * 4 + ['e1', 'e1'])

        # Test that count_line(e1)=n is the same as count_line(A)=n
        text = '''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : b
        stimulus_elements : e1, e2
        start_v           : 0
        alpha_v           : 0.1
        u                 : e1:10, e2:0

        @PHASE foo stop:e1=10
        A e1   | count_line(A)=n: B | A
        B e2   | A

        @variables x:0, n:1
        @run foo runlabel:n=1

        @variables x:1, n:2, y:3
        @run foo runlabel:n=2

        @variables x:1, n:20, y:3
        @run foo runlabel:n=20

        @figure
        @nplot e1
        @nplot e2
        '''
        script, script_output = run(text)
        history = script_output.run_outputs["n=1"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e2'] * 9 + ['e1'])

        history = script_output.run_outputs["n=2"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e1', 'e2'] * 4 + ['e1', 'e1'])

        history = script_output.run_outputs["n=20"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1'] * 10)

        # Test that count_line(A)=n is the same as A=n
        text = '''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : b
        stimulus_elements : e1, e2
        start_v           : 0
        alpha_v           : 0.1
        u                 : e1:10, e2:0

        @PHASE foo stop:e1=10
        A e1   | A=n: B | A
        B e2   | A

        @variables x:0, n:1
        @run foo runlabel:n=1

        @variables x:1, n:2, y:3
        @run foo runlabel:n=2

        @variables x:1, n:20, y:3
        @run foo runlabel:n=20

        @figure
        @nplot e1
        @nplot e2
        '''
        script, script_output = run(text)
        history = script_output.run_outputs["n=1"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e2'] * 9 + ['e1'])

        history = script_output.run_outputs["n=2"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e1', 'e2'] * 4 + ['e1', 'e1'])

        history = script_output.run_outputs["n=20"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1'] * 10)

        # Test that e1=n is the same as count_line(e1)=n
        text = '''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : b
        stimulus_elements : e1, e2
        start_v           : 0
        alpha_v           : 0.1
        u                 : e1:10, e2:0

        @PHASE foo stop:e1=10
        A e1   | count_line(A)=n: B | A
        B e2   | A

        @variables x:0, n:1
        @run foo runlabel:n=1

        @variables x:1, n:2, y:3
        @run foo runlabel:n=2

        @variables x:1, n:20, y:3
        @run foo runlabel:n=20

        @figure
        @nplot e1
        @nplot e2
        '''
        script, script_output = run(text)
        history = script_output.run_outputs["n=1"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e2'] * 9 + ['e1'])

        history = script_output.run_outputs["n=2"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e1', 'e2'] * 4 + ['e1', 'e1'])

        history = script_output.run_outputs["n=20"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1'] * 10)

        # Test that count_line(b)=n works
        text = '''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : b
        stimulus_elements : e1, e2
        start_v           : 0
        alpha_v           : 0.1
        u                 : e1:10, e2:0

        @PHASE foo stop:e1=10
        A e1   | count_line(b)=n: B | A
        B e2   | A

        @variables x:0, n:1
        @run foo runlabel:n=1

        @variables x:1, n:2, y:3
        @run foo runlabel:n=2

        @variables x:1, n:20, y:3
        @run foo runlabel:n=20

        @figure
        @nplot e1
        @nplot e2
        '''
        script, script_output = run(text)
        history = script_output.run_outputs["n=1"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e2'] * 9 + ['e1'])

        history = script_output.run_outputs["n=2"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1', 'e1', 'e2'] * 4 + ['e1', 'e1'])

        history = script_output.run_outputs["n=20"].output_subjects[0].history
        self.assertEqual(history[0::2], ['e1'] * 10)

    def test_issue125(self):
        text = '''
        ########################  Parameters   ##########################################################

        n_subjects              : 10
        mechanism               : GA
        behaviors               : behaviour, other
        stimulus_elements       : food, s0, s1, s2
        #response_requirements  :
        #mu                     :
        start_v                 : s0->behaviour:-1, s1->behaviour:-1, s2->behaviour:-1,  default: 1 
        alpha_v                 : 0.1
        alpha_w                 : 0.1
        behavior_cost           : behaviour:2, default:0
        beta                    : 1
        u                       : food:10, default:0 
        #bind_trials            : off     
        cumulative: on



        ########################  Describe Phases   #####################################################

        @phase environment stop: food=100                                               # stop when there are 100 rewards given out 
        START0       t0:0              | NEXT0                                              # Reset counter #1
        NEXT0        t0:t0+1           | t0=50: START1 | S0
        S0           s0                | NEXT0

        START1       t1:0              | NEXT1
        NEXT1        t1:t1+1           | t1=3: S_FOOD   | S1
        S1           s1                | NEXT1          

        S_FOOD       s1,s2                     | behaviour:FOOD         | START0
        FOOD         food              | START0                                 

                                                    

         

        ########################   Start Running   ######################################################

        @run environment


        #######################    Figures    ##########################################################

        xscale:food
        subject: average
        @figure Predicting stimuli


        @subplot 111  {'xlabel':'Reward number', 'ylabel':'probability', 'ylim':[-0.03,1] }
        @pplot s0->behaviour
        @pplot s1->behaviour
        @pplot s1,s2->behaviour
        @legend
        '''
        run(text)


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
        response_requirements = b1:[s1,s2], b2:[s1,s2]
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

        @phase experiment stop: START=100
        INIT_FOO   foo:0      | START
        START      s_start    | FOO
        FOO        foo:foo+1  | STEP1
        STEP1      s1         | b1: STEP2       | START
        STEP2      s2         | b2: OUTCOME     | START
        OUTCOME               | foo<=50: REWARD | NO_REWARD
        REWARD     reward     | START
        NO_REWARD  no_reward  | START

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
        self.assertEqual(plotted_xdata, list(range(0, 100)))
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
        self.assertEqual(plotted_xdata, list(range(0, 100)))
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

        @phase acquisition  stop: nju_trial= 100
        nju_trial             | CS2
        CS2        cs2        | CS1
        CS1        cs1        | US
        US         us           | @omit_learn, nju_trial

        @phase revaluation stop: nju_trial=50
        nju_trial             | CS1
        CS1        cs1        | NO_US
        NO_US      no_us      | @omit_learn, nju_trial

        @phase extinction stop: nju_trial=40
        nju_trial             | CS2
        CS2        cs2        | NO_US
        NO_US      no_us      | @omit_learn, nju_trial

        @phase reacquisition(acquisition) stop: nju_trial=40

        @run acquisition,revaluation,extinction,reacquisition   runlabel:'exp'
        @run acquisition,extinction,reacquisition   runlabel:'control'

        xscale: nju_trial
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

        @phase acquisition  stop: nju_trial=5
        nju_trial             | CS2
        CS2        cs2        | CS1
        CS1        cs1        | US
        US         us         | @omit_learn, nju_trial

        @run acquisition

        xscale: nju_trial
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

        @phase acquisition stop: nju_trial=50
        nju_trial   s_start  | STEP1
        STEP1       s1,m1,m2 | b1: STEP2   |  nju_trial
        STEP2       s2,m1,m2 | b2: REWARD  |  nju_trial
        REWARD      reward   | nju_trial

        @phase extinction stop: nju_trial=500
        nju_trial   s_start  | STEP1
        STEP1       s1       | b1: STEP2   | NEXT
        STEP2       s2       | NEXT
        NEXT                 | nju_trial

        bind_trials: on
        @run acquisition, extinction

        xscale: s_start
        subject: average

        @figure Probability
        @pplot s1->b1
        '''
        msg = "Error in @pplot: Behavior 'b1' is not a possible response to 's1'."
        with self.assertRaisesMsg(msg):
            run(text)
