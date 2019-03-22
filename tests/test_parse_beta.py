from .testutil import LsTestCase
from keywords import BETA
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[BETA]


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        beta: -1.34
        '''
        beta = parse(text)
        self.assertEqual(beta, -1.34)

    def test_redefinition(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta: 1
        beta: 0.5
        '''
        beta = parse(text)
        self.assertEqual(beta, 0.5)


class TestWithVariables(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        @variables var11:0.2, var12:-0.1, var21:12, var22:0.1
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta:    var11
        '''
        beta = parse(text)
        self.assertEqual(beta, 0.2)

        text = '''
        @variables var11:0.2, var12:-0.1, var21:12, var22:0.1
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta:    var11+1.2
        '''
        beta = parse(text)
        self.assertEqual(beta, 1.4)

        text = '''
        @variables var11:0.2, var12:-0.1, var21:12, var22:0.1
        beta:    var11+var22*var21
        '''
        beta = parse(text)
        self.assertAlmostEqual(beta, 1.4, places=6)

        text = '''
        @variables var11:0.2, var12:-0.1, var21:12, var22:2
        beta:    var11 + var22*var21 + var22**var22
        '''
        beta = parse(text)
        self.assertEqual(beta, 28.2)


class TestWithFunctions(LsTestCase):
    def setUp(self):
        pass

    def test_rand(self):
        text = '''
        beta: 100+rand(-5,5)*2
        '''
        beta = parse(text)
        self.assertLessEqual(beta, 110)
        self.assertGreaterEqual(beta, -90)
        self.assertTrue(type(beta) is int)

        text = '''
        @VARIABLES x:-5, y:5, z:2, hundred:100
        beta: hundred + rand(x,y)*z
        '''
        beta = parse(text)
        self.assertLessEqual(beta, 110)
        self.assertGreaterEqual(beta, 90)
        self.assertTrue(type(beta) is int)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta:
        mechanism: foo
        '''
        msg = "Parameter 'beta' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_empty_name_no_colon(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta
        mechanism: foo
        '''
        msg = "Parameter 'beta' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta: foo,>>>>////
        '''
        msg = "Error in expression 'foo,>>>>////': invalid syntax."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        beta: 2*rand(4,Blaps)
        '''
        msg = "Unknown variable 'Blaps'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_erroneous_rand(self):
        text = '''
        beta: rand(1.2, 3)
        '''
        msg = "First argument to 'rand' must be integer."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        beta: rand(1, 3.3)
        '''
        msg = "Second argument to 'rand' must be integer."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        beta: rand(3, 1)
        '''
        msg = "The first argument to 'rand' must be less than or equal to the second argument."
        with self.assertRaisesX(Exception, msg):
            parse(text)
