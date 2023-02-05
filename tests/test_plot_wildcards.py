import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestPlotWildcards(LsTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_wildcard_same_as_vplot1(self):
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

        @figure
        @vplot stimulus->response
        @vplot stimulus->no_response
        @vplot background->response
        @vplot background->no_response
        @vplot reward->response
        @vplot reward->no_response
        @legend

        @figure
        @vplot * -> *
        @legend
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)

    def test_wildcard_same_as_vplot2(self):
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

        @figure
        @vplot stimulus->response
        @vplot stimulus->no_response
        @legend

        @figure
        @vplot stimulus -> *
        @legend
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)

    def test_wildcard_same_as_vplot3(self):
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

        @figure
        @vplot stimulus->response
        @vplot background->response
        @vplot reward->response
        @legend

        @figure
        @vplot * -> response
        @legend
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)


    def test_wildcard_same_as_pplot1(self):
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

        @figure
        @pplot stimulus->response
        @pplot stimulus->no_response
        @pplot background->response
        @pplot background->no_response
        @pplot reward->response
        @pplot reward->no_response
        @legend

        @figure
        @pplot * -> *
        @legend
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)

    def test_wildcard_same_as_pplot2(self):
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

        @figure
        @pplot stimulus->response
        @pplot stimulus->no_response
        @legend

        @figure
        @pplot stimulus -> *
        @legend
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)

    def test_wildcard_same_as_pplot3(self):
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

        @figure
        @pplot stimulus->no_response
        @pplot background->no_response
        @pplot reward->no_response
        @legend

        @figure
        @pplot * -> no_response
        @legend
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)


    def test_wildcard_same_as_wplot(self):
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

        @figure
        @wplot stimulus
        @wplot background
        @wplot reward
        @legend

        @figure
        @wplot *
        @legend
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)

    def test_wildcard_same_as_vssplot(self):
        text = """
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        xscale:cs

        @figure
        @vssplot cs->cs        
        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us

        @figure
        @vssplot *->*
        """
        run(text)
        pd1 = get_plot_data(figure_number=1)
        pd2 = get_plot_data(figure_number=2)
        self.assertEqual(set(pd1.keys()), set(pd2.keys()))

        for lbl in pd1:
            x1 = pd1[lbl]['x']
            x2 = pd2[lbl]['x']
            self.assertAlmostEqualList(x1, x2)

            y1 = pd1[lbl]['y']
            y2 = pd2[lbl]['y']
            self.assertAlmostEqualList(y1, y2)

    def test_wildcard_same_as_vssplot(self):
        text = """
        n_subjects        = 2
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
        subject = all

        @vplot stimulus -> * 
        @legend
        """
        run(text)
        pd = get_plot_data()
        self.assertEqual(set(pd.keys()), {'v(stimulus->response), subject 2', 'v(stimulus->response), subject 1', 'v(stimulus->no_response), subject 2', 'v(stimulus->no_response), subject 1'})

    def test_wildcard_same_as_vssplot(self):
        text = """
        n_subjects        = 2
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
        subject = all

        @vplot stimulus -> * {'label':'foo'} 
        @legend
        """
        run(text)
        pd = get_plot_data()
        self.assertEqual(set(pd.keys()), {'foo, subject 2', 'foo, subject 1'})

    def test_wildcard_same_as_vssplot(self):
        text = """
        n_subjects        = 2
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
        subject = average

        @vplot stimulus -> * {'label':'foo'} 
        @legend
        """
        run(text)
        pd = get_plot_data()
        self.assertEqual(set(pd.keys()), {'foo'})


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def foo_test_no_arguments(self):
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

