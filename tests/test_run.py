import matplotlib.pyplot as plt

from .testutil import LsTestCase, run


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
        alpha_v: 1
        alpha_w: 1
        
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        @vplot e1->b1
        '''
        script, _ = run(text)
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
        alpha_v: 1
        alpha_w: 1
        start_v: s1->b:7, default:1.5
        
        @phase foo stop:s1=2
        L1 s1 | L1
        @vplot s1->b
        """
        msg = "Error on line 11: There is no @RUN."
        with self.assertRaisesMsg(msg):
            run(text)
