import matplotlib.pyplot as plt

from .testutil import LsTestCase
from parsing import Script


def run(text):
    script = Script(text)
    script.parse()
    script_output = script.run()
    script.postproc(script_output, False)
    return script


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_simple(self):
        text = '''
        mechanism: ga
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        @vplot e1->b1
        '''
        script = run(text)
        self.assertEqual(len(script.script_parser.postcmds.cmds), 1)


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
