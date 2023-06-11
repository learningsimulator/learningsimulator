import matplotlib.pyplot as plt

from .testutil import LsTestCase
from .testutil import run, get_plot_data, create_exported_files_folder, delete_exported_files_folder, remove_exported_files


class TestVMechanisms(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        create_exported_files_folder()

    def tearDown(self):
        delete_exported_files_folder()
        plt.close('all')

    def test_simple(self):
        mechanism_names_to_test = ['ga', 'sr', 'es', 'ql', 'ac']
        for mechanism_name in mechanism_names_to_test:
            text = f'''
            mechanism: {mechanism_name}
            stimulus_elements: s1, s2, rew, norew
            behaviors: b1, b2, dummy
            u: rew:1, norew:-1, default:0
            n_subjects:100
            alpha_v: 1
            alpha_w: 1 
            response_requirements: b1:[s1, s2],
                                   b2:[s1, s2],
                                   dummy:[rew, norew]

            @phase phase stop:s1=50
            new_trial s1    | b1:S2     | NOREW
            S2        s2    | b2:REW    | NOREW
            NOREW     norew | new_trial
            REW       rew   | new_trial

            @run phase

            xscale:new_trial
            @vplot s1->b1
            '''
            run(text)


class TestRescorlaWagner(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        create_exported_files_folder()

    def tearDown(self):
        delete_exported_files_folder()
        plt.close('all')

    def test_simple(self):
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
        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - expected_increasing_y[i], 6)

    def test_default_alpha_vss(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 1

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        xscale:cs

        @figure
        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        self.assertEqual(cs_cs['y'], [0.5, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(cs_us['y'], [0.5, 1.0, 1.0, 1.0, 1.0])
        self.assertEqual(us_cs['y'], [0.5, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(us_us['y'], [0.5, 0.0, 0.0, 0.0, 0.0])

    def test_xscale_stimulus(self):
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

        @figure
        xscale: cs

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - expected_increasing_y[i], 6)

    def test_xscale_phaselinelabel(self):
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

        @figure
        xscale: CS

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - expected_increasing_y[i], 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - expected_increasing_y[i], 6)

    def test_stop_phaselinelabel(self):
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

        @figure
        xscale: CS

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        '''
        run(text)
        plot_data = get_plot_data()
        cs_us = plot_data['vss(cs->us)']
        us_cs = plot_data['vss(us->cs)']
        us_us = plot_data['vss(us->us)']
        cs_cs = plot_data['vss(cs->cs)']

        expected_x = list(range(0, 5))
        self.assertEqual(cs_us['x'], expected_x)
        self.assertEqual(us_cs['x'], expected_x)
        self.assertEqual(us_us['x'], expected_x)
        self.assertEqual(cs_cs['x'], expected_x)

        expected_increasing_y = [0.5, 0.8, 0.92, 0.968, 0.9872]
        self.assertEqual(len(cs_us['y']), len(expected_increasing_y))
        for i, y in enumerate(expected_increasing_y):
            self.assertAlmostEqual(cs_us['y'][i], y, 6)
            self.assertAlmostEqual(us_cs['y'][i], 1 - y, 6)
            self.assertAlmostEqual(us_us['y'][i], 1 - y, 6)
            self.assertAlmostEqual(cs_cs['y'][i], 1 - y, 6)

    def test_compare_with_analytic(self):
        alpha = 0.6
        csus0 = 0.4
        cscs0 = 0.45
        usus0 = 0.5
        uscs0 = 0.55

        text = f'''
        mechanism: rw
        stimulus_elements: cs, us

        lambda: 1
        start_vss: cs->us: {csus0},
                   cs->cs: {cscs0},
                   us->us: {usus0},
                   us->cs: {uscs0}
        alpha_vss: {alpha}

        @phase p stop:cs=5
        CS cs     | US
        US us     | CS

        @run p
        @figure

        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        @legend
        '''
        run(text)
        plot_data = get_plot_data()
        csus = plot_data['vss(cs->us)']['y']
        cscs = plot_data['vss(cs->cs)']['y']
        usus = plot_data['vss(us->us)']['y']
        uscs = plot_data['vss(us->cs)']['y']

        csus_exact = list()
        csus_exact.append(csus0)
        for i in range(4):
            n = i + 1
            csus_exact.extend([1 - (1 - alpha)**n * (1 - csus0)] * 2)
        self.assertAlmostEqualList(csus, csus_exact)

        cscs_exact = list()
        cscs_exact.append(cscs0)
        for i in range(4):
            n = i + 1
            cscs_exact.extend([(1 - alpha)**n * cscs0] * 2)
        self.assertAlmostEqualList(cscs, cscs_exact)

        usus_exact = list()
        usus_exact.extend([usus0] * 2)
        for i in range(4):
            n = i + 1
            if n < 4:
                usus_exact.extend([(1 - alpha)**n * usus0] * 2)
            else:
                usus_exact.append((1 - alpha)**n * usus0)
        self.assertAlmostEqualList(usus, usus_exact)

        uscs_exact = list()
        uscs_exact.extend([uscs0] * 2)
        for i in range(4):
            n = i + 1
            if n < 4:
                uscs_exact.extend([1 - (1 - alpha)**n * (1 - uscs0)] * 2)
            else:
                uscs_exact.append(1 - (1 - alpha)**n * (1 - uscs0))
        self.assertAlmostEqualList(uscs, uscs_exact)

    def test_error_for_vpw(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us
        behaviors: b1, b2

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        @figure

        {}
        '''
        for cmd in ['@vplot cs->b1', '@pplot us->b2',
                    '@vexport cs->b1 ./tests/exported_files/export_filename.txt',
                    '@pexport cs->b1 ./tests/exported_files/export_filename.txt']:
            msg = "Used mechanism does not have variable 'v'."
            with self.assertRaisesMsg(msg):
                run(text.format(cmd))
        for cmd in ['@wplot cs', '@wplot us',
                    '@wexport cs ./tests/exported_files/export_filename.txt',
                    '@wexport us ./tests/exported_files/export_filename.txt']:
            msg = "Used mechanism does not have variable 'w'."
            with self.assertRaisesMsg(msg):
                run(text.format(cmd))

        remove_exported_files(['export_filename.txt'])
        self.assert_exported_files_are_removed(['export_filename.txt'])

    def test_hexport(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us
        behaviors: b1, b2

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        {}
        '''
        filename = './tests/exported_files/test_rw_hexport.txt'
        run(text.format(f'@hexport {filename}'))

        data = None
        with open(filename, 'r') as file:
            data = file.read()

        self.assertIsNotNone(data)

        expected_file_contents = '''"run","phase","subject","step","line","stimuli","behavior","cs","us"
"run1","foo",0,1,"CS","cs","",1,0
"run1","foo",0,2,"US","us","",0,1
"run1","foo",0,3,"CS","cs","",1,0
"run1","foo",0,4,"US","us","",0,1
"run1","foo",0,5,"CS","cs","",1,0
"run1","foo",0,6,"US","us","",0,1
"run1","foo",0,7,"CS","cs","",1,0
"run1","foo",0,8,"US","us","",0,1
"run1","foo",0,9,"CS","cs","",1,0
'''
        self.assertEqual(data, expected_file_contents)
        filenames = ['test_rw_hexport.txt']
        remove_exported_files(filenames)
        self.assert_exported_files_are_removed(filenames)

    def test_nexport(self):
        text = '''
        mechanism: rw
        stimulus_elements: cs, us
        behaviors: b1, b2

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo

        {}
        '''
        filename = './tests/exported_files/test_rw_nexport.txt'
        run(text.format(f'@nexport b1 {filename}'))

        data = None
        with open(filename, 'r') as file:
            data = file.read()

        self.assertIsNotNone(data)

        expected_file_contents = '''"x","n(b1)"
0,0.0
1,0.0
2,0.0
3,0.0
4,0.0
5,0.0
6,0.0
7,0.0
8,0.0
9,0.0
10,0.0
11,0.0
12,0.0
13,0.0
14,0.0
15,0.0
16,0.0
17,0.0
'''
        self.assertEqual(data, expected_file_contents)
        filenames = ['test_rw_hexport.txt']
        remove_exported_files(filenames)
        self.assert_exported_files_are_removed(filenames)

        filename = './tests/exported_files/test_rw_nexport.txt'
        run(text.format(f'@nexport cs {filename}'))

        data = None
        with open(filename, 'r') as file:
            data = file.read()

        self.assertIsNotNone(data)

        expected_file_contents = '''"x","n(cs)"
0,1.0
1,1.0
2,1.0
3,1.0
4,2.0
5,2.0
6,2.0
7,2.0
8,3.0
9,3.0
10,3.0
11,3.0
12,4.0
13,4.0
14,4.0
15,4.0
16,5.0
17,5.0
'''
        self.assertEqual(data, expected_file_contents)
        filenames = ['test_rw_hexport.txt']
        remove_exported_files(filenames)
        self.assert_exported_files_are_removed(filenames)


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

    def test_error_for_w_vss(self):
        text = """
        mechanism: sr
        stimulus_elements: cs, us
        behaviors: b1, b2
        start_v: 1
        alpha_v: 1

        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:cs=5
        CS cs     | US
        US us     | CS

        @run foo
        {}
        """
        msg = "Used mechanism does not have variable 'w'."
        with self.assertRaisesMsg(msg):
            run(text.format("@wplot cs"))
        
        msg = "Used mechanism does not have variable 'vss'."
        with self.assertRaisesMsg(msg):
            run(text.format("@vssplot cs->us"))

    def test_stop_condition_depends_on_behavior(self):
        text = """
        mechanism: rw
        stimulus_elements: cs, us
        behaviors: b1, b2
        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:b1=5
        CS cs     | US
        US us     | CS

        @phase bar stop:us=5
        CS cs     | US
        US us     | CS

        @run foo
        """
        msg = "Error on line 9: Stop condition cannot depend on behavior in mechanism 'rw'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        mechanism: rw
        stimulus_elements: cs, us
        behaviors: b1, b2
        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:b1=5
        CS cs     | US
        US us     | CS

        @phase bar stop:us=5
        CS cs     | US
        US us     | CS

        @run bar

        @figure
        @vssplot cs->us
        @vssplot us->cs
        @vssplot us->us
        @vssplot cs->cs
        """
        run(text)

        text = """
        mechanism: rw
        stimulus_elements: cs, us
        behaviors: b1, b2
        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase foo stop:b1=5
        CS cs     | US
        US us     | CS

        @phase bar stop:us=5
        CS cs     | US
        US us     | CS

        @run foo, bar
        """
        msg = "Error on line 9: Stop condition cannot depend on behavior in mechanism 'rw'."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_phase_line_logic_depends_on_behavior(self):
        text = """
        mechanism: rw
        stimulus_elements: cs, us
        behaviors: b1, b2
        lambda:    us:1, default:0
        start_vss: default:0.5
        alpha_vss: 0.6

        @phase bar stop:us=5
        CS cs     | b1:US | CS
        US us     | CS

        @run bar
        """
        msg = "Error on line 10: Phase line logic cannot depend on behavior in mechanism 'rw'."
        with self.assertRaisesMsg(msg):
            run(text)
