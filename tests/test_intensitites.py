import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestBasic(LsTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_overshadowing1(self):
        script = '''
n_subjects             : 100
mechanism              : SR

behaviors              : response,other
stimulus_elements      : a,b,empty,reward
start_v                : a->response:-2, b->response:-2, default:1
alpha_v                : 0.1
beta                   : 1
u                      : reward:1, default: 0

@variables n:200

@phase Overshadowing  stop:STIMULUS=n
STIMULUS    a[0.5],b[0.5]    |response: REWARD  | STIMULUS
REWARD      reward           | STIMULUS

@phase Overshadowing_ll(Overshadowing)  stop:STIMULUS=n
STIMULUS    a[0.9],b[0.1]      |response: REWARD  | STIMULUS

@phase Overshadowing_l(Overshadowing)  stop:STIMULUS=n
STIMULUS    a[0.7],b[0.3]      |response: REWARD  | STIMULUS

@phase Overshadowing_s(Overshadowing)  stop:STIMULUS=n
STIMULUS    a[0.3],b[0.7]      |response: REWARD  | STIMULUS

@phase Overshadowing_ss(Overshadowing)  stop:STIMULUS=n
STIMULUS    a[0.1],b[0.9]      |response: REWARD  | STIMULUS

@run Overshadowing_ll  runlabel: Overshadowing_ll
@run Overshadowing_l   runlabel: Overshadowing_l
@run Overshadowing     runlabel: Overshadowing
@run Overshadowing_s   runlabel: Overshadowing_s
@run Overshadowing_ss  runlabel: Overshadowing_ss

xscale: STIMULUS
subject: average
@figure v(a->response)

@subplot 111 {'xlabel':'Trial','ylabel':'v'}

runlabel: Overshadowing_ll
@vplot a->response  {'linewidth':2,'label':'A=0.9'}

runlabel: Overshadowing_l
@vplot a->response  {'linewidth':2,'label':'A=0.7'}

runlabel: Overshadowing
@vplot a->response  {'linewidth':2,'label':'A=0.5'}

runlabel: Overshadowing_s
@vplot a->response  {'linewidth':2,'label':'A=0.3'}

runlabel: Overshadowing_ss
@vplot a->response  {'linewidth':2,'label':'A=0.1'}
@legend
'''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        for lbl in ['A=0.1', 'A=0.3', 'A=0.5', 'A=0.7', 'A=0.9']:
            y = plot_data[lbl]['y']
            self.assertEqual(y[0], -2)

        self.assertLess(plot_data['A=0.1']['y'][50], plot_data['A=0.3']['y'][50])
        self.assertLess(plot_data['A=0.3']['y'][50], plot_data['A=0.5']['y'][50])
        self.assertLess(plot_data['A=0.5']['y'][50], plot_data['A=0.7']['y'][50])
        self.assertLess(plot_data['A=0.7']['y'][50], plot_data['A=0.9']['y'][50])

        self.assertLess(plot_data['A=0.1']['y'][-1], plot_data['A=0.3']['y'][-1])
        self.assertLess(plot_data['A=0.3']['y'][-1], plot_data['A=0.5']['y'][-1])
        self.assertLess(plot_data['A=0.5']['y'][-1], plot_data['A=0.9']['y'][-1])
        # Some strange effect
        self.assertLess(plot_data['A=0.9']['y'][-1], plot_data['A=0.7']['y'][-1])

    def test_overshadowing2(self):
        script = '''
n_subjects             : 100
mechanism              : SR

behaviors              : response,other
stimulus_elements      : a,b,empty,reward
start_v                : a->response:-2, b->response:-2, default:1
alpha_v                : 0.1
beta                   : 1
u                      : reward:1, default: 0

@variables n:155

@phase A_05  stop:STIMULUS=n
STIMULUS    a[0.5],b[0.5]    |response: REWARD  | STIMULUS
REWARD      reward           | STIMULUS

@phase A_01(A_05)  stop:STIMULUS=n
STIMULUS    a[0.1],b[0.5]      |response: REWARD  | STIMULUS

@phase A_03(A_05)  stop:STIMULUS=n
STIMULUS    a[0.3],b[0.5]      |response: REWARD  | STIMULUS

@phase A_1(A_05)  stop:STIMULUS=n
STIMULUS    a[1.0],b[0.5]      |response: REWARD  | STIMULUS


@run A_01  runlabel: A_01
@run A_03  runlabel: A_03
@run A_05  runlabel: A_05
@run A_1  runlabel: A_1

xscale: STIMULUS
subject: average
@figure v(a->response)

@subplot 111 {'xlabel':'Trial','ylabel':'v'}

runlabel: A_1
@vplot a->response  {'linewidth':2,'label':'A=1.0'}

runlabel: A_05
@vplot a->response  {'linewidth':2,'label':'A=0.5'}

runlabel: A_03
@vplot a->response  {'linewidth':2,'label':'A=0.3'}

runlabel: A_01
@vplot a->response  {'linewidth':2,'label':'A=0.1'}

@legend
'''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        ind = 150

        for lbl in ['A=0.1', 'A=0.3', 'A=0.5', 'A=1.0']:
            y = plot_data[lbl]['y']
            self.assertEqual(y[0], -2)
            self.assertIncreasing(y[20: ind])  # Flucuations in the beginning

        self.assertLess(plot_data['A=0.1']['y'][ind], -1)
        self.assertGreater(plot_data['A=0.1']['y'][ind], -1.5)

        self.assertLess(plot_data['A=0.3']['y'][ind], 0)
        self.assertGreater(plot_data['A=0.3']['y'][ind], -0.5)

        self.assertLess(plot_data['A=0.5']['y'][ind], 1)
        self.assertGreater(plot_data['A=0.5']['y'][ind], 0.5)

        self.assertLess(plot_data['A=1.0']['y'][ind], 1.2)
        self.assertGreater(plot_data['A=1.0']['y'][ind], 1.05)

        # Check that the order is consistent throughout step 50 onwards
        for i in range(50, ind):
            self.assertLess(plot_data['A=0.1']['y'][i], plot_data['A=0.3']['y'][i])
            self.assertLess(plot_data['A=0.3']['y'][i], plot_data['A=0.5']['y'][i])
            self.assertLess(plot_data['A=0.5']['y'][i], plot_data['A=1.0']['y'][i])

    def test_overshadowing2_with_intensity_variables(self):
        script = '''
n_subjects             : 100
mechanism              : SR

behaviors              : response,other
stimulus_elements      : a,b,empty,reward
start_v                : a->response:-2, b->response:-2, default:1
alpha_v                : 0.1
beta                   : 1
u                      : reward:1, default: 0

@variables n:155, a5:0.5, a1:0.1, a3:0.3, a10:1.0, b5:0.5

@phase A_05  stop:STIMULUS=n
STIMULUS    a[a5],b[b5]    |response: REWARD  | STIMULUS
REWARD      reward           | STIMULUS

@phase A_01(A_05)  stop:STIMULUS=n
STIMULUS    a[a1],b[b5]      |response: REWARD  | STIMULUS

@phase A_03(A_05)  stop:STIMULUS=n
STIMULUS    a[a3],b[b5]      |response: REWARD  | STIMULUS

@phase A_1(A_05)  stop:STIMULUS=n
STIMULUS    a[a10],b[b5]      |response: REWARD  | STIMULUS


@run A_01  runlabel: A_01
@run A_03  runlabel: A_03
@run A_05  runlabel: A_05
@run A_1  runlabel: A_1

xscale: STIMULUS
subject: average
@figure v(a->response)

@subplot 111 {'xlabel':'Trial','ylabel':'v'}

runlabel: A_1
@vplot a->response  {'linewidth':2,'label':'A=1.0'}

runlabel: A_05
@vplot a->response  {'linewidth':2,'label':'A=0.5'}

runlabel: A_03
@vplot a->response  {'linewidth':2,'label':'A=0.3'}

runlabel: A_01
@vplot a->response  {'linewidth':2,'label':'A=0.1'}

@legend
'''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        ind = 150

        for lbl in ['A=0.1', 'A=0.3', 'A=0.5', 'A=1.0']:
            y = plot_data[lbl]['y']
            self.assertEqual(y[0], -2)
            self.assertIncreasing(y[20: ind])  # Flucuations in the beginning

        self.assertLess(plot_data['A=0.1']['y'][ind], -1)
        self.assertGreater(plot_data['A=0.1']['y'][ind], -1.5)

        self.assertLess(plot_data['A=0.3']['y'][ind], 0)
        self.assertGreater(plot_data['A=0.3']['y'][ind], -0.5)

        self.assertLess(plot_data['A=0.5']['y'][ind], 1)
        self.assertGreater(plot_data['A=0.5']['y'][ind], 0.5)

        self.assertLess(plot_data['A=1.0']['y'][ind], 1.2)
        self.assertGreater(plot_data['A=1.0']['y'][ind], 1.05)

        # Check that the order is consistent throughout step 50 onwards
        for i in range(50, ind):
            self.assertLess(plot_data['A=0.1']['y'][i], plot_data['A=0.3']['y'][i])
            self.assertLess(plot_data['A=0.3']['y'][i], plot_data['A=0.5']['y'][i])
            self.assertLess(plot_data['A=0.5']['y'][i], plot_data['A=1.0']['y'][i])

    def test_overshadowing2_with_intensity_phase_variables(self):
        script = '''
n_subjects             : 100
mechanism              : SR

behaviors              : response,other
stimulus_elements      : a,b,empty,reward
start_v                : a->response:-2, b->response:-2, default:1
alpha_v                : 0.1
beta                   : 1
u                      : reward:1, default: 0

@variables n:155, a1:0.1, a3:0.3, a10:1.0

@phase A_05  stop:STIMULUS=n
H1          a5:0.5          | H2
H2          b5:0.5         | STIMULUS
STIMULUS    a[a5],b[b5]    |response: REWARD  | STIMULUS
REWARD      reward           | STIMULUS

@phase A_01(A_05)  stop:STIMULUS=n
STIMULUS    a[a1],b[b5]      |response: REWARD  | STIMULUS

@phase A_03(A_05)  stop:STIMULUS=n
STIMULUS    a[a3],b[b5]      |response: REWARD  | STIMULUS

@phase A_1(A_05)  stop:STIMULUS=n
STIMULUS    a[a10],b[b5]      |response: REWARD  | STIMULUS


@run A_01  runlabel: A_01
@run A_03  runlabel: A_03
@run A_05  runlabel: A_05
@run A_1  runlabel: A_1

xscale: STIMULUS
subject: average
@figure v(a->response)

@subplot 111 {'xlabel':'Trial','ylabel':'v'}

runlabel: A_1
@vplot a->response  {'linewidth':2,'label':'A=1.0'}

runlabel: A_05
@vplot a->response  {'linewidth':2,'label':'A=0.5'}

runlabel: A_03
@vplot a->response  {'linewidth':2,'label':'A=0.3'}

runlabel: A_01
@vplot a->response  {'linewidth':2,'label':'A=0.1'}

@legend
'''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        ind = 150

        for lbl in ['A=0.1', 'A=0.3', 'A=0.5', 'A=1.0']:
            y = plot_data[lbl]['y']
            self.assertEqual(y[0], -2)
            self.assertIncreasing(y[20: ind])  # Flucuations in the beginning

        self.assertLess(plot_data['A=0.1']['y'][ind], -1)
        self.assertGreater(plot_data['A=0.1']['y'][ind], -1.5)

        self.assertLess(plot_data['A=0.3']['y'][ind], 0)
        self.assertGreater(plot_data['A=0.3']['y'][ind], -0.5)

        self.assertLess(plot_data['A=0.5']['y'][ind], 1)
        self.assertGreater(plot_data['A=0.5']['y'][ind], 0.5)

        self.assertLess(plot_data['A=1.0']['y'][ind], 1.2)
        self.assertGreater(plot_data['A=1.0']['y'][ind], 1)

        # Check that the order is consistent throughout step 50 onwards
        for i in range(50, ind):
            self.assertLess(plot_data['A=0.1']['y'][i], plot_data['A=0.3']['y'][i])
            self.assertLess(plot_data['A=0.3']['y'][i], plot_data['A=0.5']['y'][i])
            self.assertLess(plot_data['A=0.5']['y'][i], plot_data['A=1.0']['y'][i])

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

        self.assertGreater(u10[-1], 1.35)
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
