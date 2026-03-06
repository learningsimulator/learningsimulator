import os
import shutil
import tempfile
import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, create_exported_files_folder, remove_exported_files, delete_exported_files_folder


CUSTOM_MECHANISM_CODE = '''
from mechanism import Mechanism
import keywords as kw

class MyCustomModel(Mechanism):
    name = 'mycustom'
    variables = ('v', 'w')

    def learn(self, stimulus):
        u = self.parameters.get(kw.U)
        c = self.parameters.get(kw.BEHAVIOR_COST)
        alpha_v = self.parameters.get(kw.ALPHA_V)
        alpha_w = self.parameters.get(kw.ALPHA_W)

        usum, wsum_prev = 0, 0
        for element in stimulus:
            usum += u[element]
        for element in self.prev_stimulus:
            wsum_prev += self.w[element]

        for element in self.prev_stimulus:
            alpha_v_er = alpha_v[(element, self.response)]
            self.v[(element, self.response)] += alpha_v_er * (usum - wsum_prev - c[self.response])

        for element in self.prev_stimulus:
            alpha_w_e = alpha_w[element]
            self.w[element] += alpha_w_e * (usum - wsum_prev)

    def has_w(self):
        return True
'''


class TestImportMechanism(LsTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mechanism_file = os.path.join(self.tmpdir, 'my_model.py')
        with open(self.mechanism_file, 'w') as f:
            f.write(CUSTOM_MECHANISM_CODE)
        create_exported_files_folder()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        delete_exported_files_folder()
        plt.close('all')

    def test_basic_import(self):
        text = f'''
        @import {self.mechanism_file}
        mechanism: mycustom
        stimulus_elements: s1, s2
        behaviors: b1, b2
        alpha_v: 0.1
        alpha_w: 0.1
        u: s1:1, default:0

        @phase foo stop: s1=5
        S1 s1 | S1
        S2 s2 | S1

        @run foo
        '''
        run(text)

    def test_import_with_export(self):
        export_file = os.path.join('.', 'tests', 'exported_files', 'custom_mech_export.csv')
        text = f'''
        @import {self.mechanism_file}
        mechanism: mycustom
        stimulus_elements: s1, s2
        behaviors: b1, b2
        alpha_v: 0.1
        alpha_w: 0.1
        u: s1:1, default:0

        @phase foo stop: s1=5
        S1 s1 | S1
        S2 s2 | S1

        @run foo

        @vexport s1->b1 {export_file}
        '''
        run(text)
        self.assertTrue(os.path.isfile(export_file))
        remove_exported_files(['custom_mech_export.csv'])

    def test_import_file_not_found(self):
        text = '''
        @import /nonexistent/path/model.py
        mechanism: ga
        stimulus_elements: s1
        behaviors: b1
        alpha_v: 0.1
        '''
        msg = f"Error on line 2: Import file not found: /nonexistent/path/model.py"
        with self.assertRaisesMsg(msg):
            run(text)

    def test_import_no_mechanism_class(self):
        empty_file = os.path.join(self.tmpdir, 'empty_model.py')
        with open(empty_file, 'w') as f:
            f.write('x = 42\n')
        text = f'''
        @import {empty_file}
        mechanism: ga
        stimulus_elements: s1
        behaviors: b1
        alpha_v: 0.1
        '''
        msg = f"Error on line 2: No Mechanism subclass with a 'name' attribute found in {empty_file}."
        try:
            with self.assertRaisesMsg(msg):
                run(text)
        finally:
            os.remove(empty_file)

    def test_invalid_mechanism_name_includes_custom(self):
        text = f'''
        @import {self.mechanism_file}
        mechanism: nonexistent
        stimulus_elements: s1
        behaviors: b1
        alpha_v: 0.1
        '''
        with self.assertRaises(Exception) as cm:
            run(text)
        self.assertIn('mycustom', str(cm.exception))
