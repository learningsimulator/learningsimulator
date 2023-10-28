from math import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, ceil, floor, exp, log, log10, sqrt
import os
import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data, create_exported_files_folder, remove_exported_files, delete_exported_files_folder, get_csv_file_contents


class TestExportMultiExpression(LsTestCase):
    def setUp(self):
        create_exported_files_folder()

    def tearDown(self):
        plt.close('all')

        filenames = ['vexport1_prop.txt',
                     'vexport1_line.txt',
                     'vexport2_prop.txt',
                     'vexport2_line.txt',
                     'vexport3_prop.txt',
                     'vexport3_line.txt',
                     'vexport4_prop.txt',
                     'vexport4_line.txt',
                     'vexport5_prop.txt',
                     'vexport5_line.txt',
                     'vexport6_prop.txt',
                     'vexport6_line.txt',

                     'wexport1_prop.txt',
                     'wexport1_line.txt',
                     'wexport2_prop.txt',
                     'wexport2_line.txt',

                     'pexport1_prop.txt',
                     'pexport1_line.txt'
                     'pexport2_prop.txt',
                     'pexport2_line.txt',
                     'pexport3_prop.txt',
                     'pexport3_line.txt',
                     'pexport4_prop.txt',
                     'pexport4_line.txt',
                     'pexport5_prop.txt',
                     'pexport5_line.txt',
                     'pexport6_prop.txt',
                     'pexport6_line.txt',
                     
                     'vssexport_prop.txt',
                     'vssexport_line.txt']
        remove_exported_files(filenames)
        self.assert_exported_files_are_removed(filenames)
        delete_exported_files_folder()

    def test_semicolon(self):
        text = """
        n_subjects        = 10
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -1
        alpha_v           = 0.1
        alpha_w           = 1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==7
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        
        filename: ./tests/exported_files/vexport1_prop.txt
        subject: 1
        @vexport stimulus->response; stimulus -> no_response
        @vexport stimulus->response; stimulus -> no_response ./tests/exported_files/vexport1_line.txt
        @figure 1
        @vplot stimulus->response; stimulus -> no_response
        
        filename: ./tests/exported_files/vexport2_prop.txt
        subject: all
        @vexport stimulus->response; stimulus -> no_response
        @vexport stimulus->response; stimulus -> no_response ./tests/exported_files/vexport2_line.txt
        @figure 2
        @vplot stimulus->response; stimulus -> no_response

        filename: ./tests/exported_files/wexport1_prop.txt
        subject: 1
        @wexport background; stimulus; reward
        @wexport background; stimulus; reward   ./tests/exported_files/wexport1_line.txt
        @figure 3
        @wplot background; stimulus; reward

        filename: ./tests/exported_files/wexport2_prop.txt
        subject: all
        @wexport background; stimulus; reward
        @wexport background; stimulus; reward    ./tests/exported_files/wexport2_line.txt
        @figure 4
        @wplot background; stimulus; reward

        filename: ./tests/exported_files/pexport1_prop.txt
        subject: 1
        @pexport stimulus[0.5],background[0.2] -> response ; reward[0.1],background[0.2]  -> no_response
        @pexport stimulus[0.5],background[0.2] -> response ; reward[0.1],background[0.2]  -> no_response ./tests/exported_files/pexport1_line.txt
        @figure 5
        @pplot stimulus[0.5],background[0.2] -> response ; reward[0.1],background[0.2]    -> no_response
        
        filename: ./tests/exported_files/pexport2_prop.txt
        subject: all
        @pexport stimulus[0.5],background[0.2] -> response ; reward[0.1],background[0.2]  -> no_response
        @pexport stimulus[0.5],background[0.2] -> response ; reward[0.1],background[0.2]  -> no_response ./tests/exported_files/pexport2_line.txt
        @figure 6
        @pplot stimulus[0.5],background[0.2] -> response ; reward[0.1],background[0.2]    -> no_response
        """
        run(text)

        vexport1_prop = os.path.join('.', 'tests', 'exported_files', 'vexport1_prop.txt')
        vexport1_line = os.path.join('.', 'tests', 'exported_files', 'vexport1_line.txt')
        self.assertAlmostEqualFile(vexport1_prop, vexport1_line)
        exported_titles, exported_data = get_csv_file_contents(vexport1_prop)
        self.assertListEqual(exported_titles, ["x", "v(stimulus->response)", "v(stimulus->no_response)"])
        pd = get_plot_data(figure_number=1)
        self.assertPlotExportEqual(pd, ['v(stimulus->response)', 'v(stimulus->no_response)'],
                                   exported_data)

        vexport2_prop = os.path.join('.', 'tests', 'exported_files', 'vexport2_prop.txt')
        vexport2_line = os.path.join('.', 'tests', 'exported_files', 'vexport2_line.txt')
        self.assertAlmostEqualFile(vexport2_prop, vexport2_line)
        exported_titles, exported_data = get_csv_file_contents(vexport2_prop)
        legends = ["x", "v(stimulus->response) subject 1", "v(stimulus->response) subject 2", "v(stimulus->response) subject 3", "v(stimulus->response) subject 4", "v(stimulus->response) subject 5", "v(stimulus->response) subject 6", "v(stimulus->response) subject 7", "v(stimulus->response) subject 8", "v(stimulus->response) subject 9", "v(stimulus->response) subject 10", "v(stimulus->no_response) subject 1", "v(stimulus->no_response) subject 2", "v(stimulus->no_response) subject 3", "v(stimulus->no_response) subject 4", "v(stimulus->no_response) subject 5", "v(stimulus->no_response) subject 6", "v(stimulus->no_response) subject 7", "v(stimulus->no_response) subject 8", "v(stimulus->no_response) subject 9", "v(stimulus->no_response) subject 10"]
        self.assertListEqual(exported_titles, legends)
        pd = get_plot_data(figure_number=2)
        self.assertPlotExportEqual(pd, legends[1:], exported_data)

        wexport1_prop = os.path.join('.', 'tests', 'exported_files', 'wexport1_prop.txt')
        wexport1_line = os.path.join('.', 'tests', 'exported_files', 'wexport1_line.txt')
        self.assertAlmostEqualFile(wexport1_prop, wexport1_line)
        exported_titles, exported_data = get_csv_file_contents(wexport1_prop)
        self.assertListEqual(exported_titles, ['x', 'w(background)', 'w(stimulus)', 'w(reward)'])
        pd = get_plot_data(figure_number=3)
        self.assertPlotExportEqual(pd, ['w(background)', 'w(stimulus)', 'w(reward)'],
                                   exported_data)

        wexport2_prop = os.path.join('.', 'tests', 'exported_files', 'wexport2_prop.txt')
        wexport2_line = os.path.join('.', 'tests', 'exported_files', 'wexport2_line.txt')
        self.assertAlmostEqualFile(wexport2_prop, wexport2_line)
        exported_titles, exported_data = get_csv_file_contents(wexport2_prop)
        legends = ["x", "w(background) subject 1", "w(background) subject 2", "w(background) subject 3", "w(background) subject 4", "w(background) subject 5", "w(background) subject 6", "w(background) subject 7", "w(background) subject 8", "w(background) subject 9", "w(background) subject 10", "w(stimulus) subject 1", "w(stimulus) subject 2", "w(stimulus) subject 3", "w(stimulus) subject 4", "w(stimulus) subject 5", "w(stimulus) subject 6", "w(stimulus) subject 7", "w(stimulus) subject 8", "w(stimulus) subject 9", "w(stimulus) subject 10", "w(reward) subject 1", "w(reward) subject 2", "w(reward) subject 3", "w(reward) subject 4", "w(reward) subject 5", "w(reward) subject 6", "w(reward) subject 7", "w(reward) subject 8", "w(reward) subject 9", "w(reward) subject 10"]
        self.assertListEqual(exported_titles, legends)
        pd = get_plot_data(figure_number=4)
        self.assertPlotExportEqual(pd, legends[1:], exported_data)

        pexport1_prop = os.path.join('.', 'tests', 'exported_files', 'pexport1_prop.txt')
        pexport1_line = os.path.join('.', 'tests', 'exported_files', 'pexport1_line.txt')
        self.assertAlmostEqualFile(pexport1_prop, pexport1_line)
        exported_titles, exported_data = get_csv_file_contents(pexport1_prop)
        legends = ["x", "p(stimulus[0.5],background[0.2]->response)", "p(reward[0.1],background[0.2]->no_response)"]
        self.assertListEqual(exported_titles, legends)
        pd = get_plot_data(figure_number=5)
        self.assertPlotExportEqual(pd, legends[1:], exported_data)

        pexport2_prop = os.path.join('.', 'tests', 'exported_files', 'pexport2_prop.txt')
        pexport2_line = os.path.join('.', 'tests', 'exported_files', 'pexport2_line.txt')
        self.assertAlmostEqualFile(pexport2_prop, pexport2_line)
        exported_titles, exported_data = get_csv_file_contents(pexport2_prop)
        legends = ["x", "p(stimulus[0.5],background[0.2]->response) subject 1",
                        "p(stimulus[0.5],background[0.2]->response) subject 2",
                        "p(stimulus[0.5],background[0.2]->response) subject 3",
                        "p(stimulus[0.5],background[0.2]->response) subject 4",
                        "p(stimulus[0.5],background[0.2]->response) subject 5",
                        "p(stimulus[0.5],background[0.2]->response) subject 6",
                        "p(stimulus[0.5],background[0.2]->response) subject 7",
                        "p(stimulus[0.5],background[0.2]->response) subject 8",
                        "p(stimulus[0.5],background[0.2]->response) subject 9",
                        "p(stimulus[0.5],background[0.2]->response) subject 10",
                        "p(reward[0.1],background[0.2]->no_response) subject 1",
                        "p(reward[0.1],background[0.2]->no_response) subject 2",
                        "p(reward[0.1],background[0.2]->no_response) subject 3",
                        "p(reward[0.1],background[0.2]->no_response) subject 4",
                        "p(reward[0.1],background[0.2]->no_response) subject 5",
                        "p(reward[0.1],background[0.2]->no_response) subject 6",
                        "p(reward[0.1],background[0.2]->no_response) subject 7",
                        "p(reward[0.1],background[0.2]->no_response) subject 8",
                        "p(reward[0.1],background[0.2]->no_response) subject 9",
                        "p(reward[0.1],background[0.2]->no_response) subject 10"]
        self.assertListEqual(exported_titles, legends)
        pd = get_plot_data(figure_number=6)
        self.assertPlotExportEqual(pd, legends[1:], exported_data)

    def test_semicolon_vss(self):
        text = """
        n_subjects = 3
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

        filename: ./tests/exported_files/vssexport1_prop.txt
        subject: 1
        @vssexport cs->us; cs->cs; us->cs; us->us
        @vssexport cs->us; cs->cs; us->cs; us->us ./tests/exported_files/vssexport1_line.txt
        @figure 1
        @vssplot cs->us; cs->cs; us->cs; us->us

        filename: ./tests/exported_files/vssexport2_prop.txt
        subject: all
        @vssexport cs->us; cs->cs; us->cs; us->us
        @vssexport cs->us; cs->cs; us->cs; us->us ./tests/exported_files/vssexport2_line.txt
        @figure 2
        @vssplot cs->us; cs->cs; us->cs; us->us
        """
        run(text)

        vssexport1_prop = os.path.join('.', 'tests', 'exported_files', 'vssexport1_prop.txt')
        vssexport1_line = os.path.join('.', 'tests', 'exported_files', 'vssexport1_line.txt')
        self.assertAlmostEqualFile(vssexport1_prop, vssexport1_line)
        exported_titles, exported_data = get_csv_file_contents(vssexport1_prop)
        self.assertListEqual(exported_titles, ["x", "vss(cs->us)", "vss(cs->cs)", "vss(us->cs)", "vss(us->us)"])
        pd = get_plot_data(figure_number=1)
        self.assertPlotExportEqual(pd, ["vss(cs->us)", "vss(cs->cs)", "vss(us->cs)", "vss(us->us)"],
                                   exported_data)
        
        vssexport2_prop = os.path.join('.', 'tests', 'exported_files', 'vssexport2_prop.txt')
        vssexport2_line = os.path.join('.', 'tests', 'exported_files', 'vssexport2_line.txt')
        self.assertAlmostEqualFile(vssexport2_prop, vssexport2_line)
        exported_titles, exported_data = get_csv_file_contents(vssexport2_prop)
        legends = ["x", "vss(cs->us) subject 1", "vss(cs->us) subject 2", "vss(cs->us) subject 3",
                        "vss(cs->cs) subject 1", "vss(cs->cs) subject 2", "vss(cs->cs) subject 3",
                        "vss(us->cs) subject 1", "vss(us->cs) subject 2", "vss(us->cs) subject 3",
                        "vss(us->us) subject 1", "vss(us->us) subject 2", "vss(us->us) subject 3"]
        self.assertListEqual(exported_titles, legends)
        pd = get_plot_data(figure_number=2)
        self.assertPlotExportEqual(pd, legends[1:], exported_data)

    def test_asterisk_v(self):
        text = """
        n_subjects        = 3
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -1
        alpha_v           = 0.1
        alpha_w           = 1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==7
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        
        # stimulus -> *
        subject: 1
        filename: ./tests/exported_files/vexport1_prop.txt
        @vexport stimulus->*
        @vexport stimulus->* ./tests/exported_files/vexport1_line.txt
        @figure 1
        @vplot stimulus->*
        
        subject: all
        filename: ./tests/exported_files/vexport2_prop.txt
        @vexport stimulus->*
        @vexport stimulus->* ./tests/exported_files/vexport2_line.txt
        @figure 2
        @vplot stimulus->*

        # * -> response
        subject: 1
        filename: ./tests/exported_files/vexport3_prop.txt
        @vexport *->response
        @vexport *->response ./tests/exported_files/vexport3_line.txt
        @figure 3
        @vplot *->response

        subject: all
        filename: ./tests/exported_files/vexport4_prop.txt
        @vexport *->response
        @vexport *->response ./tests/exported_files/vexport4_line.txt
        @figure 4
        @vplot *->response

        # * -> *
        subject: 1
        filename: ./tests/exported_files/vexport5_prop.txt
        @vexport *->*
        @vexport *->* ./tests/exported_files/vexport5_line.txt
        @figure 5
        @vplot *->*
        
        subject: all
        filename: ./tests/exported_files/vexport6_prop.txt
        @vexport *->*
        @vexport *->* ./tests/exported_files/vexport6_line.txt
        @figure 6
        @vplot *->*

        """
        run(text)

        # stimulus -> *
        exprs = ['v(stimulus->response)', 'v(stimulus->no_response)']
        self.checkExport('vexport1', n_subjects=1, exprs=exprs, figure_number=1)
        self.checkExport('vexport2', n_subjects=3, exprs=exprs, figure_number=2)
    
        # * -> response
        exprs = ['v(background->response)', 'v(stimulus->response)', 'v(reward->response)']
        self.checkExport('vexport3', n_subjects=1, exprs=exprs, figure_number=3)
        self.checkExport('vexport4', n_subjects=3, exprs=exprs, figure_number=4)

        # * -> *
        exprs = ['v(background->response)', 'v(background->no_response)',
                 'v(stimulus->response)', 'v(stimulus->no_response)',
                 'v(reward->response)', 'v(reward->no_response)']
        self.checkExport('vexport5', n_subjects=1, exprs=exprs, figure_number=5)
        self.checkExport('vexport6', n_subjects=3, exprs=exprs, figure_number=6)

    def test_asterisk_p(self):
        text = """
        n_subjects        = 3
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -1
        alpha_v           = 0.1
        alpha_w           = 1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==7
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        
        # stimulus[0.5],background[1.2] -> *
        subject: 1
        filename: ./tests/exported_files/pexport1_prop.txt
        @pexport stimulus[0.5],background[1.2]->*
        @pexport stimulus[0.5],background[1.2]->* ./tests/exported_files/pexport1_line.txt
        @figure 1
        @pplot stimulus[0.5],background[1.2]->*
        
        subject: all
        filename: ./tests/exported_files/pexport2_prop.txt
        @pexport stimulus[0.5],background[1.2]->*
        @pexport stimulus[0.5],background[1.2]->* ./tests/exported_files/pexport2_line.txt
        @figure 2
        @pplot stimulus[0.5],background[1.2]->*

        # * -> no_response
        subject: 1
        filename: ./tests/exported_files/pexport3_prop.txt
        @pexport *->no_response
        @pexport *->no_response ./tests/exported_files/pexport3_line.txt
        @figure 3
        @pplot *->no_response

        subject: all
        filename: ./tests/exported_files/pexport4_prop.txt
        @pexport *->no_response
        @pexport *->no_response ./tests/exported_files/pexport4_line.txt
        @figure 4
        @pplot *->no_response

        # * -> *
        subject: 1
        filename: ./tests/exported_files/pexport5_prop.txt
        @pexport *->*
        @pexport *->* ./tests/exported_files/pexport5_line.txt
        @figure 5
        @pplot *->*
        
        subject: all
        filename: ./tests/exported_files/pexport6_prop.txt
        @pexport *->*
        @pexport *->* ./tests/exported_files/pexport6_line.txt
        @figure 6
        @pplot *->*
        """
        run(text)

        # stimulus[0.5],background[1.2] -> *
        exprs = ['p(stimulus[0.5],background[1.2]->response)', 'p(stimulus[0.5],background[1.2]->no_response)']
        self.checkExport('pexport1', n_subjects=1, exprs=exprs, figure_number=1)
        self.checkExport('pexport2', n_subjects=3, exprs=exprs, figure_number=2)
    
        # * -> no_response
        exprs = ['p(background->no_response)', 'p(stimulus->no_response)', 'p(reward->no_response)']
        self.checkExport('pexport3', n_subjects=1, exprs=exprs, figure_number=3)
        self.checkExport('pexport4', n_subjects=3, exprs=exprs, figure_number=4)

        # * -> *
        exprs = ['p(background->response)', 'p(background->no_response)',
                 'p(stimulus->response)', 'p(stimulus->no_response)',
                 'p(reward->response)', 'p(reward->no_response)']
        self.checkExport('pexport5', n_subjects=1, exprs=exprs, figure_number=5)
        self.checkExport('pexport6', n_subjects=3, exprs=exprs, figure_number=6)

    def test_asterisk_w(self):
        text = """
        n_subjects        = 3
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -1
        alpha_v           = 0.1
        alpha_w           = 1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==7
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        
        subject: 1
        filename: ./tests/exported_files/wexport1_prop.txt
        @wexport *
        @wexport * ./tests/exported_files/wexport1_line.txt
        @figure 1
        @wplot *
        
        subject: all
        filename: ./tests/exported_files/wexport2_prop.txt
        @wexport *
        @wexport * ./tests/exported_files/wexport2_line.txt
        @figure 2
        @wplot *

        """
        run(text)

        exprs = ['w(background)', 'w(stimulus)', 'w(reward)']
        self.checkExport('wexport1', n_subjects=1, exprs=exprs, figure_number=1)
        self.checkExport('wexport2', n_subjects=3, exprs=exprs, figure_number=2)

    def test_asterisk_vss(self):
        text = """
        n_subjects = 3
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

        # cs -> *
        filename: ./tests/exported_files/vssexport1_prop.txt
        subject: 1
        @vssexport cs->*
        @vssexport cs->* ./tests/exported_files/vssexport1_line.txt
        @figure 1
        @vssplot cs->*

        filename: ./tests/exported_files/vssexport2_prop.txt
        subject: all
        @vssexport cs->*
        @vssexport cs->* ./tests/exported_files/vssexport2_line.txt
        @figure 2
        @vssplot cs->*

        # * -> us
        filename: ./tests/exported_files/vssexport3_prop.txt
        subject: 1
        @vssexport *->us
        @vssexport *->us ./tests/exported_files/vssexport3_line.txt
        @figure 1
        @vssplot *->us

        filename: ./tests/exported_files/vssexport4_prop.txt
        subject: all
        @vssexport *->us
        @vssexport *->us ./tests/exported_files/vssexport4_line.txt
        @figure 2
        @vssplot *->us

        # * -> *
        filename: ./tests/exported_files/vssexport5_prop.txt
        subject: 1
        @vssexport *->*
        @vssexport *->* ./tests/exported_files/vssexport5_line.txt
        @figure 1
        @vssplot *->*

        filename: ./tests/exported_files/vssexport6_prop.txt
        subject: all
        @vssexport *->*
        @vssexport *->* ./tests/exported_files/vssexport6_line.txt
        @figure 2
        @vssplot *->*

        """
        run(text)

        # cs -> *
        exprs = ['vss(cs->cs)', 'vss(cs->us)']
        self.checkExport('vssexport1', n_subjects=1, exprs=exprs, figure_number=1)
        self.checkExport('vssexport2', n_subjects=3, exprs=exprs, figure_number=2)

        # * -> us
        exprs = ['vss(cs->us)', 'vss(us->us)']
        self.checkExport('vssexport3', n_subjects=1, exprs=exprs, figure_number=3)
        self.checkExport('vssexport4', n_subjects=3, exprs=exprs, figure_number=4)

        # * -> *
        exprs = ['vss(cs->cs)', 'vss(cs->us)', 'vss(us->cs)', 'vss(us->us)']
        self.checkExport('vssexport5', n_subjects=1, exprs=exprs, figure_number=5)
        self.checkExport('vssexport6', n_subjects=3, exprs=exprs, figure_number=6)

    def test_semicolon_export(self):
        text = """
        n_subjects        = 3
        mechanism         = a
        behaviors         = response, no_response
        stimulus_elements = background, stimulus, reward
        start_v           = -1
        alpha_v           = 0.1
        alpha_w           = 1
        u                 = reward:10, default:0

        @PHASE training stop: stimulus==7
        START       stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @omit_learn, START
        NO_REWARD   background | @omit_learn, START

        @run training

        xscale: stimulus
        
        subject: 1
        filename: ./tests/exported_files/export1_prop.txt
        @export v(stimulus->response) ; p(stimulus->response) ; n(response)
        filename: ./tests/exported_files/export1_line.txt
        @export v(stimulus->response) ; p(stimulus->response) ; n(response)  # Dummy
        @figure 1
        @plot v(stimulus->response) ; p(stimulus->response) ; n(response)
        
        subject: all
        filename: ./tests/exported_files/export2_prop.txt
        @export v(stimulus->response) ; p(stimulus->response) ; n(response)
        filename: ./tests/exported_files/export2_line.txt  # Dummy
        @export v(stimulus->response) ; p(stimulus->response) ; n(response)
        @figure 2
        @plot v(stimulus->response) ; p(stimulus->response) ; n(response)
        """
        run(text)

        exprs = ['v(stimulus->response)', 'p(stimulus->response)', 'n(response)']
        self.checkExport('export1', n_subjects=1, exprs=exprs, figure_number=1)
        self.checkExport('export2', n_subjects=3, exprs=exprs, figure_number=2)

    def checkExport(self, filename_base, n_subjects, exprs, figure_number):
        exported_titles_expected = ['x']
        if n_subjects == 1:
            exported_titles_expected.extend(exprs)
        else:
            for expr in exprs:
                for i in range(n_subjects):
                    exported_titles_expected.append(expr + ' subject ' + str(i + 1))

        file_prop = filename_base + '_prop.txt'
        file_line = filename_base + '_line.txt'

        file_prop = os.path.join('.', 'tests', 'exported_files', file_prop)
        file_line = os.path.join('.', 'tests', 'exported_files', file_line)
        self.assertAlmostEqualFile(file_prop, file_line)
        exported_titles, exported_data = get_csv_file_contents(file_prop)
        self.assertListEqual(exported_titles, exported_titles_expected)
        pd = get_plot_data(figure_number=figure_number)
        self.assertPlotExportEqual(pd, exported_titles_expected[1:], exported_data)



class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_wrong_syntax_vexport(self):
        def get_script(cmd):
            return f"""
                mechanism: ga
                stimulus_elements: s1, s2
                behaviors: b
                alpha_v: 1
                alpha_w: 1
                start_v: s1->b:7, default:1.5

                @phase foo stop:s1=2
                L1 s1 | L1

                filename: foo.txt

                {cmd}
            """

        text = get_script("@vexport s1->b, s1->b->s2")
        msg = "Error on line 14: Expression must include only one '->'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = get_script("@vexport s1->b, s1->b->s2,")
        msg = "Error on line 14: Expression must include only one '->'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = get_script("@vexport s1->b, foo.txt")
        msg = "Error on line 14: Expected a behavior name, got b,."
        with self.assertRaisesMsg(msg):
            run(text)

        text = get_script("@vexport xxx foo.txt")
        msg = "Error on line 14: Expression must include a '->'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = get_script("@vexport foo.txt")
        msg = "Error on line 14: Expression must include a '->'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = get_script("@vexport s1->b b b foo.txt")
        msg = "Error on line 14: Too many components: 's1->b b b foo.txt'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = get_script("@vexport s1->")
        msg = "Error on line 14: Expected a behavior name, got ."
        with self.assertRaisesMsg(msg):
            run(text)

        text = get_script("@vexport s1->  ,  foo.txt")
        msg = "Error on line 14: Expected a behavior name, got ,."
        with self.assertRaisesMsg(msg):
            run(text)
