from .testutil import LsTestCase
from keywords import MECHANISM_NAME
from parsing import Script
from mechanism_names import GA, SR, ES, QL, AC


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[MECHANISM_NAME]


class TestBasic(LsTestCase):
    def setUp(self):
        pass

    def test_ga(self):
        text = '''
        mechanism: ga
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, GA)

        text = '''
        mechanism: GA
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, GA)

    def test_sr(self):
        text = '''
        mechanism: sr
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, SR)

        text = '''
        mechanism: Sr
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, SR)

    def test_es(self):
        text = '''
        mechanism: es
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, ES)

        text = '''
        mechanism: eS
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, ES)

    def test_ql(self):
        text = '''
        mechanism:ql
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, QL)

        text = '''
        mechanism:  QL
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, QL)

    def test_ac(self):
        text = '''
        mechanism:    ac
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, AC)

        text = '''
        mechanism:aC
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, AC)

    def test_redefinition(self):
        text = '''
        mechanism:aC
        mechanism:GA
        '''
        mechanism_name = parse(text)
        self.assertEqual(mechanism_name, GA)


class TestParseMechanismNameErrors(LsTestCase):
    def setUp(self):
        pass

    def test_no_mechanism(self):
        text = '''
        stimulus_elements: a, b
        @phase foo stop:False
        A a | A
        @run foo
        '''
        msg = "Parameter 'mechanism' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_empty_name(self):
        text = '''
        mechanism:
        stimulus_elements: a, b
        '''
        msg = "Parameter 'mechanism' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_name(self):
        text = '''
        mechanism: foo
        '''
        msg = "Invalid mechanism name 'foo'. Mechanism name must be one of the following: ac, es, ga, ql, sr."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        mechanism: 1+1
        '''
        msg = "Invalid mechanism name '1\+1'. Mechanism name must be one of the following: ac, es, ga, ql, sr."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        mechanism: ga, sr, ES, QL, AC
        '''
        msg = "Invalid mechanism name 'ga, sr, ES, QL, AC'. Mechanism name must be one of the following: ac, es, ga, ql, sr."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_comma(self):
        text = '''
        mechanism: ga,
        '''
        msg = "Value for mechanism may not end by comma."
        with self.assertRaisesX(Exception, msg):
            parse(text)
