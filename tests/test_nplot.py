import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


def get_match_script(nplot_expr, match, xscale, xscale_match, cumulative):
    return f'''
    n_subjects        : 1
    mechanism         : SR
    behaviors         : b
    stimulus_elements : s1, s2, s3
    alpha_v           : 1

    @phase ph1 stop:s3=10
    S1     s1              | S2_1
    S2_1   s2              | S2_2
    S2_2   s2              | S1S2
    S1S2   s1, s2          | S3
    S3     s3              | S1

    @run ph1

    match: {match}
    xscale_match: {xscale_match}
    cumulative: {cumulative}
    xscale: {xscale}
    @figure
    @nplot {nplot_expr}
    '''


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
        self.assertEqual(plot_data['y'], [4, 5, 5, 5, 5, 5, 5, 5, 5, 5])

    def test_simple_cumulative(self):
        def get_script(cumulative):
            return f'''
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

            #@phase ph1 stop:s3=10
            #S1_1   s1              | S2_1
            #S2_1   s2              | S1_2
            #S1_2   s1              | S2_2
            #S2_2   s2              | S3
            #S3     s3              | S1_1

            @run ph1

            cumulative: {cumulative}
            xscale: s3
            phases: ph1
            @nplot b
            '''
        text = get_script("on")
        obj, simulation_data = run(text)

        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's1', 'b', 's2', 'b', 's3', 'b'] * 10)

        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [4, 9, 14, 19, 24, 29, 34, 39, 44, 49])

        plt.close('all')

        text = get_script("off")
        obj, simulation_data = run(text)

        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's1', 'b', 's2', 'b', 's3', 'b'] * 10)

        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [4, 5, 5, 5, 5, 5, 5, 5, 5, 5])

    def test_match(self):
        # Count the five 'b' between each xscale="s3" (except that there are three 'b' before the first 's3')
        text = get_match_script(nplot_expr="b", match="exact", xscale="s3",
                                xscale_match="exact", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [4, 9, 14, 19, 24, 29, 34, 39, 44, 49])

        plt.close('all')

        # Using match="subset" has no effect when nplot_expr is not compound
        text = get_match_script(nplot_expr="b", match="subset", xscale="s3",
                                xscale_match="exact", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [4, 9, 14, 19, 24, 29, 34, 39, 44, 49])

        plt.close('all')

        # Using xscale_match="subset" has no effect when scale is not compound
        text = get_match_script(nplot_expr="b", match="subset", xscale="s3",
                                xscale_match="subset", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [4, 9, 14, 19, 24, 29, 34, 39, 44, 49])

        plt.close('all')

        # If nplot_expr="s1,s2", then match="exact" should only count the ('s1', 's2')
        # entries in the history (one between each xscale="s3")
        text = get_match_script(nplot_expr="s1,s2", match="exact", xscale="s3",
                                xscale_match="subset", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        plt.close('all')

        # Same as above with cumulative="off"
        text = get_match_script(nplot_expr="s1,s2", match="exact", xscale="s3",
                                xscale_match="subset", cumulative="off")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        plt.close('all')

        # If nplot_expr="s1", then match="exact" should NOT count the ('s1', 's2')
        # entries in the history
        text = get_match_script(nplot_expr="s1", match="exact", xscale="s3",
                                xscale_match="subset", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        plt.close('all')

        # Same as above with cumulative="off"
        text = get_match_script(nplot_expr="s1,s2", match="exact", xscale="s3",
                                xscale_match="subset", cumulative="off")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        plt.close('all')

        # If nplot_expr="s1", then match="subset" should count both the ('s1', 's2') and the 's1'
        # entries in the history (two between each xscale="s3")
        text = get_match_script(nplot_expr="s1", match="subset", xscale="s3",
                                xscale_match="subset", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [2, 4, 6, 8, 10, 12, 14, 16, 18, 20])

        plt.close('all')

        # Same as above with cumulative="off"
        text = get_match_script(nplot_expr="s1", match="subset", xscale="s3",
                                xscale_match="subset", cumulative="off")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2])

        plt.close('all')

        # If nplot_expr="s2", then match="subset" should count both the ('s1', 's2') and the 's2'
        # entries in the history (three between each xscale="s3")
        text = get_match_script(nplot_expr="s2", match="subset", xscale="s3",
                                xscale_match="subset", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [3, 6, 9, 12, 15, 18, 21, 24, 27, 30])

        plt.close('all')

        # Same as above with cumulative="off"
        text = get_match_script(nplot_expr="s2", match="subset", xscale="s3",
                                xscale_match="subset", cumulative="off")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [3, 3, 3, 3, 3, 3, 3, 3, 3, 3])

    def test_xscale_match(self):
        # Count the entries 's1','s2' exactly
        text = get_match_script(nplot_expr="b", match="exact", xscale="s1,s2",
                                xscale_match="exact", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [3, 8, 13, 18, 23, 28, 33, 38, 43, 48])

        plt.close('all')

        # Same as above with cumulative="off"
        text = get_match_script(nplot_expr="b", match="exact", xscale="s1,s2",
                                xscale_match="exact", cumulative="off")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [3, 5, 5, 5, 5, 5, 5, 5, 5, 5])

        plt.close('all')

        # Count the entries "('s1','s2'), b" exactly
        text = get_match_script(nplot_expr="b", match="exact", xscale="s1,s2 -> b",
                                xscale_match="exact", cumulative="on")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [3, 8, 13, 18, 23, 28, 33, 38, 43, 48])

        plt.close('all')

        # Same as above with cumulative="off"
        text = get_match_script(nplot_expr="b", match="exact", xscale="s1,s2 -> b",
                                xscale_match="exact", cumulative="off")
        obj, simulation_data = run(text)
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        self.assertEqual(history, ['s1', 'b', 's2', 'b', 's2', 'b', ('s1', 's2'), 'b', 's3', 'b'] * 10)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['x'], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(plot_data['y'], [3, 5, 5, 5, 5, 5, 5, 5, 5, 5])

    def test_p_vs_n1(self):
        ntrials = 180
        text = f'''
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

        @phase chaining_experiment stop: nju_trial={ntrials}
        nju_trial  s_start    | STEP1
        STEP1      s1         | b1: STEP2   |  @omit_learn, nju_trial
        STEP2      s2         | b2: OUTCOME |  @omit_learn, nju_trial
        OUTCOME               | count(STEP2)<=60: REWARD | NO_REWARD
        REWARD     reward     | @omit_learn, nju_trial
        NO_REWARD  no_reward  | @omit_learn, nju_trial

        bind_trials: off
        @run chaining_experiment

        xscale: s1
        subject: average
        cumulative: off

        # @subplot 111 {{'xlim':[1,100]}}
        @pplot s1->b1
        @nplot b1
        @legend'''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 3)
        plot_data = get_plot_data()
        pplot = plot_data['p(s1->b1)']
        nplot = plot_data['n(b1)']
        self.assertEqual(pplot['x'], list(range(ntrials)))
        self.assertEqual(nplot['x'], list(range(ntrials - 1)))
        pploty = pplot['y'][2:(ntrials - 2)]
        nploty = nplot['y'][2:(ntrials - 2)]
        sum_of_squares = 0
        for py, ny in zip(pploty, nploty):
            sum_of_squares += (py - ny)**2
        self.assertLess(sum_of_squares, 0.4)

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
        self.assertEqual(nplot['x'], list(range(0, 100)))
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
        with self.assertRaisesMsg(msg):
            run(text)
