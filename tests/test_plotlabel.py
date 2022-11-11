import matplotlib.pyplot as plt
from parsing import PlotCmd

from .testutil import LsTestCase, run


def get_legends_from_script_obj(script_obj):
    # XXX This gets the legends from the PlotCmd object. It would be better to get from
    # the <matplotlib.legend.Legend> object legend_obj obtained by
    #
    # axes = plt.figure(1).axes
    # legend_obj = axes[0].legend()  # or axes[0].legend_
    #
    # but I don't see how to exctract the legend labels from legend_obj.
    postcmds = script_obj.script_parser.postcmds.cmds
    plotcmds = []
    for postcmd in postcmds:
        if isinstance(postcmd, PlotCmd):
            plotcmds.append(postcmd)
    assert(len(plotcmds) == 1)
    plotcmd = plotcmds[0]
    plot_labels = []
    for plot_args in plotcmd.plot_data.plot_args_list:
        plot_labels.append(plot_args['label'])
    return plot_labels


class TestInitialValues(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_default_label_pplot(self):
        text = '''
        n_subjects        : 5
        mechanism         : SR
        behaviors         : respond,ignore
        stimulus_elements : s, reward
        start_v           : s->ignore:0, default:-1
        alpha_v           : 0.1
        beta              : 1
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=100
        STIMULUS    s          | respond: REWARD  | STIMULUS
        REWARD      reward     | STIMULUS

        @run instrumental_conditioning

        xscale: s
        subject: all

        @figure
        @pplot s->respond
        @legend
        '''
        script_obj, _ = run(text)
        labels = get_legends_from_script_obj(script_obj)
        expected_labels = ['p(s->respond), subject 1',
                           'p(s->respond), subject 2',
                           'p(s->respond), subject 3',
                           'p(s->respond), subject 4',
                           'p(s->respond), subject 5']
        self.assertEqual(labels, expected_labels)

    def test_default_label_vplot(self):
        text = '''
        n_subjects        : 5
        mechanism         : SR
        behaviors         : respond,ignore
        stimulus_elements : s, reward
        start_v           : s->ignore:0, default:-1
        alpha_v           : 0.1
        beta              : 1
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=100
        STIMULUS    s          | respond: REWARD  | STIMULUS
        REWARD      reward     | STIMULUS

        @run instrumental_conditioning

        xscale: s
        subject: all

        @figure
        @vplot s->respond
        @legend
        '''
        script_obj, _ = run(text)
        labels = get_legends_from_script_obj(script_obj)
        expected_labels = ['v(s->respond), subject 1',
                           'v(s->respond), subject 2',
                           'v(s->respond), subject 3',
                           'v(s->respond), subject 4',
                           'v(s->respond), subject 5']
        self.assertEqual(labels, expected_labels)

    def test_default_label_wplot(self):
        text = '''
        n_subjects        : 5
        mechanism         : GA
        behaviors         : respond,ignore
        stimulus_elements : s, reward
        start_v           : s->ignore:0, default:-1
        alpha_v           : 0.1
        beta              : 1
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=100
        STIMULUS    s          | respond: REWARD  | STIMULUS
        REWARD      reward     | STIMULUS

        @run instrumental_conditioning

        xscale: s
        subject: all

        @figure
        @wplot s
        @legend
        '''
        script_obj, _ = run(text)
        labels = get_legends_from_script_obj(script_obj)
        expected_labels = ['w(s), subject 1',
                           'w(s), subject 2',
                           'w(s), subject 3',
                           'w(s), subject 4',
                           'w(s), subject 5']
        self.assertEqual(labels, expected_labels)

    def test_default_label_nplot(self):
        text = '''
        n_subjects        : 5
        mechanism         : SR
        behaviors         : respond,ignore
        stimulus_elements : s, reward
        start_v           : s->ignore:0, default:-1
        alpha_v           : 0.1
        beta              : 1
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=100
        STIMULUS    s          | respond: REWARD  | STIMULUS
        REWARD      reward     | STIMULUS

        @run instrumental_conditioning

        xscale: s
        subject: all

        @figure
        @nplot reward
        @legend
        '''
        script_obj, _ = run(text)
        labels = get_legends_from_script_obj(script_obj)
        expected_labels = ['n(reward), subject 1',
                           'n(reward), subject 2',
                           'n(reward), subject 3',
                           'n(reward), subject 4',
                           'n(reward), subject 5']
        self.assertEqual(labels, expected_labels)

    def test_custom_label(self):
        text = '''
        n_subjects        : 5
        mechanism         : SR
        behaviors         : respond,ignore
        stimulus_elements : s, reward
        start_v           : s->ignore:0, default:-1
        alpha_v           : 0.1
        beta              : 1
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=10
        STIMULUS    s          | respond: REWARD  | STIMULUS
        REWARD      reward     | STIMULUS

        @run instrumental_conditioning

        xscale: s
        subject: all

        @figure
        @pplot s->respond {'label':'my custom'}
        @legend
        '''
        script_obj, _ = run(text)
        labels = get_legends_from_script_obj(script_obj)
        expected_labels = ['my custom, subject 1',
                           'my custom, subject 2',
                           'my custom, subject 3',
                           'my custom, subject 4',
                           'my custom, subject 5']
        self.assertEqual(labels, expected_labels)

    def test_custom_empty(self):
        text = '''
        n_subjects        : 5
        mechanism         : SR
        behaviors         : respond,ignore
        stimulus_elements : s, reward
        start_v           : s->ignore:0, default:-1
        alpha_v           : 0.1
        beta              : 1
        u                 : reward:2, default:0

        @phase instrumental_conditioning stop:s=100
        STIMULUS    s          | respond: REWARD  | STIMULUS
        REWARD      reward     | STIMULUS

        @run instrumental_conditioning

        xscale: s
        subject: all

        @figure
        @pplot s->respond {'label':''}
        @legend
        '''
        script_obj, _ = run(text)
        labels = get_legends_from_script_obj(script_obj)
        expected_labels = ['subject 1',
                           'subject 2',
                           'subject 3',
                           'subject 4',
                           'subject 5']
        self.assertEqual(labels, expected_labels)
