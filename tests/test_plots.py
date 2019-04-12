import matplotlib.pyplot as plt

from .testutil import LsTestCase, get_plot_data
from parsing import Script


def run(text):
    script_obj = Script(text)
    script_obj.parse()
    script_output = script_obj.run()
    script_obj.postproc(script_output, False)
    return script_obj, script_output


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_initial_v(self):
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase foo stop:s1=2
        L1 s1 | L1
        @run foo
        @vplot s1->b
        @vplot s2->b
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 2)
        plot_data = get_plot_data()
        s1b = plot_data['v(s1->b)']
        s2b = plot_data['v(s2->b)']
        self.assertEqual(s1b['x'], [0, 1, 2])
        self.assertEqual(s2b['x'], [0, 1, 2])
        self.assertEqual(s1b['y'][0], 7)
        self.assertEqual(s2b['y'][0], 1.5)

    def test_initial_w(self):
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_w: s1:1, s2:2
        @phase foo stop:s1=2
        L1 s1 | L1
        @run foo
        @wplot s1
        @wplot s2
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 2)
        plot_data = get_plot_data()
        s1 = plot_data['w(s1)']
        s2 = plot_data['w(s2)']
        self.assertEqual(s1['x'], [0, 1, 2])
        self.assertEqual(s2['x'], [0, 1, 2])
        self.assertEqual(s1['y'][0], 1)
        self.assertEqual(s2['y'][0], 2)


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_no_run(self):
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
