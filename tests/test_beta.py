import matplotlib.pyplot as plt

from .testutil import LsTestCase
from parsing import Script


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
        beta: e1->b1:1, e1->b2:2, default:3
        u: e2:1, default:0

        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1

        @run phase1 runlabel:beta_diff

        beta: 1
        @run phase1 runlabel:beta1

        @figure
        runlabel:beta1
        @vplot e1->b1

        @figure
        runlabel:beta_diff
        @vplot e1->b1

        '''
        # script = run(text)
        # self.assertEqual(len(script.script_parser.postcmds.cmds), 1)
