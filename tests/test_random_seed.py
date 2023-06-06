import random
import time
import math
import random
import matplotlib.pyplot as plt
from .testutil import LsTestCase, get_plot_data, run


def get_script(seed=None):
        if seed is None:
            first_line = ''
            t = 1000 * time.time()  # If a test that uses random_seed was run before this test
            random.seed(int(t) % 2**32)
        else:
            first_line = "random_seed = " + str(seed)

        return f'''
        {first_line}
        n_subjects        = 1
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = 0
        alpha_v           = 0.1
        alpha_w           = 0.1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==1000
        START       stimulus   | response: REWARD(.5) | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        
        subject: all
        @figure
        @plot v(stimulus->response)
        '''

# Check whether plot_data1 and plot_data2 are different
def is_diff(plot_data1, plot_data2, n_subjects):
    found_a_diff = False
    for subject in range(1, n_subjects + 1):
        for i in range(len(plot_data1['y'])):
            y1 = plot_data1['y'][i]
            y2 = plot_data2['y'][i]
            if abs(y1 -y2) > 4:
                found_a_diff = True
                break
        if found_a_diff:
            break
    return found_a_diff


class TestSmall(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')
        
    def test_without_seed(self):
        text = get_script(seed=None)
        run(text)
        plot_data1 = get_plot_data()

        self.tearDown()    

        run(text)
        plot_data2 = get_plot_data()

        found_a_diff = is_diff(plot_data1, plot_data2, 1)
        self.assertTrue(found_a_diff)

    def test_run_twice_with_same_seed(self):
        seed = math.floor(random.random() * 100)
        text = get_script(seed=seed)
        run(text)
        plot_data1 = get_plot_data()
        
        self.tearDown()

        run(text)
        plot_data2 = get_plot_data()
 
        found_a_diff = is_diff(plot_data1, plot_data2, 1)
        self.assertFalse(found_a_diff, f"seed={seed}")

    def test_error_for_multiple_seeds(self):
        text = '''
        random_seed = 1
        n_subjects        = 10
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -3
        alpha_v           = 0.1
        alpha_w           = 0.1
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
        msg = "Error on line 17: Can only set random_seed once."
        with self.assertRaisesMsg(msg):
            run(text)
