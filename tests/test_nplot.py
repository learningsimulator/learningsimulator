import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestInitialValues(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_simple(self):
        text = '''
        n_subjects        : 1
        mechanism         : SR
        behaviors         : b
        stimulus_elements : s1, s2, s3
        start_v           : s1->b:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : default:0
        u                 : s1:2, default:0

        @phase ph1 stop:s3=10
        S1     s1              | S2
        S2     s2              | count(S1)<2: S1 | S3H
        S3H    count_reset(S1) | S3
        S3     s3              | S1

        @run ph1

        cumulative: off
        xscale: s3
        phases: ph1
        @nplot b
        '''
        run(text)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [0, 4, 5, 5, 5, 5, 5, 5, 5, 5])

    def test_simple_cumulative(self):
        text = '''
        n_subjects        : 1
        mechanism         : SR
        behaviors         : b
        stimulus_elements : s1, s2, s3
        start_v           : s1->b:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : default:0
        u                 : s1:2, default:0

        @phase ph1 stop:s3=10
        S1     s1              | S2
        S2     s2              | count(S1)<2: S1 | S3H
        S3H    count_reset(S1) | S3
        S3     s3              | S1

        @run ph1

        cumulative: on
        xscale: s3
        phases: ph1
        @nplot b
        '''
        run(text)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [0, 4, 9, 14, 19, 24, 29, 34, 39, 44])

    def test_p_vs_n1(self):
        text = '''
        n_subjects        : 100
        mechanism         : GA
        behaviors         : b1,b2,ignore
        stimulus_elements : s_start,s1,s2,reward, no_reward
        response_requirements: b1:s1, b2:s2
        start_v           : s1->ignore:0, s2->ignore:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : ignore:0, default: 0
        u                 : reward:5, default:0

        @phase chaining_experiment stop: new_trial=120
        new_trial  s_start    | STEP1
        STEP1      s1         | b1: STEP2   |  new_trial
        STEP2      s2         | b2: OUTCOME |  new_trial
        OUTCOME               | count(new_trial)<=60: REWARD | NO_REWARD
        REWARD     reward     | new_trial
        NO_REWARD  no_reward  | new_trial

        bind_trials: off   #try also with on
        @run chaining_experiment

        xscale: s1
        subject: average
        cumulative: off

        @pplot s1->b1
        @nplot b1
        @legend
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 3)
        plot_data = get_plot_data()
        pplot = plot_data['p(s1->b1)']
        nplot = plot_data['n(b1)']
        self.assertEqual(pplot['x'], list(range(119)))
        self.assertEqual(nplot['x'], list(range(120)))
        pploty = pplot['y'][2:118]
        nploty = nplot['y'][2:118]
        sum_of_squares = 0
        for py, ny in zip(pploty, nploty):
            sum_of_squares += (py - ny)**2
        self.assertLess(sum_of_squares, 0.3)

    def test_p_vs_n2(self):
        text = '''
        n_subjects        : 500
        mechanism         : SR
        behaviors         : respond,ignore
        stimulus_elements : s, reward
        start_v           : s->ignore:0, default:-1
        alpha_v           : 0.1
        beta              : 1
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=100
        STIMULUS    s          | respond: REWARD  | STIMULUS
        REWARD      reward     | STIMULUS

        @run instrumental_conditioning

        xscale: s
        cumulative: off
        subject: average

        @figure
        @nplot reward
        @pplot s->respond
        @legend
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 4)
        plot_data = get_plot_data()
        pplot = plot_data['p(s->respond)']
        nplot = plot_data['n(reward)']
        self.assertEqual(pplot['x'], list(range(100)))
        self.assertEqual(nplot['x'], list(range(101)))
        pploty = pplot['y'][2:98]
        nploty = nplot['y'][2:98]
        sum_of_squares = 0
        for py, ny in zip(pploty, nploty):
            sum_of_squares += (py - ny)**2
        self.assertLess(sum_of_squares, 0.2)


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_xscale_is_phase_line_label(self):
        text = '''
        n_subjects        : 1
        mechanism         : SR
        behaviors         : b
        stimulus_elements : s1, s2, s3
        start_v           : s1->b:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : default:0
        u                 : s1:2, default:0

        @phase ph1 stop:s3=10
        S1     s1              | S2
        S2     s2              | count(S1)<2: S1 | S3H
        S3H    count_reset(S1) | S3
        S3     s3              | S1

        @run ph1

        cumulative: off
        xscale: S3
        phases: ph1
        @nplot b
        '''
        msg = "xscale cannot be a phase line label in @nplot/@nexport."
        with self.assertRaisesX(Exception, msg):
            run(text)
