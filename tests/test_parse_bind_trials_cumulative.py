from .testutil import LsTestCase
from keywords import BIND_TRIALS, CUMULATIVE
from parsing import Script


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
        self._test_simple(BIND_TRIALS)
        self._test_simple(CUMULATIVE)

    def _test_simple(self, name):
        text = '''
        {}: on
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'on')

        text = '''
        {}: off
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'off')

        text = '''
        {}: ON
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'on')

        text = '''
        {}: OFF
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'off')

        text = '''
        {}:     oN    
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'on')

        text = '''
        {}    :     OfF    
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'off')

    def test_redefinition(self):
        self._test_redefinition(BIND_TRIALS)
        self._test_redefinition(CUMULATIVE)

    def _test_redefinition(self, name):
        text = '''
        {}:off    
        {}:on
        '''.format(name, name)
        x = parse(text, name)
        self.assertEqual(x, 'on')

        text = '''
        {}    :     OfF    
        {}:    oN
        '''.format(name, name)
        x = parse(text, name)
        self.assertEqual(x, 'on')

        text = '''
        {}:on    
        {}:off
        '''.format(name, name)
        x = parse(text, name)
        self.assertEqual(x, 'off')

        text = '''
        {}:    oN        
        {}    :     OfF    
        '''.format(name, name)
        x = parse(text, name)
        self.assertEqual(x, 'off')

        text = '''
        {}:    oN        
        {}    :     OfF    
        {}:off    
        {}: on    
        '''.format(name, name, name, name)
        x = parse(text, name)
        self.assertEqual(x, 'on')


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        self._test_empty_name(BIND_TRIALS)
        self._test_empty_name(CUMULATIVE)

    def _test_empty_name(self, name):
        text = f'''
        {name}:
        '''
        msg = f"Error on line 2: Parameter '{name}' is not specified."
        with self.assertRaisesMsg(msg):
            parse(text, name)

        text = '''
        {}   :
        '''.format(name)
        msg = "Error on line 2: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_empty_name_no_colon(self):
        self._test_empty_name_no_colon(BIND_TRIALS)
        self._test_empty_name_no_colon(CUMULATIVE)

    def _test_empty_name_no_colon(self, name):
        text = '''
        {}
        '''.format(name)
        msg = "Error on line 2: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_invalid_value(self):
        self._test_invalid_value(BIND_TRIALS)
        self._test_invalid_value(CUMULATIVE)

    def _test_invalid_value(self, name):
        text = '''
        {}: galopp
        '''.format(name)
        msg = "Error on line 2: Parameter '{}' must be 'on' or 'off'.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)
