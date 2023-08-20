from .testutil import LsTestCase
from keywords import STIMULUS_ELEMENTS
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[STIMULUS_ELEMENTS]


class TestBasic(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        stimulus_elements: B1, b1, B2, b2
        '''
        stimulus_elements = parse(text)
        self.assertEqual(stimulus_elements, ['B1', 'b1', 'B2', 'b2'])

        text = '''
               stimulus_elements   :    B1,b1,  B2,   b2          
                '''
        stimulus_elements = parse(text)
        self.assertEqual(stimulus_elements, ['B1', 'b1', 'B2', 'b2'])

    def test_multiline(self):
        text = '''
        stimulus_elements: b1, b2,
                   b3, b4
        '''
        stimulus_elements = parse(text)
        self.assertEqual(stimulus_elements, ['b1', 'b2', 'b3', 'b4'])

        text = '''
        stimulus_elements   :    b1,
                       b2,  b3,
                b4,
                b5
        '''
        stimulus_elements = parse(text)
        self.assertEqual(stimulus_elements, ['b1', 'b2', 'b3', 'b4', 'b5'])

    def test_redefinition(self):
        text = '''
        stimulus_elements: b1, b2, b3, b4
        stimulus_elements: x1, x2
        '''
        msg = "Error on line 3: Parameter stimulus_elements already defined."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        stimulus_elements: x1, x2
        stimulus_elements: b1, b2, b3, b4
        '''
        msg = "Error on line 3: Parameter stimulus_elements already defined."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        stimulus_elements: b1, b2,
                   b3, b4
        stimulus_elements: x1,
                   x2
        '''
        msg = "Error on line 4: Parameter stimulus_elements already defined."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        stimulus_elements: x1, x2
        stimulus_elements: b1,
                   b2, b3,
                   b4
        '''
        msg = "Error on line 3: Parameter stimulus_elements already defined."
        with self.assertRaisesMsg(msg):
            parse(text)


class TestParsestimulus_elementsErrors(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        stimulus_elements: b1, , b2, b3
        '''
        msg = "Error on line 2: Found empty stimulus element name."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_duplicate(self):
        text = '''
        stimulus_elements: b1, b2, b3, b4, b2, b1
        '''
        msg = "Error on line 2: The stimulus element name 'b2' occurs more than once."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        stimulus_elements: b1, b2, b3,
                   b4, b2, b1
        '''
        msg = "Error on line 3: The stimulus element name 'b2' occurs more than once."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_stimulus_element_is_behavior(self):
        text = '''
        behaviors: e1, e2, e3
        stimulus_elements: b1, b2, b3, b4, e2
        '''
        msg = "Error on line 3: The stimulus element name 'e2' is invalid, since it is a behavior name."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        behaviors: e1, e2, e3
        stimulus_elements: b1, b2, b3, b4,
                   e2, b1
        '''
        msg = "Error on line 4: The stimulus element name 'e2' is invalid, since it is a behavior name."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_behavior_is_variable(self):
        text = '''
        @variables v1:1.2, v2:2.3, v3:3.4
        stimulus_elements: b1, b2, b3, b4, v2, v3, v1
        '''
        msg = "Error on line 3: The stimulus element name 'v2' is invalid, since it is a variable name."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        @variables v1:1.2, v2:2.3, v3:3.4
        stimulus_elements: b1, b2, b3, b4,
                   v2
        '''
        msg = "Error on line 4: The stimulus element name 'v2' is invalid, since it is a variable name."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_invalid_identifier(self):
        text = '''
        @variables v1:1.2, v2:2.3, v3:3.4
        stimulus_elements: b1, b2, b3, b4, v2. v3, v1
        '''
        msg = "Error on line 3: Stimulus element name 'v2. v3' is not a valid identifier."
        with self.assertRaisesMsg(msg):
            parse(text)
