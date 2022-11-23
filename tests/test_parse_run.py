import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data
from parsing import Script
from mechanism import Enquist, StimulusResponse, ActorCritic, Qlearning, EXP_SARSA
import keywords as kw

# @RUN  phase1,phase2,... [runlabel:lbl]


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
        self.assertEqual(run.world.nphases, 2)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, StimulusResponse))
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

    def test_multiphase_with_one_phase_per_line(self):
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
        @run phase1
             phase2
        '''
        run, parameters = parse(text, 'run1')
        self.assertEqual(run.world.nphases, 2)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, Enquist))
        self.assertTrue(run.has_w)
        self.assertEqual(run.n_subjects, 100)

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
        @run phase4
             phase1
        '''
        run, parameters = parse(text, 'run1')
        self.assertEqual(run.world.nphases, 2)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, StimulusResponse))
        self.assertFalse(run.has_w)
        self.assertEqual(run.n_subjects, 1)

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
        @run myrunlbl phase1
                      phase2
                      phase1
                      phase2
        '''
        run, parameters = parse(text, 'myrunlbl')
        self.assertEqual(run.world.nphases, 4)
        self.assertEqual(run.world.curr_phaseind, 0)
        self.assertTrue(isinstance(run.mechanism_obj, Enquist))
        self.assertTrue(run.has_w)
        self.assertEqual(run.n_subjects, 100)

        text = '''
        mechanism: ga
        n_subjects: 100
        stimulus_elements: e1, e2,
                           e3, e4, e5, e6, e7,
                           e8
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:e3=20
        X1 e3 | X2
        X2 e4 | X1
        @PHASE phase3 stop:e5=30
        L1 e5 | L2
        L2 e6 | L1
        @PHASE phase4 stop:e7=40
        L1 e7 | L2
        L2 e8 | L1

        @run myrunlbl1 phase1
                      phase2
                      phase3,
                      phase4

        @run           phase1,
                       phase4           runlabel:myrunlbl2

        @run myrunlbl3 phase1, phase2
        phase3,
        phase4

        @run
        phase1
        phase1
        phase1
        phase2         runlabel:myrunlbl4
        phase3,
        phase4     ,

        n_subjects = 42
        '''
        run, parameters = parse(text, 'myrunlbl1')
        self.assertEqual(run.world.nphases, 4)
        self.assertEqual(run.n_subjects, 100)

        run, parameters = parse(text, 'myrunlbl2')
        self.assertEqual(run.world.nphases, 2)
        self.assertEqual(run.n_subjects, 100)

        run, parameters = parse(text, 'myrunlbl3')
        self.assertEqual(run.world.nphases, 4)
        self.assertEqual(run.n_subjects, 100)

        run, parameters = parse(text, 'myrunlbl4')
        self.assertEqual(run.world.nphases, 6)
        self.assertEqual(run.n_subjects, 100)
        self.assertEqual(parameters.get(kw.N_SUBJECTS), 100)

    def test_multiphase_with_one_phase_per_line_with_run(self):
        text = '''
        mechanism: ga
        n_subjects: 1
        stimulus_elements: e1, e2,
                           e3, e4, e5
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @PHASE phase2 stop:e1=20
        X1 e1 | X2
        X2 e3 | X1
        @PHASE phase3 stop:e1=30
        L1 e1 | L2
        L2 e4 | L1
        @PHASE phase4 stop:e1=40
        L1 e1 | L2
        L2 e5 | L1

        @run myrunlbl1 phase1
                       phase2
                       phase3,
                       phase4

        @run   phase1,
               phase4           runlabel:myrunlbl2

        @run myrunlbl3 phase1, phase2
                       phase3,
                       phase4, phase4

        @run myrunlbl4
        phase1
        phase1, phase1
        phase1
        phase3,
        phase4     ,

        xscale = e1
        @figure 1
        runlabel = myrunlbl1
        @nplot e1

        @figure 2
        runlabel = myrunlbl2
        @nplot e1

        @figure 3
        runlabel = myrunlbl3
        @nplot e1

        @figure 4
        runlabel = myrunlbl4
        @nplot e1
        '''
        run(text)

        # Figure 1
        plot_data = get_plot_data(1)
        self.assertEqual(plot_data['x'], list(range(100)))
        self.assertEqual(plot_data['y'], list(range(100)))

        # Figure 2
        plot_data = get_plot_data(2)
        self.assertEqual(plot_data['x'], list(range(50)))
        self.assertEqual(plot_data['y'], list(range(50)))

        # Figure 3
        plot_data = get_plot_data(3)
        self.assertEqual(plot_data['x'], list(range(140)))
        self.assertEqual(plot_data['y'], list(range(140)))

        # Figure 4
        plot_data = get_plot_data(4)
        self.assertEqual(plot_data['x'], list(range(110)))
        self.assertEqual(plot_data['y'], list(range(110)))


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
        self.assertTrue(isinstance(run.mechanism_obj, StimulusResponse))
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
        @run phase1 runlabel:myrun1

        beta: 2.2
        n_subjects: 2
        @run phase1,phase2 runlabel:myrun2
        '''
        run1, parameters1 = parse(text, 'myrun1')
        self.assertEqual(run1.world.nphases, 1)
        self.assertEqual(run1.world.curr_phaseind, 0)
        self.assertEqual(run1.n_subjects, 1)
        self.assertEqual(parameters1.get(kw.BETA), {('e2', 'b2'): 1.1, ('e2', 'b1'): 1.1, ('e1', 'b2'): 1.1, ('e1', 'b1'): 1.1})
        self.assertEqual(parameters1.get(kw.N_SUBJECTS), 1)

        run2, parameters2 = parse(text, 'myrun2')
        self.assertEqual(run2.world.nphases, 2)
        self.assertEqual(run2.world.curr_phaseind, 0)
        self.assertEqual(run2.n_subjects, 2)
        self.assertEqual(parameters2.get(kw.BETA), {('e1', 'b2'): 2.2, ('e1', 'b1'): 2.2, ('e2', 'b2'): 2.2, ('e2', 'b1'): 2.2})
        self.assertEqual(parameters2.get(kw.N_SUBJECTS), 2)


class TestStopCondInRun(LsTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test1(self):
        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        
        @run phase1
        '''
        _, output1 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
        @PHASE phase1
        L1 e1 | L2
        L2 e2 | L1
        
        @run phase1( stop : e1 = 10 )
        '''
        _, output2 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        
        @PHASE phase2
        L1 e1 | L2
        L2 e2 | L1

        @run phase1
        '''
        _, output3 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        
        @PHASE phase2
        L1 e1 | L2
        L2 e2 | L1

        @run phase1( stop : e1 = 10 )
        '''
        _, output4 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1
        L1 e1 | L2
        L2 e2 | L1
        
        @run runlbl
            phase1( stop : e1 = 10 )
        '''
        _, output5 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1
        L1 e1 | L2
        L2 e2 | L1
        
        @run
            phase1( stop : e1 = 10 )
        '''
        _, output6 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1  stop : e1 == 10
        L1 e1 | L2
        L2 e2 | L1
        
        @run
            phase1
        '''
        _, output7 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1  stop : e1 == 10 and e1 == 10
        L1 e1 | L2
        L2 e2 | L1
        
        @run
            phase1
        '''
        _, output8 = run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1
        L1 e1 | L2
        L2 e2 | L1
        
        @run
            phase1(   stop : e1 == 10 and e1 < 100   )
        '''
        _, output9 = run(text)

        output1_subject = output1.run_outputs['run1'].output_subjects[0]
        output2_subject = output2.run_outputs['run1'].output_subjects[0]
        output3_subject = output3.run_outputs['run1'].output_subjects[0]
        output4_subject = output4.run_outputs['run1'].output_subjects[0]
        output5_subject = output5.run_outputs['runlbl'].output_subjects[0]
        output6_subject = output6.run_outputs['run1'].output_subjects[0]
        output7_subject = output7.run_outputs['run1'].output_subjects[0]
        output8_subject = output8.run_outputs['run1'].output_subjects[0]
        output9_subject = output9.run_outputs['run1'].output_subjects[0]

        self.is_equal_output_subjects(output1_subject, output2_subject)
        self.is_equal_output_subjects(output1_subject, output3_subject)
        self.is_equal_output_subjects(output1_subject, output4_subject)
        self.is_equal_output_subjects(output1_subject, output5_subject)
        self.is_equal_output_subjects(output1_subject, output6_subject)
        self.is_equal_output_subjects(output1_subject, output7_subject)
        self.is_equal_output_subjects(output1_subject, output8_subject)
        self.is_equal_output_subjects(output1_subject, output9_subject)

    def test_exceptions(self):
        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1
        L1 e1 | L2
        L2 e2 | L1

        @run phase1        
        '''
        msg = "Error on line 10: Missing stop condition for phase 'phase1'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop: e1 == 10
        L1 e1 | L2
        L2 e2 | L1

        @run xxx)yyy(
        '''
        msg = "Error on line 10: Invalid parenthesis in phase label with stop condition: xxx)yyy(."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop: e1 == 10
        L1 e1 | L2
        L2 e2 | L1

        @run xxx()
        '''
        msg = "Error on line 10: Empty condition in phase label with stop condition."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop: e1 == 10
        L1 e1 | L2
        L2 e2 | L1

        @run xxx(foo)yyy
        '''
        msg = "Error on line 10: Malformed phase label with stop condition: xxx(foo)yyy."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop: e1 == 10
        L1 e1 | L2
        L2 e2 | L1

        @run (yyy)
        '''
        msg = "Error on line 10: Empty phase label in phase with stop condition: (yyy)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop: e1 == 10
        L1 e1 | L2
        L2 e2 | L1

        @run phase1(stopp : e1 == 10)
        '''
        msg = "Error on line 10: Phase stop condition must have the form 'stop:condition'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1       e1 == 10
        L1 e1 | L2
        L2 e2 | L1

        @run phase1(stopp : e1 == 10)
        '''
        msg = "Error on line 6: Phase stop condition must have the form 'stop:condition'."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_run(self):
        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase2(phase1)
        @PHASE phase3(phase1)

        @run myrunlbl
            phase1(stop: e1=10)
            phase2(stop: e1=20)
            phase3(stop: e1=30)

        runlabel: myrunlbl
        xscale: e1
        @nplot e1
        '''
        run(text)
        plot_data = get_plot_data()
        self.assertEqual(len(plot_data['x']), 60)

        plt.close('all')

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase2 stop: e1==20
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase3
        L1 e1 | L2
        L2 e2 | L1

        @run
            phase1(stop: e1=10)
            phase2
            phase3(stop: e1=30) runlabel:myrunlbl

        runlabel: myrunlbl
        xscale: e1
        @nplot e1
        '''
        run(text)
        plot_data = get_plot_data()
        self.assertEqual(len(plot_data['x']), 60)

        plt.close('all')

        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop: Blablah
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase2 stop: Bliblahbloh
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase3 stop: Bliblahblohbleh
        L1 e1 | L2
        L2 e2 | L1

        @run
            phase1(stop: e1=30), phase2(stop: e1=20)
            phase3(stop: e1=10) runlabel:myrunlbl

        runlabel: myrunlbl
        xscale: e1
        @nplot e1
        '''
        run(text)
        plot_data = get_plot_data()
        self.assertEqual(len(plot_data['x']), 60)

    def test_space_between_phase_names(self):
        text = '''
        mechanism: sr
        stimulus_elements: e1, e2
        behaviors: b
    
        @PHASE phase1 stop: Blablah
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase2 stop: Bliblahbloh
        L1 e1 | L2
        L2 e2 | L1

        @PHASE phase3 stop: Bliblahblohbleh
        L1 e1 | L2
        L2 e2 | L1

        @run
            phase1(stop: e1=30) phase2( stop : e1 = 20)
            phase3(stop: e1=10) runlabel:myrunlbl

        runlabel: myrunlbl
        xscale: e1
        @nplot e1
        '''
        run(text)
        plot_data = get_plot_data()
        self.assertEqual(len(plot_data['x']), 60)

    def is_equal_output_subjects(self, output1_subject, output2_subject):
        self.assertEqual(output1_subject.history, output2_subject.history)
        self.assertEqual(output1_subject.first_step_phase, output2_subject.first_step_phase)
        self.assertEqual(output1_subject.phase_line_labels, output2_subject.phase_line_labels)
        self.assertEqual(output1_subject.phase_line_labels_steps, output2_subject.phase_line_labels_steps)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_no_phases_nor_label(self):
        text = '''
        @run
        '''
        msg = "Error on line 2: Parameter 'mechanism' is not specified."
        with self.assertRaisesMsg(msg):
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
        msg = "Error on line 15: Redefinition of phase 'phase3'."
        with self.assertRaisesMsg(msg):
            run, parameters = parse(text, 'run1')

    def test_undefined_phase_label(self):
        text = '''
        mechanism: ac
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1, foo runlabel:run1
        '''
        msg = "Error on line 8: Phase foo undefined."
        with self.assertRaisesMsg(msg):
            parse(text, 'run1')

        text = '''
        mechanism: ac
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run foo runlabel:myrun1
        '''
        msg = "Error on line 8: Duplicate run labels foo and myrun1 on a @run line."
        with self.assertRaisesMsg(msg):
            parse(text, 'myrun1')

        text = '''
        mechanism: ac
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1 runlabel:myrun1    runlabel: myrun42
        '''
        msg = "Error on line 8: Maximum one instance of 'runlabel:' on a @run line."
        with self.assertRaisesMsg(msg):
            parse(text, 'myrun1')

        text = '''
        mechanism: ac
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run foo runlabel:myrun1    runlabel: myrun42
        '''
        msg = "Error on line 8: Maximum one instance of 'runlabel:' on a @run line."
        with self.assertRaisesMsg(msg):
            parse(text, 'myrun1')

    def test_empty_mechanism_name(self):
        text = '''
        mechanism:
        stimulus_elements: e1, e2
        behaviors: b1, b2
        @PHASE phase1 stop:e1=10
        L1 e1 | L2
        L2 e2 | L1
        @run phase1 runlabel:run1
        '''
        msg = "Error on line 2: Parameter 'mechanism' is not specified."
        with self.assertRaisesMsg(msg):
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
        @run phase1 runlabel:mylabel
        @run phase2 runlabel:    mylabel
        '''
        msg = "Error on line 12: Duplication of run label 'mylabel'."
        with self.assertRaisesMsg(msg):
            run, parameters = parse(text, 'run1')

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

        @run phase1 runlabel:mylabel
        @run 
        phase1
        phase1 runlabel:mylabel
        phase1
        phase2 
        '''
        msg = "Error on line 17: Duplication of run label 'mylabel'."
        with self.assertRaisesMsg(msg):
            run, parameters = parse(text, 'run1')

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

        @run phase1 runlabel:mylabel
        @run phase2 runlabel:mylabel
        phase1
        phase1 
        phase1
        phase2 
        '''
        msg = "Error on line 15: Duplication of run label 'mylabel'."
        with self.assertRaisesMsg(msg):
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
        @run phase1 runlabel:run1
        @run phase2 runlabel:run1 runlabel:run2
        '''
        msg = "Error on line 12: Maximum one instance of 'runlabel:' on a @run line."
        with self.assertRaisesMsg(msg):
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
        with self.assertRaisesMsg(msg):
            run, parameters = parse(text, 'run1')
