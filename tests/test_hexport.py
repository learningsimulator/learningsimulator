import matplotlib.pyplot as plt
import csv
import os

from .testutil import LsTestCase, run, remove_exported_files, create_exported_files_folder, delete_exported_files_folder


class TestHExport(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        create_exported_files_folder()

    def tearDown(self):
        delete_exported_files_folder()
        plt.close('all')

    def test_issue_57(self):
        file = 'test_issue_57.txt'
        filepath = os.path.join('.', 'tests', 'exported_files', file)
        remove_exported_files([file])
        self.assert_exported_files_are_removed([file])

        text = '''
        n_subjects: 2
        stimulus_elements: s1, s2
        behaviors: b1, b2
        mechanism: ga

        @phase foo stop: s1=5
        S1 s1 | S2(0.5) | S1
        S2 s2 | S1

        @run foo

        @hexport ./tests/exported_files/test_issue_57.txt
        '''
        successful_attempt = False
        while not successful_attempt:
            run(text)
            self.assert_exported_files_exist([file])
            last_row = None
            with open(filepath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    last_row = row
            successful_attempt = (' ' in last_row)
        self.assertEqual(last_row.count(' '), 2)

        with open(filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    self.assertEqual(row, ["step", "stimulus subject 0", "response subject 0", "stimulus subject 1", "response subject 1"])
                else:
                    self.assertEqual(len(row), 5)
                line_count += 1


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
        msg = "There is no @RUN."
        with self.assertRaisesMsg(msg):
            run(text)
