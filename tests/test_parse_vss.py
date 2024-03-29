from .testutil import LsTestCase
from keywords import START_VSS, ALPHA_VSS
from parsing import Script


PROPS = [START_VSS, ALPHA_VSS]


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
        for prop in PROPS:
            self._test_simple(prop)

    def _test_simple(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1->e2:2, default:1
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e2'): 2, ('e1', 'e1'): 1, ('e2', 'e1'): 1, ('e2', 'e2'): 1}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: default:1, e2->e2:2
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 1, ('e1', 'e2'): 1, ('e2', 'e1'): 1, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)

    def test_multiline(self):
        for prop in PROPS:
            self._test_multiline(prop)

    def _test_multiline(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e2->e2:2,
                 default:1
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 1, ('e1', 'e2'): 1, ('e2', 'e1'): 1, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: default:1,
                 e2->e2:2
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 1, ('e1', 'e2'): 1, ('e2', 'e1'): 1, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)

    def test_scalar(self):
        for prop in PROPS:
            self._test_scalar(prop)

    def _test_scalar(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: 0.42
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 0.42, ('e1', 'e2'): 0.42, ('e2', 'e1'): 0.42, ('e2', 'e2'): 0.42}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}:default:0.42
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 0.42, ('e1', 'e2'): 0.42, ('e2', 'e1'): 0.42, ('e2', 'e2'): 0.42}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: 0
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 0, ('e1', 'e2'): 0, ('e2', 'e1'): 0, ('e2', 'e2'): 0}
        self.assertEqual(v, expected)

    def test_redefinition(self):
        for prop in PROPS:
            self._test_redefinition(prop)

    def _test_redefinition(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1:1, default: 2
        {}: e2->e2:2, default: 1
        '''.format(name, name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 1, ('e1', 'e2'): 1, ('e2', 'e1'): 1, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}:default:   0.42
        {}: default:1,
                 e2->e2:2
        '''.format(name, name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 1, ('e1', 'e2'): 1, ('e2', 'e1'): 1, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: default:1,
                 e2->e2:2
        {}: default:   0.42
        '''.format(name, name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 0.42, ('e1', 'e2'): 0.42, ('e2', 'e1'): 0.42, ('e2', 'e2'): 0.42}
        self.assertEqual(v, expected)

    def test_default_not_needed(self):
        for prop in PROPS:
            self._test_default_not_needed(prop)

    def _test_default_not_needed(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1:22,
                 e1->e2:23,
                 e2->e1:-24,
                 e2->e2:25
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 22, ('e1', 'e2'): 23, ('e2', 'e1'): -24, ('e2', 'e2'): 25}
        self.assertEqual(v, expected)

    def test_unfinished(self):
        for prop in PROPS:
            self._test_unfinished(prop)

    def _test_unfinished(self, name):
        text = '''stimulus_elements: e1, e2
        {}: default:111,
                 e2->e2:2,
        '''.format(name)
        v = parse(text, name)
        expected = {'default': 111, ('e2', 'e2'): 2, ('e1', 'e1'): None, ('e1', 'e2'): None,
                    ('e2', 'e1'): None}
        self.assertEqual(v, expected)


class TestWithVariables(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        for prop in PROPS:
            self._test_simple(prop)

    def _test_simple(self, name):
        text = '''
        @variables var11:0.2, var12:-0.1, var21:12, var22:0.1
        stimulus_elements: e1, e2
        {}: e1->e1:var11,
                 e1->e2:var12,
                 e2->e1:var21,
                 e2->e2:var22
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 0.2, ('e1', 'e2'): -0.1, ('e2', 'e1'): 12, ('e2', 'e2'): 0.1}
        self.assertEqual(v, expected)

        text = '''
        @variables var11:1, var12:2, var21:3, var22:4
        stimulus_elements: e1, e2
        {}: e1->e1:10+var11,
                 e1->e2:10+var12,
                 e2->e1:10+var21,
                 e2->e2:10+var22
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 11, ('e1', 'e2'): 12, ('e2', 'e1'): 13, ('e2', 'e2'): 14}
        self.assertEqual(v, expected)

        text = '''
        @variables var11:1, var12:2, var21:3, var22:4
        stimulus_elements: e1, e2
        {}: e1->e1:10+var11, e1->e2:10+var12, default:0
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 11, ('e1', 'e2'): 12, ('e2', 'e1'): 0, ('e2', 'e2'): 0}
        self.assertEqual(v, expected)

        text = '''
        @variables var11:1, var12:2, defval:0
        stimulus_elements: e1, e2
        {}: e1->e1:10+var11, e1->e2:10+var12, default:defval
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 11, ('e1', 'e2'): 12, ('e2', 'e1'): 0, ('e2', 'e2'): 0}
        self.assertEqual(v, expected)


class TestWithExpressions(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        for prop in PROPS:
            self._test_simple(prop)

    def _test_simple(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1: 1+2*3, e1->e2: 4-3  *   2, e2->e1: 10-1/2, e2->e2: 0+0+0-0
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 7, ('e1', 'e2'): -2, ('e2', 'e1'): 9.5, ('e2', 'e2'): 0}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1: 1+2*3,
                 e1->e2: 4**2-3  *   2,
                 e2->e1: 10-1/2,
                 e2->e2: 0+0**1+0-0
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 7, ('e1', 'e2'): 10, ('e2', 'e1'): 9.5, ('e2', 'e2'): 0}
        self.assertEqual(v, expected)


class TestWithFunctions(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        for prop in PROPS:
            self._test_rand(prop)

    def _test_rand(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1: rand(1,10), e1->e2: 4-rand(1,2), e2->e1: 10, default:11
        '''.format(name)
        v = parse(text, name)
        e1_e1 = v[('e1', 'e1')]
        self.assertLessEqual(e1_e1, 10)
        self.assertGreaterEqual(e1_e1, 1)
        self.assertTrue(type(e1_e1) is int)

        e1_e2 = v[('e1', 'e2')]
        self.assertTrue(e1_e2 in (2, 3))

        e2_e1 = v[('e2', 'e1')]
        self.assertEqual(e2_e1, 10)

        e2_e2 = v[('e2', 'e2')]
        self.assertEqual(e2_e2, 11)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1: rand(1,10),
                         e1->e2: 4-rand(1,2),
                         e2->e1: 10, default:11
        '''.format(name)
        v = parse(text, name)
        e1_e1 = v[('e1', 'e1')]
        self.assertLessEqual(e1_e1, 10)
        self.assertGreaterEqual(e1_e1, 1)
        self.assertTrue(type(e1_e1) is int)

        e1_e2 = v[('e1', 'e2')]
        self.assertTrue(e1_e2 in (2, 3))

        e2_e1 = v[('e2', 'e1')]
        self.assertEqual(e2_e1, 10)

        e2_e2 = v[('e2', 'e2')]
        self.assertEqual(e2_e2, 11)


class TestWithWildcards(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        for prop in PROPS:
            self._test_simple(prop)

    def _test_simple(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: *->e2:2, default:1
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 1, ('e1', 'e2'): 2, ('e2', 'e1'): 1, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: default:1, e1->*:2
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 2, ('e1', 'e2'): 2, ('e2', 'e1'): 1, ('e2', 'e2'): 1}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: default:1, *->*:2
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 2, ('e1', 'e2'): 2, ('e2', 'e1'): 2, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)

        text = '''
        stimulus_elements: e1, e2
        {}: *->*:2
        '''.format(name)
        v = parse(text, name)
        expected = {('e1', 'e1'): 2, ('e1', 'e2'): 2, ('e2', 'e1'): 2, ('e2', 'e2'): 2}
        self.assertEqual(v, expected)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        for prop in PROPS:
            self._test_empty_name(prop)

    def _test_empty_name(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}:
        '''.format(name)
        msg = "Error on line 3: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def _test_mixup_eb(self, name):
        pass

    def test_stimulus_element_not_defined(self):
        for prop in PROPS:
            self._test_stimulus_element_not_defined(prop)

    def _test_stimulus_element_not_defined(self, name):
        text = '''
        {}: Blaps mortisaga
        '''.format(name)
        msg = f"Error on line 2: The parameter 'stimulus_elements' must be assigned before the parameter '{name}'."
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        {}:
        '''.format(name)
        msg = "Error on line 2: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        {}: foo
        '''.format(name)
        msg = f"Error on line 2: The parameter 'stimulus_elements' must be assigned before the parameter '{name}'."
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_value(self):
        for prop in PROPS:
            self._test_invalid_value(prop)

    def _test_invalid_value(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: foo,>>>>////
        '''.format(name)
        msg = "Error on line 3: Expected 'x->y:value' or 'default:value' in '{}', got 'foo'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: foo>>>>////
        '''.format(name)
        msg = "Error on line 3: Expected 'x->y:value' or 'default:value' in '{}', got 'foo>>>>////'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  {}: default::111
               '''.format(name)
        msg = "Error on line 2: Expected 'x->y:value' or 'default:value' in '{}', got 'default::111'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  {}: e1->e1:1, blabla
               '''.format(name)
        msg = "Error on line 2: Expected 'x->y:value' or 'default:value' in '{}', got 'blabla'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_eb_value(self):
        for prop in PROPS:
            self._test_invalid_eb_value(prop)

    def _test_invalid_eb_value(self, name):
        text = '''stimulus_elements: e1, e2
                  {}: foo->bar:foobar, blabla
               '''.format(name)
        msg = "Error on line 2: Invalid value 'foobar' for 'foo->bar' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  {}: fo o ->bar:foobar, blabla
               '''.format(name)
        msg = "Error on line 2: Invalid value 'foobar' for 'fo o ->bar' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''stimulus_elements: e1, e2
                  {}: blaps:foobar, blabla
               '''.format(name)
        msg = "Error on line 2: Invalid value 'foobar' for 'blaps' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_multiple_single_values(self):
        for prop in PROPS:
            self._test_multiple_single_values(prop)

    def _test_multiple_single_values(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: 1, 2
        '''.format(name)
        msg = "Error on line 3: Expected 'x->y:value' or 'default:value' in '{}', got '1'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: 18,
                 42
        '''.format(name)
        msg = "Error on line 3: A single value for '{}' cannot be followed by other values.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: 18,
                 oipoipoi,
                 dfldfjlkdj
        '''.format(name)
        msg = "Error on line 3: A single value for '{}' cannot be followed by other values.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e2:3.22, 42
        '''.format(name)
        msg = "Error on line 3: Expected 'x->y:value' or 'default:value' in '{}', got '42'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e2:3.22, 42, 8.3
        '''.format(name)
        msg = "Error on line 3: Expected 'x->y:value' or 'default:value' in '{}', got '42'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e2:3.22,
                 42
        '''.format(name)
        msg = "Error on line 4: A single value for '{}' cannot follow other values.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_multiple_default(self):
        for prop in PROPS:
            self._test_multiple_default(prop)

    def _test_multiple_default(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1->e2:3.22, default:12, e2->e2:18, default:42
        '''.format(name)
        msg = "Error on line 3: Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e2:3.22, default:12,
                 e2->e2:18, default:42
        '''.format(name)
        msg = "Error on line 4: Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e2:3.22, default:12, e2->e2:18,
                 default:42
        '''.format(name)
        msg = "Error on line 4: Default value for '{}' can only be stated once.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_stimulus_element(self):
        for prop in PROPS:
            self._test_invalid_stimulus_element(prop)

    def _test_invalid_stimulus_element(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: E1->e2:3.22, default:12, e2->e2:18
        '''.format(name)
        msg = "Error on line 3: Error in parameter '{}': 'E1' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: E1->B2:3.22, default:12
        '''.format(name)
        msg = "Error on line 3: Error in parameter '{}': 'E1' is an invalid stimulus element.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_eb(self):
        for prop in PROPS:
            self._test_invalid_eb(prop)

    def _test_invalid_eb(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: default:12, e1->e1:22, kajsa:13, Klklklk***
        '''.format(name)
        msg = "Error on line 3: Invalid string 'kajsa' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: default:12, e1->e1:22, kajsa:freja
        '''.format(name)
        msg = "Error on line 3: Invalid value 'freja' for 'kajsa' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: default:12, e1->e1:22,
                 kajsa:freja
        '''.format(name)
        msg = "Error on line 4: Invalid value 'freja' for 'kajsa' in parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_missing_default(self):
        for prop in PROPS:
            self._test_missing_default(prop)

    def _test_missing_default(self, name):
        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1:22
        '''.format(name)
        msg = "Error on line 3: Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        stimulus_elements: e1, e2
        {}: e1->e1:22, e1->e2:-8, e2->e1:1.32
        '''.format(name)
        msg = "Error on line 3: Missing default value for parameter '{}'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)
