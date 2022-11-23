import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestCases(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_intensities(self):
        text = '''
n_subjects        : 1000
mechanism         : sr
behaviors         : response, no_response
stimulus_elements : background, stimulus, reward
start_v           : default:-1
alpha_v           : 0.1
u                 : reward:10, default:0

@PHASE training stop: stimulus=5
@new_trial  stimulus   | response: REWARD | NO_REWARD
REWARD      reward     | @new_trial
NO_REWARD   background | @new_trial

@run training

title: p(stimulus->response)
xscale: stimulus
subject: average
@figure

@pplot stimulus[0.1]->response {'label':0.1}
@pplot stimulus[0.2]->response {'label':0.2}
@pplot stimulus[0.3]->response {'label':0.3}
@pplot stimulus[0.4]->response {'label':0.4}
@pplot stimulus[0.5]->response {'label':0.5}
@pplot stimulus[0.8]->response {'label':0.8}
@pplot stimulus[1.0]->response {'label':1.0}
@pplot stimulus[2.0]->response {'label':2.0}
@legend
        '''
        script_obj, script_output = run(text)
        plot_data = get_plot_data()

        for lbl in ['0.1', '0.2', '0.3', '0.4', '0.5', '0.8', '1.0', '2.0']:
            self.assertEqual(plot_data[lbl]['x'][0], 0.0)
            self.assertEqual(plot_data[lbl]['y'][0], 0.5)

        y01 = plot_data['0.1']['y'][-1]
        y02 = plot_data['0.2']['y'][-1]
        y03 = plot_data['0.3']['y'][-1]
        y04 = plot_data['0.4']['y'][-1]
        y05 = plot_data['0.5']['y'][-1]
        y08 = plot_data['0.8']['y'][-1]
        y10 = plot_data['1.0']['y'][-1]
        y20 = plot_data['2.0']['y'][-1]

        self.assertLess(0.5, y01)
        self.assertLess(y01, y02)
        self.assertLess(y02, y03)
        self.assertLess(y03, y04)
        self.assertLess(y04, y05)
        self.assertLess(y05, y08)
        self.assertLess(y08, y10)
        self.assertLess(y10, y20)
        self.assertLess(y20, 1.0)

    def test_compound(self):
        text = '''
n_subjects        : 1000
mechanism         : sr
behaviors         : response, no_response
stimulus_elements : background, stimulus, reward
start_v           : default:-1
alpha_v           : 0.1
u                 : reward:10, default:0

@PHASE training stop: stimulus=5
@new_trial  stimulus   | response: REWARD | NO_REWARD
REWARD      reward     | @new_trial
NO_REWARD   background | @new_trial

@run training

xscale: stimulus
subject: average

@pplot background,stimulus[0.5]->response {'label':'bg'}
@pplot reward[1.5],stimulus[0.1]->response {'label':'bg1.5'}
@pplot reward[1.5],stimulus[0]->response {'label':'just_testing_[0]'}
@legend
        '''
        script_obj, script_output = run(text)
        plot_data = get_plot_data()

        for lbl in ['bg', 'bg1.5']:
            self.assertEqual(plot_data[lbl]['x'][0], 0.0)
            self.assertEqual(plot_data[lbl]['y'][0], 0.5)

        y_bg = plot_data['bg']['y'][-1]
        y_bg15 = plot_data['bg1.5']['y'][-1]
        self.assertGreater(y_bg15, 0.5)
        self.assertLess(y_bg15, 0.6)
        self.assertGreater(y_bg, 0.7)
        self.assertLess(y_bg, 0.8)

    def test_beta_mu_not_post_params(self):
        '''
        Tests that beta, mu, and response_requirements are not postprocessing parameters,
        in other words that the values for these parameters used in the postprocessing
        should come from the run that is being postprocessed.
        '''
        text = '''
        n_subjects        : 10
        mechanism         : sr
        behaviors         : response, no_response
        stimulus_elements : background, stimulus, reward
        start_v           : default:-1
        alpha_v           : 0.1
        u                 : reward:5, default:0
        beta              : 1
        mu                : 1

        @PHASE training stop: stimulus=20
        start_trial  stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | start_trial
        NO_REWARD   background | start_trial

        @run training

        xscale: stimulus
        subject: average        

        @pplot stimulus->response {'label':'orig'}

        beta:10
        @pplot stimulus->response {'label':'beta'}

        mu = stimulus->response:0.1, default:2
        @pplot stimulus->response {'label':'mu'}
        '''
        run(text)
        plot_data = get_plot_data()

        orig = plot_data['orig']['y']
        beta = plot_data['beta']['y']
        mu = plot_data['mu']['y']
        for o, b, m in zip(orig, beta, mu):
            o_rounded = round(o, 5)
            b_rounded = round(b, 5)
            m_rounded = round(m, 5)
            self.assertEqual(o_rounded, b_rounded)
            self.assertEqual(b_rounded, m_rounded)


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_no_run(self):
        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase foo stop:s1=2
        L1 s1 | L1
        @vplot s1->b
        """
        msg = "Error on line 8: There is no @RUN."
        with self.assertRaisesMsg(msg):
            run(text)

    @staticmethod
    def get_pplot_errors_script(pplot_expr):
        return f'''
n_subjects           : 1
mechanism            : SR
behaviors            : approach, eat, other
stimulus_elements    : plant, berry, sugar, no_reward
response_requirements: approach:plant, eat:berry
start_v              : plant->other:0, berry->other:0, default:-1
alpha_v              : 0.1
alpha_w              : 0.1
beta                 : 1
behavior_cost        : approach:1, default: 0
u                    : sugar:10, default:0

@phase acquisition stop: plant=30
new_trial             | PLANT
PLANT       plant     | approach: BERRY | new_trial
BERRY       berry     | eat: REWARD     | NO_REWARD
REWARD      sugar     | new_trial
NO_REWARD   no_reward | new_trial

trace: 0.25
@run acquisition runlabel:0.25

@pplot {pplot_expr}
'''

    def test_pplot_errors(self):
        pplot_exprs = [("plant[[0.25],berry -> eat", "Error on line 24: Invalid expression plant[[0.25]."),
                       ("plant0.25],berry -> eat", "Error on line 24: Expected a stimulus element, got plant0.25]."),
                       ("plant[0.25,berry -> eat", "Error on line 24: Invalid expression plant[0.25."),
                       ("plant[0.25]],berry -> eat", "Error on line 24: Invalid expression plant[0.25]]."),
                       ("plant[x],berry -> eat", "Error on line 24: Invalid expression plant[x]."),
                       ("plant(0.25),berry -> eat", "Error on line 24: Expected a stimulus element, got plant(0.25)."),
                       ("plant(0.25),berry eat", "Error on line 24: Expression must include a '->'."),
                       ("plant(0.25),berry -> eat -> approach", "Error on line 24: Expression must include only one '->'."),
                       ("-> eat -> approach", "Error on line 24: Expression must include only one '->'."),
                       ("-> eat", "Error on line 24: Expected a stimulus element, got ."),
                       ("plant[0.2]->  foo", "Error on line 24: Expected a behavior name, got foo.")]
        for pplot_expr in pplot_exprs:
            script = self.get_pplot_errors_script(pplot_expr[0])
            err_msg = pplot_expr[1]
            with self.assertRaisesMsg(err_msg):
                run(script)
