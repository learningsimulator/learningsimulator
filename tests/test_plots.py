import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestInitialValues(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_initial_v(self):
        # Test vplot
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1 -> b:7, default:1.5
        @phase foo stop:s1=3
        L1 s1 | L1
        @run foo
        @vplot s1 -> b
        @vplot s2->b
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 2)
        plot_data = get_plot_data()
        s1b = plot_data['v(s1 -> b)']
        s2b = plot_data['v(s2->b)']
        self.assertEqual(s1b['x'], [0, 1, 2])
        self.assertEqual(s2b['x'], [0, 1, 2])
        self.assertEqual(s1b['y'][0], 7)
        self.assertEqual(s2b['y'][0], 1.5)

        # Test pplot
        self.tearDown()
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1, b2
        u: s2:1, default:0
        start_v: s1->b1:0.5, default:0

        @phase foo stop:s1=10
        nju_trial s1 | b1:S2 | @omit_learn, nju_trial
        S2        s2 | @omit_learn, nju_trial

        @run foo

        @figure
        @subplot 111 - {'ylim':[-0.1, 1.1]}
        @vplot s1->b1
        @pplot s1->  b1
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 4)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['v(s1->b1)']['y'][0], 0.5)
        self.assertGreater(plot_data['p(s1->  b1)']['y'][0], 0.622)
        self.assertLess(plot_data['p(s1->  b1)']['y'][0], 0.623)

        # Test pplot with default start_v
        self.tearDown()
        text = '''
        #n_subjects: 1
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1, b2
        u: s2:1, default:0
        start_v: default:0

        @phase foo stop:s1=100
        nju_trial s1 | b1:S2 | @omit_learn, nju_trial
        S2        s2 | @omit_learn, nju_trial

        @run foo

        @figure
        xscale:s1
        @vplot s1->b1
        @pplot s1->b1
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 3)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['v(s1->b1)']['y'][0], 0)
        self.assertEqual(plot_data['p(s1->b1)']['y'][0], 0.5)

        self.assertEqual(len(plot_data['p(s1->b1)']['x']), 100)
        self.assertEqual(len(plot_data['p(s1->b1)']['y']), 100)

        self.assertLess(plot_data['v(s1->b1)']['y'][99], 1.001)
        self.assertGreater(plot_data['v(s1->b1)']['y'][99], 0.999)
        self.assertLess(plot_data['p(s1->b1)']['y'][99], 0.8)
        self.assertGreater(plot_data['p(s1->b1)']['y'][99], 0.6)

        # Same as above but without @omit_learn
        self.tearDown()
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1, b2
        u: s2:1, default:0
        bind_trials: off
        start_v: default:0

        @phase foo stop:s1=100
        nju_trial s1 | b1:S2 | nju_trial
        S2        s2 | nju_trial

        @run foo

        @figure
        xscale = s1
        @vplot s1->b1
        @pplot s1->b1
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 3)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['v(s1->b1)']['y'][0], 0)
        self.assertEqual(plot_data['p(s1->b1)']['y'][0], 0.5)

        self.assertEqual(len(plot_data['p(s1->b1)']['x']), 100)
        self.assertEqual(len(plot_data['p(s1->b1)']['y']), 100)

        self.assertGreater(plot_data['v(s1->b1)']['y'][99], 80)
        self.assertLess(plot_data['p(s1->b1)']['y'][99], 1.01)
        self.assertGreater(plot_data['p(s1->b1)']['y'][99], 0.99)

    def test_initial_w(self):
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_w: s1:1, s2:2
        @phase foo stop:s1=3
        L1 s1 | L1
        @run foo
        @wplot s1
        @wplot s2
        '''
        script_obj, script_output = run(text)
        self.assertEqual(len(script_obj.script_parser.postcmds.cmds), 2)
        plot_data = get_plot_data()
        s1 = plot_data['w(s1)']
        s2 = plot_data['w(s2)']
        self.assertEqual(s1['x'], [0, 1, 2])
        self.assertEqual(s2['x'], [0, 1, 2])
        self.assertEqual(s1['y'][0], 1)
        self.assertEqual(s2['y'][0], 2)


class TestPlotProperties(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_phases(self):
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1  # Only one behavior to make plots deterministic
        u: s2:1, default:0
        bind_trials: off
        start_v: default:0

        @phase phase1s stop:s1=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @phase phase1nt stop:new_trial=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @phase phase2s stop:s1=20
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @phase phase2nt stop:new_trial=20
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @run phase1s, phase2s runlabel:s
        @run phase1nt, phase2nt runlabel:nt

        @figure s
        runlabel: s

        phases: phase1s
        @vplot s1->b1 {'label':'only_phase1s'}

        phases: phase2s
        @vplot s1->b1 {'label':'only_phase2s'}

        phases: phase1s, phase2s
        @vplot s1->b1 {'label':'both_phase1s_and_phase2s'}


        @figure nt
        runlabel: nt

        phases: phase1nt
        @vplot s1->b1 {'label':'only_phase1nt'}

        phases: phase2nt
        @vplot s1->b1 {'label':'only_phase2nt'}

        phases: phase1nt, phase2nt
        @vplot s1->b1 {'label':'both_phase1nt_and_phase2nt'}
        '''
        script_obj, script_output = run(text)
        plot_data_s = get_plot_data(figure_number=1)
        plot_data_nt = get_plot_data(figure_number=2)
        self.assertEqual(plot_data_s['only_phase1s'],
                         plot_data_nt['only_phase1nt'])
        self.assertEqual(plot_data_s['only_phase2s'],
                         plot_data_nt['only_phase2nt'])
        self.assertEqual(plot_data_s['both_phase1s_and_phase2s'],
                         plot_data_nt['both_phase1nt_and_phase2nt'])

    def test_phases_all(self):
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1, b2
        bind_trials: off

        @phase phase1 stop:new_trial=5
        new_trial s1 | new_trial

        @run phase1

        @vplot s1->b1 {'label':'phases not set'}

        phases: all
        @vplot s1->b1 {'label':'phases: all'}

        phases: phase1
        @vplot s1->b1 {'label':'phases: phase1'}
        '''
        script_obj, script_output = run(text)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['phases not set'], plot_data['phases: all'])
        self.assertEqual(plot_data['phases: all'], plot_data['phases: phase1'])

    def test_phases_and_xscale(self):
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1  # Only one behavior to make plots deterministic
        u: s2:1, default:0
        bind_trials: off
        start_v: default:0

        @phase phase1s stop:s1=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @phase phase1nt stop:new_trial=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @phase phase2s stop:s1=20
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @phase phase2nt stop:new_trial=20
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @run phase1s, phase2s runlabel:s
        @run phase1nt, phase2nt runlabel:nt

        @figure s
        xscale: s1
        runlabel: s

        phases: phase1s
        @vplot s1->b1 {'label':'only_phase1s'}

        phases: phase2s
        @vplot s1->b1 {'label':'only_phase2s'}

        phases: phase1s, phase2s
        @vplot s1->b1 {'label':'both_phase1s_and_phase2s'}

        @figure nt
        xscale: new_trial
        runlabel: nt

        phases: phase1nt
        @vplot s1->b1 {'label':'only_phase1nt'}

        phases: phase2nt
        @vplot s1->b1 {'label':'only_phase2nt'}

        phases: phase1nt, phase2nt
        @vplot s1->b1 {'label':'both_phase1nt_and_phase2nt'}
        '''
        script_obj, script_output = run(text)
        plot_data_s = get_plot_data(figure_number=1)
        plot_data_nt = get_plot_data(figure_number=2)
        self.assertEqual(plot_data_s['only_phase1s'],
                         plot_data_nt['only_phase1nt'])
        self.assertEqual(plot_data_s['only_phase2s'],
                         plot_data_nt['only_phase2nt'])
        self.assertEqual(plot_data_s['both_phase1s_and_phase2s'],
                         plot_data_nt['both_phase1nt_and_phase2nt'])

    def test_phase_order_not_run_order1(self):
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1, b2
        u: s1:1, default:0

        @phase phase1 stop:S1=5
        S1 s1 | S1

        @run phase1
        @wplot s1
        '''
        run(text)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['y'], [0, 1, 2, 3, 4])

    def test_phase_order_not_run_order2(self):
        """
        Test that the first value in plot (x=0) is
        - inital value if the first phase in 'phases' is the first run phase,
        - last value of previous phase if the first phase in 'phases' is not the first run phase.
        """
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2
        u: s1:1

        @phase phase1 stop:S1=5
        S1 s1 | S1

        @phase phase2 stop:S2=10
        S1 s1 | new_trial

        @run phase1, phase2, phase3

        phases: phase2, phase1
        @nplot s1
        '''
        #assert(False)  # Test all plot types and that y(0) is last value in previous phase
        # (or start value if first phase)

    def test_run_phases(self):
        """
        Test that running two phases and plotting only the first is the same as running
        and plotting only the first.
        """
        text = '''
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b1  # Only one behavior to make plots deterministic
        u: s2:1, default:0
        bind_trials: off
        start_v: default:0

        @phase phase1 stop:s1=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @phase phase2 stop:s1=20
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial

        @run phase1, phase2 runlabel:both
        @run phase1 runlabel:phase1

        runlabel: both
        phases: phase1
        @vplot s1->b1 {'label':'run_both_plot_first'}

        runlabel: phase1
        phases: all
        @vplot s1->b1 {'label':'run_only_first'}
        '''
        script_obj, script_output = run(text)
        plot_data = get_plot_data()
        self.assertEqual(plot_data['run_both_plot_first'],
                         plot_data['run_only_first'])


class TestCommaSeparatedPlots(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_vwp_plots(self):
        text = '''
        mechanism: a
	    n_subjects = 10
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2
        u: s1:0.5, s2:1, default:0

        @variables i1=0.1, i2=1.0

        @phase phase1 stop:s1=10
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1

   	    xscale = s1
        @figure
        @vplot s1->b1
        @vplot s2->b1

        @figure
        @vplot s1->b1; s2->b1

        @figure
        @pplot s1->b1
        @pplot s2->b1
        @pplot s1,s2->b1

        @figure
        @pplot s1->b1; s2->b1; s1,s2->b1

        @figure
        @pplot s1[0.1],s2[1.0]->b1
        @pplot s1[1.0],s2[0.1]->b2

        @figure
        @pplot s1[0.1],s2[1.0]->b1 ; s1[1.0],s2[0.1]->b2

        @figure
        @pplot s1[i1],s2[i2]->b1 ; s1[i2],s2[i1],s3[0]->b2

        @figure
        @wplot s1
        @wplot s2

        @figure
        @wplot s1 ; s2

        xscale = all
        @figure
        @nplot s1->b1
        @nplot s1->b2

        @figure
        @nplot s1->b1 ; s1->b2
        '''
        run(text)
        
        plot_data = get_plot_data(figure_number=1)
        plot_data_comma = get_plot_data(figure_number=2)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=3)
        plot_data_comma = get_plot_data(figure_number=4)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=5)
        plot_data_comma = get_plot_data(figure_number=6)
        plot_data_comma_var = get_plot_data(figure_number=7)
        self.assertEqual(plot_data, plot_data_comma)
        self.assertEqual(plot_data['p(s1[0.1],s2[1.0]->b1)'], plot_data_comma_var['p(s1[i1],s2[i2]->b1)'])
        self.assertEqual(plot_data['p(s1[1.0],s2[0.1]->b2)'], plot_data_comma_var['p(s1[i2],s2[i1],s3[0]->b2)'])

        plot_data = get_plot_data(figure_number=8)
        plot_data_comma = get_plot_data(figure_number=9)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=10)
        plot_data_comma = get_plot_data(figure_number=11)
        self.assertEqual(plot_data, plot_data_comma)

    def test_vss_plots(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        xscale:cs

        @figure
        @vssplot cs->cs        
        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us

        @figure
        @vssplot *->*

        @figure
        @vssplot cs->cs ; cs->us ;  us->cs ;  us->us
        '''
        run(text)

        plot_data = get_plot_data(figure_number=1)
        plot_data_wild = get_plot_data(figure_number=2)
        plot_data_semi = get_plot_data(figure_number=2)
        self.assertEqual(plot_data, plot_data_wild)
        self.assertEqual(plot_data, plot_data_semi)

    def test_plots(self):
        text = '''
        mechanism: a
	    n_subjects = 10
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2
        u: s1:0.5, s2:1, default:0

        @variables i1=0.1, i2=1.0

        @phase phase1 stop:s1=10
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1

   	    xscale = s1
        @figure
        @vplot s1->b1
        @vplot s2->b1

        @figure
        @plot v(s1->b1); v(s2->b1)

        @figure
        @pplot s1->b1
        @pplot s2->b1
        @pplot s1,s2->b1

        @figure
        @plot p(s1->b1); p(s2->b1); p(s1,s2->b1)

        @figure
        @pplot s1[0.1],s2[1.0]->b1
        @pplot s1[1.0],s2[0.1]->b2

        @figure
        @plot p(s1[0.1],s2[1.0]->b1) ; p(s1[1.0],s2[0.1]->b2)

        @figure
        @plot p(s1[i1],s2[i2]->b1) ; p(s1[i2],s2[i1],s3[0]->b2)

        @figure
        @wplot s1
        @wplot s2

        @figure
        @plot w(s1) ; w(s2)

        xscale = all
        @figure
        @nplot s1->b1
        @nplot s1->b2

        @figure
        @plot n(s1->b1) ; n(s1->b2)
        '''
        run(text)

        plot_data = get_plot_data(figure_number=1)
        plot_data_comma = get_plot_data(figure_number=2)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=3)
        plot_data_comma = get_plot_data(figure_number=4)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=5)
        plot_data_comma = get_plot_data(figure_number=6)
        plot_data_comma_var = get_plot_data(figure_number=7)
        self.assertEqual(plot_data, plot_data_comma)
        self.assertEqual(plot_data['p(s1[0.1],s2[1.0]->b1)'], plot_data_comma_var['p(s1[i1],s2[i2]->b1)'])
        self.assertEqual(plot_data['p(s1[1.0],s2[0.1]->b2)'], plot_data_comma_var['p(s1[i2],s2[i1],s3[0]->b2)'])

        plot_data = get_plot_data(figure_number=8)
        plot_data_comma = get_plot_data(figure_number=9)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=10)
        plot_data_comma = get_plot_data(figure_number=11)
        self.assertEqual(plot_data, plot_data_comma)

    def test_plots_mixed(self):
        text = '''
        mechanism: a
	    n_subjects = 10
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2
        u: s1:0.5, s2:1, default:0

        @variables i1=0.1, i2=1.0

        @phase phase1 stop:s1=10
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1

   	    xscale = s1
        @figure
        @vplot s1->b1
        @pplot s2->b1

        @figure
        @plot v(s1->b1); p(s2->b1)

        @figure
        @vplot s1->b1
        @pplot s2->b1
        @pplot s1,s2->b1

        @figure
        @plot v(s1->b1); p(s2->b1); p(s1,s2->b1)

        @figure
        @pplot s1[0.1],s2[1.0]->b1
        @nplot s1->b2->s2

        @figure
        @plot p(s1[0.1],s2[1.0]->b1) ; n(s1->b2->s2)

        @figure
        @plot p(s1[i1],s2[i2]->b1) ; n(s1->b2->s2)

        @figure
        @wplot s1
        @pplot s1->b1

        @figure
        @plot w(s1) ; p(s1->b1)

        xscale = all
        @figure
        @nplot s1->b1
        @pplot s1->b1

        @figure
        @plot n(s1->b1) ; p(s1->b1)
        '''
        run(text)

        plot_data = get_plot_data(figure_number=1)
        plot_data_comma = get_plot_data(figure_number=2)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=3)
        plot_data_comma = get_plot_data(figure_number=4)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=5)
        plot_data_comma = get_plot_data(figure_number=6)
        plot_data_comma_var = get_plot_data(figure_number=7)
        self.assertEqual(plot_data, plot_data_comma)
        self.assertEqual(plot_data['p(s1[0.1],s2[1.0]->b1)'], plot_data_comma_var['p(s1[i1],s2[i2]->b1)'])
        self.assertEqual(plot_data['n(s1->b2->s2)'], plot_data_comma_var['n(s1->b2->s2)'])

        plot_data = get_plot_data(figure_number=8)
        plot_data_comma = get_plot_data(figure_number=9)
        self.assertEqual(plot_data, plot_data_comma)

        plot_data = get_plot_data(figure_number=10)
        plot_data_comma = get_plot_data(figure_number=11)
        self.assertEqual(plot_data, plot_data_comma)


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_no_run(self):
        text = """
        mechanism: ga
        stimulus_elements: s1, s2
        behaviors: b
        start_v: s1->b:7, default:1.5
        @phase foo stop:s1=2
        L1 s1 | L1
        @vplot s1->b
        """
        msg = "Error on line 8: There is no @RUN."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_wrong_subplot(self):
        text = '''
        mechanism: sr
        stimulus_elements: s1, s2
        behaviors: b1  # Only one behavior to make plots deterministic
        u: s2:1, default:0
        start_v: default:0

        @phase phase1 stop:s1=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial
        
        @run phase1

        @figure
        @subplot 1111
        @vplot s1->b1 {'label':'run_both_plot_first'}
        '''
        msg = "Error on line 15: Invalid @subplot argument 1111."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: s1, s2
        behaviors: b1  # Only one behavior to make plots deterministic
        u: s2:1, default:0
        start_v: default:0

        @phase phase1 stop:s1=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial
        
        @run phase1

        @figure
        @subplot foo
        @vplot s1->b1 {'label':'run_both_plot_first'}
        '''
        msg = "Error on line 15: Invalid @subplot argument foo."
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: s1, s2
        behaviors: b1  # Only one behavior to make plots deterministic
        u: s2:1, default:0
        start_v: default:0

        @phase phase1 stop:s1=10
        new_trial s1 | b1:S2 | new_trial
        S2        s2 | new_trial
        
        @run phase1

        @figure
        @subplot 1.2
        @vplot s1->b1 {'label':'run_both_plot_first'}
        '''
        msg = "Error on line 15: Invalid @subplot argument 1.2."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_v_semicolon1(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @vplot s1->b1 ; s2->b2 filename.txt
        '''
        msg = "Error on line 12: Expected a behavior name, got b2 filename.txt."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_v_semicolon2(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @vplot s1->b1 filename; s2->b2
        '''
        msg = "Error on line 12: Expected a behavior name, got b1 filename."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_v_semicolon3(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @vplot s1->b1 ; foo->bar ; s2->b2
        '''
        msg = "Error on line 12: Expected a stimulus element, got foo."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_v_semicolon4(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @vplot s1->b1 ; *->b1; s2->b2
        '''
        msg = "Error on line 12: Cannot use semicolon-separated expressions with wildcard."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_w_semicolon1(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @wplot s1 ; s2 filename.txt
        '''
        msg = "Error on line 12: Expected a stimulus element, got s2 filename.txt."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_w_semicolon2(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @wplot s1 filename; s2
        '''
        msg = "Error on line 12: Expected a stimulus element, got s1 filename."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_w_semicolon3(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @wplot s1 ; foo ; s2
        '''
        msg = "Error on line 12: Expected a stimulus element, got foo."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_w_semicolon4(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @wplot s1 ; *; s2
        '''
        msg = "Error on line 12: Cannot use semicolon-separated expressions with wildcard."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_p_semicolon1(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @pplot s1->b1 ; s2->b2 filename.txt
        '''
        msg = "Error on line 12: Expected a behavior name, got b2 filename.txt."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_p_semicolon2(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @pplot s1->b1 filename; s2->b2
        '''
        msg = "Error on line 12: Expected a behavior name, got b1 filename."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_p_semicolon3(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @pplot s1->b1 ; foo->bar ; s2->b2
        '''
        msg = "Error on line 12: Expected a stimulus element, got foo."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_p_semicolon4(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @pplot s1->b1 ; *->b1; s2->b2
        '''
        msg = "Error on line 12: Cannot use semicolon-separated expressions with wildcard."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_n_semicolon1(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @nplot s1->b1 ; s2->b2 filename.txt
        '''
        msg = "Error on line 12: Expected behavior name, got 'b2 filename.txt'."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_n_semicolon2(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @nplot s1->b1 filename; s2->b2
        '''
        msg = "Error on line 12: Expected behavior name, got 'b1 filename'."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_n_semicolon3(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @nplot s1->b1 ; foo->bar ; s2->b2
        '''
        msg = "Error on line 12: Expected stimulus element(s) or a behavior, got foo."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_n_semicolon4(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @nplot s1->b1 ; *->b1; s2->b2
        '''
        msg = "Error on line 12: Expected stimulus element(s) or a behavior, got *."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_vss_semicolon1(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        xscale:cs
        @vssplot cs->us ; us->cs filename.txt
        '''
        msg = "Error on line 16: Expected a stimulus element, got cs filename.txt."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_vss_semicolon2(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        xscale:cs
        @vssplot cs->us filename; us->cs
        '''
        msg = "Error on line 16: Expected a stimulus element, got us filename."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_vss_semicolon3(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        xscale:cs
        @vssplot cs->us ; foo->bar ; us->cs
        '''
        msg = "Error on line 16: Expected a stimulus element, got foo."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_vss_semicolon4(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        xscale:cs
        @vssplot cs->us ; *->us; us->cs
        '''
        msg = "Error on line 16: Cannot use semicolon-separated expressions with wildcard."
        with self.assertRaisesMsg(msg):
            run(text)




    def test_errors_wildcard(self):
        text = '''
        mechanism: a
	    n_subjects = 1
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2

        @phase phase1 stop:s1=5
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1
        @vplot *->* foo
        '''
        msg = "Error on line 12: Expected a behavior name, got * foo."
        with self.assertRaisesMsg(msg):
            run(text)