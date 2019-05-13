import matplotlib.pyplot as plt

from .testutil import LsTestCase
from .testutil import run, get_plot_data


class TestOriginalRescorlaWagner(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def foo_test_simple(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        @figure
        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - expected_increasing_y[i], 6)

    def test_xscale_stimulus(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        @figure
        xscale: cs

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - expected_increasing_y[i], 6)

    def test_xscale_phaselinelabel(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        @figure
        xscale: CS

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - expected_increasing_y[i], 6)

    def test_stop_phaselinelabel(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        @figure
        xscale: CS

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - expected_increasing_y[i], 6)

    def test_stuff(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        n_subjects: 10
        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.4

        @phase foo1 stop:cs=10
        CS cs     | US
        US us     | CS
        # NONE none | new_trial

        @phase foo2 stop:cs=5
        CS cs     | US
        US us     | CS
        # NONE none | new_trial

        @run foo1,foo2

        @figure
        xscale: cs
        subject: average
        phases: foo1

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs

        mechanism: rw
        stimulus_elements: cs, us

        n_subjects: 10
        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.4

        @phase foo1 stop:cs=10
        CS cs     | US
        US us     | CS
        # NONE none | new_trial

        @phase foo2 stop:cs=5
        CS cs     | US
        US us     | CS
        # NONE none | new_trial

        @run foo1,foo2

        @figure
        xscale: cs
        subject: average
        phases: foo1

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def foo_test_no_run(self):
        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase foo stop:s1=2
        L1 s1 | L1
        @vplot s1->b
        """
        msg = "There is no @RUN."
        with self.assertRaisesX(Exception, msg):
            run(text)
