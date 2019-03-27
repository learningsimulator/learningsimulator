from .testutil import LsTestCase
from parsing import Script


def run(text):
    script = Script(text)
    script.parse()
    script_output = script.run()
    script.postproc(script_output, False)
    return script


class TestDifferentTypes(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_chain(self):
        text = '''
n_subjects        : 1
mechanism         : SR
behaviors         : b, b0
stimulus_elements : s, reward
start_v           : s->b0:0, default:-1
alpha_v           : 0.1
alpha_w           : 0.1
beta              : 1
behavior_cost     : default:0
u                 : reward:2, default:0

@phase instrumental_conditioning stop:s=60
XSTIMULUS   s          | b: REWARD  | XSTIMULUS
REWARD      reward     | XSTIMULUS

@run instrumental_conditioning runlabel: alpha01

@figure foo bar   carr
xscale: s->b
runlabel: alpha01
@nplot s->b {'linewidth':2}
        '''
        script = run(text)
        self.assertEqual(len(script.script_parser.postcmds.cmds), 2)

    def foo_test_phase_line_label(self):
        text = '''
# Learning to respond to a stimulus

n_subjects        : 1
mechanism         : SR
behaviors         : b, b0
stimulus_elements : s, reward
start_v           : s->b0:0, default:-1
alpha_v           : 0.1
alpha_w           : 0.1
beta              : 1
behavior_cost     : default:0
u                 : reward:2, default:0

@phase instrumental_conditioning stop:s=60
XSTIMULUS   s          | b: REWARD  | XSTIMULUS
REWARD      reward     | XSTIMULUS

@run instrumental_conditioning runlabel: alpha01

@figure foo bar   carr
xscale: XSTIMULUS
runlabel: alpha01
@nplot s->b {'linewidth':2}
        '''
        script = run(text)
        self.assertEqual(len(script.script_parser.postcmds.cmds), 2)
