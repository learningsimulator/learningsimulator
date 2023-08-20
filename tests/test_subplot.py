import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_single_subject(self):
        text = '''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : response, no_response
        stimulus_elements : background, stimulus, reward
        start_v           : default:-1
        alpha_v           : 0.1
        u                 : reward:10, default:0

        @PHASE training stop: stimulus=10
        @new_trial  stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @new_trial
        NO_REWARD   background | @new_trial

        @run training

        @figure 1
        @panel 111 subplot title 1   {'facecolor':'red'}
        subject: average
        @vplot stimulus->response

        @figure 2
        @subplot (1,   1,1  ) subplot title 2
        @vplot stimulus->response

        @figure 3
        @subplot 224 subplot title 3{'facecolor':'red'}
        @vplot stimulus->response

        @figure 4
        @subplot (  2,2,4  ) subplot title 4
        @vplot stimulus->response

        @figure 5
        @subplot (4,4,16)
        @vplot stimulus->response
        '''
        run(text)

        ax1 = plt.figure(1).axes[0]
        ax2 = plt.figure(2).axes[0]
        ax3 = plt.figure(3).axes[0]
        ax4 = plt.figure(4).axes[0]

        self.assertEqual(ax1.get_title(), "subplot title 1")
        self.assertEqual(ax2.get_title(), "subplot title 2")
        self.assertEqual(ax3.get_title(), "subplot title 3")
        self.assertEqual(ax4.get_title(), "subplot title 4")

        self.assertEqual(ax1.get_facecolor(), (1, 0, 0, 1))
        self.assertEqual(ax2.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(ax3.get_facecolor(), (1, 0, 0, 1))
        self.assertEqual(ax4.get_facecolor(), (1, 1, 1, 1))

        pos1 = ax1.get_position()
        pos2 = ax2.get_position()
        pos3 = ax3.get_position()
        pos4 = ax4.get_position()

        self.assertEqual(pos1.x0, pos2.x0)
        self.assertEqual(pos1.y0, pos2.y0)
        self.assertEqual(pos3.x0, pos4.x0)
        self.assertEqual(pos3.y0, pos4.y0)
        self.assertGreater(pos3.x0, pos1.x0)
        self.assertEqual(pos3.y0, pos1.y0)

        plot_data1 = get_plot_data(figure_number=1, axes_number=1)
        plot_data2 = get_plot_data(figure_number=2, axes_number=1)
        self.assertEqual(plot_data1, plot_data2)

    def test_subplotgrid_in_figure(self):
        text = '''
        mechanism: sr
        n_subjects = 1
        stimulus_elements: s1, s2
        behaviors: b1, b2
        alpha_v: 1
        u: s1:0, s2:10, default:0

        @phase phase1 stop:s1=10
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1

        xscale = s1

        @figure(1,2) Figure number one
        @subplot  Subplot number one
        @nplot s1->b1
        @subplot  Subplot number two {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2

        @figure Figure number two
        @subplot 121  Subplot number one
        @nplot s1->b1
        @subplot 122 Subplot number two {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2

        @figure(12) Figure number three
        subplottitle = Subplot number one
        @subplot
        @nplot s1->b1
        subplottitle = Subplot number two
        @panel {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2

        @figure Figure number four
        subplottitle = Subplot number one
        @subplot 121
        @nplot s1->b1
        subplottitle = Subplot number two
        @subplot 122 {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2
        '''
        run(text)

        fig1_ax1 = plt.figure(1).axes[0]
        fig1_ax2 = plt.figure(1).axes[1]

        fig2_ax1 = plt.figure(2).axes[0]
        fig2_ax2 = plt.figure(2).axes[1]

        fig3_ax1 = plt.figure(3).axes[0]
        fig3_ax2 = plt.figure(3).axes[1]

        fig4_ax1 = plt.figure(1).axes[0]
        fig4_ax2 = plt.figure(1).axes[1]

        self.assertEqual(plt.figure(1)._suptitle.get_text(), "Figure number one")
        self.assertEqual(plt.figure(2)._suptitle.get_text(), "Figure number two")
        self.assertEqual(plt.figure(3)._suptitle.get_text(), "Figure number three")
        self.assertEqual(plt.figure(4)._suptitle.get_text(), "Figure number four")

        self.assertEqual(fig1_ax1.get_title(), "Subplot number one")
        self.assertEqual(fig2_ax1.get_title(), "Subplot number one")
        self.assertEqual(fig3_ax1.get_title(), "Subplot number one")
        self.assertEqual(fig4_ax1.get_title(), "Subplot number one")

        self.assertEqual(fig1_ax2.get_title(), "Subplot number two")
        self.assertEqual(fig2_ax2.get_title(), "Subplot number two")
        self.assertEqual(fig3_ax2.get_title(), "Subplot number two")
        self.assertEqual(fig4_ax2.get_title(), "Subplot number two")

        self.assertEqual(fig1_ax1.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(fig2_ax1.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(fig3_ax1.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(fig4_ax1.get_facecolor(), (1, 1, 1, 1))

        self.assertEqual(fig1_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))
        self.assertEqual(fig2_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))
        self.assertEqual(fig3_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))
        self.assertEqual(fig4_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))

        self.assertEqual(fig1_ax1.get_position().x0, fig2_ax1.get_position().x0)
        self.assertEqual(fig1_ax1.get_position().x0, fig3_ax1.get_position().x0)
        self.assertEqual(fig1_ax1.get_position().x0, fig4_ax1.get_position().x0)

        self.assertEqual(fig1_ax1.get_position().y0, fig2_ax1.get_position().y0)
        self.assertEqual(fig1_ax1.get_position().y0, fig3_ax1.get_position().y0)
        self.assertEqual(fig1_ax1.get_position().y0, fig4_ax1.get_position().y0)

    def test_subplot_22(self):
        text = '''
        @figure(2,2)
        @subplot 1
        @subplot 2
        @panel   3
        @subplot 4

        @figure
        @subplot 221 1
        @subplot 222 2
        @subplot 223 3
        @panel   224 4
        '''
        run(text)

        ax1 = plt.figure(1).axes[0]
        ax2 = plt.figure(1).axes[1]
        ax3 = plt.figure(1).axes[2]
        ax4 = plt.figure(1).axes[3]
        self.assertEqual(ax1.get_title(), "1")
        self.assertEqual(ax2.get_title(), "2")
        self.assertEqual(ax3.get_title(), "3")
        self.assertEqual(ax4.get_title(), "4")

        ax1 = plt.figure(2).axes[0]
        ax2 = plt.figure(2).axes[1]
        ax3 = plt.figure(2).axes[2]
        ax4 = plt.figure(2).axes[3]
        self.assertEqual(ax1.get_title(), "1")
        self.assertEqual(ax2.get_title(), "2")
        self.assertEqual(ax3.get_title(), "3")
        self.assertEqual(ax4.get_title(), "4")


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    @staticmethod
    def get_text(subplot_args):
        return f'''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : response, no_response
        stimulus_elements : background, stimulus, reward
        start_v           : default:-1
        alpha_v           : 0.1
        u                 : reward:10, default:0

        @PHASE training stop: stimulus=10
        @new_trial  stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @new_trial
        NO_REWARD   background | @new_trial

        @run training

        @figure 1
        @subplot {subplot_args}
        @vplot stimulus->response
        '''

    def test_errors(self):
        text = self.get_text("112 subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument 112."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text(" (1 , 1   ,2   ) subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument (1, 1, 2)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("foo subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument foo."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,4,17) subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument (4, 4, 17)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,0,10)")
        msg = "Error on line 18: Invalid @subplot argument (4, 0, 10)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,1)")
        msg = "Error on line 18: Invalid @subplot argument (4, 1)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(a,   1)")
        msg = "Error on line 18: Invalid @subplot argument (a,."  # Since (a,1) is not a tuple since a is undefined
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,)")
        msg = "Error on line 18: Invalid @subplot argument (4,)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(-42,4)")
        msg = "Error on line 18: Invalid @subplot argument (-42, 4)."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_subplotgrid_in_figure(self):
        text = """
        @figure
        @subplot foo # Should give error since foo is not subplotspec
        """
        msg = "Error on line 3: Invalid @subplot argument foo."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figurefoo
        @subplot foo
        """
        msg = "Error on line 2: Invalid expression '@figurefoo'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(foo)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(121)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1,foo)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1,-1)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1,1,4)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1, 1.4)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @variables m = 1, n = 2
        @figure(m,n)
        @subplot foo
        """
        msg = "Error on line 3: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(2,2)
        @subplot
        @subplot
        @subplot
        @subplot
        @subplot  # One too many
        """
        msg = "num must be an integer with 1 <= num <= 4, not 5"
        with self.assertRaisesMsg(msg):
            run(text)
