from .testutil import LsTestCase
from keywords import U, ALPHA_W, START_W, LAMBDA
from parsing import Script

prop_names = (U, ALPHA_W, START_W, LAMBDA)


def parse(text, name):
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
        for name in prop_names:
            self._test_simple(name)

    def _test_simple(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e2:2, default:1
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 1, 'e2': 2}
        self.assertEqual(w, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: default:1, e2:2
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 1, 'e2': 2}
        self.assertEqual(w, expected)

    def test_multiline(self):
        for name in prop_names:
            self._test_multiline(name)

    def _test_multiline(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e2:2,
                 default:1
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 1, 'e2': 2}
        self.assertEqual(w, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: default:1,
                 e2:2
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 1, 'e2': 2}
        self.assertEqual(w, expected)

    def test_scalar(self):
        for name in prop_names:
            self._test_scalar(name)

    def _test_scalar(self, name):
        text = '''
        stimulus_elements: e1, e2, e3
        {}: 0.42
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 0.42, 'e2': 0.42, 'e3': 0.42}
        self.assertEqual(w, expected)

        text = '''
        stimulus_elements: e1, e2, e3
        {}: 0
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 0, 'e2': 0, 'e3': 0}
        self.assertEqual(w, expected)

        text = '''
        stimulus_elements: e1, e2, e3
        {}:default:0.42
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 0.42, 'e2': 0.42, 'e3': 0.42}
        self.assertEqual(w, expected)

    def test_redefinition(self):
        for name in prop_names:
            self._test_redefinition(name)

    def _test_redefinition(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1:1, default: 2
        {}: e2:2, default: 1
        '''.format(name, name)
        w = parse(text, name)
        expected = {'e1': 1, 'e2': 2}
        self.assertEqual(w, expected)

        text = '''
        stimulus_elements: e1, e2, e3
        {}:default:   0.42
        {}: default:1,
                 e2:2
        '''.format(name, name)
        w = parse(text, name)
        expected = {'e1': 1, 'e2': 2, 'e3': 1}
        self.assertEqual(w, expected)

        text = '''
        stimulus_elements: e1, e2, e3, e4
        {}: default:1,
                 e2:2
        {}: default:   0.42
        '''.format(name, name)
        w = parse(text, name)
        expected = {'e1': 0.42, 'e2': 0.42, 'e3': 0.42, 'e4': 0.42}
        self.assertEqual(w, expected)

    def test_default_not_needed(self):
        for name in prop_names:
            self._test_default_not_needed(name)

    def _test_default_not_needed(self, name):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        {}: e1:22,
                 e2:-24,    e3:18
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 22, 'e2': -24, 'e3': 18}
        self.assertEqual(w, expected)

    def test_unfinished(self):
        for name in prop_names:
            self._test_unfinished(name)

    def _test_unfinished(self, name):
        text = '''stimulus_elements: e1, e2
        {}: default:111,
                 e2:2,
        '''.format(name)
        w = parse(text, name)
        expected = {'default': 111, 'e2': 2, 'e1': None}
        self.assertEqual(w, expected)


class TestWithVariables(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        for name in prop_names:
            self._test_simple(name)

    def _test_simple(self, name):
        text = '''
        @variables var1:0.1, var2:-0.2
        stimulus_elements: e1, e2
        {}: e1:var1,
            e2:var2
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 0.1, 'e2': -0.2}
        self.assertEqual(w, expected)

        text = '''
        @variables var1:1, var2:-2
        stimulus_elements: e1, e2
        {}: e1:10+var1,
            e2:10+var2
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 11, 'e2': 8}
        self.assertEqual(w, expected)

        text = '''
        @variables var1:1, var2:2
        stimulus_elements: e1, e2, e3
        {}: e1:10+var1, e2:10+var2, default:3
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 11, 'e2': 12, 'e3': 3}
        self.assertEqual(w, expected)

        text = '''
        @variables var11:1, var12:2, defval:0
        stimulus_elements: e1, e2, e3
        {}: e1:10+var11, e2:12, default:defval
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 11, 'e2': 12, 'e3': 0}
        self.assertEqual(w, expected)


class TestWithExpressions(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        for name in prop_names:
            self._test_simple(name)

    def _test_simple(self, name):
        text = '''
        stimulus_elements: e1, e2, e3, e4
        {}: e1: 1+2*3, e2: 4-3  *   2, e3: 10-1/2, e4: 0+0+0-0
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 7, 'e2': -2, 'e3': 9.5, 'e4': 0}
        self.assertEqual(w, expected)

        text = '''
        stimulus_elements: e1, e2, e3, e4
        behaviors: b1, b2
        {}: e1: 1+2*3,
                 e2: 4**2-3  *   2,
                 e3: 10-1/2,
                 e4: 0+0**1+0-0
        '''.format(name)
        w = parse(text, name)
        expected = {'e1': 7, 'e2': 10, 'e3': 9.5, 'e4': 0}
        self.assertEqual(w, expected)


class TestWithFunctions(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        for name in prop_names:
            self._test_rand(name)

    def _test_rand(self, name):
        text = '''
        stimulus_elements: e1, e2, e3, e4
        {}: e1: rand(1,10), e2: 4-rand(1,2), default:11, e3: 10
        '''.format(name)
        w = parse(text, name)

        e1 = w['e1']
        self.assertLessEqual(e1, 10)
        self.assertGreaterEqual(e1, 1)
        self.assertTrue(type(e1) is int)

        e2 = w['e2']
        self.assertTrue(e2 in (2, 3))

        e3 = w['e3']
        self.assertEqual(e3, 10)

        e4 = w['e4']
        self.assertEqual(e4, 11)

        # XXX should not work, no comma
        text = '''
        stimulus_elements: e1, e2, e3, e4
        {}: e1: 111,
            e2: 222,
            e3: 333,
            e4: 444
        {}: e1: rand(1,10),
            e2: 4-rand(1,2),
            e3: 10, default:11
        '''.format(name, name)
        w = parse(text, name)

        e1 = w['e1']
        self.assertLessEqual(e1, 10)
        self.assertGreaterEqual(e1, 1)
        self.assertTrue(type(e1) is int)

        e2 = w['e2']
        self.assertTrue(e2 in (2, 3))

        e3 = w['e3']
        self.assertEqual(e3, 10)

        e4 = w['e4']
        self.assertEqual(e4, 11)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        for name in prop_names:
            self._test_empty_name(name)

    def _test_empty_name(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}:
        '''.format(name)
        msg = "Error on line 3: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def _test_empty_name_no_colon(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}
        behaviors: b1, b2
        '''.format(name)
        msg = "Error on line 3: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_duplicate(self):
        for name in prop_names:
            self._test_duplicate(name)

    def _test_duplicate(self, name):
        text = '''
        stimulus_elements: e1, e2, e3, e4
        {}: e1:0.123, e2:4.56, e3:99, e1:-22, e18:knas
        '''.format(name)
        msg = "Error on line 3: Invalid value 'knas' for 'e18' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: ee1, e2, e3, e4
        {}: ee1:0.123, e2:4.56, ee1:99, foo->bar:1, default:Blaps
        '''.format(name)
        msg = "Error on line 3: Error in parameter '{}': 'foo->bar' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2, e3, e4
        {}: e1:0.123, e2:4.56, foo:1, e1:99, default:-22
        '''.format(name)
        msg = "Error on line 3: Error in parameter '{}': 'foo' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_stimulus_element_not_defined(self):
        for name in prop_names:
            self._test_stimulus_element_not_defined(name)

    def _test_stimulus_element_not_defined(self, name):
        text = '''
        behaviors: b1, b2
        {}: Blaps mortisaga
        '''.format(name)
        msg = "Error on line 3: The parameter 'stimulus_elements' must be assigned before the parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''  # XXX borde bli fel på saknad stimulus elöement?
        behaviors: b1, b2
        {}:
        '''.format(name)
        msg = "Error on line 3: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        {}: foo
        '''.format(name)
        msg = "Error on line 2: The parameter 'stimulus_elements' must be assigned before the parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_value(self):
        for name in prop_names:
            self._test_invalid_value(name)

    def _test_invalid_value(self, name):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: foo,>>>>////
        '''.format(name)
        msg = "Error on line 4: Expected 'element:value' or 'default:value' in '{}', got 'foo'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: foo>>>>////
        '''.format(name)
        msg = "Error on line 4: Expected 'element:value' or 'default:value' in '{}', got 'foo>>>>////'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: default::111
               '''.format(name)
        msg = "Error on line 3: Expected 'element:value' or 'default:value' in '{}', got 'default::111'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: e1->b1:1, blabla
               '''.format(name)
        msg = "Error on line 3: Error in parameter '{}': 'e1->b1' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_e_value(self):
        for name in prop_names:
            self._test_invalid_e_value(name)

    def _test_invalid_e_value(self, name):
        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: foo->bar:foobar, blabla
               '''.format(name)
        msg = "Error on line 3: Invalid value 'foobar' for 'foo->bar' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: fo o ->bar:foobar, blabla
               '''.format(name)
        msg = "Error on line 3: Invalid value 'foobar' for 'fo o ->bar' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  {}: blaps:foobar, blabla
               '''.format(name)
        msg = "Error on line 3: Invalid value 'foobar' for 'blaps' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_multiple_single_values(self):
        for name in prop_names:
            self._test_multiple_single_values(name)

    def _test_multiple_single_values(self, name):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: 1, 2
        '''.format(name)
        msg = "Error on line 4: Expected 'element:value' or 'default:value' in '{}', got '1'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: 18,
                 42
        '''.format(name)
        msg = "Error on line 4: A single value for '{}' cannot be followed by other values.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: 18,
                 oipoipoi,
                 dfldfjlkdj
        '''.format(name)
        msg = "Error on line 4: A single value for '{}' cannot be followed by other values.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: e1:3.22, 42
        '''.format(name)
        msg = "Error on line 4: Expected 'element:value' or 'default:value' in '{}', got '42'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: e1:3.22, 42, 8.3
        '''.format(name)
        msg = "Error on line 4: Expected 'element:value' or 'default:value' in '{}', got '42'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: e2:3.22,
                 42
        '''.format(name)
        msg = "Error on line 5: A single value for '{}' cannot follow other values.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_multiple_default(self):
        for name in prop_names:
            self._test_multiple_default(name)

    def _test_multiple_default(self, name):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: e1:3.22, default:12, e2:18, default:42
        '''.format(name)
        msg = "Error on line 4: Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: e1:3.22, default:12,
                 e2:18, default:42
        '''.format(name)
        msg = "Error on line 5: Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: e1:3.22, default:12, e2:18,
                 default:42
        '''.format(name)
        msg = "Error on line 5: Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_stimulus_element(self):
        for name in prop_names:
            self._test_invalid_stimulus_element(name)

    def _test_invalid_stimulus_element(self, name):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: E1:3.22, default:12, e2->b2:18
        '''.format(name)
        msg = "Error on line 4: Error in parameter '{}': 'E1' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: E1:3.22, default:12
        '''.format(name)
        msg = "Error on line 4: Error in parameter '{}': 'E1' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_eb(self):
        for name in prop_names:
            self._test_invalid_eb(name)

    def _test_invalid_eb(self, name):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: default:12, e1:22, kajsa:13, Klklklk***
        '''.format(name)
        msg = "Error on line 4: Error in parameter '{}': 'kajsa' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: default:12, e1:22, kajsa:freja
        '''.format(name)
        msg = "Error on line 4: Invalid value 'freja' for 'kajsa' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: default:12, e1:22,
                 kajsa:freja
        '''.format(name)
        msg = "Error on line 5: Invalid value 'freja' for 'kajsa' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_missing_default(self):
        for name in prop_names:
            self._test_missing_default(name)

    def _test_missing_default(self, name):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        {}: e1:22
        '''.format(name)
        msg = "Error on line 4: Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        {}: e1:22, e2:1.32
        '''.format(name)
        msg = "Error on line 4: Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2, e3
        {}: e1: 111
            e2: 222
            e3: 333
            e4: 444
        '''.format(name)
        msg = "Error on line 3: Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)
