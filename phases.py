import copy
import re

from exceptions import ParseException
from util import ParseUtil, is_valid_name
import keywords as kw
from keywords import PHASEDIV, STIMULUS_ELEMENTS, BEHAVIORS
from variables import Variables


class Phases():
    def __init__(self):
        self.phases = dict()  # Keys are phase labels, values are Phase objects

    def add_phase(self, label, stop_condition_str, lineno):
        if label in self.phases:
            raise Exception("Internal error.")
        self.phases[label] = Phase(label, stop_condition_str, lineno)

    def inherit_from(self, inherit_from, label, stop_condition_str, lineno):
        if inherit_from not in self.phases:
            raise Exception("Internal error.")
        inherited_phase = self.phases[inherit_from]
        if label in self.phases:
            raise Exception("Internal error.")

        self.phases[label] = Phase(label, stop_condition_str, lineno)  # Not inherited_phase.copy()!
        self.phases[label].lines = copy.deepcopy(inherited_phase.lines)
        self.phases[label].stop_condition_str = stop_condition_str
        self.phases[label].lineno = lineno
        self.phases[label].is_inherited = True

    def append_line(self, label, line, lineno):
        if label not in self.phases:
            raise Exception("Internal error.")
        self.phases[label].append_line(line, lineno)

    def parse_phase(self, label, parameters, variables):
        if label not in self.phases:
            raise Exception("Internal error.")
        self.phases[label].parse(parameters, variables)

    def get(self, label):
        return self.phases[label]

    def get_all(self):
        return self.phases

    def contains(self, label):
        return label in self.phases

    def make_world(self, labels):
        return World(self.phases, labels)

    def is_phase_label(self, name):
        for _, phase in self.phases.items():
            if phase.is_phase_label(name):
                return True
        return False


class Phase():
    '''A number of rows of text, and a stop condition (string).'''

    def __init__(self, label, stop_condition_str, lineno):
        self.label = label
        self.stop_condition_str = stop_condition_str
        self.lineno = lineno
        self.lines = list()  # List of tuples (line, lineno)

        # Set in parse
        self.stimulus_elements = None
        self.behaviors = None
        self.global_variables = None
        self.local_variables = None
        self.linelabels = list()
        self.end_condition = None
        self.phase_lines = dict()  # Keys are phase line labels, values are PhaseLine objects
        self.first_label = None
        self.curr_lineobj = None
        self.event_counter = None

        self.is_first_line = True
        self.is_inherited = False
        self.is_parsed = False

        self.first_stimulus_presented = False

    def append_line(self, line, lineno):
        self.lines.append((line, lineno))

    def parse(self, parameters, global_variables):
        self.parameters = parameters
        self.global_variables = global_variables

        stimulus_elements = parameters.get(STIMULUS_ELEMENTS)
        behaviors = parameters.get(BEHAVIORS)

        phase_lines_afterlabel = list()
        linenos = list()

        # First iteration through lines: Create list of lines (and labels)
        for line_lineno in self.lines:
            line, lineno = line_lineno
            label, afterlabel = ParseUtil.split1_strip(line)
            if afterlabel is None:
                raise ParseException(lineno, "Phase line contains only label.")
            coincide_err = f"The phase line label '{label}' coincides with the name of a "
            if label in stimulus_elements:
                raise ParseException(lineno, coincide_err + "stimulus element.")
            elif label in behaviors:
                raise ParseException(lineno, coincide_err + "behavior.")
            if label in self.linelabels and not self.is_inherited:
                raise ParseException(lineno, f"Duplicate of phase line label '{label}'.")
            self.linelabels.append(label)
            phase_lines_afterlabel.append(afterlabel)
            linenos.append(lineno)
            if self.first_label is None:  # Set self.first_label to the label of the first line
                self.first_label = label

        # Second iteration: Create PhaseLine objects and put in the dict self.phase_lines
        for label, after_label, lineno in zip(self.linelabels, phase_lines_afterlabel, linenos):
            self.phase_lines[label] = PhaseLine(self, lineno, label, after_label, self.linelabels,
                                                self.parameters, self.global_variables)
            if label == "new_trial":  # Change self.first_label to the new_trial line
                self.first_label = label

        self.initialize_local_variables()
        self.event_counter = PhaseEventCounter(self.linelabels, self.parameters)

        self.subject_reset()
        self.is_parsed = True

    def initialize_local_variables(self):
        self.local_variables = Variables()

    def subject_reset(self):
        self.event_counter = PhaseEventCounter(self.linelabels, self.parameters)
        self.stop_condition = EndPhaseCondition(self.lineno, self.stop_condition_str)
        self._make_current_line(self.first_label)
        self.prev_linelabel = None
        self.is_first_line = True
        self.initialize_local_variables()
        self.first_stimulus_presented = False

    def next_stimulus(self, response, ignore_response_increment=False, preceeding_help_lines=None):
        # if not self.is_parsed:
        #     raise Exception("Internal error: Cannot call Phase.next_stimulus" +
        #                     " before Phase.parse().")

        if not preceeding_help_lines:
            preceeding_help_lines = list()

        if not ignore_response_increment:
            # if not self.is_first_line:
            if response is not None:
                self.event_counter.increment_count(response)
                self.event_counter.increment_count_line(response)

        if self.first_stimulus_presented:
            variables_both = Variables.join(self.global_variables, self.local_variables)
            if self.stop_condition.is_met(variables_both, self.event_counter):
                return None, None, preceeding_help_lines

        if self.is_first_line:
            assert(response is None)
            rowlbl = self.first_label
            self.is_first_line = False
        else:
            rowlbl = self.curr_lineobj.next_line(response, self.global_variables, self.local_variables,
                                                 self.event_counter)
            self.prev_linelabel = self.curr_lineobj.label
            self._make_current_line(rowlbl)

        stimulus = self.phase_lines[rowlbl].stimulus
        if stimulus is not None:
            for element, intensity in stimulus.items():
                if type(intensity) is str:  # element[var] where var is a (local) variable
                    variables_both = Variables.join(self.global_variables, self.local_variables)
                    stimulus[element], err = ParseUtil.evaluate(intensity, variables=variables_both)
                    if err:
                        raise ParseException(self.phase_lines[rowlbl].lineno, err)

        if rowlbl != self.prev_linelabel:
            self.event_counter.reset_count_line()
            self.event_counter.line_label = rowlbl

        self.event_counter.increment_count(rowlbl)
        self.event_counter.increment_count_line(rowlbl)

        if stimulus is None:  # Help line
            action = self.phase_lines[rowlbl].action
            self._perform_action(action)
            preceeding_help_lines.append(rowlbl)
            stimulus, rowlbl, preceeding_help_lines = self.next_stimulus(response, ignore_response_increment=True,
                                                                         preceeding_help_lines=preceeding_help_lines)
        else:
            for stimulus_element in stimulus:
                self.event_counter.increment_count(stimulus_element)
                self.event_counter.increment_count_line(stimulus_element)
            self.first_stimulus_presented = True

        return stimulus, rowlbl, preceeding_help_lines

    def _make_current_line(self, label):
        # self.curr_linelabel = label
        self.curr_lineobj = self.phase_lines[label]
        # self.endphase_obj.update_itemfreq(label)

    def perform_actions(self, actions):
        for action in actions:
            self._perform_action(action)

    def _perform_action(self, action):
        """
        Sets a variable (x:3) or count_reset(event).
        """
        if len(action) == 0:  # No action to perform
            return

        if action.count(':') == 1 or action.count('=') == 1:
            if action.count('=') == 1:
                sep = '='
            else:
                sep = ':'
            var_name, value_str = ParseUtil.split1_strip(action, sep=sep)
            variables_join = Variables.join(self.global_variables, self.local_variables)
            value, err = ParseUtil.evaluate(value_str, variables_join)
            if err:
                raise Exception(err)
            err = self.local_variables.set(var_name, value, self.parameters)
            if err:
                raise Exception(err)

        elif action.startswith("count_reset(") and action.endswith(")"):
            event = action[12:-1]
            self.event_counter.reset_count(event)
        else:
            raise Exception("Internal error.")

    def is_phase_label(self, label):
        return label in self.linelabels

    def copy(self):
        cpy = copy.deepcopy(self)
        cpy.stop_condition = copy.deepcopy(self.stop_condition)
        return cpy


class PhaseEventCounter():
    def __init__(self, linelabels, parameters):
        stimulus_elements = parameters.get(STIMULUS_ELEMENTS)
        behaviors = parameters.get(BEHAVIORS)
        event_names = list(stimulus_elements) + list(behaviors) + linelabels
        # event_names = set(linelabels).union(stimulus_elements).union(behaviors)

        # self.count_line counts events on current line
        self.count_line = {key: 0 for key in event_names}

        # The name of the current line
        self.line_label = None

        # self.event_counter counts all events, reset by count_reset()
        self.count = {key: 0 for key in event_names}

        # List of all possible count() and count_line() calls, used in replace_count_functions()
        self.count_calls = dict()
        self.count_line_calls = dict()
        for event in event_names:
            self.count_calls[event] = f"count({event})"
            self.count_line_calls[event] = f"count_line({event})"

    def increment_count(self, event):
        self.count[event] += 1

    def increment_count_line(self, event):
        self.count_line[event] += 1

    def reset_count_line(self):
        for key in self.count_line:
            self.count_line[key] = 0

    def reset_count(self, event):
        self.count[event] = 0

    def get_count(self, event):
        return self.count[event]

    def get_count_line(self, event):
        return self.count_line[event]

    def replace_count_functions(self, expr):
        for event, call in self.count_calls.items():
            expr = expr.replace(call, str(self.count[event]))
        for event, call in self.count_line_calls.items():
            expr = expr.replace(call, str(self.count_line[event]))
        if self.line_label is not None:
            expr = expr.replace("count_line()", str(self.count_line[self.line_label]))
        return expr

    # def eval(self, expr, variables):
    #     comps = ["==", "<=", ">=", "<", ">"]
    #     comp_count_fcns = [self.count_eq, self.count_leq, self.count_geq,
    #                        self.count_less, self.count_gr]
    #     n_comps = len(comps)
    #     comp_counts = [expr.count(comp) for comp in comps]
    #     matches0 = [i for i, x in enumerate(comp_counts) if x == 0]
    #     matches1 = [i for i, x in enumerate(comp_counts) if x == 1]
    #     if len(matches0) != (n_comps - 1) or len(matches1) != 1:
    #         return None

    #     comp_ind = matches1[0]
    #     comp = comps[comp_ind]
    #     comp_count_fcn = comp_count_fcns[comp_ind]
    #     lhs, rhs = ParseUtil.split1_strip(expr, sep=comp)

    #     # Check that rhs is an int
    #     rhs, err = ParseUtil.parse_int(rhs, variables)
    #     if err:
    #         return None

    #     # Check that lhs is event, count(event) or count_line(event)
    #     if lhs in self.event_names:
    #         event = lhs
    #         return comp_count_fcn(event, rhs)
    #     elif lhs.startswith("count(") and lhs.endswith(")"):
    #         event = lhs[6:-1].strip()
    #         if event in self.event_names:
    #             return comp_count_fcn(event, rhs)
    #     elif lhs.startswith("count_line(") and lhs.endswith(")"):
    #         event = lhs[11:-1].strip()
    #         if event in self.event_names:
    #             return comp_count_fcn(event, rhs, is_line=True)
    #     else:
    #         return None

    # def count_eq(self, event, val, is_line=False):
    #     if is_line:
    #         return self.count_line[event] == val
    #     else:
    #         return self.count[event] == val

    # def count_leq(self, event, val, is_line=False):
    #     if is_line:
    #         return self.count_line[event] <= val
    #     else:
    #         return self.count[event] <= val

    # def count_geq(self, event, val, is_line=False):
    #     if is_line:
    #         return self.count_line[event] >= val
    #     else:
    #         return self.count[event] >= val

    # def count_less(self, event, val, is_line=False):
    #     if is_line:
    #         return self.count_line[event] < val
    #     else:
    #         return self.count[event] < val

    # def count_gr(self, event, val, is_line=False):
    #     if is_line:
    #         return self.count_line[event] > val
    #     else:
    #         return self.count[event] > val


def check_action(action, parameters, global_variables, lineno, all_linelabels):
    if action.count(':') == 1 or action.count('=') == 1:
        if action.count('=') == 1:
            sep = '='
        else:
            sep = ':'
        var_name, _ = ParseUtil.split1_strip(action, sep=sep)
        var_err = is_valid_name(var_name, parameters, kw)
        if var_err is not None:
            raise ParseException(lineno, var_err)
        if global_variables.contains(var_name):
            raise ParseException(lineno, "Cannot modify global variable inside a phase.")
    elif action.startswith("count_reset(") and action.endswith(")"):
        behaviors = parameters.get(BEHAVIORS)
        stimulus_elements = parameters.get(STIMULUS_ELEMENTS)
        event = action[12:-1]
        if event not in stimulus_elements and event not in behaviors and event not in all_linelabels:
            raise ParseException(lineno, f"Unknown event '{event}' in count_reset.")
    else:
        raise ParseException(lineno, f"Unknown action '{action}'.")


class PhaseLine():
    def __init__(self, phase_obj, lineno, label, after_label, all_linelabels, parameters, global_variables):
        self.lineno = lineno
        self.label = label
        self.parameters = parameters
        self.all_linelabels = all_linelabels

        self.is_help_line = False
        self.stimulus = None  # A dict with an intensity for each element in stimulus_elememts
        self.action = None

        self.action, logic = ParseUtil.split1_strip(after_label, sep=PHASEDIV)
        if logic is None:
            raise ParseException(lineno, f"Missing separator '{PHASEDIV}' on phase line.")
        action_list = ParseUtil.comma_split_strip(self.action)

        first_element, _, _ = ParseUtil.parse_element_and_intensity(action_list[0], variables=None,
                                                                    safe_intensity_eval=True)
        self.is_help_line = (len(action_list) == 1) and (first_element not in parameters.get(STIMULUS_ELEMENTS))
        if self.is_help_line:
            self.stimulus = None
            if action_list[0] != '':
                check_action(action_list[0], parameters, global_variables, lineno, all_linelabels)
        else:
            self.stimulus, err = ParseUtil.parse_elements_and_intensities(self.action, global_variables,
                                                                          safe_intensity_eval=True)
            if err:
                raise ParseException(lineno, err)

            for element in self.stimulus:
                if element not in parameters.get(STIMULUS_ELEMENTS):
                    raise ParseException(lineno, f"Expected a stimulus element, got '{element}'.")

            self.action = None

        if len(logic) == 0:
            raise ParseException(lineno, f"Line with label '{label}' has no conditions.")
        self.conditions = PhaseLineConditions(phase_obj, lineno, self.is_help_line, logic, parameters,
                                              all_linelabels, global_variables)

    def next_line(self, response, global_variables, local_variables, event_counter):
        label = self.conditions.next_line(response, global_variables, local_variables, event_counter)
        return label


class PhaseLineConditions():
    def __init__(self, phase_obj, lineno, is_help_line, logic_str, parameters, all_linelabels,
                 global_variables):
        self.phase_obj = phase_obj

        # list of PhaseLineCondition objects
        self.conditions = list()

        self.logic_str = logic_str
        cond_gotos = logic_str.split(PHASEDIV)
        cond_gotos = [c.strip() for c in cond_gotos]
        n_logicparts = len(cond_gotos)
        for i, cond_goto in enumerate(cond_gotos):
            condition_obj = PhaseLineCondition(lineno, is_help_line, cond_goto, i,
                                               n_logicparts, parameters, all_linelabels, global_variables)
            self.conditions.append(condition_obj)

    def next_line(self, response, global_variables, local_variables, event_counter):
        for i, condition in enumerate(self.conditions):
            self.phase_obj.perform_actions(condition.unconditional_actions)
            condition_met, label = condition.is_met(response, global_variables, local_variables,
                                                    event_counter)
            if condition_met:
                self.phase_obj.perform_actions(condition.conditional_actions)
                return label
        raise Exception(f"No condition in '{self.logic_str}' was met for response '{response}'.")


class PhaseLineCondition():
    def __init__(self, lineno, is_help_line, cond_goto, logicpart_index, n_logicparts, parameters,
                 all_linelabels, global_variables):
        self.lineno = lineno

        # Unconditional actions
        self.unconditional_actions = list()

        # The condition
        self.condition = None

        # Whether or not the condition is a behavior
        self.condition_is_behavior = False

        # Conditional actions
        self.conditional_actions = list()

        # Row label to go to
        self.goto = None  # List of 2-lists [probability, row_label]

        self._parse(lineno, is_help_line, cond_goto, logicpart_index, n_logicparts, parameters,
                    all_linelabels, global_variables)

    def _parse(self, lineno, is_help_line, condition_and_actions, logicpart_index, n_logicparts, parameters,
               all_linelabels, global_variables):
        '''
        Args:
            condition_and_actions (str): Examples are
                "b=5: x:2, y=2, ROWLBL",
                "x:2, y:2, ROWLBL",
                "@break"
                "x=1: @break"
                "x:1"
                "@break, x:1"
        '''
        self.condition = None

        ca_list = ParseUtil.comma_split_strip(condition_and_actions)

        found_condition = False
        any_rowlbl_prob = False
        found_rowlbl = False
        goto_list = list()
        goto_list_index = list()
        for i, ca in enumerate(ca_list):
            err = f"Invalid statement '{ca}'."
            n_colons = ca.count(':')
            if n_colons == 0:
                contains_condition = False
                action = ca
            elif n_colons == 1:
                before_colon, after_colon = ParseUtil.split1_strip(ca, ':')
                contains_condition = self._is_condition(before_colon, parameters)
                if contains_condition:
                    if self.condition is not None:  # Cannot have multiple conditions
                        raise ParseException(lineno, f"Multiple conditions ('{self.condition}' and '{before_colon}') found in '{condition_and_actions}'.")
                    self.condition = before_colon
                    action = after_colon
                else:
                    action = ca
            elif n_colons == 2:
                colon_inds = [m.start() for m in re.finditer(':', ca)]
                if colon_inds[1] - colon_inds[0] == 1:
                    raise ParseException(lineno, err)
                before_first_colon, after_first_colon = ParseUtil.split1_strip(ca, ':')
                if not self._is_condition(before_first_colon, parameters):
                    raise ParseException(lineno, err)
                if self.condition is not None:  # Cannot have multiple conditions
                    raise ParseException(lineno, f"Multiple conditions ('{self.condition}' and '{before_first_colon}') found in '{condition_and_actions}'.")
                contains_condition = True
                self.condition = before_first_colon
                action = after_first_colon
            else:
                raise ParseException(lineno, err)

            if contains_condition and found_rowlbl:
                raise ParseException(lineno, f"Found condition '{self.condition}' after row label '{','.join(goto_list)}'.")

            found_condition = found_condition or contains_condition
            is_rowlbl, is_rowlbl_prob = self._is_rowlbl(action, all_linelabels)
            any_rowlbl_prob = (any_rowlbl_prob or is_rowlbl_prob)
            if is_rowlbl:
                found_rowlbl = True
                goto_list.append(action)
                goto_list_index.append(i)
            else:
                check_action(action, parameters, global_variables, lineno, all_linelabels)
                if found_rowlbl:
                    err = f"Row label(s) must be the last action(s). Found '{action}' after row-label."
                    raise ParseException(lineno, err)
                if found_condition:  # self.condition is not None:
                    self.conditional_actions.append(action)
                else:
                    self.unconditional_actions.append(action)

            is_last_action = (i == len(ca_list) - 1)
            if is_last_action and not is_rowlbl:
                raise ParseException(lineno, f"Last action must be a row label, found '{action}'.")

        if found_condition:
            self.condition_is_behavior = (self.condition in parameters.get(BEHAVIORS))
            cond_depends_on_behavior, err = ParseUtil.depends_on(self.condition, parameters.get(BEHAVIORS))
            if err is not None:
                raise ParseException(lineno, err)
            if cond_depends_on_behavior and is_help_line:
                raise ParseException(lineno, "Condition on help line cannot depend on response.")

        goto_str = ','.join(goto_list)

        # A deterministic ROWLBL cannot have elif/else continuation
        if (not found_condition) and found_rowlbl and not any_rowlbl_prob:
            if logicpart_index < n_logicparts - 1:
                err = f"The unconditional goto row label '{goto_str}' cannot be continued."
                raise ParseException(lineno, err)

        if len(goto_list) > 0:
            self._parse_goto(goto_str, lineno, all_linelabels, global_variables)

    def _is_rowlbl(self, lbl, all_linelabels):
        """Checks if the specified string is a row-label, either just the label or LABEL(something)."""
        if lbl in all_linelabels:
            return True, False
        lindex = lbl.find("(")
        rindex = lbl.find(")")
        if (lindex > 0) and (rindex == len(lbl) - 1) and (lbl[0:lindex] in all_linelabels):
            return True, True
        return False, None

    def _is_condition(self, condition, parameters):
        if condition in parameters.get(BEHAVIORS):
            return True
        return not condition.isidentifier()

    def is_met(self, response, global_variables, local_variables, event_counter):
        variables_both = Variables.join(global_variables, local_variables)
        if self.condition is None:
            ismet = True
        elif self.condition_is_behavior:
            ismet = (self.condition == response)
        else:
            ismet, err = ParseUtil.evaluate(self.condition, variables_both, event_counter,
                                            ParseUtil.PHASE_LINE)
            if err:
                raise ParseException(self.lineno, err)
            if type(ismet) is not bool:
                raise ParseException(self.lineno, f"Condition '{self.condition}' is not a boolean expression.")

        if ismet:
            label = self._goto_if_met(variables_both)
            if label is None:  # In "ROW1(0.1),ROW2(0.3)", goto_if_met returns None with prob. 0.6
                ismet = False
        else:
            label = None
        return ismet, label

    def _goto_if_met(self, variables):
        goto_prob_cumsum = list()
        cumsum = 0
        for i in range(len(self.goto)):
            prob = self.goto[i][0]
            if type(prob) is str:
                self.goto[i][0], err = ParseUtil.evaluate(prob, variables=variables)
                if err:
                    raise ParseException(self.lineno, err)
            cumsum += self.goto[i][0]
            goto_prob_cumsum.append(cumsum)
        if cumsum > 1:
            raise ParseException(self.lineno, f"Sum of probabilities is {cumsum}>1.")

        ind = ParseUtil.weighted_choice(goto_prob_cumsum)
        if ind is None:
            return None
        else:
            return self.goto[ind][1]

    def _parse_goto(self, goto_str, lineno, all_linelabels, global_variables):
        self.goto = list()
        err = f"Invalid condition '{goto_str}'. "
        lbls_and_probs = goto_str.split(',')
        lbls_and_probs = [lbl_and_prob.strip() for lbl_and_prob in lbls_and_probs]
        for lbl_and_prob in lbls_and_probs:
            if lbl_and_prob in all_linelabels:
                if len(lbls_and_probs) > 1:
                    raise ParseException(lineno, f"Invalid condition '{goto_str}'.")
                self.goto.append([1, lbl_and_prob])
            else:
                if '(' and ')' in lbl_and_prob:
                    if lbl_and_prob.count('(') > 1 or lbl_and_prob.count(')') > 1:
                        raise ParseException(lineno, err + "Too many parentheses.")
                    lindex = lbl_and_prob.find('(')
                    rindex = lbl_and_prob.find(')')
                    if lindex > rindex:
                        raise ParseException(lineno, err + "Mismatched parentheses.")

                    lbl = lbl_and_prob[0:lindex]
                    if lbl not in all_linelabels:
                        raise ParseException(lineno, err + f"Unknown line label '{lbl}'.")
                    prob_str = lbl_and_prob[(lindex + 1): rindex]
                    isprob, prob = ParseUtil.is_prob(prob_str, global_variables)

                    if not isprob:
                        if prob is not None:
                            raise ParseException(lineno, err + f"Expected a probability, got '{prob_str}'.")
                        prob = prob_str
                    for prob_lbl in self.goto:
                        if prob_lbl[1] == lbl:
                            raise ParseException(lineno, err + f"Label '{lbl}' duplicated.")
                    self.goto.append([prob, lbl])
                else:
                    raise ParseException(lineno, err + f"Invalid line label '{goto_str}'.")


class EndPhaseCondition():
    def __init__(self, lineno, endcond_str):
        self.lineno = lineno
        self.cond = endcond_str

    def is_met(self, variables, event_counter):
        ismet, err = ParseUtil.evaluate(self.cond, variables, event_counter, ParseUtil.STOP_COND)
        if err:
            raise ParseException(self.lineno, err)
        if type(ismet) is not bool:
            raise ParseException(self.lineno, f"Condition '{self.cond}' is not a boolean expression.")
        return ismet


class World():
    """
    A world, consisting of a number of Phase objects, producing a sequence of stimuli depending on
    the incoming sequence of responses.
    """

    def __init__(self, phases_dict, phase_labels):
        # self.phase_labels = phase_labels
        self.phases = [phases_dict[phase_label].copy() for phase_label in phase_labels]
        # for phase_label in phase_labels:
        #     self.phases[phase_label] = phases_obj.get(phase_label)
        self.nphases = len(phase_labels)
        self.curr_phaseind = 0  # Index into phase_labels

    def next_stimulus(self, response):
        """Returns a stimulus-tuple and current phase label."""
        curr_phase = self.phases[self.curr_phaseind]
        stimulus, row_lbl, preceeding_help_lines = curr_phase.next_stimulus(response)
        if stimulus is None:  # Phase done
            if self.curr_phaseind + 1 >= self.nphases:  # No more phases
                return None, curr_phase.label, row_lbl, preceeding_help_lines
            else:  # Go to next phase
                self.curr_phaseind += 1
                return self.next_stimulus(None)
        else:
            return stimulus, curr_phase.label, row_lbl, preceeding_help_lines

    # def get_phase_labels(self):
    #     phase_labels = [phase.label for phase in self.phases]
    #     return phase_labels

    def subject_reset(self):
        self.curr_phaseind = 0
        for phase in self.phases:
            phase.subject_reset()


# ------------------------------------

# class ScriptPhases():
#     def __init__(self):
#         # A 3-tuple. Index 0 is phase labels, index 1 is corresponding Phase objects, index 2
#         # is PhaseWorld objects
#         self.phases = (list(), list(), list())

    # def add(self, newblock, parameters):
    #     label = newblock.pvdict[LABEL]
    #     rows = newblock.content.splitlines()
    #     if label in self.phases[0]:
    #         ind = self.phases[0].index(label)
    #         self.phases[1][ind].add_rows(rows)
    #         self.phases[1][ind].pvdict.update(newblock.pvdict)
    #         self.phases[2][ind] = self.phases[1][ind].make_world(parameters)
    #     else:
    #         self.phases[0].append(label)
    #         phase_obj = Phase(newblock.pvdict, rows)
    #         self.phases[1].append(phase_obj)
    #         self.phases[2].append(phase_obj.make_world(parameters))

    # def make_world(self, phases_to_use):
    #     if len(phases_to_use) == 0:  # Empty tuple means all phases
    #         phases_to_use = self.phases[0]  # list(self.phases.keys())
    #     phase_worlds = list()
    #     for lbl in phases_to_use:
    #         if lbl not in self.phases[0]:
    #             raise Exception("Invalid phase label '{}'.".format(lbl))
    #         ind = self.phases[0].index(lbl)

    #         # Copy needed if phases_to_use is for example ('phase1','phase1')
    #         phase_obj = copy.deepcopy(self.phases[2][ind])

    #         phase_worlds.append(phase_obj)
    #     return LsWorld.World(phase_worlds)
