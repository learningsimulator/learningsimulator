from .testutil import LsTestCase
from parsing import Script
from mechanism import Enquist, RescorlaWagner, ActorCritic, Qlearning, EXP_SARSA
import keywords as kw

# @RUN  phase1,phase2,... [label:lbl]


def parse(text, run_label):
    script = Script(text)
    script.parse()
    script_parser = script.script_parser
    run_obj = script_parser.runs.get(run_label)
    parameters = run_obj.mechanism_obj.parameters
    return run_obj, parameters


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        mechanism: ga
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        '''
        run, parameters = parse(text, 'run1')
        self.assertEqual(run.world.phase_labels, ['phase1'])
        self.assertEqual(run.world.nphases, 1)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, Enquist))
        self.assertTrue(run.has_w)
        self.assertEqual(run.n_subjects, 1)

        # Test scalar expansion
        stimulus_elements = parameters.get(kw.STIMULUS_ELEMENTS)
        behaviors = parameters.get(kw.BEHAVIORS)
        self.assertEqual(len(parameters.get(kw.START_V).keys()), 4)
        self.assertEqual(len(parameters.get(kw.ALPHA_V).keys()), 4)
        self.assertEqual(set(parameters.get(kw.ALPHA_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.START_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.U).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.BEHAVIOR_COST).keys()), behaviors)

    def test_multiphase(self):
        text = '''
        mechanism: ga
        n_subjects: 100
        stimulus_elements: e1, e2,
                           e3
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:False
        X1 e3 | X2
        X2 e3 | X1
        @run phase1 , phase2
        '''
        run, parameters = parse(text, 'run1')
        self.assertEqual(run.world.phase_labels, ['phase1', 'phase2'])
        self.assertEqual(run.world.nphases, 2)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, Enquist))
        self.assertTrue(run.has_w)
        self.assertEqual(run.n_subjects, 100)

        # Test scalar expansion
        stimulus_elements = parameters.get(kw.STIMULUS_ELEMENTS)
        behaviors = parameters.get(kw.BEHAVIORS)
        self.assertEqual(len(parameters.get(kw.START_V).keys()), 6)
        self.assertEqual(len(parameters.get(kw.ALPHA_V).keys()), 6)
        self.assertEqual(set(parameters.get(kw.ALPHA_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.START_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.U).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.BEHAVIOR_COST).keys()), behaviors)

        text = '''
        mechanism: ga
        stimulus_elements: e1, e2,
                           e3
        behaviors: b1,
                   b2, b3
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:False
        X1 e3 | X2
        X2 e3 | X1
        @run phase1
        '''
        run, parameters = parse(text, 'run1')
        self.assertEqual(run.world.phase_labels, ['phase1'])
        self.assertEqual(run.world.nphases, 1)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, Enquist))
        self.assertTrue(run.has_w)
        self.assertEqual(run.n_subjects, 1)

        # Test scalar expansion
        stimulus_elements = parameters.get(kw.STIMULUS_ELEMENTS)
        behaviors = parameters.get(kw.BEHAVIORS)
        self.assertEqual(len(parameters.get(kw.START_V).keys()), 9)
        self.assertEqual(len(parameters.get(kw.ALPHA_V).keys()), 9)
        self.assertEqual(set(parameters.get(kw.ALPHA_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.START_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.U).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.BEHAVIOR_COST).keys()), behaviors)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2,
                           e3
        behaviors: b1,
                   b2, b3
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:False
        X1 e3 | X2
        X2 e3 | X1
        @PHASE phase3 stop:e1=100
        L1 e1 | L1
        @PHASE phase4 stop:e1=100
        L1 e1 | L1
        @run phase4, phase1
        '''
        run, parameters = parse(text, 'run1')
        self.assertEqual(run.world.phase_labels, ['phase4', 'phase1'])
        self.assertEqual(run.world.nphases, 2)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, RescorlaWagner))
        self.assertFalse(run.has_w)
        self.assertEqual(run.n_subjects, 1)

        # Test scalar expansion
        stimulus_elements = parameters.get(kw.STIMULUS_ELEMENTS)
        behaviors = parameters.get(kw.BEHAVIORS)
        self.assertEqual(len(parameters.get(kw.START_V).keys()), 9)
        self.assertEqual(len(parameters.get(kw.ALPHA_V).keys()), 9)
        self.assertEqual(set(parameters.get(kw.ALPHA_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.START_W).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.U).keys()), stimulus_elements)
        self.assertEqual(set(parameters.get(kw.BEHAVIOR_COST).keys()), behaviors)

    def test_multiple_run_with_different_behaviors(self):
        text = '''
        mechanism:   ga
        stimulus_elements: e1, e2
        behaviors: b1, b2
        behavior_cost: b1:1, b2:2

        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1

        @run phase1

        behaviors: x, y, z
        behavior_cost: x:1, y:2, z:3
        @run phase1
        '''
        _, parameters1 = parse(text, 'run1')
        self.assertEqual(parameters1.get(kw.BEHAVIORS), {'b1', 'b2'})
        self.assertEqual(set(parameters1.get(kw.START_V).keys()),
                         {('e1', 'b1'), ('e1', 'b2'), ('e2', 'b1'), ('e2', 'b2')})

        _, parameters2 = parse(text, 'run2')
        self.assertEqual(parameters2.get(kw.BEHAVIORS), {'x', 'y', 'z'})
        self.assertEqual(set(parameters2.get(kw.START_V).keys()),
                         {('e1', 'x'), ('e1', 'y'), ('e1', 'z'),
                          ('e2', 'x'), ('e2', 'y'), ('e2', 'z')})

    def test_mechanisms(self):
        """
        GA = 'ga'
        SR = 'sr'
        ES = 'es'
        QL = 'ql'
        AC = 'ac'
        """
        text = '''
        mechanism: ga
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        '''
        run, _ = parse(text, 'run1')
        self.assertTrue(isinstance(run.mechanism_obj, Enquist))
        self.assertTrue(run.has_w)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        '''
        run, _ = parse(text, 'run1')
        self.assertTrue(isinstance(run.mechanism_obj, RescorlaWagner))
        self.assertFalse(run.has_w)

        text = '''
        mechanism: ac
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        '''
        run, _ = parse(text, 'run1')
        self.assertTrue(isinstance(run.mechanism_obj, ActorCritic))
        self.assertTrue(run.has_w)

        text = '''
        mechanism: ql
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        '''
        run, _ = parse(text, 'run1')
        self.assertTrue(isinstance(run.mechanism_obj, Qlearning))
        self.assertFalse(run.has_w)

        text = '''
        mechanism: es
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1
        '''
        run, _ = parse(text, 'run1')
        self.assertTrue(isinstance(run.mechanism_obj, EXP_SARSA))
        self.assertFalse(run.has_w)

    def test_change_parameters(self):
        text = '''
        mechanism: es
        stimulus_elements: e1, e2
        behaviors: b1, b2

        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase2 stop:e1=10
        L1 e1 | L2
        L2 e2 | L3
        L3 e1 | L1

        beta: 1.1
        @run phase1 label:myrun1

        beta: 2.2
        n_subjects: 2
        @run phase1,phase2 label:myrun2
        '''
        run1, parameters1 = parse(text, 'myrun1')
        self.assertEqual(set(run1.world.phase_labels), {'phase1'})
        self.assertEqual(run1.world.nphases, 1)
        self.assertEqual(run1.world.curr_phaseind, 0)
        self.assertEqual(run1.n_subjects, 1)
        self.assertEqual(parameters1.get(kw.BETA), 1.1)
        self.assertEqual(parameters1.get(kw.N_SUBJECTS), 1)

        run2, parameters2 = parse(text, 'myrun2')
        self.assertEqual(set(run2.world.phase_labels), {'phase1', 'phase2'})
        self.assertEqual(run2.world.nphases, 2)
        self.assertEqual(run2.world.curr_phaseind, 0)
        self.assertEqual(run2.n_subjects, 2)
        self.assertEqual(parameters2.get(kw.BETA), 2.2)
        self.assertEqual(parameters2.get(kw.N_SUBJECTS), 2)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_no_phases_nor_label(self):
        text = '''
        @run
        '''
        msg = "@RUN line must have the form '@RUN phases \[label:runlabel\]."
        with self.assertRaisesX(Exception, msg):
            run, parameters = parse(text, '_')

    def test_redefinition_of_phase(self):
        text = '''
        mechanism: sr
        stimulus_elements: e1, e2,
                           e3
        behaviors: b1,
                   b2, b3
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:False
        X1 e3 | X2
        X2 e3 | X1
        @PHASE phase3 stop:e1=100
        L1 e1 | L1
        @PHASE phase3 stop:e1=100
        L1 e1 | L1
        @run phase4, phase1
        '''
        msg = "Redefinition of phase 'phase3'."
        with self.assertRaisesX(Exception, msg):
            run, parameters = parse(text, 'run1')

    def test_undefined_phase_label(self):
        text = '''
        mechanism: ac
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run foo label:run1
        '''
        msg = "Phase foo undefined."
        with self.assertRaisesX(Exception, msg):
            parse(text, 'run1')

    def test_empty_mechanism_name(self):
        text = '''
        mechanism:
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1 label:run1
        '''
        msg = "Parameter 'mechanism' is not specified."
        with self.assertRaisesX(Exception, msg):
            run, parameters = parse(text, 'run1')

    def test_duplicated_run_label(self):
        text = '''
        mechanism:  sr
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1 label:mylabel
        @run phase2 label:    mylabel
        '''
        msg = "Duplication of run label 'mylabel'."
        with self.assertRaisesX(Exception, msg):
            run, parameters = parse(text, 'run1')

    def test_multiple_labels(self):
        text = '''
        mechanism:   ga
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1 label:run1
        @run phase2 label:run1 label:run2
        '''
        msg = "Maximum one instance of 'label:' on a @run line."
        with self.assertRaisesX(Exception, msg):
            run, parameters = parse(text, 'run1')

    def test_redefine_stimulus_elements_or_behaviors(self):
        text = '''
        mechanism:   ga
        stimulus_elements: e1, e2
        behaviors: b1, b2
        behavior_cost: b1:1, b2:2
        behaviors: x, y, z

        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1

        @run phase1
        '''
        msg = "The parameter 'behavior_cost' does not match 'behaviors'."
        with self.assertRaisesX(Exception, msg):
            run, parameters = parse(text, 'run1')
