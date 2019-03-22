from .testutil import LsTestCase
from keywords import N_SUBJECTS
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[N_SUBJECTS]


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        n_subjects: 100
        '''
        n_subjects = parse(text)
        self.assertEqual(n_subjects, 100)

    def test_redefinition(self):
        text = '''
        n_subjects: 1
        stimulus_elements: e1, e2
        behaviors: b1, b2
        n_subjects: 110011
        beta: 0.5
        '''
        n_subjects = parse(text)
        self.assertEqual(n_subjects, 110011)


class TestWithVariables(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        @variables var11:2, var12:-1, var21:12, var22:1
        n_subjects:    var11
        '''
        n_subjects = parse(text)
        self.assertEqual(n_subjects, 2)

        text = '''
        @variables var11:20, var12:-1, var21:12, var22:0.1
        stimulus_elements: e1, e2
        behaviors: b1, b2
        n_subjects:    var11+12
        '''
        n_subjects = parse(text)
        self.assertEqual(n_subjects, 32)

        text = '''
        @variables var11:2, var12:-0.1, var21:12, var22:1
        n_subjects:    var11+var22*var21
        '''
        n_subjects = parse(text)
        self.assertEqual(n_subjects, 14)

        text = '''
        @variables var11:2, var12:-1, var21:3, var22:2
        n_subjects:    var11 + var22*var21 + var22**var22
        '''
        n_subjects = parse(text)
        self.assertEqual(n_subjects, 12)

        text = '''
        @variables x:1
        '''
        n_subjects = parse(text)
        self.assertEqual(n_subjects, 1)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        n_subjects:
        mechanism: foo
        '''
        msg = "Parameter 'n_subjects' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_empty_name_no_colon(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        n_subjects
        mechanism: foo
        '''
        msg = "Parameter 'n_subjects' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        n_subjects: foo,>>>>////
        '''
        msg = "Error in expression 'foo,>>>>////': invalid syntax."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        n_subjects: 2*rand(4,Blaps)
        '''
        msg = "Unknown variable 'Blaps'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_erroneous_rand(self):
        text = '''
        n_subjects: rand(1.2, 3)
        '''
        msg = "First argument to 'rand' must be integer."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        n_subjects: rand(1, 3.3)
        '''
        msg = "Second argument to 'rand' must be integer."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        n_subjects: rand(3, 1)
        '''
        msg = "The first argument to 'rand' must be less than or equal to the second argument."
        with self.assertRaisesX(Exception, msg):
            parse(text)
