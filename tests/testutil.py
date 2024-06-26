import os.path
import unittest
import matplotlib.pyplot as plt
import re
import csv

from parsing import Script
from PIL import Image, UnidentifiedImageError


def run(text):
    script_obj = Script(text)
    script_obj.parse()
    script_output = script_obj.run()
    script_obj.postproc(script_output)
    script_obj.plot(block=False)
    return script_obj, script_output


def check_run_output_subject(test_obj, output):
    check_run_output_subject_vw(test_obj, output.v)
    if hasattr(output, 'w'):
        check_run_output_subject_vw(test_obj, output.w)


def check_run_output_subject_vw(test_obj, output_vw):
    # Check that each steps-list starts with 0 and ends with the same value
    max_step = 0
    for key, val in output_vw.items():
        test_obj.assertEqual(val.steps[0], 0)
        if max_step == 0:
            max_step = val.steps[-1]
        test_obj.assertEqual(val.steps[-1], max_step)

    # Check that no values (except 0 and max_step) occur more than once
    steps_union = set()
    for key, val in output_vw.items():
        for step in val.steps:
            if step != 0 and step != max_step:
                test_obj.assertNotIn(step, steps_union)
                steps_union.add(step)
    all_steps = list(steps_union)
    all_steps.sort()
    test_obj.assertEqual(all_steps, list(range(1, max_step)))


def create_exported_files_folder():
    exported_files_folder = os.path.join('.', 'tests', 'exported_files')
    if not os.path.exists(exported_files_folder):
        access_rights = 0o777
        os.mkdir(exported_files_folder, access_rights)


def delete_exported_files_folder():
    exported_files_folder = os.path.join('.', 'tests', 'exported_files')

    if os.path.exists(exported_files_folder):

        # Delete all files in the folder
        for filename in os.listdir(exported_files_folder):
            file_path = os.path.join(exported_files_folder, filename)
            os.remove(file_path)

        # Delete the folder itself
        os.rmdir(exported_files_folder)


def remove_exported_files(filenames=None):
    if filenames is None:
        filenames = os.listdir(os.path.join('.', 'tests', 'exported_files')) 
    for filename in filenames:
        filepath = os.path.join('.', 'tests', 'exported_files', filename)
        if os.path.isfile(filepath):
            os.remove(filepath)


def get_plot_data(figure_number=1, axes_number=1):
    """figure_number and axes_number are 1-index based."""
    axes = plt.figure(figure_number).axes
    ax = axes[axes_number - 1]

    lines = ax.get_lines()
    if len(lines) == 1:
        line = lines[0]
        return {'x': list(line.get_xdata(True)),
                'y': list(line.get_ydata(True))}
    else:
        out = dict()
        for line in lines:
            out[line.get_label()] = {'x': list(line.get_xdata(True)),
                                     'y': list(line.get_ydata(True))}
        return out

def get_csv_file_contents(file):
    data = None
    with open(file) as f:
        reader = csv.reader(f)
        data = list(reader)
    titles = data[0]
    data_rows = data[1:]
    return titles, data_rows


class LsTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def assertRaisesMsg(self, msg):
        return super().assertRaisesRegex(Exception, '^' + re.escape(msg) + '$')

    def assertAlmostEqualList(self, list1, list2, places=7):
        self.assertEqual(len(list1), len(list2))
        for val1, val2 in zip(list1, list2):
            self.assertAlmostEqual(val1, val2, places)

    def assertAlmostEqualFile(self, file1, file2, places=7):
        data1 = None
        with open(file1) as file:
            reader = csv.reader(file)
            data1 = list(reader)
        self.assertIsNotNone(data1)

        data2 = None
        with open(file2) as file:
            reader = csv.reader(file)
            data2 = list(reader)
        self.assertIsNotNone(data2)

        titles1 = data1[0]
        titles2 = data2[0]
        self.assertEqual(len(titles1), len(titles2))
        for title1, title2 in zip(titles1, titles2):
            self.assertEqual(title1, title2)

        data_rows1 = data1[1:]
        data_rows2 = data2[1:]
        for data_row1, data_row2 in zip(data_rows1, data_rows2):
            self.assertAlmostEqualList(data_row1, data_row2)

    def assert_exported_files_are_removed(self, filenames=None):
        if filenames is None:
            filenames = os.listdir(os.path.join('.', 'tests', 'exported_files')) 
        for filename in filenames:
            fullpath = os.path.join('.', 'tests', 'exported_files', filename)
            self.assertFalse(os.path.isfile(fullpath))

    def assert_exported_files_exist(self, filenames):
        for filename in filenames:
            filepath = os.path.join('.', 'tests', 'exported_files', filename)
            self.assertTrue(os.path.isfile(filepath), msg=f"{filepath} does not exist.") 

    def assertImageFileFormat(self, f, fileformat):
        cannot_open = ('pdf', 'raw', 'rgba', 'svg', 'svgz', 'pgf')
        try:
            im = Image.open(f)
            self.assertTrue(fileformat not in cannot_open)
        except UnidentifiedImageError as ex:
            self.assertTrue(fileformat in cannot_open)
            return
        except Exception as ex:
            self.assertTrue(False, f"Unexpected exception raised when opening {fileformat} file: {ex}")
            return

        info = im.info
        im.close()

        if fileformat in ('eps', 'ps'):
            check = 'PS-Adobe' in info
        elif fileformat in ('jpeg', 'jpg'):
            check = 'jfif' in info
        elif fileformat == 'png':
            check = 'dpi' in info
        elif fileformat in ('tif', 'tiff'):
            check = ('dpi' in info and 'compression' in info)
        elif fileformat == 'webp':
            check = ('loop' in info and 'background' in info)
        else:
            assert(False), f"Internal error: Test for file format {fileformat} not implemented."
        
        self.assertTrue(check), f"File {f} is not a {fileformat} file."

    def assertIncreasing(self, list1):
        is_increasing = True
        if len(list1) > 0:
            prev = list1[0]
            for x in list1[1:]:
                is_increasing = (x >= prev)
                if not is_increasing:
                    break
                prev = x
        self.assertTrue(is_increasing)

    def assertPlotExportEqual(self, pd, plot_legends, exported_data):
        # Check that all plot data have the same length as exported data 
        n_exported_data = len(exported_data)
        for plot_legend in plot_legends:
            self.assertEqual(len(pd[plot_legend]['x']), n_exported_data)
            self.assertEqual(len(pd[plot_legend]['y']), n_exported_data)

        # Check that y-values for all plots are the same as exported data
        for i in range(n_exported_data):
            e = exported_data[i]
            x = pd[plot_legends[0]]['x'][i]
            self.assertAlmostEqual(x, float(e[0]))
            for j, plot_legend in enumerate(plot_legends):
                y = pd[plot_legend]['y'][i]
                self.assertAlmostEqual(y, float(e[j + 1]))

    def assertImageDPI(self, filename, dpi):
        im = Image.open(filename)
        dpi_x, dpi_y = im.info['dpi']
        im.close()
        self.assertAlmostEqual(dpi_x, dpi, delta=0.1)
        self.assertAlmostEqual(dpi_y, dpi, delta=0.1)
