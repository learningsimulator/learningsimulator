import unittest
import matplotlib.pyplot as plt

from parsing import Script


def get_plotdata(fig_num):
    ax = plt.figure(fig_num).axes
    # self.assertEqual(len(ax), 1)
    lines = ax[0].get_lines()
    # self.assertEqual(len(lines), 1)
    x = lines[0].get_xdata(True)
    y = lines[0].get_ydata(True)
    return list(x), list(y)


class TestEvalProps(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_phase_stop_condition(self):
        script = '''
        mechanism :         sr
        behaviors :         R1,R2
        stimulus_elements : E,rew
        u                 : rew:1, E:0

        @phase B3 stop:B=3
        A E   | count_line()=5:B | A
        B rew | A

        @run B3 label:B3

        @phase rew5 stop:rew=5
        A E   | count_line()=5:B | A
        B rew | A

        @run rew5 label:rew5
        '''
        script_obj = Script(script)
        script_obj.parse()
        simulation_data = script_obj.run()
        self.run_B3 = simulation_data.run_outputs["B3"].output_subjects[0]
        self.run_rew5 = simulation_data.run_outputs["rew5"].output_subjects[0]

        cnt_rew1 = 0
        for h in self.run_B3.history:
            if h == 'rew':
                cnt_rew1 += 1
        self.assertEqual(cnt_rew1, 3)

        cnt_rew2 = 0
        for h in self.run_rew5.history:
            if h == 'rew':
                cnt_rew2 += 1

        self.assertEqual(cnt_rew2, 5)

    def test_phases(self):
        script = '''
        mechanism :         sr
        behaviors :         R, RR
        stimulus_elements : E1, rew1, E2, rew2
        u                 : rew1:1, rew2:1, E1:0, E2:0

        @phase phase1 stop:B=3
        A E1   | count_line()=5:B | A
        B rew1 | A

        @phase phase2 stop:B=6
        A E2   | count_line()=5:B | A
        B rew2 | A

        @run phase1,phase2

        @figure
        phases: phase1
        @nplot rew1

        @figure
        @nplot rew2
        '''
        script_obj = Script(script)
        script_obj.parse()
        s = script_obj.run()
        script_obj.postproc(s, block=False)

        x, y = get_plotdata(1)
        # print(s.run_outputs['run1'].output_subjects[0].history)
        # print(s.run_outputs['run1'].output_subjects[0].first_step_phase)
        x_expected = list()
        for i in range(37):
            x_expected.append(i)
        y_expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                      2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                      3, 3]
        self.assertEqual(x, x_expected)
        self.assertEqual(y, y_expected)
