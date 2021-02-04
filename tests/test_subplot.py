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
        @subplot 111 subplot title 1
        subject: average
        @vplot stimulus->response

        @figure 2
        @subplot (1,   1,1  ) subplot title 2
        @vplot stimulus->response

        @figure 3
        @subplot 224 subplot title 3
        @vplot stimulus->response

        @figure 4
        @subplot (  2,2,4  ) subplot title 4
        @vplot stimulus->response

        @figure 5
        @subplot (4,4,16)
        @vplot stimulus->response
        '''
        script_obj, script_output = run(text)

        ax1 = plt.figure(1).axes[0]
        ax2 = plt.figure(2).axes[0]
        ax3 = plt.figure(3).axes[0]
        ax4 = plt.figure(4).axes[0]

        self.assertEqual(ax1.get_title(), "subplot title 1")
        self.assertEqual(ax2.get_title(), "subplot title 2")
        self.assertEqual(ax3.get_title(), "subplot title 3")
        self.assertEqual(ax4.get_title(), "subplot title 4")

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
            script_obj, script_output = run(text)

        text = self.get_text(" (1 , 1   ,2   ) subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument (1, 1, 2)."
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)

        text = self.get_text("foo subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument foo."
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)

        text = self.get_text("(4,4,17) subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument (4, 4, 17)."
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)

        text = self.get_text("(4,0,10)")
        msg = "Error on line 18: Invalid @subplot argument (4, 0, 10)."
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)

        text = self.get_text("(4,1)")
        msg = "Error on line 18: Invalid @subplot argument (4, 1)."
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)

        text = self.get_text("(a,   1)")
        msg = "Error on line 18: Invalid @subplot argument (a,."  # Since (a,1) is not a tuple since a is undefined
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)

        text = self.get_text("(4,)")
        msg = "Error on line 18: Invalid @subplot argument (4,)."
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)

        text = self.get_text("(-42,4)")
        msg = "Error on line 18: Invalid @subplot argument (-42, 4)."
        with self.assertRaisesMsg(msg):
            script_obj, script_output = run(text)
