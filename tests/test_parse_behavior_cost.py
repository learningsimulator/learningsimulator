from .testutil import LsTestCase
from keywords import BEHAVIOR_COST
from parsing import Script

name = BEHAVIOR_COST


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[name]


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        behaviors: b1, b2
        {}: b2:2, default:1
        '''.format(name)
        c = parse(text)
        expected = {'b1': 1, 'b2': 2}
        self.assertEqual(c, expected)

        text = '''
        behaviors: b1, b2
        {}: default:1, b2:2
        '''.format(name)
        c = parse(text)
        expected = {'b1': 1, 'b2': 2}
        self.assertEqual(c, expected)

    def test_multiline(self):
        text = '''
        behaviors: b1, b2
        {}: b2:2,
                 default:1
        '''.format(name)
        c = parse(text)
        expected = {'b1': 1, 'b2': 2}
        self.assertEqual(c, expected)

        text = '''
        behaviors: b1, b2
        {}: default:1,
                 b2:2
        '''.format(name)
        c = parse(text)
        expected = {'b1': 1, 'b2': 2}
        self.assertEqual(c, expected)

    def test_scalar(self):
        text = '''
        behaviors: b1, b2, b3
        {}: 0.42
        '''.format(name)
        w = parse(text)
        expected = {'b1': 0.42, 'b2': 0.42, 'b3': 0.42}
        self.assertEqual(w, expected)

        text = '''
        behaviors:  b1, b2, b3
        {}:default:0.42
        '''.format(name)
        w = parse(text)
        expected = {'b1': 0.42, 'b2': 0.42, 'b3': 0.42}
        self.assertEqual(w, expected)

        text = '''
        behaviors: b1, b2, b3
        {}: 0
        '''.format(name)
        w = parse(text)
        expected = {'b1': 0, 'b2': 0, 'b3': 0}
        self.assertEqual(w, expected)

    def test_redefinition(self):
        text = '''
        behaviors: b1, b2
        {}: b1:1, default: 2
        {}: b2:2, default: 1
        '''.format(name, name)
        w = parse(text)
        expected = {'b1': 1, 'b2': 2}
        self.assertEqual(w, expected)

        text = '''
        behaviors: b1, b2, b3
        {}:default:   0.42
        {}: default:1,
                 b2:2
        '''.format(name, name)
        w = parse(text)
        expected = {'b1': 1, 'b2': 2, 'b3': 1}
        self.assertEqual(w, expected)

        text = '''
        behaviors: b1, b2, b3, b4
        {}: default:1,
                 b2:2
        {}: default:   0.42
        '''.format(name, name)
        w = parse(text)
        expected = {'b1': 0.42, 'b2': 0.42, 'b3': 0.42, 'b4': 0.42}
        self.assertEqual(w, expected)

    def _test_default_not_needed(self, name):
        text = '''
        behaviors: b1, b2, b3
        behaviors: b1, b2
        {}: b1:22,
                 b2:-24,    b3:18
        '''.format(name)
        w = parse(text)
        expected = {'b1': 22, 'b2': -24, 'b3': 18}
        self.assertEqual(w, expected)

    def test_comma(self):
        text = '''behaviors: b1, b2
        {}: default:111,
                 b2:2,
        '''.format(name)
        w = parse(text)
        expected = {'default': 111, 'b2': 2, 'b1': None}
        self.assertEqual(w, expected)


class TestWithVariables(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        @variables var1:0.1, var2:-0.2
        behaviors: b1, b2
        {}: b1:var1,
            b2:var2
        '''.format(name)
        w = parse(text)
        expected = {'b1': 0.1, 'b2': -0.2}
        self.assertEqual(w, expected)

        text = '''
        @variables var1:1, var2:-2
        behaviors: b1, b2
        {}: b1:10+var1,
            b2:10+var2
        '''.format(name)
        w = parse(text)
        expected = {'b1': 11, 'b2': 8}
        self.assertEqual(w, expected)

        text = '''
        @variables var1:1, var2:2
        behaviors: b1, b2, b3
        {}: b1:10+var1, b2:10+var2, default:3
        '''.format(name)
        w = parse(text)
        expected = {'b1': 11, 'b2': 12, 'b3': 3}
        self.assertEqual(w, expected)

        text = '''
        @variables var11:1, var12:2, defval:0
        behaviors: b1, b2, b3
        {}: b1:10+var11, b2:12, default:defval
        '''.format(name)
        w = parse(text)
        expected = {'b1': 11, 'b2': 12, 'b3': 0}
        self.assertEqual(w, expected)


class TestWithExpressions(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        behaviors: b1, b2, b3, b4
        {}: b1: 1+2*3, b2: 4-3  *   2, b3: 10-1/2, b4: 0+0+0-0
        '''.format(name)
        c = parse(text)
        expected = {'b1': 7, 'b2': -2, 'b3': 9.5, 'b4': 0}
        self.assertEqual(c, expected)

        text = '''
        behaviors: b1, b2, b3, b4
        {}: b1: 1+2*3,
                 b2: 4**2-3  *   2,
                 b3: 10-1/2,
                 b4: 0+0**1+0-0
        '''.format(name)
        c = parse(text)
        expected = {'b1': 7, 'b2': 10, 'b3': 9.5, 'b4': 0}
        self.assertEqual(c, expected)


class TestWithFunctions(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        behaviors: b1, b2, b3, b4
        {}: b1: rand(1,10), b2: 4-rand(1,2), default:11, b3: 10
        '''.format(name)
        w = parse(text)

        b1 = w['b1']
        self.assertLessEqual(b1, 10)
        self.assertGreaterEqual(b1, 1)
        self.assertTrue(type(b1) is int)

        b2 = w['b2']
        self.assertTrue(b2 in (2, 3))

        b3 = w['b3']
        self.assertEqual(b3, 10)

        b4 = w['b4']
        self.assertEqual(b4, 11)

        # XXX should not work, no comma
        text = '''
        behaviors: b1, b2, b3, b4
        {}: b1: 111,
            b2: 222,
            b3: 333,
            b4: 444
        {}: b1: rand(1,10),
            b2: 4-rand(1,2),
            b3: 10, default:11
        '''.format(name, name)
        w = parse(text)

        b1 = w['b1']
        self.assertLessEqual(b1, 10)
        self.assertGreaterEqual(b1, 1)
        self.assertTrue(type(b1) is int)

        b2 = w['b2']
        self.assertTrue(b2 in (2, 3))

        b3 = w['b3']
        self.assertEqual(b3, 10)

        b4 = w['b4']
        self.assertEqual(b4, 11)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        behaviors: b1, b2
        {}:
        '''.format(name)
        msg = "Parameter '{}' is not specified.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def _test_empty_name_no_colon(self, name):
        text = '''
        behaviors: b1, b2
        {}
        behaviors: b1, b2
        '''.format(name)
        msg = "Parameter '{}' is not specified.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_duplicate(self):
        text = '''
        behaviors: b1, b2, b3, b4
        {}: b1:0.123, b2:4.56, b3:99, b1:-22, b18:knas
        '''.format(name)
        msg = "Duplicate of b1 in '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: eb1, b2, b3, b4
        {}: eb1:0.123, b2:4.56, eb1:99, foo->bar:1, default:Blaps
        '''.format(name)
        msg = "Duplicate of eb1 in '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2, b3, b4
        {}: b1:0.123, b2:4.56, foo:1, b1:99, default:-22
        '''.format(name)
        msg = "'foo' is an invalid behavior name.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_behavior_not_defined(self):
        text = '''
        stimulus_elements: e1, e2
        {}: Blaps mortisaga
        '''.format(name)
        msg = "The parameter 'behaviors' must be assigned before the parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''  # XXX borde bli fel på saknad stimulus elöement?
        behaviors: b1, b2
        {}:
        '''.format(name)
        msg = "Parameter '{}' is not specified.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        {}: foo
        '''.format(name)
        msg = "The parameter 'behaviors' must be assigned before the parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        behaviors: b1, b2
        behaviors: b1, b2
        {}: foo,>>>>////
        '''.format(name)
        msg = "Expected 'element:value' or 'default:value' in '{}', got 'foo'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        behaviors: b1, b2
        {}: foo>>>>////
        '''.format(name)
        msg = "Expected 'element:value' or 'default:value' in '{}', got 'foo>>>>////'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''behaviors: b1, b2
                  {}: default::111
               '''.format(name)
        msg = "Expected 'element:value' or 'default:value' in '{}', got 'default::111'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''behaviors: b1, b2
                  {}: b1->b1:1, blabla
               '''.format(name)
        msg = "Error in parameter '{}': 'b1->b1' is an invalid behavior name.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_e_value(self):
        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: foo->bar:foobar, blabla
               '''.format(name)
        msg = ""  # XXX
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: fo o ->bar:foobar, blabla
               '''.format(name)
        msg = "Invalid value 'foobar' for 'fo o ->bar' in parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: blaps:foobar, blabla
               '''.format(name)
        msg = "Invalid value 'foobar' for 'blaps' in parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_multiple_single_values(self):
        text = '''
        behaviors: b1, b2
        {}: 1, 2
        '''.format(name)
        msg = "Expected 'element:value' or 'default:value' in '{}', got '1'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: 18,
                 42
        '''.format(name)
        msg = "A single value for '{}' cannot be followed by other values.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: 18,
                 oipoipoi,
                 dfldfjlkdj
        '''.format(name)
        msg = "A single value for '{}' cannot be followed by other values.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: b1:3.22, 42
        '''.format(name)
        msg = "Expected 'element:value' or 'default:value' in '{}', got '42'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: b1:3.22, 42, 8.3
        '''.format(name)
        msg = "Expected 'element:value' or 'default:value' in '{}', got '42'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: b2:3.22,
                 42
        '''.format(name)
        msg = "A single value for '{}' cannot follow other values.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_multiple_default(self):
        text = '''
        behaviors: b1, b2
        {}: b1:3.22, default:12, b2:18, default:42
        '''.format(name)
        msg = "Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: will_be_overwritten1, will_be_overwritten2, will_be_overwritten3
        behaviors: b1, b2
        {}: b1:3.22, default:12,
                 b2:18, default:42
        '''.format(name)
        msg = "Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: b1:3.22, default:12, b2:18,
                 default:42
        '''.format(name)
        msg = "Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_behavior_name(self):
        text = '''
        behaviors: b1, b2
        {}: b1:3.22, default:12, b2->b2:18
        '''.format(name)
        msg = "'b2->b2' is an invalid behavior name."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: B1:3.22, default:12
        '''.format(name)
        msg = "'B1' is an invalid behavior name."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_eb(self):
        text = '''
        behaviors: b1, b2
        {}: default:12, b1:22, kajsa:13, Klklklk***
        '''.format(name)
        msg = "Error in parameter '{}': 'kajsa' is an invalid behavior name.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: default:12, b1:22, kajsa:freja
        '''.format(name)
        msg = "Invalid value 'freja' for 'kajsa' in parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2
        {}: default:12, b1:22,
                 kajsa:freja
        '''.format(name)
        msg = "Invalid value 'freja' for 'kajsa' in parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_missing_default(self):
        text = '''
        behaviors: b1, b2
        {}: b1:22
        '''.format(name)
        msg = "Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2, b3
        {}: b1:22, b2:1.32
        '''.format(name)
        msg = "Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2, b3
        {}: b1: 111
            b2: 222
            b3: 333
            b4: 444
        '''.format(name)
        msg = "Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        behaviors: b1, b2, b3, b4
        behaviors: b1, b2
        {}: b1: 1+2*3,
                 b2: 4**2-3  *   2,
                 b3: 10-1/2,
                 b4: 0+0**1+0-0
        '''.format(name)
        msg = "Error in parameter 'behavior_cost': 'b3' is an invalid behavior name."
        with self.assertRaisesX(Exception, msg):
            parse(text)
