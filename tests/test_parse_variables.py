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

    def test_random(self):
        text = '''
        @variables  x = 1,
                    y = 2,
                    z = rand(x,y),
                    w = choice(x,y,3.4),
                    q = choice([x,y,3.5], [x/10,y/10,0.3])
        '''
        var_values = parse(text)
        self.assertEqual(var_values['x'], 1)
        self.assertEqual(var_values['y'], 2)
        self.assertTrue(var_values['z'] in (1, 2))
        self.assertTrue(var_values['w'] in (1, 2, 3.4))
        self.assertTrue(var_values['q'] in (1, 2, 3.5))

    def test_random_distribution(self):
        text = '''
        @variables  x = 1, y = 2, z = rand(x,y),
                    w = choice(x,y,3.4),
                    q = choice([x,y,3.5], [x/10,y/10,0.3]), foo = 0.1
        '''
        z_values = list()
        w_values = list()
        q_values = list()
        N = 30000
        for _ in range(N):
            var_values = parse(text)

            self.assertEqual(var_values['x'], 1)
            self.assertEqual(var_values['y'], 2)
            self.assertTrue(var_values['z'] in (1, 2))
            self.assertTrue(var_values['w'] in (1, 2, 3.4))
            self.assertTrue(var_values['q'] in (1, 2, 3.5))

            z_values.append(var_values['z'])
            w_values.append(var_values['w'])
            q_values.append(var_values['q'])

        z_1 = z_values.count(1)
        z_2 = z_values.count(2)

        w_1 = w_values.count(1)
        w_2 = w_values.count(2)
        w_34 = w_values.count(3.4)

        q_1 = q_values.count(1)
        q_2 = q_values.count(2)
        q_35 = q_values.count(3.5)

        TOL = 0.01
        self.assertLess(abs(z_1 / N - 1 / 2), TOL)
        self.assertLess(abs(z_2 / N - 1 / 2), TOL)

        self.assertLess(abs(w_1 / N - 1 / 3), TOL)
        self.assertLess(abs(w_2 / N - 1 / 3), TOL)
        self.assertLess(abs(w_34 / N - 1 / 3), TOL)

        self.assertLess(abs(q_1 / N - 0.1 / 0.6), TOL)
        self.assertLess(abs(q_2 / N - 0.2 / 0.6), TOL)
        self.assertLess(abs(q_35 / N - 0.3 / 0.6), TOL)

    def test_reset_previously_defined1(self):
        text = '''
        @variables  x = 1, y = 2,
                    z = 3
        x = 100
        y = 200
        z = 300
        '''
        var_values = parse(text)
        self.assertEqual(var_values, {'x': 100, 'y': 200, 'z': 300})

    def test_reset_previously_defined2(self):
        text = '''
        @variables  x = 1, y = 2,
                    z = 3
        @variables x = 100
        @variables y = 200, z = 300
        '''
        var_values = parse(text)
        self.assertEqual(var_values, {'x': 100, 'y': 200, 'z': 300})


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty(self):
        text = '''
        @variables
        '''
        msg = "Error on line 2: @VARIABLES not specified."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_invalid_valvar(self):
        text = '''
        @variables foo bar
        '''
        msg = ""
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_invalid_value(self):
        text = '''
        @variables foo:bar, x:1, y:2
        '''
        msg = ""
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        @variables foo:bar:foobar, x:1, y:2
        '''
        msg = ""
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        @variables x:1:2, y:2
        '''
        msg = ""
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_variable_name_is_stimulus(self):
        pass

    def test_variable_name_is_behavior(self):
        pass

    def test_invalid_identifier(self):
        text = '''
        @variables v1:1.2, 1v2:2.3, v3:3.4
        '''
        msg = "Error on line 2: Variable name '1v2' is not a valid identifier."
        with self.assertRaisesMsg(msg):
            parse(text)

        text = '''
        @variables v1:1.2,
                   1v2:2.3, v3:3.4
        '''
        msg = "Error on line 3: Variable name '1v2' is not a valid identifier."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_forgot_comma(self):
        text = '''
        @variables  x :1,
                    y: 2,
                    z :   3
                    w : -1.2
        '''
        msg = "Error on line 5: Invalid expression 'w : -1.2'."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_end_by_comma(self):
        text = '''
               @variables  x :1,
                           y: 2,
                           z :   3,
                           w : -1.2,
                mechanism: dkjfldskj
                '''
        msg = "Error on line 6: Variable name 'mechanism' is a keyword."
        with self.assertRaisesMsg(msg):
            parse(text)

    def test_reset_previously_undefined(self):
        text = '''
        @variables  x = 1, y = 2,
                    z = 3
        x = 100
        y = 200
        z = 300
        w = 4
        '''
        msg = "Error on line 7: Invalid expression 'w = 4'."
        with self.assertRaisesMsg(msg):
            parse(text)
