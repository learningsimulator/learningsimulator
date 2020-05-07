from .testutil import LsTestCase
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.variables.values


class TestBasic(LsTestCase):
    def test_basic(self):
        text = '''
        @variables    x:1, y:2
        '''
        var_values = parse(text)
        self.assertEqual(var_values, {'x': 1, 'y': 2})

        text = '''
        @variables  x :1, y: 2,
                    z :   3
        '''
        var_values = parse(text)
        self.assertEqual(var_values, {'x': 1, 'y': 2, 'z': 3})

        text = '''
        @variables  x :1,
                    y: 2,
                    z :   3,
                    w : -1.2
        '''
        var_values = parse(text)
        self.assertEqual(var_values, {'x': 1, 'y': 2, 'z': 3, 'w': -1.2})

    def test_ref_var(self):
        text = '''
        @variables  x :1, y: 2,
                    z :   3, w : x
        '''
        var_values = parse(text)
        self.assertEqual(var_values, {'x': 1, 'y': 2, 'z': 3, 'w': 1})

    def test_comma(self):
        text = '''@variables  x :1,
                              y: 2,
                              z :   3,
                              w : -1.2,'''
        var_values = parse(text)
        self.assertEqual(var_values, {'x': 1, 'y': 2, 'z': 3, 'w': -1.2})


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty(self):
        text = '''
        @variables
        '''
        msg = "@VARIABLES not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_valvar(self):
        text = '''
        @variables foo bar
        '''
        msg = ""
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        @variables foo:bar, x:1, y:2
        '''
        msg = ""
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        @variables foo:bar:foobar, x:1, y:2
        '''
        msg = ""
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        @variables x:1:2, y:2
        '''
        msg = ""
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_variable_name_is_stimulus(self):
        pass

    def test_variable_name_is_behavior(self):
        pass

    def test_invalid_identifier(self):
        text = '''
        @variables v1:1.2, 1v2:2.3, v3:3.4
        '''
        msg = "Error on line 2: Variable name must be a valid identifier. '1v2'' is not."
        with self.assertRaisesX(Exception, msg):
            parse(text)

        text = '''
        @variables v1:1.2,
                   1v2:2.3, v3:3.4
        '''
        msg = "Error on line 3: Variable name must be a valid identifier. '1v2'' is not."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_forgot_comma(self):
        text = '''
        @variables  x :1,
                    y: 2,
                    z :   3
                    w : -1.2
        '''
        msg = "Error on line 5: Invalid expression 'w : -1.2'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_end_by_comma(self):
        text = '''
               @variables  x :1,
                           y: 2,
                           z :   3,
                           w : -1.2,
                mechanism: dkjfldskj
                '''
        msg = "Error on line 6: Variable name must not be a keyword. 'mechanism' is."
        with self.assertRaisesX(Exception, msg):
            parse(text)
