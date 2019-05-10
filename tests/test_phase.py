import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data
from parsing import Script


def parse(text, phase_label):
    script = Script(text)
    script.parse()
    script_parser = script.script_parser
    phase_obj = script_parser.phases.phases[phase_label]
    if not phase_obj.is_parsed:
        phase_obj.parse(script_parser.parameters, script_parser.variables)
    return phase_obj


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for i in range(1, 19):
            stimulus, _, _ = phase.next_stimulus('b2')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',))
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

    def test_first_line(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e1=10
        L2           e2 | new_trial
        new_trial   e1 | L2
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for i in range(1, 19):
            stimulus, _, _ = phase.next_stimulus('b1')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',), f"{i}")
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

    def test_variables(self):
        text = '''
        @variables nsteps: 10
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e1=nsteps
        L2           e2 | new_trial
        new_trial   e1 | L2
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for i in range(1, 19):
            stimulus, _, _ = phase.next_stimulus('b1')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',), f"{i}")
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

        text = '''
        @variables n:5
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:local_var=n
        L0 local_var:0           | L1
        L1 e1                    | L2
        L2 e2                    | H1
        H1 local_var:local_var+1 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for i in range(1, 10):
            stimulus, _, _ = phase.next_stimulus('b2')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',))
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)
        self.assertEqual(phase.local_variables.values['local_var'], 5)

    def test_local_variable_in_stop(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:local_var=5
        L0 local_var:0           | L1
        L1 e1                    | L2
        L2 e2                    | H1
        H1 local_var:local_var+1 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e1',))
        for i in range(1, 10):
            stimulus, _, _ = phase.next_stimulus('b2')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',))
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)
        self.assertEqual(phase.local_variables.values['local_var'], 5)

        # Default 0 for local_var
        text = '''
        stimulus_elements: e1, e2, par1, par2
        behaviors: b1, b2

        # Squeeze in a little test of inheritance
        @PHASE parent stop:local_var2=5
        L0 local_var2:9            | L2
        L1 par1                    | L1
        L2 par2,par1               | L1
        H1 local_var2:local_var2+1 | H1

        @PHASE phase_label(parent) stop:local_var=5
        L0                       | L1
        L1 e1                    | L2
        L2 e2                    | H1
        H1 local_var:local_var+1 | L1

        beta: 1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for i in range(1, 10):
            stimulus, _, _ = phase.next_stimulus('b2')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',))
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)
        self.assertEqual(phase.local_variables.values['local_var'], 5)

    def test_line_label_in_stop(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:L1=10
        L1 e1               | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for _ in range(1, 10):
            stimulus, _, _ = phase.next_stimulus('b1')
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)


class TestInheritance(LsTestCase):
    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE bar(foo) stop:e1=3
        L2 e3 | L1

        xscale: all  # Just to finish the parsing of bar
        '''
        phase = parse(text, 'bar')

        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE bar(foo) stop:e3=3
        L1 e3 | L2

        xscale: all  # Just to finish the parsing of bar
        '''
        phase = parse(text, 'bar')

        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

    def test_multiple_space(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE     bar(foo)     stop   :    e3 =     3
        L1 e3 | L2

        xscale: all  # Just to finish the parsing of bar
        '''
        phase = parse(text, 'bar')

        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e3',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

    def test_wrong_parent_name(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE bar(foofel) stop:e1=3
        L2 e3 | L1

        xscale: all  # Just to finish the parsing of bar
        '''
        msg = "Invalid phase label 'foofel'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'bar')

    def test_wrong_child_name(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE foo(foo) stop:e1=3
        L2 e3 | L1

        xscale: all  # Just to finish the parsing of bar
        '''
        msg = "Redefinition of phase 'foo'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'bar')

    def test_wrong_syntax(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE bar (foo) stop:e1=3
        L2 e3 | L1

        xscale: all  # Just to finish the parsing of bar
        '''
        msg = "Phase stop condition must have the form 'stop:condition'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'bar')

    def test_wrong_parentheses1(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE bar((foo)) stop:e1=3
        L2 e3 | L1

        xscale: all  # Just to finish the parsing of bar
        '''
        msg = "Invalid phase label '\(foo\)'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'bar')

    def test_wrong_parentheses2(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE bar(foo)baz stop:e1=3
        L2 e3 | L1

        xscale: all  # Just to finish the parsing of bar
        '''
        msg = "Phase label 'bar\(foo\)baz' is not a valid identifier."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'bar')

    def test_wrong_parentheses3(self):
        text = '''
        stimulus_elements: e1, e2, e3
        behaviors: b1, b2
        @PHASE foo stop:L1=5
        L1 e1 | L2
        L2 e2 | L1

        @PHASE barbazfoo) stop:e1=3
        L2 e3 | L1

        xscale: all  # Just to finish the parsing of bar
        '''
        msg = "Phase label 'barbazfoo\)' is not a valid identifier."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'bar')


class TestHelpLine(LsTestCase):
    def setUp(self):
        pass

    def test_no_action(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e1=10
        L1 e1 | H1
        H1    | L2
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for i in range(1, 19):
            stimulus, _, _ = phase.next_stimulus('b1')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',))
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e1=10
        L1 e1 | H1
        H1    | H2
        H2    | L2
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for i in range(1, 19):
            stimulus, _, _ = phase.next_stimulus('b1')
            if i % 2 == 0:
                self.assertEqual(stimulus, ('e1',))
            else:
                self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

    def test_ignore_response_increment(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:b1=5
        L1 e1 | H1
        H1    | L2
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)  # First stimulus
        self.assertEqual(stimulus, ('e1',))

        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNotNone(stimulus)  # Now count(b1) is 6

        # With two consecutive help lines
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:b1=5
        L1 e1  | H1
        H1     | H2
        H2 x:0 | L2
        L2 e2  | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)  # First stimulus
        self.assertEqual(stimulus, ('e1',))

        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNotNone(stimulus)  # Now count(b1) is 6

        # With two consecutive help lines
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:b1=5
        L1 e1  | H1
        H1     | H2
        H2 x:0 | L2
        L2 e2  | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)  # First stimulus
        self.assertEqual(stimulus, ('e1',))

        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNotNone(stimulus)  # Now count(b1) is 6

    def test_count_in_logic(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e2=1
        L1 e1 | count(e1)=5 : L3 | L2
        L2 e1 | L1
        L3 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)  # First stimulus
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

    def test_count_reset(self):
        # Reset a stimulus element
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e2=3
        L1 e1              | count(e1)=5 : H | L2
        L2 e1              | L1
        H  count_reset(e1) | L3
        L3 e2              | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        for _ in range(1, 5):
            stimulus, _, _ = phase.next_stimulus('b1')
            self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

        for _ in range(5):
            stimulus, _, _ = phase.next_stimulus('b1')
            self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

        for _ in range(5):
            stimulus, _, _ = phase.next_stimulus('b1')
            self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

        # Reset a behavior
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:False  # Never stop
        L1 e1              | count(b1)>=5 : H | L2
        L2 e1              | L1
        H  count_reset(b1) | L3
        L3 e2              | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)  # First stimulus
        self.assertEqual(stimulus, ('e1',))
        for i in range(2, 100):
            stimulus, _, _ = phase.next_stimulus('b1')
            if i % 6 == 0:
                self.assertEqual(stimulus, ('e2',))
            else:
                self.assertEqual(stimulus, ('e1',))

        # Reset a line label
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:L1=10  # L1 will never be 10
        L1 e1              | L1=5:H | L1
        H  count_reset(L1) | L2
        L2 e2              | L1
        '''
        phase = parse(text, 'phase_label')
        first = True
        for _ in range(1, 10):
            for i in range(5):
                if first:
                    stimulus, _, _ = phase.next_stimulus(None)
                    first = False
                else:
                    stimulus, _, _ = phase.next_stimulus('b1')
                self.assertEqual(stimulus, ('e1',))
            stimulus, _, _ = phase.next_stimulus('b1')
            self.assertEqual(stimulus, ('e2',))

        # Reset a line label
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:XH=10
        XL1 e1               | count(XL1)=5 : XH | XL2
        XL2 e1               | XL1
        XH  count_reset(XL1) | XL3
        XL3 e2               | XL1
        '''
        phase = parse(text, 'phase_label')
        first = True
        for i in range(1, 100):
            if first:
                stimulus, _, _ = phase.next_stimulus(None)
            else:
                stimulus, _, _ = phase.next_stimulus('b1')
            if i % 10 == 0:
                self.assertEqual(stimulus, ('e2',))
            else:
                self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)

    def test_count_line(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e2=5
        L1 e1 | count_line(b1)=3 : L2 | L1
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e1',))
        for _ in range(42):
            stimulus, _, _ = phase.next_stimulus('b2')
            self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        for _ in range(42):
            stimulus, _, _ = phase.next_stimulus('b2')
            self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

        # Test same thing but with b1=3 instead of count_line(b1)=3
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e2=5
        L1 e1 | b1=3 : L2 | L1
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e1',))
        for _ in range(42):
            stimulus, _, _ = phase.next_stimulus('b2')
            self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        for _ in range(42):
            stimulus, _, _ = phase.next_stimulus('b2')
            self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

    def test_count_line_noarg(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e2=5
        L1 e1 | count_line()=3 : L2 | L1
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e2=2
        L1 e1 | count_line(L1)=3 : L2 | L1
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e1',))
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertIsNone(stimulus)


class TestWithPlots(LsTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_stopcond_stimulus(self):
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b

        @phase phase1 stop:s=2
        NT s | NT

        @run phase1

        @nplot s
        '''
        run(text)
        plot_data = get_plot_data()
        ns = plot_data
        self.assertEqual(ns['x'], [0, 1, 2, 3, 4])
        self.assertEqual(ns['y'], [0, 1, 1, 2, 2])

    def test_stopcond_phase_line_label(self):
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b

        @phase phase1 stop:NT=2
        NT s | NT

        @run phase1

        @nplot s
        '''
        run(text)
        plot_data = get_plot_data()
        ns = plot_data
        self.assertEqual(ns['x'], [0, 1, 2, 3, 4])
        self.assertEqual(ns['y'], [0, 1, 1, 2, 2])

    def test_stopcond_stimulus_with_xscale(self):
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b

        @phase phase1 stop:s=2
        NT s | NT

        @run phase1

        xscale: s
        @nplot s
        '''
        run(text)
        plot_data = get_plot_data()
        ns = plot_data
        self.assertEqual(ns['x'], [0, 1, 2])
        self.assertEqual(ns['y'], [0, 1, 2])

    def test_stopcond_stimulus_with_phases(self):
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b

        @phase phase1 stop:s=2
        NT s | NT

        @phase phase2 stop:s=2
        NT s | NT

        @run phase1, phase2

        phases: phase2
        @nplot s
        '''
        run(text)
        plot_data = get_plot_data()
        ns = plot_data
        self.assertEqual(ns['x'], [0, 1, 2, 3, 4])
        self.assertEqual(ns['y'], [0, 1, 1, 2, 2])

    def test_stopcond_phase_line_label_with_xscale(self):
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b

        @phase phase1 stop:NT=2
        NT s | NT

        @run phase1

        xscale: NT
        @nplot s
        '''
        msg = "xscale cannot be a phase line label in @nplot/@nexport."
        with self.assertRaisesX(Exception, msg):
            run(text)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_no_label(self):
        text = '''
        @PHASE
        '''
        msg = "@PHASE line must have the form '@PHASE label stop:condition'."
        with self.assertRaisesX(Exception, msg):
            parse(text, '_')

    def test_wrong_stopcond(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e11=10
        L1 e1 | L2
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        msg = "Unknown variable 'e11'."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus(None)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e1
        L1 e1 | L2
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        msg = "Condition 'e1' is not a boolean expression."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus(None)

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:count(b1)=5
        L1 e1 | H1
        H1    | L2
        L2 e2 | L1
        '''
        phase = parse(text, 'phase_label')
        msg = "Unknown variable 'count'."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus(None)

    def test_no_stopcond(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label
        L1 e1 | L2
        L2 e2 | L1
        '''
        msg = "@PHASE line must have the form '@PHASE label stop:condition'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

    def test_empty_stopcond(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:
        L1 e1 | L2
        L2 e2 | L1
        '''
        msg = "Phase stop condition must have the form 'stop:condition'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label blaps
        L1 e1 | L2
        L2 e2 | L1
        '''
        msg = "Phase stop condition must have the form 'stop:condition'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stopp:e1=10
        L1 e1 | L2
        L2 e2 | L1
        '''
        msg = "Phase stop condition must have the form 'stop:condition'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

    def test_help_line_with_response(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e1=10
        L1 e1 | H
        H     | b1:L1 | L1
        '''
        msg = "Condition on help line cannot depend on response."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

    def test_modify_global_variable(self):
        text = '''
        @variables var1:1, var2:2*var1+1
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:count(H1)=10
        L1 e1          | H1
        H1 var1:var1+1 | L2
        L2 e2          | L1
        '''
        msg = "Cannot modify global variable inside a phase."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

    def test_unknown_local_variable(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:local_var=5
        L0 local_var:y           | L1
        L1 e1                    | L2
        L2 e2                    | H1
        H1 local_var:local_var+1 | L1
        '''
        phase = parse(text, 'phase_label')
        msg = "Unknown variable 'y'."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus(None)

    def test_syntax_error_in_expression(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:local_var=5
        L0 local_var: 1+/1       | L1
        L1 e1                    | L2
        L2 e2                    | H1
        H1 local_var:local_var+1 | L1
        '''
        phase = parse(text, 'phase_label')
        msg = "Error in expression '1\+/1': invalid syntax."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus(None)

    def test_cannot_evaluate_expression(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:local_var=5
        L0 local_var: rand(1,)   | L1
        L1 e1                    | L2
        L2 e2                    | H1
        H1 local_var:local_var+1 | L1
        '''
        phase = parse(text, 'phase_label')
        msg = "Cannot evaluate expression 'rand\(1,\)': rand\(\) missing 1 required positional argument: 'stop'."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus(None)

    def test_eval_output_not_number(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:local_var=5
        L0 local_var:'foo'       | L1
        L1 e1                    | L2
        L2 e2                    | H1
        H1 local_var:local_var+1 | L1
        '''
        phase = parse(text, 'phase_label')
        msg = "Error in expression ''foo''."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus(None)

    def test_invalid_count_reset(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:e2=3
        L1 e1               | count(e1)=5 : H | L2
        L2 e1               | L1
        H  count_reset(e1X) | L3
        L3 e2               | L1
        '''
        msg = "Unknown event 'e1X' in count_reset."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

    def test_invalid_line_label_in_logic(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase_label stop:False  # Never stop
        XL1 e1              | count(b1)>=5 : H | L2
        XL2 e1              | L1
        XH  count_reset(b1) | L3
        XL3 e2              | L1
        '''
        msg = "Invalid line label 'H'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'phase_label')

    def test_phase_line_contains_only_label(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE thelabel stop:foo
        XL1 e1              | count(b1)>=5 : H | L2
        XL2
        XH  count_reset(b1) | L3
        XL3 e2              | L1
        '''
        msg = "Phase line contains only label."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_phase_line_label_is_stimulus(self):
        text = '''
        stimulus_elements: e1, e2, FOO
        behaviors: b1, b2
        @PHASE thelabel stop:False
        FOO e1             | count(b1)>=5 : H | L2
        b1  e1
        H  count_reset(b1) | L3
        L3 e2              | L1
        '''
        msg = "The phase line label 'FOO' coincides with the name of a stimulus element."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_phase_line_label_is_behavior(self):
        text = '''
        stimulus_elements: e1, e2, FOO
        behaviors: b1, b2, BAR
        @PHASE thelabel stop:False
        L1  e1              | count(b1)>=5 : H | b1
        b1  e1              | L1
        BAR count_reset(b1) | L3
        L3  e2              | L1
        '''
        msg = "The phase line label 'b1' coincides with the name of a behavior."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_duplicate_phase_line_label(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e1              | H
        H   e1              | L1
        BAR count_reset(b1) | H
        L1  e2              | L1
        '''
        msg = "Duplicate of phase line label 'L1'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_not_parsed(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e1              | H
        H   e1              | L1
        BAR count_reset(b1) | H
        L1  e2              | L1
        '''
        script = Script(text)
        script.parse()
        script_parser = script.script_parser
        phase_obj = script_parser.phases.phases['thelabel']
        with self.assertRaises(Exception):
            phase_obj.next_stimulus(None)

    def test_missing_separator(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e1 | L2
        L2  e2
        '''
        msg = "Missing separator '|' on phase line."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_unknown_stimulus_element_or_action(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e11 | L2
        L2  e2  | L1
        '''
        msg = "Unknown stimulus element or action 'e11'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  coun_reset(e1) | L2
        L2  e2             | L1
        '''
        msg = "Unknown stimulus element or action 'coun_reset\(e1\)'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_invalid_stimulus_element(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e1,e11 | L2
        L2  e2     | L1
        '''
        msg = "Expected a stimulus element, got 'e11'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_no_conditions(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e1   | L2
        L2  e2   |
        '''
        msg = "Line with label 'L2' has no conditions."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_unknown_event_in_count_reset(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e1                 | L2
        L2  count_reset(foo)   |
        '''
        msg = "Unknown event 'foo' in count_reset."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_no_condition_met(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop:e1==10
        L1  e1                 | b3=7:L2 | b2=42:L2
        L2  e2                 | L1
        '''
        phase = parse(text, 'thelabel')
        stimulus, _, _ = phase.next_stimulus(None)
        self.assertEqual(stimulus, ('e1',))
        msg = "No condition in 'b3\=7\:L2 \| b2\=42\:L2' was met for response 'b1'."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus('b1')

        text = """
        mechanism: ga
        stimulus_elements : lever1, lever2, lever3, reward
        behaviors : R

        @phase vi stop: reward=25000
        FI3 lever1       | count_line()=3:ON     | FI3
        FI2 lever2       | count_line()=2:ON     | FI2
        ON  lever3       | R:REWARD | ON
        REWARD  reward   | ON(1/6),FI2(1/6),FI3(1/6)

        @run vi
        """
        phase = parse(text, 'vi')
        stimulus, _, _ = phase.next_stimulus(None)
        msg = "No condition in 'ON\(1/6\),FI2\(1/6\),FI3\(1/6\)' was met for response 'R'."
        with self.assertRaisesX(Exception, msg):
            for _ in range(100):
                phase.next_stimulus('R')

    def test_prob_greater_than_1(self):
        text = """
        mechanism: ga
        stimulus_elements : lever1, lever2, lever3, reward
        behaviors : R

        @phase vi stop: reward=25000
        FI3 lever1       | count_line()=3:ON     | FI3
        FI2 lever2       | count_line()=2:ON     | FI2
        ON  lever3       | R:REWARD | ON
        REWARD  reward   | ON(1/2),FI2(1/2),FI3(1/2)

        @run vi
        """
        msg = "Invalid condition 'ON\(1/2\),FI2\(1/2\),FI3\(1/2\)'. Sum of probabilities is 1.5>1."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'vi')

    def test_condition_has_more_than_one_colon(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==1
        L1  e1  | b3=1 :: L2 | L1
        L2  e2  | L1
        '''
        msg = "Error on line 5: Condition b3=1 :: L2 has more than one colon."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_condition_not_boolean(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | 42:L2 | L1
        L2  e2  | L1
        '''
        phase = parse(text, 'thelabel')
        phase.next_stimulus(None)
        msg = "Condition '42' is not a boolean expression."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus('b3')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | e1:L2 | L1
        L2  e2  | L1
        '''
        phase = parse(text, 'thelabel')
        phase.next_stimulus(None)
        msg = "Condition 'e1' is not a boolean expression."
        with self.assertRaisesX(Exception, msg):
            phase.next_stimulus('b3')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | b1:L2 | L1
        L2  e2  | L1
        '''
        phase = parse(text, 'thelabel')
        phase.next_stimulus(None)
        stimulus, _, _ = phase.next_stimulus('b1')
        self.assertEqual(stimulus, ('e2',))

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | b1:L2 | L1
        L2  e2  | L1
        '''
        phase = parse(text, 'thelabel')
        phase.next_stimulus(None)
        stimulus, _, _ = phase.next_stimulus('b2')
        self.assertEqual(stimulus, ('e1',))

    def test_invalid_condition(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2,L1 | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2,L1'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2(0.5),L1 | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2\(0.5\),L1'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2((0.5)),L1(0.1) | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2\(\(0.5\)\),L1\(0.1\)'. Too many parentheses."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2)0.5(,L1(0.1) | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2\)0.5\(,L1\(0.1\)'. Mismatched parentheses."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2(0.5), LL1(0.1) | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2\(0.5\), LL1\(0.1\)'. Unknown line label 'LL1'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2(0.5), L1(1.1) | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2\(0.5\), L1\(1.1\)'. Expected a probability, got '1.1'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2(0.2),L1(-0.9) | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2\(0.2\),L1\(-0.9\)'. Expected a probability, got '-0.9'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2(0.5),L1(0.2),L2(0.01) | L1
        L2  e2  | L1
        L3  e1  | L2
        '''
        msg = "Invalid condition 'L2\(0.5\),L1\(0.2\),L2\(0.01\)'. Label 'L2' duplicated."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L22 | L1
        L2  e2  | L1
        '''
        msg = "Invalid line label 'L22'."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE thelabel stop : e1==4
        L1  e1  | L2(0.2),L1(0.9) | L1
        L2  e2  | L1
        '''
        msg = "Invalid condition 'L2\(0.2\),L1\(0.9\)'. Sum of probabilities is 1.1>1."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')

    def test_invalid_phase_label(self):
        text = '''
        stimulus_elements: e1, e2
        behaviors: b1, b2, b3
        @PHASE 123thelabel stop : e1==4
        L1  e1  | L2(0.2),L1(0.9) | L1
        L2  e2  | L1
        '''
        msg = "Phase label '123thelabel' is not a valid identifier."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'thelabel')
