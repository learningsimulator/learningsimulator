import matplotlib as mpl
import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data, remove_exported_files, delete_exported_files_folder, create_exported_files_folder

FILEFORMATS = ['eps', 'jpeg', 'jpg', 'pdf', 'png', 'ps', 
               'pgf', # (possibly starts LaTeX)
               'raw', 'rgba', 'svg', 'svgz', 'tif', 'tiff', 'webp']

FILEFORMATS_SHORT = ['jpg', 'pdf', 'png', 'ps', 
                     'pgf', # (possibly starts LaTeX)
                     'raw', 'rgba', 'svg', 'tif', 'webp']

class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        create_exported_files_folder()

    def tearDown(self):
        plt.close('all')

        remove_exported_files()
        self.assert_exported_files_are_removed()
        delete_exported_files_folder()

    def test_single_subject(self):
        text = '''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : response, no_response
        stimulus_elements : background, stimulus, reward
        start_v           : default:-1
        alpha_v           : 0.1
        u                 : reward:10, default:0

        @PHASE training stop: stimulus=10
        @new_trial  stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @new_trial
        NO_REWARD   background | @new_trial

        @run training

        @figure 1
        @panel 111 subplot title 1   {'facecolor':'red'}
        subject: average
        @vplot stimulus->response

        @figure 2
        @subplot (1,   1,1  ) subplot title 2
        @vplot stimulus->response

        @figure 3
        @subplot 224 subplot title 3{'facecolor':'red'}
        @vplot stimulus->response

        @figure 4
        @subplot (  2,2,4  ) subplot title 4
        @vplot stimulus->response

        @figure 5
        @subplot (4,4,16)
        @vplot stimulus->response
        '''
        run(text)

        ax1 = plt.figure(1).axes[0]
        ax2 = plt.figure(2).axes[0]
        ax3 = plt.figure(3).axes[0]
        ax4 = plt.figure(4).axes[0]

        self.assertEqual(ax1.get_title(), "subplot title 1")
        self.assertEqual(ax2.get_title(), "subplot title 2")
        self.assertEqual(ax3.get_title(), "subplot title 3")
        self.assertEqual(ax4.get_title(), "subplot title 4")

        self.assertEqual(ax1.get_facecolor(), (1, 0, 0, 1))
        self.assertEqual(ax2.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(ax3.get_facecolor(), (1, 0, 0, 1))
        self.assertEqual(ax4.get_facecolor(), (1, 1, 1, 1))

        pos1 = ax1.get_position()
        pos2 = ax2.get_position()
        pos3 = ax3.get_position()
        pos4 = ax4.get_position()

        self.assertEqual(pos1.x0, pos2.x0)
        self.assertEqual(pos1.y0, pos2.y0)
        self.assertEqual(pos3.x0, pos4.x0)
        self.assertEqual(pos3.y0, pos4.y0)
        self.assertGreater(pos3.x0, pos1.x0)
        self.assertEqual(pos3.y0, pos1.y0)

        plot_data1 = get_plot_data(figure_number=1, axes_number=1)
        plot_data2 = get_plot_data(figure_number=2, axes_number=1)
        self.assertEqual(plot_data1, plot_data2)

    def test_subplotgrid_in_figure(self):
        text = '''
        mechanism: sr
        n_subjects = 1
        stimulus_elements: s1, s2
        behaviors: b1, b2
        alpha_v: 1
        u: s1:0, s2:10, default:0

        @phase phase1 stop:s1=10
        START     s1 | b1:S2 | START
        S2        s2 | START

        @run phase1

        xscale = s1

        @figure(1,2) Figure number one
        @subplot  Subplot number one
        @nplot s1->b1
        @subplot  Subplot number two {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2

        @figure Figure number two
        @subplot 121  Subplot number one
        @nplot s1->b1
        @subplot 122 Subplot number two {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2

        @figure(12) Figure number three
        subplottitle = Subplot number one
        @subplot
        @nplot s1->b1
        subplottitle = Subplot number two
        @panel {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2

        @figure Figure number four
        subplottitle = Subplot number one
        @subplot 121
        @nplot s1->b1
        subplottitle = Subplot number two
        @subplot 122 {'facecolor': (0.5, 0.6, 0.7)}
        @nplot s1->b2
        '''
        run(text)

        fig1_ax1 = plt.figure(1).axes[0]
        fig1_ax2 = plt.figure(1).axes[1]

        fig2_ax1 = plt.figure(2).axes[0]
        fig2_ax2 = plt.figure(2).axes[1]

        fig3_ax1 = plt.figure(3).axes[0]
        fig3_ax2 = plt.figure(3).axes[1]

        fig4_ax1 = plt.figure(1).axes[0]
        fig4_ax2 = plt.figure(1).axes[1]

        self.assertEqual(plt.figure(1)._suptitle.get_text(), "Figure number one")
        self.assertEqual(plt.figure(2)._suptitle.get_text(), "Figure number two")
        self.assertEqual(plt.figure(3)._suptitle.get_text(), "Figure number three")
        self.assertEqual(plt.figure(4)._suptitle.get_text(), "Figure number four")

        self.assertEqual(fig1_ax1.get_title(), "Subplot number one")
        self.assertEqual(fig2_ax1.get_title(), "Subplot number one")
        self.assertEqual(fig3_ax1.get_title(), "Subplot number one")
        self.assertEqual(fig4_ax1.get_title(), "Subplot number one")

        self.assertEqual(fig1_ax2.get_title(), "Subplot number two")
        self.assertEqual(fig2_ax2.get_title(), "Subplot number two")
        self.assertEqual(fig3_ax2.get_title(), "Subplot number two")
        self.assertEqual(fig4_ax2.get_title(), "Subplot number two")

        self.assertEqual(fig1_ax1.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(fig2_ax1.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(fig3_ax1.get_facecolor(), (1, 1, 1, 1))
        self.assertEqual(fig4_ax1.get_facecolor(), (1, 1, 1, 1))

        self.assertEqual(fig1_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))
        self.assertEqual(fig2_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))
        self.assertEqual(fig3_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))
        self.assertEqual(fig4_ax2.get_facecolor(), (0.5, 0.6, 0.7, 1))

        self.assertEqual(fig1_ax1.get_position().x0, fig2_ax1.get_position().x0)
        self.assertEqual(fig1_ax1.get_position().x0, fig3_ax1.get_position().x0)
        self.assertEqual(fig1_ax1.get_position().x0, fig4_ax1.get_position().x0)

        self.assertEqual(fig1_ax1.get_position().y0, fig2_ax1.get_position().y0)
        self.assertEqual(fig1_ax1.get_position().y0, fig3_ax1.get_position().y0)
        self.assertEqual(fig1_ax1.get_position().y0, fig4_ax1.get_position().y0)

    def test_subplot_22(self):
        text = '''
        @figure(2,2)
        @subplot 1
        @subplot 2
        @panel   3
        @subplot 4

        @figure
        @subplot 221 1
        @subplot 222 2
        @subplot 223 3
        @panel   224 4
        '''
        run(text)

        ax1 = plt.figure(1).axes[0]
        ax2 = plt.figure(1).axes[1]
        ax3 = plt.figure(1).axes[2]
        ax4 = plt.figure(1).axes[3]
        self.assertEqual(ax1.get_title(), "1")
        self.assertEqual(ax2.get_title(), "2")
        self.assertEqual(ax3.get_title(), "3")
        self.assertEqual(ax4.get_title(), "4")

        ax1 = plt.figure(2).axes[0]
        ax2 = plt.figure(2).axes[1]
        ax3 = plt.figure(2).axes[2]
        ax4 = plt.figure(2).axes[3]
        self.assertEqual(ax1.get_title(), "1")
        self.assertEqual(ax2.get_title(), "2")
        self.assertEqual(ax3.get_title(), "3")
        self.assertEqual(ax4.get_title(), "4")

    def test_figprops(self):
        text = '''
        mechanism: sr
        stimulus_elements: s1, s2, s3, s4
        behaviors: b1, b2, b3, b4
        alpha_v: 1

        @phase foo stop:s1=10
        L1 s1 | L1

        @run foo
        
	    xscale: s1

        @figure(2,2) {'facecolor': 'red', 'edgecolor':[0,0,1]}

	    @subplot n
        @plot n(s1)

	    @subplot 2n
        @plot n(s1) * 2

	    @subplot n^2
        @plot n(s1) ** 2

	    @subplot sqrt(n)
        @plot sqrt(n(s1))

        @figure {'facecolor': [0.5, 0.6, 0.7], 'edgecolor': [0, 1, 0]}
        @plot n(s1)

        @figure my title     {'facecolor': [0.5, 0.6, 0.7], 'edgecolor':'blue'}
        @plot n(s1)
        '''
        run(text)
        self.assertEqual(plt.figure(1).get_facecolor(), (1.0, 0.0, 0.0, 1.0))
        self.assertEqual(plt.figure(1).get_edgecolor(), (0.0, 0.0, 1.0, 1.0))

        self.assertEqual(plt.figure(2).get_facecolor(), (0.5, 0.6, 0.7, 1.0))
        self.assertEqual(plt.figure(2).get_edgecolor(), (0.0, 1.0, 0.0, 1.0))

        self.assertEqual(plt.figure(3).get_facecolor(), (0.5, 0.6, 0.7, 1.0))
        self.assertEqual(plt.figure(3).get_edgecolor(), (0.0, 0.0, 1.0, 1.0))
        self.assertEqual(plt.figure(3)._suptitle.get_text(), "my title")


    def test_prop_combinations_with_subplot(self):
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b
        alpha_v: 1

        @phase foo stop:s=10
        L1 s | L1

        @run foo
        
        @figure
        @plot n(s)

        @figure(3,3) my title
	    @subplot
	    @plot n(s)

        @figure(33)  my title {'facecolor': 'red'}
	    @subplot
	    @plot n(s)

        @figure(12)  {'facecolor': 'red'}
	    @subplot
	    @plot n(s)

        @figure(13)  filename:./tests/exported_files/my_file1.png
	    @subplot
	    @plot n(s)

        @figure(3,1) filename:./tests/exported_files/my_file2.png {'dpi': 150}
	    @subplot
	    @plot n(s)

        @figure(1,2) my title filename:    ./tests/exported_files/my_file3.png
	    @subplot
	    @plot n(s)

        @figure(2,1) my title {'facecolor': 'red'} filename: ./tests/exported_files/my_file4.png
	    @subplot
	    @plot n(s)

        @figure(32)  {'facecolor': 'red'} filename: ./tests/exported_files/my_file5.png
	    @subplot
	    @plot n(s)

        @figure(3,2) my title filename:./tests/exported_files/my_file6.png {'dpi': 150}
	    @subplot
	    @plot n(s)

        @figure(1,1) my title   {'facecolor': 'red'}          filename: ./tests/exported_files/my_file7.png   {'dpi': 150}
	    @subplot
	    @plot n(s)

        @figure(11)  {'facecolor': 'red'} filename:./tests/exported_files/my_file8.png {'dpi': 200}
	    @subplot
	    @plot n(s)
        '''
        run(text)

        default_facecolor = plt.figure(1).get_facecolor()
        red = (1.0, 0.0, 0.0, 1.0)

        # The displayed figures

        self.assertEqual(set(plt.get_fignums()), {1, 2, 3, 4})  # Three figs to display
        
        self.assertEqual(plt.figure(2)._suptitle.get_text(), "my title")
        self.assertEqual(plt.figure(2).get_facecolor(), default_facecolor)

        self.assertEqual(plt.figure(3)._suptitle.get_text(), " my title")
        self.assertEqual(plt.figure(3).get_facecolor(), red)
        
        self.assertEqual(plt.figure(4)._suptitle.get_text(), "")
        self.assertEqual(plt.figure(4).get_facecolor(), red)

        # The saved figures
        FILENAMES = ['my_file1.png',
                     'my_file2.png',
                     'my_file3.png',
                     'my_file4.png',
                     'my_file5.png',
                     'my_file6.png',
                     'my_file7.png',
                     'my_file8.png'
                    ]
        self.assert_exported_files_exist(FILENAMES)
        self.assertImageDPI('./tests/exported_files/my_file1.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file2.png', 150)
        self.assertImageDPI('./tests/exported_files/my_file3.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file4.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file5.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file6.png', 150)
        self.assertImageDPI('./tests/exported_files/my_file7.png', 150)
        self.assertImageDPI('./tests/exported_files/my_file8.png', 200)

    def test_prop_combinations_without_subplot(self):
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b
        alpha_v: 1

        @phase foo stop:s=10
        L1 s | L1

        @run foo
        
        @figure
        @plot n(s)

        @figure my title
	    @subplot
	    @plot n(s)

        @figure  my title {'facecolor': 'red'}
	    @subplot
	    @plot n(s)

        @figure  {'facecolor': 'red'}
	    @subplot
	    @plot n(s)

        @figure  filename:./tests/exported_files/my_file1.png
	    @subplot
	    @plot n(s)

        @figure filename:./tests/exported_files/my_file2.png {'dpi': 150}
	    @subplot
	    @plot n(s)

        @figure my title filename:    ./tests/exported_files/my_file3.png
	    @subplot
	    @plot n(s)

        @figure my title {'facecolor': 'red'} filename: ./tests/exported_files/my_file4.png
	    @subplot
	    @plot n(s)

        @figure  {'facecolor': 'red'} filename: ./tests/exported_files/my_file5.png
	    @subplot
	    @plot n(s)

        @figure my title filename:./tests/exported_files/my_file6.png {'dpi': 150}
	    @subplot
	    @plot n(s)

        @figure my title   {'facecolor': 'red'}          filename: ./tests/exported_files/my_file7.png   {'dpi': 150}
	    @subplot
	    @plot n(s)

        @figure  {'facecolor': 'red'} filename:./tests/exported_files/my_file8.png {'dpi': 200}
	    @subplot
	    @plot n(s)
        '''
        run(text)

        default_facecolor = plt.figure(1).get_facecolor()
        red = (1.0, 0.0, 0.0, 1.0)

        # The displayed figures

        self.assertEqual(set(plt.get_fignums()), {1, 2, 3, 4})  # Three figs to display
        
        self.assertEqual(plt.figure(2)._suptitle.get_text(), "my title")
        self.assertEqual(plt.figure(2).get_facecolor(), default_facecolor)

        self.assertEqual(plt.figure(3)._suptitle.get_text(), " my title")
        self.assertEqual(plt.figure(3).get_facecolor(), red)
        
        self.assertEqual(plt.figure(4)._suptitle.get_text(), "")
        self.assertEqual(plt.figure(4).get_facecolor(), red)

        # The saved figures
        FILENAMES = ['my_file1.png',
                     'my_file2.png',
                     'my_file3.png',
                     'my_file4.png',
                     'my_file5.png',
                     'my_file6.png',
                     'my_file7.png',
                     'my_file8.png'
                    ]
        self.assert_exported_files_exist(FILENAMES)
        self.assertImageDPI('./tests/exported_files/my_file1.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file2.png', 150)
        self.assertImageDPI('./tests/exported_files/my_file3.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file4.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file5.png', 100)
        self.assertImageDPI('./tests/exported_files/my_file6.png', 150)
        self.assertImageDPI('./tests/exported_files/my_file7.png', 150)
        self.assertImageDPI('./tests/exported_files/my_file8.png', 200)

    # test paths
    # test file types
    # test file names with and without ext (filename.blabla)
    # test dpi, format in savefig_props
    def test_fileformats(self):
        def get_script(fileformat):
            text = f'''
            mechanism: sr
            stimulus_elements: s
            behaviors: b
            alpha_v: 1

            @phase foo stop:s=10
            L1 s | L1

            @run foo
        
            # Should create my_file1
            @figure filename:./tests/exported_files/my_file1    {{'dpi':150, 'format':'{fileformat}'}}
            @plot n(s)

            # Should create my_file2.{fileformat}
            @figure filename:./tests/exported_files/my_file2.{fileformat}    {{'dpi':150, 'format':'{fileformat}'}}
            @plot n(s)

            # Should create my_file3.{fileformat}
            @figure filename:./tests/exported_files/my_file3.{fileformat}    {{'dpi':150}}
            @plot n(s)

            # Should create my_file1.blabla
            @figure filename:./tests/exported_files/my_file1.blabla    {{'dpi':150, 'format':'{fileformat}'}}
            @plot n(s)

            # Should create my_file2.blabla.{fileformat}
            @figure filename:./tests/exported_files/my_file2.blabla.{fileformat}    {{'dpi':150, 'format':'{fileformat}'}}
            @plot n(s)

            # Should create my_file3.blabla.{fileformat}
            @figure filename:./tests/exported_files/my_file3.blabla.{fileformat}    {{'dpi':150}}
            @plot n(s)

            # Should create my_file4.jpg.{fileformat}
            @figure filename:./tests/exported_files/my_file4.jpg.{fileformat}    {{'dpi':150, 'format':'{fileformat}'}}
            @plot n(s)
            '''
            return text

        for fileformat in FILEFORMATS:
            text = get_script(fileformat)
            run(text)

            expected_created_files = [f'my_file1',
                                      f'my_file2.{fileformat}',
                                      f'my_file3.{fileformat}',
                                      f'my_file1.blabla',
                                      f'my_file2.blabla.{fileformat}',
                                      f'my_file3.blabla.{fileformat}',
                                      f'my_file4.jpg.{fileformat}'
                                      ]
            self.assert_exported_files_exist(expected_created_files)

            for f in expected_created_files:
                self.assertImageFileFormat(f"./tests/exported_files/{f}", fileformat)

    def test_fileformats_with_ext(self):
        def get_script(fileformat, ext):
            text = f'''
            mechanism: sr
            stimulus_elements: s
            behaviors: b
            alpha_v: 1

            @phase foo stop:s=10
            L1 s | L1

            @run foo
        
            # Should create my_file.{ext}
            @figure filename:./tests/exported_files/my_file.{ext}    {{'dpi':150, 'format':'{fileformat}'}}
            @plot n(s)
            '''
            return text
        
        for fileformat in FILEFORMATS_SHORT:
            for ext in FILEFORMATS_SHORT:
                if fileformat != ext:
                    text = get_script(fileformat, ext)
                    run(text)
                    self.assert_exported_files_exist([f'my_file.{ext}'])
                    self.assertImageFileFormat(f"./tests/exported_files/my_file.{ext}", fileformat)

    def test_default_fileformat(self):
        default_format = mpl.rcParams["savefig.format"]

        text = f'''
        mechanism: sr
        stimulus_elements: s
        behaviors: b
        alpha_v: 1

        @phase foo stop:s=10
        L1 s | L1

        @run foo
    
        # Should create my_file_def.{default_format} (since {default_format} is default)
        @figure filename:./tests/exported_files/my_file_def    {{'dpi':150}}
        @plot n(s)
        '''
        run(text)
        self.assert_exported_files_exist([f'my_file_def.{default_format}'])
        self.assertImageFileFormat(f"./tests/exported_files/my_file_def.{default_format}", default_format)
        
    def test_title(self):
        # test parameter title
        text = '''
        mechanism: sr
        stimulus_elements: s
        behaviors: b
        alpha_v: 1

        @phase foo stop:s=10
        L1 s | L1

        @run foo
    
        title = My title 1
        @figure filename:./tests/exported_files/my_file_title1.png    {{'dpi':150}}
        @plot n(s)

        title = My title 2
        @figure filename:./tests/exported_files/my_file_title2.png
        @plot n(s)

        title = My title 3
        @figure {'facecolor': 'blue'}
        @plot n(s)

        title = BLAPS
        @figure My title 4 {'facecolor': 'blue'}
        @plot n(s)

        title = BLABLA
        @figure My title 5
        @plot n(s)
        '''
        run(text)

        self.assertEqual(plt.figure(3)._suptitle.get_text(), "My title 3")
        self.assertEqual(plt.figure(4)._suptitle.get_text(), "My title 4")
        self.assertEqual(plt.figure(5)._suptitle.get_text(), "My title 5")


class TestExceptions(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    @staticmethod
    def get_text(subplot_args):
        return f'''
        n_subjects        : 1
        mechanism         : sr
        behaviors         : response, no_response
        stimulus_elements : background, stimulus, reward
        start_v           : default:-1
        alpha_v           : 0.1
        u                 : reward:10, default:0

        @PHASE training stop: stimulus=10
        @new_trial  stimulus   | response: REWARD | NO_REWARD
        REWARD      reward     | @new_trial
        NO_REWARD   background | @new_trial

        @run training

        @figure 1
        @subplot {subplot_args}
        @vplot stimulus->response
        '''

    def test_errors(self):
        text = self.get_text("112 subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument 112."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text(" (1 , 1   ,2   ) subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument (1, 1, 2)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("foo subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument foo."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,4,17) subplot title 1")
        msg = "Error on line 18: Invalid @subplot argument (4, 4, 17)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,0,10)")
        msg = "Error on line 18: Invalid @subplot argument (4, 0, 10)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,1)")
        msg = "Error on line 18: Invalid @subplot argument (4, 1)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(a,   1)")
        msg = "Error on line 18: Invalid @subplot argument (a,."  # Since (a,1) is not a tuple since a is undefined
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(4,)")
        msg = "Error on line 18: Invalid @subplot argument (4,)."
        with self.assertRaisesMsg(msg):
            run(text)

        text = self.get_text("(-42,4)")
        msg = "Error on line 18: Invalid @subplot argument (-42, 4)."
        with self.assertRaisesMsg(msg):
            run(text)

    def test_errors_subplotgrid_in_figure(self):
        text = """
        @figure
        @subplot foo # Should give error since foo is not subplotspec
        """
        msg = "Error on line 3: Invalid @subplot argument foo."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figurefoo
        @subplot foo
        """
        msg = "Error on line 2: Invalid expression '@figurefoo'."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(foo)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(121)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1,foo)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1,-1)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1,1,4)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @figure(1, 1.4)
        @subplot foo
        """
        msg = "Error on line 2: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        text = """
        @variables m = 1, n = 2
        @figure(m,n)
        @subplot foo
        """
        msg = "Error on line 3: Invalid @figure command."
        with self.assertRaisesMsg(msg):
            run(text)

        # Disabled test until this error message is propagated to GUI.
        # Currently the error message depends on Python version.        
        # text = """
        # @figure(2,2)
        # @subplot
        # @subplot
        # @subplot
        # @subplot
        # @subplot  # One too many
        # """
        # msg = "num must be 1 <= num <= 4, not 5"
        # with self.assertRaisesMsg(msg):
        #     run(text)

    def test_wrong_filespecs(self):
        text = '''
        mechanism: sr
        stimulus_elements: s1, s2, s3, s4
        behaviors: b1, b2, b3, b4
        alpha_v: 1

        @phase foo stop:s1=10
        L1 s1 | L1

        @run foo
        
	    xscale: s1

        @figure filename:my_file1.blabla {'dpi':50}
        '''
        msg = "Format 'blabla' is not supported (supported formats: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp)"
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: s1, s2, s3, s4
        behaviors: b1, b2, b3, b4
        alpha_v: 1

        @phase foo stop:s1=10
        L1 s1 | L1

        @run foo
        
	    xscale: s1

        @figure filename:my_file1 {'dpi':50, 'format':'foobar'}
        '''
        msg = "Format 'foobar' is not supported (supported formats: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp)"
        with self.assertRaisesMsg(msg):
            run(text)

        text = '''
        mechanism: sr
        stimulus_elements: s1, s2, s3, s4
        behaviors: b1, b2, b3, b4
        alpha_v: 1

        @phase foo stop:s1=10
        L1 s1 | L1

        @run foo
        
	    xscale: s1

        @figure filename:my_file1 {'dpi':-50}
        '''
        msg = "dpi must be positive"
        with self.assertRaisesMsg(msg):
            run(text)
