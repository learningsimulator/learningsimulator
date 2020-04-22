import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestBasic(LsTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_compare_external_intensity_with_u(self):
        script = '''
n_subjects        : 100
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

@PHASE training2 stop: stimulus=5
@new_trial  stimulus   | response: REWARD | NO_REWARD
REWARD      reward[2]  | @new_trial
NO_REWARD   background | @new_trial

@run training runlabel:reward=10,reward[1]

xscale: stimulus
subject: average
@figure

runlabel: reward=10,reward[1]
@vplot stimulus->response {'label':'reward=10,reward[1]'}

u : reward:5, default:0
@run training runlabel:reward=5,reward[2]

runlabel:reward=5,reward[2]
@vplot stimulus->response {'label':'reward=5,reward[2]'}

@legend

runlabel: reward=10,reward[1]
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
        script_obj, script_output = run(script)
        plot_data = get_plot_data(1)

        u10 = plot_data['reward=10,reward[1]']['y']
        u5 = plot_data['reward=5,reward[2]']['y']

        # Test that u10 is increasing
        self.assertIncreasing(u10)

        # Test that u5 is increasing
        self.assertIncreasing(u5)

        self.assertGreater(u10[-1], 1.5)
        self.assertLess(u10[-1], 2)

        self.assertGreater(u5[-1], 0)
        self.assertLess(u5[-1], 0.5)

        # Test the pplots
        plot_data = get_plot_data(2)

        yend_prev = plot_data['0.1']['y'][-1]
        for lbl in ['0.2', '0.3', '0.4', '0.5', '0.8', '1.0', '2.0']:
            y = plot_data[lbl]['y']
            self.assertIncreasing(y)

            yend = y[-1]
            self.assertGreater(yend, yend_prev)
            yend_prev = yend
