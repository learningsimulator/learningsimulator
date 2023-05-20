import matplotlib.pyplot as plt

from .testutil import LsTestCase, get_plot_data, run


def get_script(seed=None):
        if seed is None:
            first_line = ''
        else:
            first_line = "random_seed = " + str(seed)

        return f'''
        {first_line}
        n_subjects        = 10
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -3
        alpha_v           = 0.1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==10
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        
        subject: all
        @figure
        @plot v(stimulus->response)
        '''


class TestSmall(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_with_seed(self):
        text = get_script(seed=1)
        run(text)
        plot_data = get_plot_data()
        
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 1']['x'], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 1']['y'], [-3.0, -1.7, -0.53, -0.53, 0.523, 1.4707, 2.32363, 3.091267, 3.7821403, 4.40392627])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 2']['y'], [-3.0, -1.7, -0.53, -0.53, 0.523, 1.4707, 2.32363, 3.091267, 3.7821403, 4.40392627])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 3']['y'], [-3.0, -3.0, -3.0, -3.0, -1.7, -0.53, 0.523, 1.4707, 2.32363, 3.091267])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 4']['y'], [-3.0, -1.7, -0.53, 0.523, 1.4707, 2.32363, 3.091267, 3.7821403, 4.40392627, 4.963533643])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 5']['y'], [-3.0, -3.0, -3.0, -3.0, -3.0, -1.7, -0.53, 0.523, 1.4707, 2.32363])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 6']['y'], [-3.0, -3.0, -3.0, -3.0, -1.7, -0.53, 0.523, 1.4707, 2.32363, 2.32363])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 7']['y'], [-3.0, -3.0, -1.7, -1.7, -0.53, 0.523, 1.4707, 2.32363, 3.091267, 3.7821403])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 8']['y'], [-3.0, -1.7, -0.53, 0.523, 1.4707, 2.32363, 3.091267, 3.7821403, 4.40392627, 4.963533643])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 9']['y'], [-3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -1.7, -1.7])
        self.assertAlmostEqualList(plot_data['v(stimulus->response) subject 10']['y'], [-3.0, -1.7, -0.53, 0.523, 1.4707, 2.32363, 3.091267, 3.7821403, 4.40392627, 4.963533643])
        
    def test_without_seed(self):
        text = get_script(seed=None)
        run(text)
        plot_data1 = get_plot_data()
        
        self.tearDown()    

        run(text)
        plot_data2 = get_plot_data()

        # Check that plot_data1 and plot_data2 are different
        found_a_diff = False
        for subject in range(1, 11):
            key = f'v(stimulus->response) subject {subject}'
            for i in range(len(plot_data1[key]['y'])):
                y1 = plot_data1[key]['y'][i]
                y2 = plot_data2[key]['y'][i]
                if abs(y1 -y2) > 4:
                    found_a_diff = True
                    break
            if found_a_diff:
                break
        self.assertTrue(found_a_diff)

    def test_error_for_multiple_seeds(self):
        text = '''
        random_seed = 1
        n_subjects        = 10
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -3
        alpha_v           = 0.1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==10
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        random_seed = 2
        @run training

        xscale: stimulus
        
        subject: all
        @figure
        @plot v(stimulus->response)
        '''
        msg = "Error on line 16: Can only set random_seed once."
        with self.assertRaisesMsg(msg):
            run(text)
