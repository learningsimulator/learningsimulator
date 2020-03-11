from .testutil import LsTestCase
from keywords import TRACE
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[TRACE]


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        trace: 0.6
        '''
        trace = parse(text)
        self.assertEqual(trace, 0.6)

    def test_redefinition(self):
        text = '''
        trace: 0.4
        stimulus_elements: e1, e2
        behaviors: b1, b2
        trace: 0.5
        beta: 0.7
        '''
        trace = parse(text)
        self.assertEqual(trace, 0.5)


class TestWithVariables(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        @variables var11:0.2, var12:-0.1, var21:0.12, var22:0.1
        trace:    var11
        '''
        trace = parse(text)
        self.assertEqual(trace, 0.2)

        text = '''
        @variables var11:0.2, var12:-1, var21:12, var22:0.1
        stimulus_elements: e1, e2
        behaviors: b1, b2
        trace:    var11+0.12
        '''
        trace = parse(text)
        self.assertEqual(trace, 0.32)

        text = '''
        @variables var11:0.2, var12:-0.1, var21:0.12, var22:0.1
        trace:    var11+var22*var21
        '''
        trace = parse(text)
        self.assertAlmostEqual(trace, 0.212, 6)

        text = '''
        @variables var05:0.05, var11:-5, var12:-1, var21:3, var22:2
        trace:    var05 * (var11 + var22*var21 + var22**var22)
        '''
        trace = parse(text)
        self.assertEqual(trace, 0.25)

        text = '''
        @variables x:1
        '''
        trace = parse(text)
        self.assertEqual(trace, 0)

        text = '''
        trace: rand(0, 1)
        '''
        trace = parse(text)
        self.assertLessEqual(trace, 1)
        self.assertGreaterEqual(trace, 0)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        trace:
        mechanism: foo
        '''
        msg = "Parameter 'trace' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_empty_name_no_colon(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        trace
        mechanism: foo
        '''
        msg = "Parameter 'trace' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        trace: foo,>>>>////
        '''
        msg = "Error in expression 'foo,>>>>////': invalid syntax."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        trace: 2*rand(4,Blaps)
        '''
        msg = "Unknown variable 'Blaps'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_erroneous_rand(self):
        text = '''
        trace: rand(1.2, 3)
        '''
        msg = "First argument to 'rand' must be integer."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        trace: rand(1, 3.3)
        '''
        msg = "Second argument to 'rand' must be integer."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        trace: rand(3, 1)
        '''
        msg = "The first argument to 'rand' must be less than or equal to the second argument."
        with self.assertRaisesX(Exception, msg):
            parse(text)
