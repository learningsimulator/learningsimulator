from .testutil import LsTestCase
from keywords import RESPONSE_REQUIREMENTS
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[RESPONSE_REQUIREMENTS]


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        response_requirements: b1:e1, b2:e2
        '''
        rr = parse(text)
        expected = {'b1': {'e1'}, 'b2': {'e2'}, 'b3': {'e1', 'e2'}}
        self.assertEqual(rr, expected)

    def test_multiline(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        response_requirements: b1:e1,
                               b2:e2
        '''
        rr = parse(text)
        expected = {'b1': {'e1'}, 'b2': {'e2'}, 'b3': {'e1', 'e2'}}
        self.assertEqual(rr, expected)

        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2,
                   b3
        response_requirements: b1:[e1,e3] ,
                               b2:e2
        '''
        rr = parse(text)
        expected = {'b1': {'e1', 'e3'}, 'b2': {'e2'}, 'b3': {'e1', 'e2', 'e3'}}
        self.assertEqual(rr, expected)

    def test_redefinition(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2,
                   b3
        response_requirements: b1:[e1,e3] ,
                               b2:e2
        response_requirements: b1:e1,
                               b2:e2, b3:[e2,e3]
        '''
        rr = parse(text)
        expected = {'b1': {'e1'}, 'b2': {'e2'}, 'b3': {'e2', 'e3'}}
        self.assertEqual(rr, expected)

        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2,
                   b3
        response_requirements: b1:[e1,e2,e3] ,
                               b2:[e1,e2,      e3]
        response_requirements: b1:[e1,e2,e3],
                               b2:[e1,e2,e3],
                               b3:[e1,e2,e3]
        '''
        rr = parse(text)
        expected = {'b1': {'e1', 'e2', 'e3'}, 'b2': {'e1', 'e2', 'e3'}, 'b3': {'e1', 'e2', 'e3'}}
        self.assertEqual(rr, expected)

    def test_unfinished(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2,
                   b3
        response_requirements: b1:[e1,e2,e3] ,
        '''
        rr = parse(text)
        expected = {'b1': {'e1', 'e2', 'e3'}, 'b2': None, 'b3': None}
        self.assertEqual(rr, expected)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements:
        '''
        msg = "Parameter 'response_requirements' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def _test_empty_name_no_colon(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements
        '''
        msg = "Parameter '{}' not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_duplicate(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b1:e2
        '''
        msg = "Duplication of behavior 'b1' in response_requirements."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:e2,
                               b1:e2, fgjfkjglgj
        '''
        msg = "Duplication of behavior 'b1' in response_requirements."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2, e3, e4
        behaviors: b1, b2, b3, b4
        response_requirements: b1:e1, b2:[e2,e4]      ,
                               b2:e2
        '''
        msg = "Duplication of behavior 'b2' in response_requirements."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_stimulus_element_not_defined(self):
        text = '''
        behaviors: b1, b2
        response_requirements: Blaps mortisaga
        '''
        msg = "The parameter 'stimulus_elements' must be assigned before the parameter 'response_requirements'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: s1, s2
        response_requirements: Blaps mortisaga
        '''
        msg = "The parameter 'behaviors' must be assigned before the parameter 'response_requirements'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: s1, s2
        response_requirements: b1:s1, b2:s2
        '''
        msg = "The parameter 'behaviors' must be assigned before the parameter 'response_requirements'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        response_requirements: foo
        '''
        msg = "The parameter 'stimulus_elements' must be assigned before the parameter 'response_requirements'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: foo,>>>>////
        '''
        msg = "Expected 'behavior:stimulus_element', got 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: foo>>>>////
        '''
        msg = "Expected 'behavior:stimulus_element', got 'foo>>>>////'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1::e1
        '''
        msg = "Expected 'behavior:stimulus_element', got 'b1::e1'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:
        '''
        msg = "Expected 'behavior:stimulus_element', got 'b1:'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: :e1
        '''
        msg = "Expected 'behavior:stimulus_element', got ':e1'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_behavior_name(self):
        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  response_requirements: b1:e1, B2:e2
                  '''
        msg = "Unknown behavior name 'B2'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  response_requirements: foo:bar, blabla
               '''
        msg = "Unknown behavior name 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  response_requirements: e2:b1, foo:bar
               '''
        msg = "Unknown behavior name 'e2'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''stimulus_elements: e1, e2
                  behaviors: b1, b2
                  response_requirements: b2:e1, foo:bar
               '''
        msg = "Unknown behavior name 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_stimulus_element(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:E1, b2:[e1,e2]
        '''
        msg = "Unknown stimulus element 'E1'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:E1,
                               b2:[e1,e2]
        '''
        msg = "Unknown stimulus element 'E1'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b2:[e1,e2],
                               b1:E1
        '''
        msg = "Unknown stimulus element 'E1'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:[e1,foo]
        '''
        msg = "Unknown stimulus element 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1,
                               b2:[e1,foo]
        '''
        msg = "Unknown stimulus element 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:[e1,foo,e2]
        '''
        msg = "Unknown stimulus element 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b2:[e1,foo,e2], b1:e1
        '''
        msg = "Unknown stimulus element 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1,
                               b2:[e1,foo]
        '''
        msg = "Unknown stimulus element 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_malformed_expression(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:[e1,e]2
        '''
        msg = "Malformed expression '\[e1,e\]2'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:[e1,e]2
        '''
        msg = "Malformed expression '\[e1,e\]2'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:[[[e1,e]2
        '''
        msg = "Malformed expression '\[\[\[e1,e\]2'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:wewew[e1,e2]
        '''
        msg = "Malformed expression 'wewew\[e1,e2\]'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        response_requirements: b1:e1, b2:[[e1,e2]]
        '''
        msg = "Malformed expression '\[\[e1,e2\]\]'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    # def test_no_possible_respone(self):
    #     text = '''
    #     stimulus_elements: e1, e2, e3, e4
    #     behaviors: b1, b2, b3
    #     response_requirements: b1:e1, b2:[e1,e2]
    #     '''
    #     msg = "Invalid response_requirements: Stimulus elements [foo] has no possible responses."
    #     with self.assertRaisesX(Exception, msg):
    #         parse(text)
