from .testutil import LsTestCase

from parsing import Script
from phases import World
import util

from .testutil import check_run_output_subject


def parse(text):
    script = Script(text)
    script.parse()
    script_parser = script.script_parser
    runs = script_parser.runs
    nruns = len(runs.runs)
    if nruns != 1:
        phases = script_parser.phases.phases
        for phaselbl, phase in phases.items():
            if not phase.is_parsed:
                phase.parse(script_parser.parameters, script_parser.variables)
        world = World(phases, list(phases.keys()))
    else:
        run = list(runs.runs.values())[0]
        world = run.world
    return world, script


def check_logic(self, condition, lineno, cond, cond_is_behavior, goto):
    self.assertEqual(condition.lineno, lineno)
    self.assertEqual(condition.cond, cond)
    self.assertEqual(condition.cond_is_behavior, cond_is_behavior)
    self.assertEqual(condition.goto, goto)


class TestMisc(LsTestCase):
    def setUp(self):
        pass

    def test_wrong_endcond(self):
        script = """
        mechanism: GA
        behaviors: R0, R1, R2
        stimulus_elements: E0, E1, E2
        response_requirements:    R0: [E0, E1],
                                  R1: E1,
                                  R2: [E0, E1, E2]

        @phase foo stop:E00=100
        PL0    E0  |  PL1
        PL1    E1  |  PL2
        PL2    E2  |  PL0
        """
        world, _ = parse(script)
        msg = "Unknown variable 'E00'."
        world.next_stimulus(None)
        with self.assertRaisesMsg(msg):
            world.next_stimulus('R0')

    def test_repeat_phase(self):
        script = """
        mechanism: GA
        behaviors: R0, R1, R2
        stimulus_elements: E0, E1, E2

        @phase foo stop:E0=10
        PL0    E0  |  PL1
        PL1    E1  |  PL2
        PL2    E2  |  PL0

        @run foo, foo
        """
        w, script_obj = parse(script)
        simulation_data = script_obj.run()
        history = simulation_data.run_outputs["run1"].output_subjects[0].history
        _, cumsum = util.find_and_cumsum(history, 'E0', True)
        self.assertEqual(cumsum[-1], 20)

        out = simulation_data.run_outputs["run1"].output_subjects[0]
        check_run_output_subject(self, out)


class TestClassicalConditioning(LsTestCase):
    def setUp(self):
        script = """
        stimulus_elements: context, reward, us
        behaviors: R, foo

        @phase pretraining stop:reward=20
        CONTEXT context        | count_line()=25:US       | CONTEXT
        US      us,context     | R: REWARD   | CONTEXT
        REWARD  reward,context | CONTEXT
        """
        self.world, _ = parse(script)

    def test_props(self):
        phase = self.world.phases[0]
        self.assertEqual(phase.first_label, "CONTEXT")
        self.assertEqual(phase.stop_condition.lineno, 5)
        self.assertEqual(phase.stop_condition.cond, "reward=20")

        row = phase.phase_lines["CONTEXT"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {"context": 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 6, 'count_line()=25', False, [[1, "US"]])
        check_logic(self, conditions[1], 6, None, False, [[1, "CONTEXT"]])

        row = phase.phase_lines["US"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {"us": 1, "context": 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 7, 'R', True, [[1, "REWARD"]])
        check_logic(self, conditions[1], 7, None, False, [[1, "CONTEXT"]])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {"reward": 1, "context": 1})
        self.assertEqual(len(conditions), 1)
        check_logic(self, conditions[0], 8, None, False, [[1, "CONTEXT"]])

    def test_run(self):
        world = self.world
        s = world.next_stimulus(None)
        self.assertEqual(s, ({"context": 1}, 'pretraining', 'CONTEXT', []))

        for _ in range(24):
            s = world.next_stimulus('foo')
            self.assertEqual(s, ({"context": 1}, 'pretraining', 'CONTEXT', []))
        s = world.next_stimulus('foo')
        self.assertEqual(s, ({"us": 1, "context": 1}, 'pretraining', 'US', []))

        s = world.next_stimulus('R')
        self.assertEqual(s[0], {"reward": 1, "context": 1})

        for _ in range(25):
            s = world.next_stimulus('foo')
            self.assertEqual(s[0], {"context": 1})

        s = world.next_stimulus('R')
        self.assertEqual(s[0], {"us": 1, "context": 1})

        for i in range(19):
            for j in range(25):
                s = world.next_stimulus('foo')
                self.assertEqual(s[0], {"context": 1})
            s = world.next_stimulus('R')
            self.assertEqual(s[0], {"us": 1, "context": 1})
            s = world.next_stimulus('R')
            self.assertEqual(s[0], {"reward": 1, "context": 1})

        s = world.next_stimulus('R')
        self.assertIsNone(s[0])

        for _ in range(100):
            s = world.next_stimulus('R')
            self.assertIsNone(s[0])


class TestFixedInterval(LsTestCase):
    def setUp(self):
        script = """
        stimulus_elements: lever, reward, foo
        behaviors: R, bar

        @phase fixed_interval stop:reward=25
        OFF    lever   | count_line()=4:ON | OFF
        ON     lever   | R: REWARD | ON
        REWARD reward  | OFF
        """
        self.world, _ = parse(script)

    def test_props(self):
        phase = self.world.phases[0]
        self.assertEqual(phase.first_label, "OFF")
        self.assertEqual(phase.stop_condition.lineno, 5)
        self.assertEqual(phase.stop_condition.cond, "reward=25")

        self.assertEqual(len(phase.phase_lines), 3)

        row = phase.phase_lines["OFF"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {"lever": 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 6, "count_line()=4", False, [[1, "ON"]])
        check_logic(self, conditions[1], 6, None, False, [[1, "OFF"]])

        row = phase.phase_lines["ON"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {"lever": 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 7, "R", True, [[1, "REWARD"]])
        check_logic(self, conditions[1], 7, None, False, [[1, "ON"]])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {"reward": 1})
        self.assertEqual(len(conditions), 1)
        check_logic(self, conditions[0], 8, None, False, [[1, "OFF"]])

    def test_run(self):
        pass


class TestFixedRatio(LsTestCase):
    def setUp(self):
        script = """
        stimulus_elements : lever, reward
        behaviors : R, R0

        @phase fixed_ratio stop:reward=23
        OFF lever       | count_line(R)=4: ON   | OFF
        ON  lever       | R: REWARD | ON
        REWARD  reward  | OFF
        """
        self.world, _ = parse(script)

    def test_props(self):
        phase = self.world.phases[0]
        self.assertEqual(phase.first_label, "OFF")
        self.assertEqual(phase.stop_condition.lineno, 5)
        self.assertEqual(phase.stop_condition.cond, "reward=23")

        self.assertEqual(len(phase.phase_lines), 3)

        row = phase.phase_lines["OFF"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'lever': 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 6, 'count_line(R)=4', False, [[1, "ON"]])
        check_logic(self, conditions[1], 6, None, False, [[1, "OFF"]])

        row = phase.phase_lines["ON"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'lever': 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 7, 'R', True, [[1, "REWARD"]])
        check_logic(self, conditions[1], 7, None, False, [[1, "ON"]])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'reward': 1})
        self.assertEqual(len(conditions), 1)
        check_logic(self, conditions[0], 8, None, False, [[1, "OFF"]])

    def test_run(self):
        world = self.world
        s = world.next_stimulus(None)
        self.assertEqual(s[0], {'lever': 1})

        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'reward': 1})

        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})

        for _ in range(100):
            s = world.next_stimulus('R0')
            self.assertEqual(s[0], {'lever': 1})

        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'reward': 1})


class TestProbabilitySchedule(LsTestCase):
    def setUp(self):
        script = """
        stimulus_elements : lever, reward1, reward2
        behaviors : R, reward

        @phase prob_shedule stop:reward=100000
        LEVER    lever   | R: REWARD1(0.2),REWARD2(0.3) | LEVER
        REWARD1  reward1 | LEVER
        REWARD2  reward2 | LEVER
        """
        self.world, _ = parse(script)

    def test_props(self):
        phase = self.world.phases[0]
        self.assertEqual(phase.first_label, "LEVER")
        self.assertEqual(phase.stop_condition.lineno, 5)
        self.assertEqual(phase.stop_condition.cond, "reward=100000")

        self.assertEqual(len(phase.phase_lines), 3)

        row = phase.phase_lines["LEVER"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'lever': 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 6, "R", True, [[0.2, "REWARD1"], [0.3, "REWARD2"]])
        check_logic(self, conditions[1], 6, None, False, [[1, "LEVER"]])

        row = phase.phase_lines["REWARD1"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'reward1': 1})
        self.assertEqual(len(conditions), 1)
        check_logic(self, conditions[0], 7, None, False, [[1, "LEVER"]])

        row = phase.phase_lines["REWARD2"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'reward2': 1})
        self.assertEqual(len(conditions), 1)
        check_logic(self, conditions[0], 8, None, False, [[1, "LEVER"]])

    def test_run(self):
        world = self.world
        s = world.next_stimulus(None)[0]
        self.assertEqual(s, {'lever': 1})

        d = {'lever': 0, 'reward1': 0, 'reward2': 0}
        n = 200000
        prev_was_lever = True
        for _ in range(n):
            s = world.next_stimulus('R')[0]
            s = list(s.keys())[0]
            if prev_was_lever:
                d[s] += 1
            prev_was_lever = (s == 'lever')

        ncounts = sum(d.values())
        self.assertAlmostEqual(d['reward1'] / ncounts, 0.2, 2)
        self.assertAlmostEqual(d['reward2'] / ncounts, 0.3, 2)
        self.assertAlmostEqual(d['lever'] / ncounts, 0.5, 2)


class TestVariableInterval(LsTestCase):
    def setUp(self):
        script = """
        stimulus_elements: lever3, lever2, leveron, reward
        behaviors: R, R1, foo, bar, foobar

        @phase variable_interval stop:reward =200000
        FI3 lever3      | count_line()=3:ON   | FI3
        FI2 lever2      | count_line()=2:ON   | FI2
        ON  leveron     | R:REWARD | ON
        REWARD  reward  | ON(1/3),FI2(1/3),FI3(1/3)
        """
        self.world, _ = parse(script)

    def test_props(self):
        phase = self.world.phases[0]
        self.assertEqual(phase.first_label, "FI3")
        self.assertEqual(phase.stop_condition.lineno, 5)
        self.assertEqual(phase.stop_condition.cond, "reward =200000")

        self.assertEqual(len(phase.phase_lines), 4)

        row = phase.phase_lines["FI3"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'lever3': 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 6, "count_line()=3", False, [[1, "ON"]])
        check_logic(self, conditions[1], 6, None, False, [[1, "FI3"]])

        row = phase.phase_lines["FI2"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'lever2': 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 7, "count_line()=2", False, [[1, "ON"]])
        check_logic(self, conditions[1], 7, None, False, [[1, "FI2"]])

        row = phase.phase_lines["ON"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'leveron': 1})
        self.assertEqual(len(conditions), 2)
        check_logic(self, conditions[0], 8, "R", True, [[1, "REWARD"]])
        check_logic(self, conditions[1], 8, None, False, [[1, "ON"]])

        row = phase.phase_lines["REWARD"]
        conditions = row.conditions.conditions
        self.assertEqual(row.stimulus, {'reward': 1})
        self.assertEqual(len(conditions), 1)
        check_logic(self, conditions[0], 9, None, False,
                    [[1 / 3, "ON"], [1 / 3, "FI2"], [1 / 3, "FI3"]])

    def test_run(self):
        world = self.world
        s = world.next_stimulus(None)
        self.assertEqual(s[0], {'lever3': 1})

        s = world.next_stimulus('foo')
        self.assertEqual(s[0], {'lever3': 1})

        s = world.next_stimulus('bar')
        self.assertEqual(s[0], {'lever3': 1})

        s = world.next_stimulus('foobar')
        self.assertEqual(s[0], {'leveron': 1})

        for _ in range(100):
            s = world.next_stimulus('foobar')
            self.assertEqual(s[0], {'leveron': 1})
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'reward': 1})

        d = {'lever3': 0, 'lever2': 0, 'leveron': 0}
        n = 200000
        prev_was_reward = True
        for _ in range(n):
            s = world.next_stimulus('R')[0]
            s = list(s.keys())[0]
            if prev_was_reward:
                d[s] += 1
            prev_was_reward = (s == 'reward')

        ncounts = sum(d.values())
        self.assertAlmostEqual(d['lever3'] / ncounts, 1 / 3, 1)
        self.assertAlmostEqual(d['lever2'] / ncounts, 1 / 3, 1)
        self.assertAlmostEqual(d['leveron'] / ncounts, 1 / 3, 1)


class TestVariableRatio(LsTestCase):
    def setUp(self):
        script = """
        stimulus_elements : lever, leveron, reward
        behaviors : R, R1, bar

        @phase variable_ratio stop:reward = 250000
        FR3 lever      | count_line(R)=2 : ON  | FR3
        FR2 lever      | R : ON  | FR2
        ON  leveron    | R:REWARD    | R1:ON
        REWARD  reward | ON(1/3),FR2(1/3),FR3(1/3)
        """
        self.world, _ = parse(script)

    def test_props(self):
        pass

    def test_run(self):
        world = self.world
        s = world.next_stimulus(None)
        self.assertEqual(s[0], {'lever': 1})

        # First R
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'lever': 1})

        for _ in range(142):
            s = world.next_stimulus('bar')
            self.assertEqual(s[0], {'lever': 1})

        # Second R, go to ON
        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'leveron': 1})

        for _ in range(107):
            s = world.next_stimulus('R1')
            self.assertEqual(s[0], {'leveron': 1})

        s = world.next_stimulus('R')
        self.assertEqual(s[0], {'reward': 1})

        d = {'lever': 0, 'leveron': 0}
        n = 200000
        prev_was_reward = True
        for _ in range(n):
            s_dict = world.next_stimulus('R')[0]
            s = list(s_dict.keys())[0]
            if prev_was_reward:
                d[s] += 1
            prev_was_reward = (s == 'reward')

        ncounts = sum(d.values())
        self.assertAlmostEqual(d['lever'] / ncounts, 2 / 3, 2)
        self.assertAlmostEqual(d['leveron'] / ncounts, 1 / 3, 2)


class TestFixedTime(LsTestCase):
    def setUp(self):
        script = """
        stimulus_elements : lever, reward
        behaviors : foofoo, foo, bar

        @phase fixed_time stop:reward=2500
        LEVER   lever   | count_line()=5: REWARD  | LEVER
        REWARD  reward  | LEVER
        """
        self.world, _ = parse(script)

    def test_props(self):
        pass

    def test_run(self):
        world = self.world
        s = world.next_stimulus(None)[0]
        self.assertEqual(s, {'lever': 1})

        for _ in range(4):
            s = world.next_stimulus('foo')[0]
            self.assertEqual(s, {'lever': 1})

        s = world.next_stimulus('foo')[0]
        self.assertEqual(s, {'reward': 1})

        for i in range(100):
            for _ in range(5):
                s = world.next_stimulus('foo')[0]
                self.assertEqual(s, {'lever': 1})
            s = world.next_stimulus('bar')[0]
            self.assertEqual(s, {'reward': 1})
