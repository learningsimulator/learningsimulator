from .testutil import LsTestCase
from keywords import BEHAVIORS
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[BEHAVIORS]


class TestBasic(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        behaviors: B1, b1, B2, b2
        '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['B1', 'b1', 'B2', 'b2'])

        text = '''
               behaviors   :    B1,b1,  B2,   b2
               '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['B1', 'b1', 'B2', 'b2'])

        text = '''
               behaviors   =    B1,b1,  B2,   b2
               '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['B1', 'b1', 'B2', 'b2'])

    def test_multiline(self):
        text = '''
        behaviors: b1, b2,
                   b3, b4
        '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['b1', 'b2', 'b3', 'b4'])

        text = '''
        behaviors   :    b1,
                       b2,  b3,
                b4,
                b5
        '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['b1', 'b2', 'b3', 'b4', 'b5'])

    def test_redefinition(self):
        text = '''
        behaviors: b1, b2, b3, b4
        behaviors: x1, x2
        '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['x1', 'x2'])

        text = '''
        behaviors: x1, x2
        behaviors: b1, b2, b3, b4
        '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['b1', 'b2', 'b3', 'b4'])

        text = '''
        behaviors: b1, b2,
                   b3, b4
        behaviors: x1,
                   x2
        '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['x1', 'x2'])

        text = '''
        behaviors: x1, x2
        behaviors: b1,
                   b2, b3,
                   b4
        '''
        behaviors = parse(text)
        self.assertEqual(behaviors, ['b1', 'b2', 'b3', 'b4'])


class TestParseBehaviorsErrors(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        behaviors: b1, , b2, b3
        '''
        msg = "Error on line 2: Found empty behavior name."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_duplicate(self):
        text = '''
        behaviors: b1, b2, b3, b4, b2, b1
        '''
        msg = "Error on line 2: The behavior name 'b2' occurs more than once."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        behaviors: b1, b2, b3,
                   b4, b2, b1
        '''
        msg = "Error on line 3: The behavior name 'b2' occurs more than once."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_behavior_is_stimulus(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2, b3, b4, e2
        '''
        msg = "Error on line 3: The behavior name 'e2' is invalid, since it is a stimulus element."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2, b3, b4,
                   e2, b1
        '''
        msg = "Error on line 4: The behavior name 'e2' is invalid, since it is a stimulus element."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_behavior_is_variable(self):
        text = '''
        @variables v1:1.2, v2:2.3, v3:3.4
        behaviors: b1, b2, b3, b4, v2, v3, v1
        '''
        msg = "Error on line 3: The behavior name 'v2' is invalid, since it is a variable name."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        @variables v1:1.2, v2:2.3, v3:3.4
        behaviors: b1, b2, b3, b4,
                   v2
        '''
        msg = "Error on line 4: The behavior name 'v2' is invalid, since it is a variable name."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_invalid_identifier(self):
        text = '''
        @variables v1:1.2, v2:2.3, v3:3.4
        behaviors: b1, b2, b3, b4, v2. v3, v1
        '''
        msg = "Error on line 3: Behavior name 'v2. v3' is not a valid identifier."
        with self.assertRaisesMsg(msg):
            parse(text)
