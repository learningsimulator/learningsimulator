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
        self.assertTrue(mechanism_name in GA)

        text = '''
        mechanism: Alearning
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in GA)

    def test_sr(self):
        text = '''
        mechanism: sr
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in SR)

        text = '''
        mechanism: StimulusResponse
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in SR)

    def test_es(self):
        text = '''
        mechanism: es
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in ES)

        text = '''
        mechanism: expectedSARSA
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in ES)

    def test_ql(self):
        text = '''
        mechanism:ql
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in QL)

        text = '''
        mechanism:  Qlearning
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in QL)

    def test_ac(self):
        text = '''
        mechanism:    ac
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in AC)

        text = '''
        mechanism:aCtorcritiC
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in AC)

    def test_redefinition(self):
        text = '''
        mechanism:aC
        mechanism:GA
        '''
        mechanism_name = parse(text)
        self.assertTrue(mechanism_name in GA)


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
        msg = "Error on line 5: Parameter 'mechanism' is not specified."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_empty_name(self):
        text = '''
        mechanism:
        stimulus_elements: a, b
        '''
        msg = "Error on line 2: Parameter 'mechanism' is not specified."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_invalid_name(self):
        text = '''
        mechanism: foo
        '''
        msg = "Error on line 2: Invalid mechanism name 'foo'. Mechanism name must be one of the following: a, ac, actorcritic, alearning, es, expectedsarsa, ga, ql, qlearning, rescorlawagner, rw, sr, stimulusresponse."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        mechanism: 1+1
        '''
        msg = "Error on line 2: Invalid mechanism name '1+1'. Mechanism name must be one of the following: a, ac, actorcritic, alearning, es, expectedsarsa, ga, ql, qlearning, rescorlawagner, rw, sr, stimulusresponse."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        mechanism: ga, sr, ES, QL, AC
        '''
        msg = "Error on line 2: Invalid mechanism name 'ga, sr, ES, QL, AC'. Mechanism name must be one of the following: a, ac, actorcritic, alearning, es, expectedsarsa, ga, ql, qlearning, rescorlawagner, rw, sr, stimulusresponse."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_comma(self):
        text = '''
        mechanism: ga,
        '''
        msg = "Error on line 2: Value for mechanism may not end by comma."
        with self.assertRaisesMsg(msg):
            parse(text)
