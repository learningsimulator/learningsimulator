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
        print(script.script_parser.postcmds.cmds)
