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

        xscale: stimulus

        @figure average
        subject: average
        @vplot stimulus->response

        @figure all
        subject: all
        @vplot stimulus->response

        @figure 1
        subject: 1
        @vplot stimulus->response
        '''
        script_obj, script_output = run(text)

        plot_data = get_plot_data(figure_number=1)
        self.assertEqual(set(plot_data.keys()), {'x', 'y'})

        plot_data = get_plot_data(figure_number=2)
        self.assertEqual(set(plot_data.keys()), {'x', 'y'})

        plot_data = get_plot_data(figure_number=3)
        self.assertEqual(set(plot_data.keys()), {'x', 'y'})

    def test_multiple_subjects(self):
        text = '''
        n_subjects        : 10
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

        xscale: stimulus

        @figure average
        subject: average
        @vplot stimulus->response

        @figure all
        subject: all
        @vplot stimulus->response

        @figure 1
        subject: 1
        @vplot stimulus->response

        @figure 2
        subject: 2
        @vplot stimulus->response

        @figure 3
        subject: 3
        @vplot stimulus->response

        @figure 4
        subject: 4
        @vplot stimulus->response

        @figure 5
        subject: 5
        @vplot stimulus->response

        @figure 6
        subject: 6
        @vplot stimulus->response

        @figure 7
        subject: 7
        @vplot stimulus->response

        @figure 8
        subject: 8
        @vplot stimulus->response

        @figure 9
        subject: 9
        @vplot stimulus->response

        @figure 10
        subject: 10
        @vplot stimulus->response
        '''
        script_obj, script_output = run(text)

        plot_data = get_plot_data(figure_number=1)
        self.assertEqual(set(plot_data.keys()), {'x', 'y'})

        plot_data = get_plot_data(figure_number=2)
        self.assertEqual(set(plot_data.keys()), {'v(stimulus->response), subject 1',
                                                 'v(stimulus->response), subject 2',
                                                 'v(stimulus->response), subject 3',
                                                 'v(stimulus->response), subject 4',
                                                 'v(stimulus->response), subject 5',
                                                 'v(stimulus->response), subject 6',
                                                 'v(stimulus->response), subject 7',
                                                 'v(stimulus->response), subject 8',
                                                 'v(stimulus->response), subject 9',
                                                 'v(stimulus->response), subject 10'})

        for figure_number in [3, 4, 5, 6, 7, 8, 9, 10]:
            plot_data = get_plot_data(figure_number=figure_number)
            self.assertEqual(set(plot_data.keys()), {'x', 'y'})

        # Check that each single subject plots is the same as the corresponding subject in
        # the 'all' subject plot
        for figure_number in [3, 4, 5, 6, 7, 8, 9, 10]:
            single_subject_plot_data = get_plot_data(figure_number=figure_number)
            lbl = f"v(stimulus->response), subject {figure_number - 2}"
            all_subject_plot_data = get_plot_data(figure_number=2)[lbl]
            self.assertEqual(single_subject_plot_data, all_subject_plot_data)


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    @staticmethod
    def get_text(n_subjects, subject):
        return f'''
        n_subjects        : {n_subjects}
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

        xscale: stimulus

        subject: {subject}
        @vplot stimulus->response
        '''

    def test_single_subject(self):
        text = self.get_text('1', 'foo')
        msg = "Error on line 19: Parameter subject must be 'average', 'all', or a positive integer."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text('1', '0')
        msg = "Error on line 19: Parameter subject must be 'average', 'all', or a positive integer."
        with self.assertRaisesMsg(msg):
            run(text)

        self.tearDown()
        text = self.get_text('1', '2')
        msg = "The value (2) for the parameter 'subject' exceeds the number of subjects (1)."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_multiple_subjects(self):
        text = self.get_text('10', 'foo')
        msg = "Error on line 19: Parameter subject must be 'average', 'all', or a positive integer."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text('10', '0')
        msg = "Error on line 19: Parameter subject must be 'average', 'all', or a positive integer."
        with self.assertRaisesMsg(msg):
            run(text)

        self.tearDown()
        text = self.get_text('10', '11')
        msg = "The value (11) for the parameter 'subject' exceeds the number of subjects (10)."
        with self.assertRaisesMsg(msg):
            run(text)
