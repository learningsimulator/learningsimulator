import unittest

import LsScript
import LsUtil
from LsWorld import PhaseWorld
from LsExceptions import LsParseException

from tests.LsTestUtil import check_run_output_subject


def make_phase(phase, pv, stimulus_elements, behaviors):
    phase = [s.strip() for s in phase.splitlines()]
    return PhaseWorld(phase, pv, stimulus_elements, behaviors)


class TestPhaseWorld(unittest.TestCase):

    def setUp(self):
        self.classical_cond = self.setup_classical_conditioning()
        self.fixed_interval = self.setup_fixed_interval()
        self.fixed_ratio = self.setup_fixed_ratio()
        self.probability_schedule = self.setup_probability_schedule()
        self.variable_interval = self.setup_variable_interval()
        self.variable_ratio = self.setup_variable_ratio()
        self.fixed_time = self.setup_fixed_time()

    def test_wrong_endcond(self):
        script = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E0', 'E1', 'E2'],
            'response_requirements': {
                                      'R0': ['E0', 'E1'],
                                      'R1': 'E1',
                                      'R2': ['E0', 'E1', 'E2']
                                      }
        }

        @phase {'label':'foo', 'end':'E00=100'}
        PL0    'E0'  |  PL1
        PL1    'E1'  |  PL2
        PL2    'E2'  |  PL0

        @run
        """
        with self.assertRaises(LsParseException):
            script_obj = LsScript.LsScript(script)
            script_obj.run()

    def setup_classical_conditioning(self):
        phase = """CONTEXT context              | 25:US       | CONTEXT
                   US      ('us','context')     | R: REWARD   | CONTEXT
                   REWARD  ('reward','context') | CONTEXT"""
        pv = {'label': 'pretraining', 'end': 'reward=20'}
        stimulus_elements = ['context', 'reward', 'us']
        behaviors = ['R', 'foo']
        return make_phase(phase, pv, stimulus_elements, behaviors)

    def test_repeat_phase(self):
        script = """
        @parameters
        {
            'mechanism': 'GA',
            'behaviors': ['R0', 'R1', 'R2'],
            'stimulus_elements': ['E0', 'E1', 'E2'],
        }

        @phase {'label':'foo', 'end':'E0=10'}
        PL0    'E0'  |  PL1
        PL1    'E1'  |  PL2
        PL2    'E2'  |  PL0

        @run {'phases': ('foo','foo')}
        """
        script_obj = LsScript.LsScript(script)
        simulation_data = script_obj.run()
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        _, cumsum = LsUtil.find_and_cumsum(history, 'E0', True)
        self.assertEqual(cumsum[-1], 20)

        out = simulation_data.run_outputs["run1"].output_subjects[0]
        check_run_output_subject(self, out)

    def test_classical_conditioning_props(self):
        phase = self.classical_cond
        self.assertEqual(phase.first_label, "CONTEXT")
        self.assertEqual(phase.endphase_obj.item, "reward")
        self.assertEqual(phase.endphase_obj.limit, 20)

        self.assertEqual(len(phase.phase_lines), 3)

        row = phase.phase_lines["CONTEXT"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("context",))
        self.assertEqual(len(conditions), 2)
        self.assertEqual(conditions[0].count, 25)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "US")])

        row = phase.phase_lines["US"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("us", "context"))
        self.assertEqual(len(conditions), 2)
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "CONTEXT")])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("reward", "context"))
        self.assertEqual(len(conditions), 1)
        self.assertIsNone(conditions[0].count)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "CONTEXT")])

    def test_classical_conditioning_run(self):
        phase = self.classical_cond
        s = phase.next_stimulus(None)
        self.assertEqual(s, ("context",))

        for _ in range(24):
            s = phase.next_stimulus('foo')
            self.assertEqual(s, ("context",))
        s = phase.next_stimulus('foo')
        self.assertEqual(s, ("us", "context",))

        s = phase.next_stimulus('R')
        self.assertEqual(s, ("reward", "context",))

        for _ in range(25):
            s = phase.next_stimulus('foo')
            self.assertEqual(s, ("context",))

        s = phase.next_stimulus('R')
        self.assertEqual(s, ("us", "context",))

        for i in range(19):
            for j in range(25):
                s = phase.next_stimulus('foo')
                self.assertEqual(s, ("context",))
            s = phase.next_stimulus('R')
            self.assertEqual(s, ("us", "context",))
            s = phase.next_stimulus('R')
            self.assertEqual(s, ("reward", "context",))

        s = phase.next_stimulus('R')
        self.assertIsNone(s)

        for _ in range(100):
            s = phase.next_stimulus('R')
            self.assertIsNone(s)

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

    def setup_fixed_interval(self):
        phase = """OFF    'lever'   | 4:ON | OFF
                   ON     'lever'   | R: REWARD | ON
                   REWARD 'reward'  | OFF """
        pv = {'label': 'fixed_interval', 'end': 'reward=25'}
        stimulus_elements = ['lever', 'reward', 'foo']
        behaviors = ['R', 'bar']
        return make_phase(phase, pv, stimulus_elements, behaviors)

    def test_fixed_interval_props(self):
        phase = self.fixed_interval
        self.assertEqual(phase.first_label, "OFF")
        self.assertEqual(phase.endphase_obj.item, "reward")
        self.assertEqual(phase.endphase_obj.limit, 25)

        self.assertEqual(len(phase.phase_lines), 3)

        row = phase.phase_lines["OFF"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("lever",))
        self.assertEqual(len(conditions), 2)
        self.assertEqual(conditions[0].count, 4)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "ON")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "OFF")])

        row = phase.phase_lines["ON"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("lever",))
        self.assertEqual(len(conditions), 2)

        self.assertIsNone(conditions[0].count)
        self.assertEqual(conditions[0].response, 'R')
        self.assertEqual(conditions[0].goto, [(1, "REWARD")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "ON")])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("reward",))
        self.assertEqual(len(conditions), 1)
        self.assertIsNone(conditions[0].count)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "OFF")])

    def test_fixed_interval_run(self):
        pass

    def setup_fixed_ratio(self):
        phase = """OFF 'lever'       | R=4: ON   | OFF
                   ON  'lever'       | R: REWARD | ON
                   REWARD  'reward'  | OFF"""
        pv = {'label': 'fixed_ratio', 'end': 'reward = 23'}
        stimulus_elements = ['lever', 'reward']
        behaviors = ['R', 'R0']
        return make_phase(phase, pv, stimulus_elements, behaviors)

    def test_fixed_ratio_props(self):
        phase = self.fixed_ratio
        self.assertEqual(phase.first_label, "OFF")
        self.assertEqual(phase.endphase_obj.item, "reward")
        self.assertEqual(phase.endphase_obj.limit, 23)

        self.assertEqual(len(phase.phase_lines), 3)

        row = phase.phase_lines["OFF"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("lever",))
        self.assertEqual(len(conditions), 2)
        self.assertEqual(conditions[0].count, 4)
        self.assertEqual(conditions[0].response, 'R')
        self.assertEqual(conditions[0].goto, [(1, "ON")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "OFF")])

        row = phase.phase_lines["ON"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("lever",))
        self.assertEqual(len(conditions), 2)
        self.assertIsNone(conditions[0].count)
        self.assertEqual(conditions[0].response, 'R')
        self.assertEqual(conditions[0].goto, [(1, "REWARD")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "ON")])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("reward",))
        self.assertEqual(len(conditions), 1)
        self.assertIsNone(conditions[0].count)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "OFF")])

    def test_fixed_ratio_run(self):
        phase = self.fixed_ratio
        s = phase.next_stimulus(None)
        self.assertEqual(s, ('lever',))

        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('reward',))

        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))

        for _ in range(100):
            s = phase.next_stimulus('R0')
            self.assertEqual(s, ('lever',))

        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('lever',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('reward',))

    def setup_probability_schedule(self):
        phase = """LEVER    'lever'   | R: REWARD1(0.2),REWARD2(0.3) | LEVER
                   REWARD1  'reward1'  | LEVER
                   REWARD2  'reward2'  | LEVER"""
        pv = {'label': 'prob_schedule', 'end': 'reward=100000'}
        stimulus_elements = ['lever', 'reward1', 'reward2']
        behaviors = ['R', 'reward']
        return make_phase(phase, pv, stimulus_elements, behaviors)

    def test_probability_schedule_props(self):
        phase = self.probability_schedule
        self.assertEqual(phase.first_label, "LEVER")
        self.assertEqual(phase.endphase_obj.item, "reward")
        self.assertEqual(phase.endphase_obj.limit, 100000)

        self.assertEqual(len(phase.phase_lines), 3)

        row = phase.phase_lines["LEVER"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("lever",))
        self.assertEqual(len(conditions), 2)
        self.assertIsNone(conditions[0].count)
        self.assertEqual(conditions[0].response, 'R')
        self.assertEqual(conditions[0].goto, [(0.2, "REWARD1"), (0.3, "REWARD2")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "LEVER")])

        row = phase.phase_lines["REWARD1"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("reward1",))
        self.assertEqual(len(conditions), 1)
        self.assertIsNone(conditions[0].count)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "LEVER")])

        row = phase.phase_lines["REWARD2"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("reward2",))
        self.assertEqual(len(conditions), 1)
        self.assertIsNone(conditions[0].count)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "LEVER")])

    def test_probability_schedule_run(self):
        phase = self.probability_schedule
        s = phase.next_stimulus(None)
        self.assertEqual(s, ('lever',))

        d = {'lever': 0, 'reward1': 0, 'reward2': 0}
        n = 100000
        prev_was_lever = True
        for _ in range(n):
            s = phase.next_stimulus('R')[0]
            if prev_was_lever:
                d[s] += 1
            prev_was_lever = (s == 'lever')

        ncounts = sum(d.values())
        self.assertAlmostEqual(d['reward1'] / ncounts, 0.2, 2)
        self.assertAlmostEqual(d['reward2'] / ncounts, 0.3, 2)
        self.assertAlmostEqual(d['lever'] / ncounts, 0.5, 2)

    def setup_variable_interval(self):
        phase = """FI3 'lever3'      | 3:ON   | FI3
                   FI2 'lever2'      | 2:ON   | FI2
                   ON  'leveron'     | R:REWARD | ON
                   REWARD  'reward'  | ON(1/3),FI2(1/3),FI3(1/3)"""
        pv = {'label': 'variable_interval1', 'end': 'reward = 200000'}
        stimulus_elements = ['lever3', 'lever2', 'leveron', 'reward']
        behaviors = ['R', 'R1', 'foo', 'bar', 'foobar']
        return make_phase(phase, pv, stimulus_elements, behaviors)

    def test_variable_interval_props(self):
        phase = self.variable_interval
        self.assertEqual(phase.first_label, "FI3")
        self.assertEqual(phase.endphase_obj.item, "reward")
        self.assertEqual(phase.endphase_obj.limit, 200000)

        self.assertEqual(len(phase.phase_lines), 4)

        row = phase.phase_lines["FI3"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("lever3",))
        self.assertEqual(len(conditions), 2)
        self.assertEqual(conditions[0].count, 3)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "ON")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "FI3")])

        row = phase.phase_lines["FI2"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("lever2",))
        self.assertEqual(len(conditions), 2)
        self.assertEqual(conditions[0].count, 2)
        self.assertIsNone(conditions[0].response)
        self.assertEqual(conditions[0].goto, [(1, "ON")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "FI2")])

        row = phase.phase_lines["ON"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("leveron",))
        self.assertEqual(len(conditions), 2)
        self.assertIsNone(conditions[0].count)
        self.assertEqual(conditions[0].response, 'R')
        self.assertEqual(conditions[0].goto, [(1, "REWARD")])
        self.assertIsNone(conditions[1].count)
        self.assertIsNone(conditions[1].response)
        self.assertEqual(conditions[1].goto, [(1, "ON")])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, ("reward",))
        self.assertEqual(len(conditions), 1)
        self.assertIsNone(conditions[0].count)
        self.assertIsNone(conditions[0].response)
        self.assertAlmostEqual(conditions[0].goto[0][0], 1 / 3, 6)
        self.assertAlmostEqual(conditions[0].goto[1][0], 1 / 3, 6)
        self.assertAlmostEqual(conditions[0].goto[2][0], 1 / 3, 6)
        self.assertEqual(conditions[0].goto[0][1], "ON")
        self.assertEqual(conditions[0].goto[1][1], "FI2")
        self.assertEqual(conditions[0].goto[2][1], "FI3")

    def test_variable_interval_run(self):
        phase = self.variable_interval
        s = phase.next_stimulus(None)
        self.assertEqual(s, ('lever3',))

        s = phase.next_stimulus('foo')
        self.assertEqual(s, ('lever3',))

        s = phase.next_stimulus('bar')
        self.assertEqual(s, ('lever3',))

        s = phase.next_stimulus('foobar')
        self.assertEqual(s, ('leveron',))

        for _ in range(100):
            s = phase.next_stimulus('foobar')
            self.assertEqual(s, ('leveron',))
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('reward',))

        d = {'lever3': 0, 'lever2': 0, 'leveron': 0}
        n = 200000
        prev_was_reward = True
        for _ in range(n):
            s = phase.next_stimulus('R')[0]
            if prev_was_reward:
                d[s] += 1
            prev_was_reward = (s == 'reward')

        ncounts = sum(d.values())
        self.assertAlmostEqual(d['lever3'] / ncounts, 1 / 3, 1)
        self.assertAlmostEqual(d['lever2'] / ncounts, 1 / 3, 1)
        self.assertAlmostEqual(d['leveron'] / ncounts, 1 / 3, 1)

    def setup_variable_ratio(self):
        phase = """FR3 'lever'   | 'R'=2:ON  | FR3
                   FR2 'lever'   |  R =1:ON  | FR2
                   ON  'leveron'   | 'R':REWARD | 'R1':ON
                   REWARD  'reward'  | ON(1/3),FR2(1/3),FR3(1/3)"""
        pv = {'label': 'variable_ratio1', 'end': 'reward = 250000'}
        stimulus_elements = ['lever', 'leveron', 'reward']
        behaviors = ['R', 'R1', 'bar']
        return make_phase(phase, pv, stimulus_elements, behaviors)

    def test_variable_ratio_props(self):
        pass

    def test_variable_ratio_run(self):
        phase = self.variable_ratio
        s = phase.next_stimulus(None)
        self.assertEqual(s, ('lever',))

        s = phase.next_stimulus('R')[0]
        self.assertEqual(s, 'lever')

        for _ in range(100):
            s = phase.next_stimulus('bar')
            self.assertEqual(s, ('lever',))

        s = phase.next_stimulus('R')
        s = phase.next_stimulus('R')
        self.assertEqual(s, ('leveron',))

        for _ in range(100):
            s = phase.next_stimulus('R1')
            self.assertEqual(s, ('leveron',))

        s = phase.next_stimulus('R')
        self.assertEqual(s, ('reward',))

        d = {'lever': 0, 'leveron': 0}
        n = 200000
        prev_was_reward = True
        for _ in range(n):
            s = phase.next_stimulus('R')[0]
            if prev_was_reward:
                d[s] += 1
            prev_was_reward = (s == 'reward')

        ncounts = sum(d.values())
        self.assertAlmostEqual(d['lever'] / ncounts, 2 / 3, 2)
        self.assertAlmostEqual(d['leveron'] / ncounts, 1 / 3, 2)

    def setup_fixed_time(self):
        phase = """LEVER   'lever'   | 5: REWARD  | LEVER
                   REWARD  'reward'  | LEVER"""
        pv = {'label': 'fixed_time', 'end': 'reward = 2500'}
        stimulus_elements = ['lever', 'reward']
        behaviors = ['foofoo', 'foo', 'bar']
        return make_phase(phase, pv, stimulus_elements, behaviors)

    def test_fixed_time_props(self):
        pass

    def test_fixed_time_run(self):
        phase = self.fixed_time

        s = phase.next_stimulus('foofoo')[0]
        self.assertEqual(s, 'lever')

        for _ in range(4):
            s = phase.next_stimulus('foo')[0]
            self.assertEqual(s, 'lever')

        s = phase.next_stimulus('foo')[0]
        self.assertEqual(s, 'reward')

        for i in range(100):
            for _ in range(5):
                s = phase.next_stimulus('foo')[0]
                self.assertEqual(s, 'lever')
            s = phase.next_stimulus('bar')[0]
            self.assertEqual(s, 'reward')

    def test_err1(self):
        phase = """FI3 'lever'       | FI2=3:ON   | FI3
                   FI2 'lever'       | 2:ON   | FI2
                   ON  'lever '      | R:REWARD | ON
                   REWARD  'reward'   | ON(1/3),FI2(1/3),FI3(1/3)"""
        pv = {'label': 'variable_interval1', 'end': 'reward = 25'}
        stimulus_elements = ['lever', 'reward']
        behaviors = ['R']
        with self.assertRaises(LsParseException):
            phase = make_phase(phase, pv, stimulus_elements, behaviors)

    def test_err2(self):
        phase = """FI3 'lever1'       | 3:ON     | FI3
                   FI2 'lever2'       | 2:ON     | FI2
                   ON   lever3        | R:REWARD | ON
                   REWARD  'reward'   | ON(1/6),FI2(1/6),FI3(1/6)"""
        pv = {'label': 'vi', 'end': 'reward = 25000'}
        stimulus_elements = ['lever1', 'lever2', 'lever3', 'reward']
        behaviors = ['R', 'foo']
#        with self.assertRaises(LsParseException):
        phase = make_phase(phase, pv, stimulus_elements, behaviors)

        for i in range(3):
            s = phase.next_stimulus('R')[0]
            self.assertEqual(s, 'lever1')
        s = phase.next_stimulus('foo')[0]
        self.assertEqual(s, 'lever3')

        s = phase.next_stimulus('R')[0]
        self.assertEqual(s, 'reward')

        ntries = 0
        nfails = 0
        for _ in range(100000):
            if s == "reward":
                ntries += 1
                try:
                    s = phase.next_stimulus('R')[0]
                except Exception:
                    nfails += 1
            else:
                s = phase.next_stimulus('R')[0]

        self.assertAlmostEqual(nfails / ntries, 1 / 2, 1)

# if __name__ == '__main__':
#     unittest.main()
