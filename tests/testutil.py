import os.path
import unittest
import matplotlib.pyplot as plt
import re

from parsing import Script


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


def remove_files(filenames):
    for filename in filenames:
        fullpath = "./tests/exported_files/{}".format(filename)
        if os.path.isfile(fullpath):
            os.remove(fullpath)


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


class LsTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def assertRaisesMsg(self, msg):
        return super().assertRaisesRegex(Exception, re.escape(msg))

    def assertAlmostEqualList(self, list1, list2, places=7):
        self.assertEqual(len(list1), len(list2))
        for val1, val2 in zip(list1, list2):
            self.assertAlmostEqual(val1, val2, places)

    def assert_files_are_removed(self, filenames):
        for filename in filenames:
            fullpath = "./tests/exported_files/{}".format(filename)
            self.assertFalse(os.path.isfile(fullpath))

    def assert_files_exist(self, filenames):
        for filename in filenames:
            fullpath = "./tests/exported_files/{}".format(filename)
            self.assertTrue(os.path.isfile(fullpath))

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
