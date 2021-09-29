from .testutil import LsTestCase
from keywords import TITLE, SUBPLOTTITLE
from parsing import Script

prop_names = (TITLE, SUBPLOTTITLE)


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
        for name in prop_names:
            self._test_simple(name)

    def _test_simple(self, name):
        text = '''
        {}: Hello
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'Hello')

        text = '''
        {}: Hello world!
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'Hello world!')

        text = '''
        {}  :  Hello
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'Hello')

        text = '''
        {}:Hello world!
        '''.format(name)
        x = parse(text, name)
        self.assertEqual(x, 'Hello world!')

    def test_redefinition(self):
        for name in prop_names:
            self._test_redefinition(name)

    def _test_redefinition(self, name):
        text = '''
        {}: Hello world!
        {}: New x  with  spaces...
        '''.format(name, name)
        x = parse(text, name)
        self.assertEqual(x, 'New x  with  spaces...')

        text = '''
        {}: Hello world!
        {}: New x  with  space,
        '''.format(name, name)
        x = parse(text, name)
        self.assertEqual(x, 'New x  with  space,')

        text = '''
        {}: Hello world!
        {}: New x  with  spaces,,,
        '''.format(name, name)
        x = parse(text, name)
        self.assertEqual(x, 'New x  with  spaces,,,')


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_empty_name(self):
        for name in prop_names:
            self._test_empty_name(name)

    def _test_empty_name(self, name):
        text = '''
        {}:
        '''.format(name)
        msg = "Error on line 2: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)

    def test_empty_name_no_colon(self):
        for name in prop_names:
            self._test_empty_name_no_colon(name)

    def _test_empty_name_no_colon(self, name):
        text = '''
        {}
        '''.format(name)
        msg = "Error on line 2: Parameter '{}' is not specified.".format(name)
        with self.assertRaisesMsg(msg):
            parse(text, name)
