from math import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, ceil, floor, exp, log, log10, sqrt

import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestPlotArithmetic(LsTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_plot_same_as_xplot(self):
        text = """
        n_subjects        = 10
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -1
        alpha_v           = 0.1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==50
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        @vplot stimulus->response    {'label': 'vplot'}
        @plot v(stimulus->response)  {'label': 'plotv'}

        @pplot stimulus->response    {'label': 'pplot'}
        @plot p(stimulus->response)  {'label': 'plotp'}

        @wplot stimulus    {'label': 'wplot'}
        @plot w(stimulus)  {'label': 'plotw'}

        @nplot stimulus->response->reward    {'label': 'nplot'}
        @plot n(stimulus->response->reward)  {'label': 'plotn'}
        """
        run(text)
        pd = get_plot_data()
        self.assertAlmostEqualList(pd['vplot']['y'], pd['plotv']['y'])
        self.assertAlmostEqualList(pd['pplot']['y'], pd['plotp']['y'])
        self.assertAlmostEqualList(pd['wplot']['y'], pd['plotw']['y'])
        self.assertAlmostEqualList(pd['nplot']['y'], pd['plotn']['y'])

    def test_correct_computations(self):
        text = """
        n_subjects        = 10
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -1
        alpha_v           = 0.1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==50
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        @vplot stimulus->response         {'label': 'vplot'}
        @pplot stimulus->response         {'label': 'pplot'}
        @wplot stimulus                   {'label': 'wplot'}
        @nplot stimulus->response->reward {'label': 'nplot'}

        @plot v(stimulus->response) + 10 * p(stimulus->response) - w(stimulus)**3 / (1 + n(stimulus->response->reward)) {'label': 'expr'}
        """
        run(text)
        pd = get_plot_data()
        vplot = pd['vplot']['y']
        pplot = pd['pplot']['y']
        wplot = pd['wplot']['y']
        nplot = pd['nplot']['y']
        expr = pd['expr']['y']
        for v, p, w, n, e_lesim in zip(vplot, pplot, wplot, nplot, expr):
            e_python = v + 10 * p - w**3 / (1 + n)
            self.assertAlmostEqual(e_lesim, e_python)

    def test_consecutive_pplot(self):
        text = """
n_subjects           : 100
mechanism            : A
behaviors            : approach, eat, other
stimulus_elements    : plant, berry, sugar, no_reward
response_requirements: approach:plant, eat:berry
start_v              : plant->other:0, berry->other:0, default:-2
alpha_v              : 0.1
alpha_w              : 0.1
beta                 : 1
behavior_cost        : approach:1, default: 0
u                    : sugar:10, default:0

@phase acquisition stop: plant=200
START                 | PLANT
PLANT       plant     | approach: BERRY | START
BERRY       berry     | eat: REWARD     | NO_REWARD
REWARD      sugar     | START
NO_REWARD   no_reward | START

@run acquisition

xscale = plant
cumulative = off
@plot n(plant->approach->berry->eat)  {'label':'nplot'}
@plot p(plant->approach) * p(berry->eat)  {'label':'pplot'}
"""
        run(text)
        pd = get_plot_data()
        nplot = pd['nplot']['y']
        pplot = pd['pplot']['y']
        for n, p in zip(nplot, pplot):
            d = abs(n - p)
            self.assertLess(d, 0.155)

    def test_pplot_with_compound_stimuli(self):  # Same test as in test_pplot but with @plot p(...) instead of @pplot ...
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

# @pplot background,stimulus[0.5]->response {'label':'bg'}
# @pplot reward[1.5],stimulus[0.1]->response {'label':'bg1.5'}
# @pplot reward[1.5],stimulus[0]->response {'label':'just_testing_[0]'}

@plot p(background,stimulus[0.5]->response) {'label':'bg'}
@plot p(reward[1.5],stimulus[0.1]->response) {'label':'bg1.5'}
@plot p(reward[1.5],stimulus[0]->response) {'label':'just_testing_[0]'}

@legend
        '''
        run(text)
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

    def test_using_variables(self):
        text = """
        mechanism: sr
        stimulus_elements: s
        behaviors: b

        @variables x = -1, y = 2, z = 3

        @phase phase1 stop:s=10
        NT s | NT

        @run phase1

        xscale: s
        @plot n(s)  {'label': 'nplot'}
        @plot n(s)**y + x - z * sin(n(s)) {'label': 'expr'}
        """
        run(text)
        pd = get_plot_data()
        nplot = pd['nplot']['y']
        expr = pd['expr']['y']
        x = -1
        y = 2
        z = 3
        for n, e_lesim in zip(nplot, expr):
            e_python = n**y + x - z * sin(n)
            self.assertAlmostEqual(e_lesim, e_python)

    def test_all_math_functions(self):
        text = """
        n_subjects        = 1
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, s, reward
        start_v           = -1
        alpha_v           = 0.1
        u                 = reward:10, default:0

        @PHASE training stop: s==5
        START       s          | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: s

        @plot v(s->response)  {'label': 'vplot'}

        @plot sin(n(s)) + cos(n(s)) + tan(n(s)) + asin(n(s) / (n(s)+1)) + acos(n(s) / (n(s)+1)) + atan(n(s) / (n(s)+1))  {'label': 'trig'}
        @plot sinh(n(s)) + cosh(n(s)) + tanh(n(s)) + asinh(n(s) / (n(s)+1)) + acosh(1 + n(s)/(n(s)+1)) + atanh(n(s)/(n(s)+1))  {'label': 'hyp'}
        @plot ceil(v(s->response)) + floor(v(s->response)) + round(v(s->response))  {'label':'rounding'}
        @plot exp(n(s)) + log(1+n(s)) + log10(1+n(s)) + sqrt(n(s))  {'label': 'other'}
        """
        run(text)
        pd = get_plot_data()
        vplot = pd['vplot']['y']
        trig = pd['trig']['y']
        hyp = pd['hyp']['y']
        rounding = pd['rounding']['y']
        other = pd['other']['y']
        n = 0
        for t, h, r, o, v in zip(trig, hyp, rounding, other, vplot):
            t_python = sin(n) + cos(n) + tan(n) + asin(n / (n + 1)) + acos(n / (n + 1)) + atan(n / (n + 1))
            self.assertAlmostEqual(t_python, t)

            h_python = sinh(n) + cosh(n) + tanh(n) + asinh(n / (n + 1)) + acosh(1 + n / (n + 1)) + atanh(n / (n + 1))
            self.assertAlmostEqual(h_python, h)

            r_python = ceil(v) + floor(v) + round(v)
            self.assertAlmostEqual(r_python, r)

            o_python = exp(n) + log(1 + n) + log10(1 + n) + sqrt(n)
            self.assertAlmostEqual(o_python, o)

            n += 1

    def test_multiple_n(self):
        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b, b2
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=20
        L1 s1 | L1
        @run blaps

        cumulative = off
        xscale = all
        @plot n(s1) + n(s2) - n(s1->b)        
        xscale = s2
        @plot n(s1) + n(s2) - n(s1->b)

        cumulative = on
        xscale = all
        @plot n(s1) + n(s2) - n(s1->b)        
        xscale = s2
        @plot n(s1) + n(s2) - n(s1->b)
        """
        run(text)


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_no_arguments(self):
        text_base = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot {}
        """

        text = text_base.format("v()")
        msg = "Error on line 8: Expression must include a '->'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("p()")
        msg = "Error on line 8: Expression must include a '->'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("w()")
        msg = "Error on line 8: Expected a stimulus element, got ."
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("n()")
        msg = "Error on line 8: Expected stimulus element(s) or a behavior, got ."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_no_right_parentesis(self):
        text_base = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot {}
        """
        text = text_base.format("v(s1->b")
        msg = "Error on line 9: Missing right parenthesis in expression v(s1->b"
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("p(s1->b")
        msg = "Error on line 9: Missing right parenthesis in expression p(s1->b"
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("w(s1")
        msg = "Error on line 9: Missing right parenthesis in expression w(s1"
        with self.assertRaisesMsg(msg):
            run(text)
        
        text = text_base.format("n(s1->b->s2")
        msg = "Error on line 9: Missing right parenthesis in expression n(s1->b->s2"
        with self.assertRaisesMsg(msg):
            run(text)


    def test_wrong_parenteses(self):
        text_base = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot {}
        """
        for e in {"v((s1->b))", "p((((((s1->b))", "w(s1)))))", "n((s1->b->s2))"}:
            text = text_base.format(e)
            msg = "Error on line 9: Error in expression."
            with self.assertRaisesMsg(msg):
                run(text)

        text = text_base.format("s1->b")
        msg = "Error on line 9: Invalid expression s1->b"
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("blaps")
        msg = "Error on line 9: Invalid expression blaps"
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("")
        msg = "Error on line 9: Invalid @plot command."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_space_after_at(self):
        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @ plot
        """
        msg = "Error on line 9: Phase @ undefined."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @ plot foo
        """
        msg = "Error on line 9: Phase @ undefined."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_undefined_function(self):
        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot foo(n(s))
        """
        msg = "Error on line 9: Invalid name foo in expression."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot round2(n(s))
        """
        msg = "Error on line 9: Invalid name round2 in expression."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_error_in_function(self):
        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot n(s) / 0
        """
        msg = "Error on line 9: Expected stimulus element(s) or a behavior, got s."
        with self.assertRaisesMsg(msg):
            run(text)

        text_base = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot {}
        """
        msg = "Error on line 9: Expression evaluation failed."
        for e in {"n(s1) / 0", "log(-n(b))", "v(s1->b) / (v(s1->b)-v(s1->b))"}:
            text = text_base.format(e)
            with self.assertRaisesMsg(msg):
                run(text)

        text = text_base.format("n(s1) / (v(s1->b) + v(s1->b))")
        with self.assertRaisesMsg("Error on line 9: Cannot mix n with v,p,w,vss when xscale is 'all'."):
            run(text)

    def test_wildcard(self):
        text_base = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot {}
        """
        msg = "Error on line 9: Wildcard syntax not supported in @plot/@export."
        for e in {"v(s1-> * )", "w( *)", "w(* )", "v(s1->b) + v(*->b)"}:
            text = text_base.format(e)
            with self.assertRaisesMsg(msg):
                run(text)

        text = text_base.format("n(*)")
        with self.assertRaisesMsg("Error on line 9: Expected stimulus element(s) or a behavior, got *."):
            run(text)                

    def test_try_boom(self):
        text_base = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase blaps stop:s1=2
        L1 s1 | L1
        @run blaps
        @plot {}
        """
        msg = "Error on line 9: Error in expression."
        text = text_base.format("@plot __import__('os').system('clear')+w(s)")
        with self.assertRaisesMsg(msg):
            run(text)

        text = text_base.format("@plot __import__('os').system('clear')")
        msg = "Error on line 9: Invalid expression @plot __import__('os').system('clear')"
        with self.assertRaisesMsg(msg):
            run(text)
