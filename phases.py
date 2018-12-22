from exceptions import ParseException
from util import ParseUtil
from keywords import PHASEDIV, STIMULUS_ELEMENTS, BEHAVIORS, BIND_TRIALS
from variables import Variables


class Phases():
    def __init__(self):
        self.phases = dict()  # Keys are phase labels, values are Phase objects

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

    def add_phase(self, label, stop_condition, lineno):
        if label in self.phases:
            raise Exception("Internal error.")
        self.phases[label] = Phase(label, stop_condition, lineno)

    def append_line(self, label, line, lineno):
        if label not in self.phases:
            raise Exception("Internal error.")
        self.phases[label].append_line(line, lineno)

    def labels_set(self):
        """Return all phase labels as a set."""
        return set(self.phases.keys())

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


class Phase():
    '''A number of rows of text, and a stop condition (string).'''

    def __init__(self, label, stop_condition, lineno):
        self.label = label
        self.stop_condition = stop_condition
        self.lineno = lineno
        self.lines = list()  # List of tuples (line, lineno)

        # Set in parse
        self.stimulus_elements = None
        self.behaviors = None
        self.variables = None
        self.linelabels = list()
        self.end_condition = None
        self.phase_lines = dict()  # Keys are phase line labels, values are PhaseLine objects
        self.first_label = None
        self.curr_lineobj = None
        self.event_counter = None

        self.is_first_line = True

        self.is_parsed = False

    def append_line(self, line, lineno):
        self.lines.append((line, lineno))

    def parse(self, parameters, variables):
        self.parameters = parameters
        self.variables = variables

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
            if label in self.linelabels:
                raise ParseException(lineno, f"Duplicate of phase line label '{label}'.")
            self.linelabels.append(label)
            phase_lines_afterlabel.append(afterlabel)
            linenos.append(lineno)
            if self.first_label is None:  # Set self.first_label to the label of the first line
                self.first_label = label

        # Second iteration: Create PhaseLine objects and put in the dict self.phase_lines
        for label, after_label, lineno in zip(self.linelabels, phase_lines_afterlabel, linenos):
            self.phase_lines[label] = PhaseLine(lineno, label, after_label, self.linelabels,
                                                self.parameters, self.variables)
            if label == "@new_trial":  # Change self.first_label to the @new_trial line
                self.first_label = label

        # Local variables
        action_lhs_vars = dict()
        for label, phase_line_obj in self.phase_lines.items():
            if phase_line_obj.action_lhs_var is not None:
                action_lhs_vars[phase_line_obj.action_lhs_var] = 0
        self.local_variables = Variables(action_lhs_vars)

        self.event_counter = PhaseEventCounter(self.linelabels, self.parameters)

        self.subject_reset()
        self.is_parsed = True

    def subject_reset(self):
        self.event_counter = PhaseEventCounter(self.linelabels, self.parameters)
        self.end_condition = EndPhaseCondition(self.lineno, self.stop_condition)
        self._make_current_line(self.first_label)
        self.prev_linelabel = None
        self.is_first_line = True

    def next_stimulus(self, response, ignore_response_increment=False):
        # if not self.is_parsed:
        #     raise Exception("Internal error: Cannot call Phase.next_stimulus" +
        #                     " before Phase.parse().")

        variables = Variables.join(self.variables, self.local_variables)

        if not ignore_response_increment:
            # if not self.is_first_line:
            if response is not None:
                self.event_counter.increment_count(response)
                self.event_counter.increment_count_line(response)

        if self.end_condition.is_met(variables, self.event_counter):
            return None, None

        if self.is_first_line:
            assert(response is None)
            rowlbl = self.first_label
            self.is_first_line = False
        else:
            rowlbl = self.curr_lineobj.next_line(response, variables, self.event_counter)
            self.prev_linelabel = self.curr_lineobj.label
            self._make_current_line(rowlbl)

        stimulus = self.phase_lines[rowlbl].stimulus

        if rowlbl != self.prev_linelabel:
            self.event_counter.reset_count_line()
            self.event_counter.line_label = rowlbl

        self.event_counter.increment_count(rowlbl)
        self.event_counter.increment_count_line(rowlbl)

        if stimulus is None:  # Help line
            action = self.phase_lines[rowlbl].action
            self._perform_action(action)
            stimulus = self.next_stimulus(response, ignore_response_increment=True)
        else:
            for stimulus_element in stimulus:
                self.event_counter.increment_count(stimulus_element)
                self.event_counter.increment_count_line(stimulus_element)

        return stimulus, rowlbl

    def _make_current_line(self, label):
        # self.curr_linelabel = label
        self.curr_lineobj = self.phase_lines[label]
        # self.endphase_obj.update_itemfreq(label)

    def _perform_action(self, action):
        """
        Sets a variable (x:3) or count_reset(event).
        """

        if len(action) == 0:  # No action to perform
            return

        if action.count(':') == 1:
            var_name, value_str = ParseUtil.split1_strip(action, sep=':')
            variables_join = Variables.join(self.variables, self.local_variables)
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


class PhaseEventCounter():
    def __init__(self, linelabels, parameters):
        stimulus_elements = parameters.get(STIMULUS_ELEMENTS)
        behaviors = parameters.get(BEHAVIORS)
        event_names = list(stimulus_elements) + list(behaviors) + linelabels
        # event_names = set(linelabels).union(stimulus_elements).union(behaviors)

        # self.count_line counts events on current line, start at 1 since it is  incremented only
        # when previous line is the same as current
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


class PhaseLine():
    def __init__(self, lineno, label, after_label, all_linelabels, parameters, variables):
        self.lineno = lineno
        self.label = label
        self.parameters = parameters
        self.variables = variables
        self.all_linelabels = all_linelabels

        self.is_help_line = False
        self.stimulus = None
        self.action = None

        self.consec_linecnt = 1
        self.consec_respcnt = 1
        # self.prev_response = None

        self.action_lhs_var = None

        self.action, logic = ParseUtil.split1_strip(after_label, sep=PHASEDIV)
        if logic is None:
            raise ParseException(lineno, f"Missing separator '{PHASEDIV}' on phase line.")
        action_list = ParseUtil.comma_split_strip(self.action)
        self.is_help_line = len(action_list) == 1 and action_list[0] not in parameters.get(STIMULUS_ELEMENTS)
        if self.is_help_line:
            self.stimulus = None
            if action_list[0] != '':
                self._check_action(action_list[0])
        else:
            for element in action_list:
                if element not in parameters.get(STIMULUS_ELEMENTS):
                    raise ParseException(lineno, f"Expected a stimulus element, got '{element}'.")
            self.stimulus = tuple(action_list)
            self.action = None

        if len(logic) == 0:
            raise ParseException(lineno, f"Line with label '{label}' has no conditions.")
        self.conditions = PhaseLineConditions(lineno, self.is_help_line, logic, parameters,
                                              all_linelabels, variables)

    def _check_action(self, action):
        behaviors = self.parameters.get(BEHAVIORS)
        stimulus_elements = self.parameters.get(STIMULUS_ELEMENTS)
        if action.count(':') == 1:
            var_name, _ = ParseUtil.split1_strip(action, sep=':')
            if self.variables.contains(var_name):
                raise ParseException(self.lineno, "Cannot modify global variable inside a phase.")
            else:
                self.action_lhs_var = var_name
        elif action.startswith("count_reset(") and action.endswith(")"):
            event = action[12:-1]
            if event not in stimulus_elements and event not in behaviors and event not in self.all_linelabels:
                raise ParseException(self.lineno, f"Unknown event '{event}' in count_reset.")
        else:
            raise ParseException(self.lineno, f"Unknown stimulus element or action '{action}'.")

    def next_line(self, response, variables, event_counter):
        label = self.conditions.next_line(response, variables, event_counter)
        return label


class PhaseLineConditions():
    def __init__(self, lineno, is_help_line, conditions_str, parameters, all_linelabels,
                 global_variables):
        # self.variables = variables

        # list of PhaseLineCondition objects
        self.conditions = list()

        self.conditions_str = conditions_str
        cond_gotos = conditions_str.split(PHASEDIV)
        cond_gotos = [c.strip() for c in cond_gotos]
        for cond_goto in cond_gotos:
            condition_obj = PhaseCondition(lineno, is_help_line, cond_goto,
                                           parameters, all_linelabels, global_variables)
            self.conditions.append(condition_obj)

    def next_line(self, response, variables, event_counter):
        for condition in self.conditions:
            condition_met, label = condition.is_met(response, variables, event_counter)
            if condition_met:
                return label
        raise Exception(f"No condition in '{self.conditions_str}' was met for response '{response}'.")


class PhaseCondition():
    def __init__(self, lineno, is_help_line, cond_goto, parameters, all_linelabels,
                 global_variables):
        self.lineno = lineno

        # Before colon
        self.cond = None
        self.cond_is_behavior = False

        # After colon
        self.goto = list()  # List of 2-tuples (probability, row_label)

        self._parse(lineno, is_help_line, cond_goto, parameters, all_linelabels, global_variables)

    def _parse(self, lineno, is_help_line, cond_goto, parameters, all_linelabels,
               global_variables):
        n_colons = cond_goto.count(':')
        if n_colons > 1:
            raise ParseException(lineno, f"Condition {cond_goto} has more than one colon.")
        if n_colons == 0:
            self.cond = None
            self.cond_is_behavior = False
            goto = cond_goto
        else:  # n_colons == 1
            cond, goto = ParseUtil.split1_strip(cond_goto, ':')
            self.cond = cond
            self.cond_is_behavior = cond in parameters.get(BEHAVIORS)
            if self.cond_is_behavior and is_help_line:
                raise ParseException(lineno, "Condition on help line cannot depend on response.")
        self._parse_goto(goto, lineno, all_linelabels, global_variables)

    def is_met(self, response, variables, event_counter):
        if self.cond is None:
            ismet = True
        elif self.cond_is_behavior:
            ismet = (self.cond == response)
        else:
            ismet, err = ParseUtil.evaluate(self.cond, variables, event_counter)
            if err:
                raise ParseException(self.lineno, err)
            if type(ismet) is not bool:
                raise ParseException(self.lineno, f"Condition '{self.cond}' is not a boolean expression.")
        if ismet:
            label = self._goto_if_met()
            if label is None:  # In "ROW1(0.1),ROW2(0.3)", goto_if_met returns None with prob. 0.6
                ismet = False
        else:
            label = None
        return ismet, label

    def _goto_if_met(self):
        tuple_ind = ParseUtil.weighted_choice(self.goto_prob_cumsum)
        if tuple_ind is None:
            return None
        else:
            return self.goto[tuple_ind][1]

    def _parse_goto(self, goto, lineno, all_linelabels, global_variables):
        # lbls_and_probs = ParseUtil.split1_strip(goto, sep=',')
        err = f"Invalid condition '{goto}'. "
        lbls_and_probs = goto.split(',')
        lbls_and_probs = [lbl_and_prob.strip() for lbl_and_prob in lbls_and_probs]
        for lbl_and_prob in lbls_and_probs:
            if lbl_and_prob in all_linelabels:
                if len(lbls_and_probs) > 1:
                    raise ParseException(lineno, f"Invalid condition '{goto}'.")
                self.goto.append((1, lbl_and_prob))
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
                        raise ParseException(lineno, err + f"Expected a probability, got '{prob_str}'.")
                    for prob_lbl in self.goto:
                        if prob_lbl[1] == lbl:
                            raise ParseException(lineno, err + f"Label '{lbl}' duplicated.")
                    self.goto.append((prob, lbl))
                else:
                    raise ParseException(lineno, err + f"Invalid line label '{goto}'.")

        self.goto_prob_cumsum = list()
        cumsum = 0
        for prob_lbl in self.goto:
            cumsum += prob_lbl[0]
            self.goto_prob_cumsum.append(cumsum)
        if cumsum > 1:
            raise ParseException(lineno, err + f"Sum of probabilities is {cumsum}>1.")


class PhaseCondition_old():
    def __init__(self, lineno, is_help_line, condition_str, parameters, all_linelabels, variables):
        # Before colon
        self.response = None
        self.count = None

        # After colon
        self.goto = list()  # List of 2-tuples (probability, row_label)

        # To speed up random row selection
        self.goto_prob_cumsum = None

        self._parse(lineno, is_help_line, condition_str, parameters, all_linelabels, variables)

    def is_met(self, response, event_counter):
        pass
        # ismet = False
        # if (self.response is not None) and (self.count is not None):
        #     ismet = (response == self.response) and (consec_respcnt >= self.count)
        # elif (self.response is None) and (self.count is not None):
        #     ismet = (consec_linecnt >= self.count)
        # elif (self.response is not None) and (self.count is None):
        #     ismet = (response == self.response)
        # else:  # (self.response is None) and (self.count is None):
        #     ismet = True

        # if ismet:
        #     label = self._goto_if_met()
        #     if label is None:  # In "ROW1(0.1),ROW2(0.3)", goto_if_met returns None with prob. 0.6
        #         ismet = False
        # else:
        #     label = None
        # return ismet, label

    def _goto_if_met(self):
        tuple_ind = ParseUtil.weighted_choice(self.goto_prob_cumsum)
        if tuple_ind is None:
            return None
        else:
            return self.goto[tuple_ind][1]

    def _parse(self, lineno, is_help_line, condition_str, parameters, all_linelabels, variables):
        if condition_str.count(':') > 1:
            raise ParseException(lineno, "Condition '{}' has more than one colon.".format(condition_str))
        lcolon, rcolon = ParseUtil.split1_strip(condition_str, ':')
        if rcolon is None:
            rcolon = lcolon
            lcolon = None

        # ---------- First parse lcolon ----------
        if lcolon is not None:
            if '=' in lcolon:
                response, count_str = ParseUtil.split1_strip(lcolon, '=')
                errmsg = "Expected an integer, got '{}'.".format(count_str)
                posintval, err = ParseUtil.parse_posint(count_str, variables)
                if err:
                    raise ParseException(lineno, err)
                if not posintval:
                    raise ParseException(lineno, errmsg)
                self.count = posintval
            else:
                if lcolon in parameters.get(BEHAVIORS):
                    response = lcolon
                else:
                    posintval, err = ParseUtil.parse_posint(lcolon, variables)
                    if err:
                        raise ParseException(lineno, err)
                    if posintval:
                        response = None
                        self.count = posintval
                    else:
                        raise ParseException(lineno, errmsg)

            # Check that response is valid
            if response is not None:
                if response not in parameters.get(BEHAVIORS):
                    raise ParseException(lineno, "Unknown response '{}'.".format(response))
                if is_help_line:
                    raise ParseException(lineno, "Condition on help line cannot depend on response.")
                self.response = response

        # ---------- Then parse rcolon ----------
        lbls_and_probs = rcolon.split(',')
        for lbl_and_prob in lbls_and_probs:
            if lbl_and_prob in all_linelabels:
                if len(lbls_and_probs) > 1:
                    raise ParseException(lineno, "Invalid condition '{}'.".format(lbls_and_probs))
                self.goto.append((1, lbl_and_prob))
            else:
                if '(' and ')' in lbl_and_prob:
                    if lbl_and_prob.count('(') > 1 or lbl_and_prob.count(')') > 1:
                        raise ParseException(lineno, "Invalid condition '{}'. Too many parentheses".format(lbl_and_prob))
                    if lbl_and_prob.find('(') > lbl_and_prob.find('('):
                        raise ParseException(lineno, "Invalid condition '{}'.".format(lbl_and_prob))
                    lindex = lbl_and_prob.find('(')
                    rindex = lbl_and_prob.find(')')
                    lbl = lbl_and_prob[0:lindex]
                    if lbl not in all_linelabels:
                        raise ParseException(lineno, "Invalid line label '{}'.".format(lbl))
                    prob_str = lbl_and_prob[(lindex + 1): rindex]
                    isprob, prob = ParseUtil.is_prob(prob_str)
                    if not isprob:
                        raise ParseException(lineno, "Expected a probability, got {}.".format(prob_str))
                    for prob_lbl in self.goto:
                        if prob_lbl[1] == lbl:
                            raise ParseException(lineno, "Label {0} duplicated in {1}.".format(lbl, rcolon))
                    self.goto.append((prob, lbl))
                else:
                    raise ParseException(lineno, "Malformed condition '{}'.".format(condition_str))

        self.goto_prob_cumsum = list()
        cumsum = 0
        for prob_lbl in self.goto:
            cumsum += prob_lbl[0]
            self.goto_prob_cumsum.append(cumsum)
        if cumsum > 1:
            raise ParseException(lineno, "Sum of probabilities in '{0}' is {1}>1.".format(rcolon, cumsum))


class EndPhaseCondition():
    def __init__(self, lineno, endcond_str):
        self.lineno = lineno
        self.cond = endcond_str

    def is_met(self, variables, event_counter):
        ismet, err = ParseUtil.evaluate(self.cond, variables, event_counter)
        if err:
            raise ParseException(self.lineno, err)
        if type(ismet) is not bool:
            raise ParseException(self.lineno, f"Condition '{self.cond}' is not a boolean expression.")
        return ismet


class EndPhaseCondition_old():
    def __init__(self, lineno, endcond_str, valid_items, variables):
        lhsrhs, err = ParseUtil.parse_equals(endcond_str)
        if err:
            raise ParseException(lineno, err)
        item = lhsrhs[0]
        number_str = lhsrhs[1]
        if item not in valid_items:
            raise ParseException(lineno, "Error in condition {0}. Invalid item {1}.".format(endcond_str, item))
        self.item = item
        # isnumber, number = ParseUtil.is_posint(number_str)
        # errmsg = "Expected positive integer. Got '{}'.".format(number_str)
        posintval, err = ParseUtil.parse_posint(number_str, variables)
        if err:
            raise ParseException(lineno, err)
        if not posintval:
            raise ParseException(lineno, "Error on condition {0}. {1} is not an integer.".format(endcond_str, posintval))
        self.limit = posintval

        self.itemfreq = 0
        # self.itemfreq = dict()
        # for item in valid_items:
        #     self.itemfreq[item] = 0

    def update_itemfreq(self, item):
        if type(item) is tuple:
            for element in item:
                if element == self.item:
                    self.itemfreq += 1
                # self.itemfreq[element] += 1
        else:
            if item == self.item:
                self.itemfreq += 1
            # self.itemfreq[item] += 1

    def is_met(self):
        # if self.item not in self.itemfreq:
        #     return False
        # else:
        # return self.itemfreq[self.item] >= self.limit
        return self.itemfreq >= self.limit


class World():
    """
    A world, consisting of a number of Phase objects, producing a sequence of stimuli depending on
    the incoming sequence of responses.
    """

    def __init__(self, phases_dict, phase_labels):
        self.phase_labels = phase_labels
        self.phases = [phases_dict[phase_label] for phase_label in phase_labels]
        # for phase_label in phase_labels:
        #     self.phases[phase_label] = phases_obj.get(phase_label)
        self.nphases = len(phase_labels)
        self.curr_phaseind = 0  # Index into phase_labels

    def next_stimulus(self, response):
        """Returns a stimulus-tuple and current phase label."""
        curr_phase = self.phases[self.curr_phaseind]
        stimulus, row_lbl = curr_phase.next_stimulus(response)
        if stimulus is None:  # Phase done
            if self.curr_phaseind + 1 >= self.nphases:  # No more phases
                return None, curr_phase.label, row_lbl
            else:  # Go to next phase
                self.curr_phaseind += 1
                return self.next_stimulus(response)
        else:
            return stimulus, curr_phase.label, row_lbl

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
