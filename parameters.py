import os

import keywords as kw
import mechanism_names as mn
import mechanism
from util import ParseUtil, make_readable_list_of_strings

# All parameters and their defaults.
PD = {kw.BEHAVIORS: list(),              # list of (restricted) strings                  , REQ
      kw.STIMULUS_ELEMENTS: list(),      # list of (restricted) strings                  , REQ
      kw.MECHANISM_NAME: '',             # One of the available ones                      REQ
      kw.START_V: 0,                     # Scalar or list of se->b:val or default:val   ,
      kw.START_VSS: 0,                   # Scalar or list of se->se:val or default:val  ,
      kw.ALPHA_V: 1,                     # -"-                                          ,
      kw.ALPHA_VSS: 1,                   # Scalar or list of se->se:val or default:val  ,
      kw.BETA: 1,                        # -"-                                          ,
      kw.MU: 0,                          # -"-                                          ,
      kw.DISCOUNT: 1,                    # Scalar
      kw.TRACE: 0,                       # Scalar (number between 0 and 1)
      kw.U: 0,                           # Scalar or list of se:val or default:val      ,
      kw.LAMBDA: 0,                      # Scalar or list of se:val or default:val      ,
      kw.START_W: 0,                     # -"-                                          ,
      kw.ALPHA_W: 1,                     # -"-                                          ,
      kw.BEHAVIOR_COST: 0,               # Scalar or list of b:val or default:val       ,
      kw.RESPONSE_REQUIREMENTS: dict(),  # List of b:se or b:(se1,se2,...)              ,
      kw.BIND_TRIALS: 'off',             # on or off
      kw.N_SUBJECTS: 1,                  # Positive integer
      kw.TITLE: '',                      # String                                      (,)
      kw.SUBPLOTTITLE: '',               # String                                      (,)
      kw.RUNLABEL: '',                   # String (restricted), for postrocessing only (,)
      kw.SUBJECT: 'average',             # average, all or zero-based index
      kw.XSCALE: 'all',                  # all or s1->b1->s2->..., s=se1,se2,...
      kw.XSCALE_MATCH: 'subset',         # subset or exact
      kw.EVAL_PHASES: 'all',             # @post: all or list of phase labels           ,
      kw.CUMULATIVE: 'on',               # on or off
      kw.MATCH: 'subset',                # subset or exact
      kw.FILENAME: ''}                   # valid path                                     REQ


def is_parameter_name(name):
    return name in PD


def check_is_parameter_name(name):
    if not is_parameter_name(name):
        return f"Internal error: Invalid parameter name '{name}'."
    return None


class Parameters():
    def __init__(self):
        # All parameters and their valuess
        self.val = dict(PD)
        # self.got = dict.fromkeys(PD, False)

    def str_append(self, prop, v_str, variables, phases, all_run_labels, to_be_continued):
        err = check_is_parameter_name(prop)
        if err:
            return err
        if not self.is_csv(prop):
            return f"Internal error: Parameter '{prop}' is not of type list."
        return self.str_set(prop, v_str, variables, phases, all_run_labels,
                            to_be_continued, True)

    def str_set(self, prop, v_str, variables, phases, all_run_labels, to_be_continued,
                is_appending=False):
        """
        Parses the specified value (as a string) of the specified parameter and sets the resulting
        value. The input variables is a Variables object.

        Returns error message if parsing failed.
        """
        err = check_is_parameter_name(prop)
        if err:
            return err

        # all_phase_labels = phases.labels_set()
        if prop == kw.BEHAVIORS:
            return self._parse_behaviors(v_str, variables, is_appending)

        elif prop == kw.STIMULUS_ELEMENTS:
            return self._parse_stimulus_elements(v_str, variables, is_appending)

        elif prop == kw.MECHANISM_NAME:
            return self._parse_mechanism_name(v_str)

        elif prop in (kw.START_VSS, kw.ALPHA_VSS):
            return self._parse_alphastart_vss(prop, v_str, variables, to_be_continued,
                                              is_appending)

        elif prop in (kw.START_W, kw.ALPHA_W, kw.U, kw.LAMBDA):
            return self._parse_stimulus_values(prop, v_str, variables, to_be_continued,
                                               is_appending)

        elif prop in (kw.BETA, kw.MU, kw.START_V, kw.ALPHA_V):
            return self._parse_stimulus_response_values(prop, v_str, variables,
                                                        to_be_continued, is_appending)

        # Float
        elif prop in (kw.DISCOUNT, kw.TRACE):
            v, err = ParseUtil.evaluate(v_str, variables)
            if err:
                return err
            if (v < 0) or (v > 1):
                return f"Parameter '{prop}' must be a number >=0 and <=1."
            self.val[prop] = v
            return None

        elif prop == kw.BEHAVIOR_COST:
            return self._parse_behavior_cost(v_str, variables, to_be_continued, is_appending)

        elif prop == kw.RESPONSE_REQUIREMENTS:
            return self._parse_response_requirements(v_str, to_be_continued, is_appending)

        # 'on' or 'off'
        elif prop in (kw.BIND_TRIALS, kw.CUMULATIVE):
            v_str_lower = v_str.lower()
            if v_str_lower not in ('on', 'off'):
                return "Parameter '{}' must be 'on' or 'off'.".format(prop)
            self.val[prop] = v_str_lower
            return None

        # Positive integer
        elif prop == kw.N_SUBJECTS:
            v, err = ParseUtil.parse_posint(v_str, variables)
            if err:
                return err
            if not v:
                return "Parameter {} must be a positive integer.".format(kw.N_SUBJECTS)
            self.val[kw.N_SUBJECTS] = v
            return None

        # Any nonempty (after strip) string
        elif prop in (kw.TITLE, kw.SUBPLOTTITLE):
            if to_be_continued:  # Add the removed comma
                v_str = v_str + ","
            self.val[prop] = v_str
            return None

        # 'average', 'all' or 1-based index
        elif prop == kw.SUBJECT:
            return self._parse_subject(v_str, variables)

        # 'all' or s1->b1->s2->..., s=se1,se2,...
        elif prop == kw.XSCALE:
            return self._parse_xscale(v_str, phases)

        # 'subset' or 'exact'
        elif prop in (kw.MATCH, kw.XSCALE_MATCH):
            if v_str.lower() not in ('subset', 'exact'):
                return "Parameter {} must be 'subset' or 'exact'.".format(prop)
            self.val[prop] = v_str
            return None

        # 'all' or cs-list of phase labels
        elif prop == kw.PHASES:
            return self._parse_phases(v_str)  # , all_phase_labels)

        # String (@run-labels) (for postprocessing)
        elif prop == kw.RUNLABEL:
            if v_str not in all_run_labels:
                return "Invalid @RUN-label {}".format(v_str)
            self.val[kw.RUNLABEL] = v_str
            return None

        # Valid path to writable file
        elif prop == kw.FILENAME:
            filename = v_str
            file = None
            try:
                file = open(filename, 'w', newline='')
            except Exception as ex:
                return str(ex)
            finally:
                if file is not None:
                    file.close()
                    try:
                        os.remove(filename)
                    except Exception as ex:
                        return str(ex)
            self.val[kw.FILENAME] = filename
            return None

    def make_mechanism_obj(self):
        """
        Returns a Mechanism object (None of error) and error message (None if no error).
        GA = 'ga'
        SR = 'sr'
        ES = 'es'
        QL = 'ql'
        AC = 'ac'
        RW = 'rw'
        MECHANISM_NAMES = (GA, SR, ES, QL, AC, RW)
        """
        mechanism_name = self.val[kw.MECHANISM_NAME]
        if not mechanism_name:
            return None, "Parameter 'mechanism' is not specified."

        self.scalar_expand()

        if mechanism_name in mn.SR:
            mechanism_obj = mechanism.StimulusResponse(self)
        elif mechanism_name in mn.QL:
            mechanism_obj = mechanism.Qlearning(self)
        # elif mechanism_name == SARSA:
        #     mechanism_obj = LsMechanism.SARSA(**self.parameters)
        elif mechanism_name in mn.ES:
            mechanism_obj = mechanism.EXP_SARSA(self)
        elif mechanism_name in mn.AC:
            mechanism_obj = mechanism.ActorCritic(self)
        elif mechanism_name in mn.GA:
            mechanism_obj = mechanism.Enquist(self)
        elif mechanism_name in mn.RW:
            mechanism_obj = mechanism.OriginalRescorlaWagner(self)
        else:
            raise Exception(f"Internal error. Unknown mechanism {mechanism_name}.")
        return mechanism_obj, None

    def _parse_behaviors(self, behaviors_str, variables, is_appending):
        """
        Parse the string behaviors_str with comma-separated behavior names and return the
        corrsponding set of strings.

        Example: "B1,  B2,B123" returns {'B1', 'B2', 'B123'}
        """
        if not is_appending:
            self.val[kw.BEHAVIORS] = list()
        behaviors_list = behaviors_str.split(',')
        for b in behaviors_list:
            b = b.strip()
            if len(b) == 0:
                return "Found empty behavior name."
            if b in self.val[kw.BEHAVIORS]:
                return f"The behavior name '{b}' occurs more than once."
            if b in self.val[kw.STIMULUS_ELEMENTS]:
                return f"The behavior name '{b}' is invalid, since it is a stimulus element."
            if variables.contains(b):
                return f"The behavior name '{b}' is invalid, since it is a variable name."
            if not b.isidentifier():
                return f"Behavior name '{b}' is not a valid identifier."
            self.val[kw.BEHAVIORS].append(b)
        return None  # No error

    def _parse_stimulus_elements(self, stimulus_elements_str, variables, is_appending):
        """
        Parse the string stimulus_elements_str with comma-separated stimulus element names and
        return the corrsponding set of strings.

        Example: "E1,  E2,E123" returns {'E1', 'E2', 'E123'}
        """
        if not is_appending:
            self.val[kw.STIMULUS_ELEMENTS] = list()
        stimulus_elements_list = stimulus_elements_str.split(',')
        for e in stimulus_elements_list:
            e = e.strip()
            if len(e) == 0:
                return "Found empty stimulus element name."
            if e in self.val[kw.STIMULUS_ELEMENTS]:
                return f"The stimulus element name '{e}' occurs more than once."
            if e in self.val[kw.BEHAVIORS]:
                return f"The stimulus element name '{e}' is invalid, since it is a behavior name."
            if variables.contains(e):
                return f"The stimulus element name '{e}' is invalid, since it is a variable name."
            if not e.isidentifier():
                return f"Stimulus element name '{e}' is not a valid identifier."
            self.val[kw.STIMULUS_ELEMENTS].append(e)
        return None  # No error

    def _parse_mechanism_name(self, mechanism_name):
        """
        Parse the string mechanism_name with a mechanism name and return the corrsponding string.
        """
        mn_lower = mechanism_name.lower()
        if mn_lower not in mn.MECHANISM_NAMES:
            cs_valid_names = ', '.join(sorted(mn.MECHANISM_NAMES))
            return "Invalid mechanism name '{}'. ".format(mechanism_name) + \
                   "Mechanism name must be one of the following: {}.".format(cs_valid_names)
        self.val[kw.MECHANISM_NAME] = mn_lower
        return None

    def _parse_phases(self, v_str):
        if v_str == 'all':
            self.val[kw.PHASES] = v_str  # list(all_phase_labels)
        else:
            phase_labels = ParseUtil.comma_split_strip(v_str)
            for phase_label in phase_labels:
                if len(phase_label) == 0:
                    return "Expected comma-separated list of phase labels, found {}".format(phase_labels)
                # else:
                #     if phase_label not in all_phase_labels:
                #         return "Undefined phase label '{}'.".format(phase_label)
            self.val[kw.PHASES] = phase_labels
        return None

    def _parse_behavior_cost(self, behavior_cost_str, variables, to_be_continued, is_appending):
        if not self.val[kw.BEHAVIORS]:
            return f"The parameter 'behaviors' must be assigned before the parameter '{kw.BEHAVIOR_COST}'."

        # Create and populate the struct with None values
        if not is_appending:
            self.val[kw.BEHAVIOR_COST] = dict()
            for e in self.val[kw.BEHAVIORS]:
                self.val[kw.BEHAVIOR_COST][e] = None
            self.val[kw.BEHAVIOR_COST][kw.DEFAULT] = None

        single_c, _ = ParseUtil.evaluate(behavior_cost_str, variables)
        if single_c is not None:
            if is_appending:
                return "A single value for '{}' cannot follow other values.".format(kw.BEHAVIOR_COST)
            elif to_be_continued:
                return "A single value for '{}' cannot be followed by other values.".format(kw.BEHAVIOR_COST)
            else:
                for key in self.val[kw.BEHAVIOR_COST]:
                    self.val[kw.BEHAVIOR_COST][key] = single_c
                self.val[kw.BEHAVIOR_COST].pop(kw.DEFAULT)
        else:
            cs = ParseUtil.comma_split(behavior_cost_str)
            cs = [x.strip() for x in cs]
            for bc_str in cs:  # bc_str is 'e:value' or 'default:value'
                if bc_str.count(':') != 1:
                    return "Expected 'element:value' or 'default:value' in '{}', got '{}'.".format(kw.BEHAVIOR_COST, bc_str)
                b, c_str = bc_str.split(':')
                b = b.strip()
                c_str = c_str.strip()
                c, err = ParseUtil.evaluate(c_str, variables)
                if err:
                    return f"Invalid value '{c_str}' for '{b}' in parameter '{kw.BEHAVIOR_COST}'."

                if b == kw.DEFAULT:
                    if self.val[kw.BEHAVIOR_COST][kw.DEFAULT] is not None:
                        return "Default value for '{}' can only be stated once.".format(kw.BEHAVIOR_COST)
                    self.val[kw.BEHAVIOR_COST][kw.DEFAULT] = c
                else:
                    if b == "*":
                        bs = self.val[kw.BEHAVIORS]
                    else:
                        bs = [b]
                        if b not in self.val[kw.BEHAVIORS]:
                            return f"Error in parameter '{kw.BEHAVIOR_COST}': '{b}' is an invalid behavior name."
                    for b in bs:
                        self.val[kw.BEHAVIOR_COST][b] = c

            if not to_be_continued:
                # Set the default value for non-set behaviors
                err = self._set_default_values(kw.BEHAVIOR_COST)
                if err:
                    return err

        return None  # No error

    def _parse_stimulus_response_values(self, NAME, sr_str, variables, to_be_continued,
                                        is_appending):
        """
        Parse the string sr_str with a value for stimulus-response pairs.

        Example: "S1->R1: 1.23, S2->R1:3.45, default:1" sets the parameter to
                 {('S1','R1'):1.23, ('S1','R2'):1, ('S2','R1'):3.45, ('S2','R2'):1}
                 under the assumption that
                 behaviors = {'R1', 'R2'} and
                 stimulus_elements = {'S1', 'S2'}
        """
        if not self.val[kw.STIMULUS_ELEMENTS]:
            return f"The parameter 'stimulus_elements' must be assigned before the parameter '{NAME}'."
        if not self.val[kw.BEHAVIORS]:
            return f"The parameter 'behaviors' must be assigned before the parameter '{NAME}'."

        # Create and populate the struct with None values
        if not is_appending:
            self.val[NAME] = dict()
            for e in self.val[kw.STIMULUS_ELEMENTS]:
                for b in self.val[kw.BEHAVIORS]:
                    self.val[NAME][(e, b)] = None
            self.val[NAME][kw.DEFAULT] = None

        single_v, _ = ParseUtil.evaluate(sr_str, variables)
        if single_v is not None:
            if is_appending:
                return f"A single value for '{NAME}' cannot follow other values."
            elif to_be_continued:
                return f"A single value for '{NAME}' cannot be followed by other values."
            else:
                for key in self.val[NAME]:
                    self.val[NAME][key] = single_v
                self.val[NAME].pop(kw.DEFAULT)
        else:
            vs = ParseUtil.comma_split(sr_str)
            vs = [x.strip() for x in vs]
            for eb_v_str in vs:  # eb_v_str is 'e->b:value' or 'default:value'
                if eb_v_str.count(':') != 1:
                    return f"Expected 'x->y:value' or 'default:value' in '{NAME}', got '{eb_v_str}'."
                eb, v_str = eb_v_str.split(':')
                eb = eb.strip()
                v_str = v_str.strip()
                v, err = ParseUtil.evaluate(v_str, variables)
                if err:
                    return f"Invalid value '{v_str}' for '{eb}' in parameter '{NAME}'."

                if eb == kw.DEFAULT:
                    if self.val[NAME][kw.DEFAULT] is not None:
                        return f"Default value for '{NAME}' can only be stated once."
                    self.val[NAME][kw.DEFAULT] = v
                elif eb.count('->') == 1:
                    e, b = eb.split('->')
                    e = e.strip()
                    b = b.strip()
                    if e == "*":
                        es = self.val[kw.STIMULUS_ELEMENTS]
                    else:
                        es = [e]
                        if e not in self.val[kw.STIMULUS_ELEMENTS]:
                            return f"Error in parameter '{NAME}': '{e}' is an invalid stimulus element."

                    if b == "*":
                        bs = self.val[kw.BEHAVIORS]
                    else:
                        bs = [b]
                        if b not in self.val[kw.BEHAVIORS]:
                            return f"Error in parameter '{NAME}': '{b}' is an invalid behavior name."
                    for e in es:
                        for b in bs:
                            self.val[NAME][(e, b)] = v
                else:
                    return f"Invalid string '{eb}' in parameter '{NAME}'."

            if not to_be_continued:
                # Set the default value for non-set stimulus-behavior pairs
                err = self._set_default_values(NAME)
                if err:
                    return err

        return None  # No error

    def _parse_alphastart_vss(self, NAME, vss_str, variables, to_be_continued,
                              is_appending):
        """
        Parse the string vss_str with a start_vss/alpha_vss specification.

        Example: "S1->S2: 1.23, S2->S1:3.45, default:1" sets the parameter to
                 {('S1','S2'):1.23, ('S2','S1'):3.45, ('S1','S1'):1, ('S2','S2'):1}
                 under the assumption that stimulus_elements = {'S1', 'S2'}
        """
        if not self.val[kw.STIMULUS_ELEMENTS]:
            return f"The parameter 'stimulus_elements' must be assigned before the parameter '{NAME}'."

        # Create and populate the struct with None values
        if not is_appending:
            self.val[NAME] = dict()
            for e1 in self.val[kw.STIMULUS_ELEMENTS]:
                for e2 in self.val[kw.STIMULUS_ELEMENTS]:
                    self.val[NAME][(e1, e2)] = None
            self.val[NAME][kw.DEFAULT] = None

        single_vss, _ = ParseUtil.evaluate(vss_str, variables)
        if single_vss is not None:
            if is_appending:
                return f"A single value for '{NAME}' cannot follow other values."
            elif to_be_continued:
                return f"A single value for '{NAME}' cannot be followed by other values."
            else:
                for key in self.val[NAME]:
                    self.val[NAME][key] = single_vss
                self.val[NAME].pop(kw.DEFAULT)
        else:
            vs = ParseUtil.comma_split(vss_str)
            vs = [x.strip() for x in vs]
            for ee_str in vs:  # eb_v_str is 'e1->e2:value' or 'default:value'
                if ee_str.count(':') != 1:
                    return f"Expected 'x->y:value' or 'default:value' in '{NAME}', got '{ee_str}'."
                ee, v_str = ee_str.split(':')
                ee = ee.strip()
                v_str = v_str.strip()
                v, err = ParseUtil.evaluate(v_str, variables)
                if err:
                    return f"Invalid value '{v_str}' for '{ee}' in parameter '{NAME}'."

                if ee == kw.DEFAULT:
                    if self.val[NAME][kw.DEFAULT] is not None:
                        return f"Default value for '{NAME}' can only be stated once."
                    self.val[NAME][kw.DEFAULT] = v
                elif ee.count('->') == 1:
                    e1, e2 = ee.split('->')
                    e1 = e1.strip()
                    e2 = e2.strip()
                    if e1 == "*":
                        e1s = self.val[kw.STIMULUS_ELEMENTS]
                    else:
                        e1s = [e1]
                        if e1 not in self.val[kw.STIMULUS_ELEMENTS]:
                            return f"Error in parameter '{NAME}': '{e1}' is an invalid stimulus element."
                    if e2 == "*":
                        e2s = self.val[kw.STIMULUS_ELEMENTS]
                    else:
                        e2s = [e2]
                        if e2 not in self.val[kw.STIMULUS_ELEMENTS]:
                            return f"Error in parameter '{NAME}': '{e2}' is an invalid stimulus element."
                    for e1 in e1s:
                        for e2 in e2s:
                            self.val[NAME][(e1, e2)] = v
                else:
                    return f"Invalid string '{ee}' in parameter '{NAME}'."

            if not to_be_continued:
                # Set the default value for non-set stimulus-stimulus pairs
                err = self._set_default_values(NAME)
                if err:
                    return err

        return None  # No error

    def _parse_response_requirements(self, v_str, to_be_continued, is_appending):
        if not self.val[kw.STIMULUS_ELEMENTS]:
            return f"The parameter 'stimulus_elements' must be assigned before the parameter '{kw.RESPONSE_REQUIREMENTS}'."
        if not self.val[kw.BEHAVIORS]:
            return f"The parameter 'behaviors' must be assigned before the parameter '{kw.RESPONSE_REQUIREMENTS}'."

        if not is_appending:
            self.val[kw.RESPONSE_REQUIREMENTS] = dict()
            for b in self.val[kw.BEHAVIORS]:
                self.val[kw.RESPONSE_REQUIREMENTS][b] = None

        rrs = ParseUtil.comma_split_sq(v_str)
        for rr in rrs:
            if rr.count(':') != 1:
                return "Expected 'behavior:stimulus_element', got '{}'.".format(rr)
            b, s = rr.split(':')
            b = b.strip()
            s = s.strip()
            if len(b) == 0 or len(s) == 0:
                return "Expected 'behavior:stimulus_element', got '{}'.".format(rr)
            if b not in self.val[kw.BEHAVIORS]:
                return "Unknown behavior name '{}'.".format(b)
            if self.val[kw.RESPONSE_REQUIREMENTS][b] is not None:
                return "Duplication of behavior '{}' in {}.".format(b, kw.RESPONSE_REQUIREMENTS)
            if '[' in s or ']' in s:
                if s.count('[') != 1 or s.count(']') != 1 or s[0] != '[' or s[-1] != ']':
                    return "Malformed expression '{}'.".format(s)
                s = s[1:-1]  # Strip the '['and the ']'
                es = s.split(',')
                for e in es:
                    e = e.strip()
                    if e not in self.val[kw.STIMULUS_ELEMENTS]:
                        return "Unknown stimulus element '{}'.".format(e)
                    self._response_requirements_add_element(b, e)
            else:
                if s not in self.val[kw.STIMULUS_ELEMENTS]:
                    return "Unknown stimulus element '{}'.".format(s)
                self._response_requirements_add_element(b, s)

        if not to_be_continued:
            # For the unrestricted behaviors, add all stimulus elements
            for b in self.val[kw.RESPONSE_REQUIREMENTS]:
                if self.val[kw.RESPONSE_REQUIREMENTS][b] is None:
                    self.val[kw.RESPONSE_REQUIREMENTS][b] = set(self.val[kw.STIMULUS_ELEMENTS])

            # Check that each stimulus element has at least one feasible response
            stimulus_elements_in_rr = []
            for stimulus_list in self.val[kw.RESPONSE_REQUIREMENTS].values():
                stimulus_elements_in_rr.extend(stimulus_list)
            if set(stimulus_elements_in_rr) != set(self.val[kw.STIMULUS_ELEMENTS]):
                elements_without_response = set(self.val[kw.STIMULUS_ELEMENTS]) - set(stimulus_elements_in_rr)
                elements_without_response = list(elements_without_response)
                elements_without_response.sort()  # To make error message testable
                elements_without_response_str = make_readable_list_of_strings(elements_without_response)
                err = f"Invalid {kw.RESPONSE_REQUIREMENTS}: "
                if len(elements_without_response) == 1:
                    return err + f"Stimulus element {elements_without_response_str} has no possible responses."
                else:
                    return err + f"Stimulus elements {elements_without_response_str} have no possible responses."

        return None  # No error

    def _response_requirements_add_element(self, b, e):
        if self.val[kw.RESPONSE_REQUIREMENTS][b] is None:
            self.val[kw.RESPONSE_REQUIREMENTS][b] = {e}
        else:
            self.val[kw.RESPONSE_REQUIREMENTS][b].add(e)

    def _parse_stimulus_values(self, NAME, stimulus_values, variables, to_be_continued,
                               is_appending):
        if not self.val[kw.STIMULUS_ELEMENTS]:
            return f"The parameter 'stimulus_elements' must be assigned before the parameter '{NAME}'."

        # Create and populate the struct with None values
        if not is_appending:
            self.val[NAME] = dict()
            for e in self.val[kw.STIMULUS_ELEMENTS]:
                self.val[NAME][e] = None
            self.val[NAME][kw.DEFAULT] = None

        single_w, _ = ParseUtil.evaluate(stimulus_values, variables)
        if single_w is not None:
            if is_appending:
                return "A single value for '{}' cannot follow other values.".format(NAME)
            elif to_be_continued:
                return "A single value for '{}' cannot be followed by other values.".format(NAME)
            else:
                for key in self.val[NAME]:
                    self.val[NAME][key] = single_w
                self.val[NAME].pop(kw.DEFAULT)
        else:
            ws = ParseUtil.comma_split(stimulus_values)
            ws = [x.strip() for x in ws]
            for e_w_str in ws:  # eb_w_str is 'e:value' or 'default:value'
                if e_w_str.count(':') != 1:
                    return "Expected 'element:value' or 'default:value' in '{}', got '{}'.".format(NAME, e_w_str)
                e, w_str = e_w_str.split(':')
                e = e.strip()
                w_str = w_str.strip()
                w, err = ParseUtil.evaluate(w_str, variables)
                if err:
                    return "Invalid value '{}' for '{}' in parameter '{}'.".format(w_str, e, NAME)

                if e == kw.DEFAULT:
                    if self.val[NAME][kw.DEFAULT] is not None:
                        return "Default value for '{}' can only be stated once.".format(NAME)
                    self.val[NAME][kw.DEFAULT] = w
                else:
                    if e == "*":
                        es = self.val[kw.STIMULUS_ELEMENTS]
                    else:
                        es = [e]
                        if e not in self.val[kw.STIMULUS_ELEMENTS]:
                            return f"Error in parameter '{NAME}': '{e}' is an invalid stimulus element."
                    for e in es:
                        self.val[NAME][e] = w

            if not to_be_continued:
                # Set the default value for non-set stimulus elements
                err = self._set_default_values(NAME)
                if err:
                    return err

        return None  # No error

    def _parse_subject(self, v_str, variables):
        err = f"Parameter {kw.SUBJECT} must be 'average', 'all', or a positive integer."
        if v_str.lower() in ('average', 'all'):
            self.val[kw.SUBJECT] = v_str.lower()
        else:
            v, interr = ParseUtil.parse_posint(v_str, variables)
            if interr:  # Parsing error
                return err + " " + interr
            if v is None:  # Parsing worked, but negative integer
                return err
            self.val[kw.SUBJECT] = v - 1  # Zero-based index internally
        return None

    def _parse_xscale(self, xscale, phases):
        if not self.val[kw.STIMULUS_ELEMENTS]:
            return f"The parameter 'stimulus_elements' must be assigned before the parameter '{kw.XSCALE}'."
        if not self.val[kw.BEHAVIORS] and self.val[kw.MECHANISM_NAME] not in mn.RW:
            return f"The parameter 'behaviors' must be assigned before the parameter '{kw.XSCALE}'."

        if phases.is_phase_label(xscale):
            pass
        elif xscale == 'all':
            pass
        else:
            xscale, _, _, err = ParseUtil.parse_chain(xscale, self.val[kw.STIMULUS_ELEMENTS],
                                                      self.val[kw.BEHAVIORS])
            if err:
                return err

        self.val[kw.XSCALE] = xscale
        return None

    def _set_default_values(self, NAME):
        default_needed = False
        for key in self.val[NAME]:
            if key is not kw.DEFAULT and self.val[NAME][key] is None:
                default_needed = True
                break
        if default_needed and self.val[NAME][kw.DEFAULT] is None:
            return f"Missing default value for parameter '{NAME}'."
        else:
            for key in self.val[NAME]:
                if self.val[NAME][key] is None:
                    self.val[NAME][key] = self.val[NAME][kw.DEFAULT]
            self.val[NAME].pop(kw.DEFAULT)

    def get(self, prop):
        return self.val[prop]

    def may_end_with_comma(self, prop):
        return self.is_csv(prop) or prop in (kw.TITLE, kw.SUBPLOTTITLE, kw.RUNLABEL)

    def is_csv(self, prop):
        return prop in (kw.BEHAVIORS, kw.STIMULUS_ELEMENTS, kw.BETA, kw.MU, kw.LAMBDA, kw.START_V,
                        kw.START_VSS, kw.START_W, kw.ALPHA_V, kw.ALPHA_VSS, kw.ALPHA_W,
                        kw.BEHAVIOR_COST, kw.U, kw.RESPONSE_REQUIREMENTS, kw.PHASES)

    def scalar_expand(self):
        """
        Expand dict-parameters that are defined by scalar. If defined as dict, check that keys are
        compatible with stimulus elements and behaviors.
        """
        behaviors = self.val[kw.BEHAVIORS]
        stimulus_elements = self.val[kw.STIMULUS_ELEMENTS]

        # Check START_VSS and ALPHA_VSS
        expected_ss_keys = set()
        for stimulus_element1 in stimulus_elements:
            for stimulus_element2 in stimulus_elements:
                key = (stimulus_element1, stimulus_element2)
                expected_ss_keys.add(key)

        for param_name in [kw.START_VSS, kw.ALPHA_VSS]:
            start_vss = self.val[param_name]
            if type(start_vss) is dict:
                if set(start_vss.keys()) != expected_ss_keys:
                    self._raise_match_err(param_name, kw.STIMULUS_ELEMENTS)
            else:  # scalar expand
                self.val[param_name] = dict()
                scalar = start_vss
                for stimulus_element1 in stimulus_elements:
                    for stimulus_element2 in stimulus_elements:
                        key = (stimulus_element1, stimulus_element2)
                        self.val[param_name][key] = scalar

        expected_sb_keys = set()
        for stimulus_element in stimulus_elements:
            for behavior in behaviors:
                key = (stimulus_element, behavior)
                expected_sb_keys.add(key)

        # Check START_V
        self._scalar_expand_element_behavior(kw.START_V, stimulus_elements, behaviors,
                                             expected_sb_keys)

        # Check ALPHA_V
        self._scalar_expand_element_behavior(kw.ALPHA_V, stimulus_elements, behaviors,
                                             expected_sb_keys)

        # Check BETA
        self._scalar_expand_element_behavior(kw.BETA, stimulus_elements, behaviors,
                                             expected_sb_keys)

        # Check MU
        self._scalar_expand_element_behavior(kw.MU, stimulus_elements, behaviors,
                                             expected_sb_keys)

        expected_s_keys = set()
        for stimulus_element in stimulus_elements:
            expected_s_keys.add(stimulus_element)

        # Check U
        self._scalar_expand_element(kw.U, stimulus_elements, expected_s_keys)

        # Check START_W
        self._scalar_expand_element(kw.START_W, stimulus_elements, expected_s_keys)

        # Check ALPHA_W
        self._scalar_expand_element(kw.ALPHA_W, stimulus_elements, expected_s_keys)

        # Check LAMBDA
        self._scalar_expand_element(kw.LAMBDA, stimulus_elements, expected_s_keys)

        # Check BEHAVIOR_COST
        expected_b_keys = set()
        for behavior in behaviors:
            expected_b_keys.add(behavior)

        behavior_cost = self.val[kw.BEHAVIOR_COST]
        if type(behavior_cost) is dict:
            if set(behavior_cost.keys()) != expected_b_keys:
                self._raise_match_err(kw.BEHAVIOR_COST, kw.BEHAVIORS)
        else:  # scalar expand
            self.val[kw.BEHAVIOR_COST] = dict()
            scalar = behavior_cost
            for behavior in behaviors:
                self.val[kw.BEHAVIOR_COST][behavior] = scalar

    def _scalar_expand_element_behavior(self, param_name, stimulus_elements, behaviors,
                                        expected_sb_keys):
        val = self.val[param_name]
        if type(val) is dict:
            if set(val.keys()) != expected_sb_keys:
                self._raise_match_err(param_name, kw.STIMULUS_ELEMENTS, kw.BEHAVIORS)
        else:  # scalar expand
            self.val[param_name] = dict()
            scalar = val
            for stimulus_element in stimulus_elements:
                for behavior in behaviors:
                    key = (stimulus_element, behavior)
                    self.val[param_name][key] = scalar

    def _scalar_expand_element(self, param_name, stimulus_elements, expected_s_keys):
        val = self.val[param_name]
        if type(val) is dict:
            if set(val.keys()) != expected_s_keys:
                self._raise_match_err(param_name, kw.STIMULUS_ELEMENTS)
        else:  # scalar expand
            self.val[param_name] = dict()
            scalar = val
            for stimulus_element in stimulus_elements:
                self.val[param_name][stimulus_element] = scalar

    @staticmethod
    def _raise_match_err(param1, param2, param3=None):
        if param3:
            err = f"The parameter '{param1}' does not match '{param2}' and '{param3}'."
        else:
            err = f"The parameter '{param1}' does not match '{param2}'."
        raise Exception(err)
