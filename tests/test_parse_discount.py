from .testutil import LsTestCase
from keywords import DISCOUNT
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[DISCOUNT]


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        discount: 0.6
        '''
        discount = parse(text)
        self.assertEqual(discount, 0.6)

    def test_redefinition(self):
        text = '''
        discount: 0.4
        stimulus_elements: e1, e2
        behaviors: b1, b2
        discount: 0.5
        beta: 0.7
        '''
        discount = parse(text)
        self.assertEqual(discount, 0.5)


class TestWithVariables(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        @variables var11:0.2, var12:-0.1, var21:0.12, var22:0.1
        discount:    var11
        '''
        discount = parse(text)
        self.assertEqual(discount, 0.2)

        text = '''
        @variables var11:0.2, var12:-1, var21:12, var22:0.1
        stimulus_elements: e1, e2
        behaviors: b1, b2
        discount:    var11+0.12
        '''
        discount = parse(text)
        self.assertEqual(discount, 0.32)

        text = '''
        @variables var11:0.2, var12:-0.1, var21:0.12, var22:0.1
        discount:    var11+var22*var21
        '''
        discount = parse(text)
        self.assertAlmostEqual(discount, 0.212, 6)

        text = '''
        @variables var05:0.05, var11:-5, var12:-1, var21:3, var22:2
        discount:    var05 * (var11 + var22*var21 + var22**var22)
        '''
        discount = parse(text)
        self.assertEqual(discount, 0.25)

        text = '''
        @variables x:1
        '''
        discount = parse(text)
        self.assertEqual(discount, 1)

        text = '''
        discount: rand(0, 1)
        '''
        discount = parse(text)
        self.assertLessEqual(discount, 1)
        self.assertGreaterEqual(discount, 0)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        discount:
        mechanism: foo
        '''
        msg = "Parameter 'discount' is not specified."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_empty_name_no_colon(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        discount
        mechanism: foo
        '''
        msg = "Parameter 'discount' is not specified."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        discount: foo,>>>>////
        '''
        msg = "Error in expression 'foo,>>>>////': invalid syntax."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        discount: 2*rand(4,Blaps)
        '''
        msg = "Unknown variable 'Blaps'."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_erroneous_rand(self):
        text = '''
        discount: rand(1.2, 3)
        '''
        msg = "First argument to 'rand' must be integer."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        discount: rand(1, 3.3)
        '''
        msg = "Second argument to 'rand' must be integer."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        discount: rand(3, 1)
        '''
        msg = "The first argument to 'rand' must be less than or equal to the second argument."
        with self.assertRaisesMsg(msg):
            parse(text)
