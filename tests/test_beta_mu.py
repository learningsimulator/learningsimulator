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

    @staticmethod
    def get_script_for_start_v_test(start_v_str='1', beta_str='e1->b1:3, default:1', mu_str='0'):
        return f'''
        n_subjects: 100
        mechanism: ga
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta: {beta_str}
        mu: {mu_str}
        u: e2:1, default:0
        start_v: {start_v_str}
        alpha_v                : 1
        alpha_w                : 1

        @PHASE phase1 stop:e1=100
        L1 e1 | L2
        L2 e2 | L1

        @run phase1 runlabel:beta_diff

        xscale: e1

        @figure beta: e1->b1:3, default:1
        runlabel:beta_diff
        @vplot e1->b1
        @vplot e1->b2
        @vplot e2->b1
        @vplot e2->b2
        @legend
        '''

    def test_pos_start_v(self):
        start_v_text = self.get_script_for_start_v_test(start_v_str='1')
        run(start_v_text)
        plot_data = get_plot_data()
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e1->b2)']['y'][-1])
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b1)']['y'][-1])
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b2)']['y'][-1])

    def test_neg_start_v(self):
        start_v_text = self.get_script_for_start_v_test(start_v_str='-1')
        run(start_v_text)
        plot_data = get_plot_data()
        self.assertLess(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e1->b2)']['y'][-1])
        self.assertLess(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b1)']['y'][-1])
        self.assertLess(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b2)']['y'][-1])

    def test_scalar_beta_nonscalar_mu_pos_start_v(self):
        start_v_text = self.get_script_for_start_v_test(start_v_str='1', beta_str='1',
                                                        mu_str='e1->b1:3, default:1')
        run(start_v_text)
        plot_data = get_plot_data()
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e1->b2)']['y'][-1])
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b1)']['y'][-1])
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b2)']['y'][-1])

    def test_scalar_beta_nonscalar_mu_neg_start_v(self):
        start_v_text = self.get_script_for_start_v_test(start_v_str='-1', beta_str='1',
                                                        mu_str='e1->b1:3, default:1')
        run(start_v_text)
        plot_data = get_plot_data()
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e1->b2)']['y'][-1])
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b1)']['y'][-1])
        self.assertGreater(plot_data['v(e1->b1)']['y'][-1], plot_data['v(e2->b2)']['y'][-1])
