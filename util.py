import ast
import re
import random
import os
import sys


def rand(start, stop):
    if not type(start) is int:
        raise Exception("First argument to 'rand' must be integer.")
    if not type(stop) is int:
        raise Exception("Second argument to 'rand' must be integer.")
    if start > stop:
        raise Exception("The first argument to 'rand' must be less than or equal to the second argument.")
    return random.randint(start, stop)


def choice(*args):
    def _is_numeric_iter(vec):
        return all(isinstance(x, (int, float)) for x in vec)

    def _choice_float(population, weights=None):
        ERRMSG = "Found non-number in 'choice'."
        if not _is_numeric_iter(population):
            raise Exception(ERRMSG)
        if weights is None:
            return random.choice(population)
        if not _is_numeric_iter(weights):
            raise Exception(ERRMSG)
        return random.choices(population=population, weights=weights, k=1)[0]

    nargs = len(args)
    if nargs == 0:
        raise Exception("The function 'choice' must have at least one argument.")
    elif nargs == 1:
        if type(args[0]) is list:
            return _choice_float(args[0])
        else:
            raise Exception("Single input to 'choice' must be a list.")
    elif nargs == 2 and all(isinstance(x, list) for x in args):
        return _choice_float(args[0], args[1])
    else:
        return _choice_float(args)


def count(event_counter, event):
    return event_counter.count[event]


def count_line(event_counter, event):
    return event_counter.count_line[event]


class ParseUtil():
    # Used for evaluation in EndPhaseCondition.is_met and PhaseLineCondition.is_met
    STOP_COND = 0
    PHASE_LINE = 1

    @staticmethod
    def is_float(expr):
        """
        Check that the specified expression represents a number. Return the number (None if it
        does not represent a number) and the error (None if it does represent a number).
        """
        try:
            value = float(expr)
            return value, None
        except ValueError:
            err = "'{}' does not represent a number".format(expr)
            return None, err

    # @staticmethod
    # def is_number(string):
    #     try:
    #         val = ast.literal_eval(string)
    #         return True, val
    #     except ValueError:
    #         if string.count('/') != 1:
    #             return False, None
    #         else:
    #             num_str, den_str = string.split('/')
    #             num_ok, num = ParseUtil.is_number(num_str)
    #             den_ok, den = ParseUtil.is_number(den_str)
    #             if num_ok and den_ok:
    #                 return True, num / den
    #             else:
    #                 return False, None

    @staticmethod
    def is_prob(string, variables):
        val, err = ParseUtil.evaluate(string, variables)
        if err:
            return False, None
        else:
            if val < 0 or val > 1:
                return False, val
        return True, val

    @staticmethod
    def comma_split(string):
        '''
        Split the specified string at each comma (,) except the commas within parenthesis. For
        example, split 'a:1, b:2, c:rand(a,b,c), c:3' into ['a:1', 'b:2', 'c:rand(a,b,c)', 'c:3'].
        '''
        return re.split(r',\s*(?![^()]*\))', string)

    @staticmethod
    def comma_split_strip(string):
        cs = ParseUtil.comma_split(string)
        for i, _ in enumerate(cs):
            cs[i] = cs[i].strip()
        return cs

    @staticmethod
    def comma_split_sq(string):  # XXX
        if '(' in string or ')' in string:
            raise Exception("Internal error. Cannot use ParseUtil.comma_split_sq on strings that contain '(' or ')'.")
        sp = ParseUtil.comma_split(string.replace('[', '(').replace(']', ')'))
        for i, s in enumerate(sp):
            sp[i] = s.replace('(', '[').replace(')', ']')
        return sp

    @staticmethod
    def parse_posint(v_str, variables):
        v, parse_err = ParseUtil.evaluate(v_str, variables)
        if parse_err:
            return None, parse_err
        if type(v) is not int:
            return None, None
        if v <= 0:
            return None, None
        return v, None

    @staticmethod
    def parse_int(v_str, variables):
        v, parse_err = ParseUtil.evaluate(v_str, variables)
        if parse_err:
            return None, parse_err
        if type(v) is not int:
            return None, None
        return v, None

    @staticmethod
    def _single2double_eq(expr0):
        expr = expr0
        if expr.find('=') >= 0:
            if expr.find('==') < 0 and expr.find('<=') < 0 and expr.find('>=') < 0:
                expr = expr0.replace("=", "==")
        return expr

    @staticmethod
    def variables_in_expr(expr):
        expr = ParseUtil._single2double_eq(expr)
        tree = ast.parse(expr, mode='eval')
        out = list()
        for node in ast.walk(tree):
            if type(node) is ast.Name:
                out.append(node.id)
        return out

    @staticmethod
    def depends_on(expr_orig, var_list):
        expr = ParseUtil._single2double_eq(expr_orig)
        tree, err = ParseUtil.ast_parse(expr)
        if err is not None:
            return None, err
        for node in ast.walk(tree):
            if type(node) is ast.Name:
                name = node.id
                if name in var_list:
                    return True, err
        return False, None

    @staticmethod
    def ast_parse(expr):
        try:
            tree = ast.parse(expr, mode='eval')
        except Exception as ex:
            err = f"Error in expression '{expr}': {ex}."
            err = err.replace(" (<unknown>, line 1)", "")
            return None, err
        return tree, None

    # def replace_initial_behaviors(expr, behaviors, last_response):
    #     """
    #     Replace any intial occurence of "b1 or b2 or ... or bn" in expr (where each b is in behaviors)
    #     with "False or True or ... or False" where True is for the behavior matching last_response.
    #     """
    #     def _is_behavior(b):
    #         # Ignore any parenthesis adjacent to behavior: "(b1 or b2) and ..."
    #         b_noparenthesis = re.sub(r'[()]*', '', b)
    #         return b_noparenthesis in behaviors, b_noparenthesis

    #     replaced_expr = ''
    #     words = expr.split()
    #     initial_behaviors_done = False
    #     expecting_behavior = True
    #     the_rest = ''
    #     for i, word in enumerate(words):
    #         if set(word).issubset({'(', ')'}):  # Ignore any parenthesis as own words: "( b1 or b2 ) and ..."
    #             replaced_expr += word
    #             continue
    #         if expecting_behavior:
    #             is_behavior, behavior = _is_behavior(word)
    #             if is_behavior:
    #                 # replaced_expr += f"{behavior == last_response} "  # "True"/"False"
    #                 replaced_expr += word.replace(behavior, f"{behavior == last_response} ")
    #             else:
    #                 initial_behaviors_done = True
    #         else:  # expecting "or"
    #             if word == "or":
    #                 replaced_expr += "or "
    #             else:
    #                 if i == 1 and word in ("=", "==", "<=", ">=", "<", ">"):
    #                     return expr  # A behavior followed by comparison, e.g. "b1 == 5"
    #                 initial_behaviors_done = True
    #         if initial_behaviors_done:
    #             the_rest = " ".join(words[i:])
    #             break
    #         expecting_behavior = not expecting_behavior
    #     replaced_expr += the_rest
    #     return replaced_expr.strip()

    @staticmethod
    def _make_bool_behavior_context(behaviors, true_behavior):
        assert(true_behavior in behaviors), f"{true_behavior} not in {behaviors}."
        behavior_context = {b: False for b in behaviors}
        behavior_context[true_behavior] = True
        return behavior_context

    @staticmethod
    def evaluate(expr, variables=None, phase_event_counter=None, phase_event_counter_type=None):
        """
        Evaluate the specified expression using the specified Variables and PhaseEventCounter
        objects.

        Returns evaluated_value, error
        """
        expr_orig = expr

        expr = ParseUtil._single2double_eq(expr)

        context = {'rand': rand, 'choice': choice}
        if variables is not None:
            context.update(variables.values)

        if phase_event_counter is not None:
            if phase_event_counter_type == ParseUtil.STOP_COND:
                context.update(phase_event_counter.count)
            elif phase_event_counter_type == ParseUtil.PHASE_LINE:
                # expr = ParseUtil.replace_initial_behaviors(expr, phase_event_counter.behaviors,
                #                                            phase_event_counter.last_response)
                expr = phase_event_counter.replace_count_functions(expr)
                behavior_context = ParseUtil._make_bool_behavior_context(phase_event_counter.behaviors,
                                                                         phase_event_counter.last_response)
                context.update(behavior_context)
                context.update(phase_event_counter.get_count_line_linelabels())
            else:
                return None, "Internal error."

            # Try simple evaluation (e.g. "count(event)=12", "event=42")
            # out = phase_event_counter.eval(expr, variables)
            # if out is not None:
            #     return out

            # Replace count(event) with count(PEC,event) and
            # count_line(event) with count_line(PEC,event)
            # expr = expr.replace("count(", f"count({PEC},")
            # expr = expr.replace("count_line(", f"count_line({PEC},")

        # Make sure that the expression is valid
        tree, err = ParseUtil.ast_parse(expr)
        if err is not None:
            return None, err

        # if phase_event_counter:
        #     context.update({'count': phase_event_counter.get_count,
        #                     'count_line': phase_event_counter.get_count_line})

        # Check that all contained variables are in variables
        has_boolean_operator = False
        for node in ast.walk(tree):
            if type(node) is ast.Name:
                name = node.id
                if name in context:
                    continue
                if (variables is not None) and variables.contains(name):
                    continue
                if (phase_event_counter is not None) and (name in phase_event_counter.count):
                    continue
                return None, f"Unknown variable '{name}'."
            if type(node) is ast.BoolOp:
                has_boolean_operator = True

        # Now it is safe to evaluate using eval
        try:
            out = eval(expr, {"__builtins__": None}, context)
        except Exception as ex:
            err = f"Cannot evaluate expression '{expr_orig}': {ex}"
            if not err.endswith("."):  # Some errors {ex} ends with period, some don't
                err = err + "."
            return None, err

        # Due to short-circuiting, "0 and False" is 0 (int), but "1 and False" is False (bool)
        if has_boolean_operator:
            out = bool(out)

        type_out = type(out)
        if type_out is not int and type_out is not float and type_out is not bool:
            return None, f"Error in expression '{expr_orig}'."
        else:
            return out, None
        # code = compile(tree, filename='', mode='eval')
        # return eval(code)

    @staticmethod
    def split1(string, sep=' '):
        string_spl = string.split(sep, 1)
        out0 = string_spl[0]
        if len(string_spl) == 1:
            out1 = None
        else:
            out1 = string_spl[1]
        return out0, out1

    @staticmethod
    def split1_strip(string, sep=' '):
        out0, out1 = ParseUtil.split1(string, sep)
        if out0 is not None:
            out0 = out0.strip()
        if out1 is not None:
            out1 = out1.strip()
        return out0, out1

    def weighted_choice(prob_cumsum):
        '''
        Returns index into prob_cumsum, chosen at random with probabilities given by prob_cumsum.
        If sum(prob_cumsum)<1, None is returned with probability (1-sum(prob_cumsum)).
        '''
        prob_cumsum1 = prob_cumsum[:]
        prob_cumsum1.append(1)
        rnd = random.random()
        ind = 0
        for i, cumsum_part in enumerate(prob_cumsum1):
            if rnd < cumsum_part:
                ind = i
                break
        if ind == len(prob_cumsum1) - 1:
            return None
        else:
            return i

    def is_dict(string):
        try:
            d = ast.literal_eval(string)
            if type(d) is dict:
                return True, d
            else:
                return False, None
        except Exception:
            return False, None

    @staticmethod
    def parse_chain(v_str, all_stimulus_elements, all_behaviors):
        """Parse a chain, for example 's1->b1->s2' and return a list (['s1','b1','s2'])."""
        out = list()
        chain = v_str.replace(' ', '').split('->')
        first_link = chain[0].split(',')
        chain_starts_with_stimulus = first_link[0] in all_stimulus_elements
        if chain_starts_with_stimulus:
            # Check that all elements in first_link are stimulus elements
            for s in first_link:
                if s not in all_stimulus_elements:
                    return None, f"Expected stimulus element, got '{s}'."
        elif first_link[0] not in all_behaviors:
            return None, f"Expected stimulus element(s) or a behavior, got {first_link[0]}."
        expecting_stimulus = chain_starts_with_stimulus
        for sb in chain:
            if expecting_stimulus:
                stimulus_elements = sb.split(',')
                for e in stimulus_elements:
                    if e not in all_stimulus_elements:
                        return None, f"Expected stimulus element, got '{e}'."
                if len(stimulus_elements) == 1:
                    out.append(stimulus_elements[0])
                else:
                    out.append(tuple(stimulus_elements))
            else:
                if sb not in all_behaviors:
                    return None, f"Expected behavior name, got '{sb}'."
                out.append(sb)
            expecting_stimulus = not expecting_stimulus
        return out, None

    @staticmethod
    def get_ending_dict(string):
        """
        Return the rstripped string preceeding the dict at the end of the specified string,
        and the dict itself if any (otherwise None).

        Example:
            get_ending_string(" foo  bar    {'a' : 1}")
            returns " foo  bar", {'a': 1}

            get_ending_string(" foo  bar    {'a' : 1}")
            returns " foo  bar", None
        """
        string_len = len(string)
        for i in reversed(range(string_len)):
            candidate = string[i: string_len]
            is_dict, d = ParseUtil.is_dict(candidate)
            if is_dict:
                preceeding_dict = string[0: i].rstrip()  # Strip spaces separating string from dict
                return preceeding_dict, d
        return string, None

    @staticmethod
    def parse_stimulus_behavior(expr, all_stimulus_elements, all_behaviors, variables):
        """
        From an expression of the form "s1[i1],s2[i2],...->r", return the
        tuple t where t[0] = (('s1',i1), ('s2',i2), ...) and t[1] = 'r'.
        """
        arrow_inds = [m.start() for m in re.finditer('->', expr)]
        n_arrows = len(arrow_inds)
        if n_arrows == 0:
            return None, None, "Expression must include a '->'."
        elif n_arrows > 1:
            return None, None, "Expression must include only one '->'."

        elements, behavior = expr.split('->')
        stimulus, err = ParseUtil.parse_elements_and_intensities(elements, variables)
        if err:
            return None, None, err

        for element in stimulus:
            if element not in all_stimulus_elements:
                return None, None, f"Expected a stimulus element, got {element}."

        behavior = behavior.strip()
        if behavior not in all_behaviors:
            return None, None, f"Expected a behavior name, got {behavior}."

        return stimulus, behavior, None

    @staticmethod
    def parse_elements_and_intensities(stimulus, variables, safe_intensity_eval=False):
        """Parse an expression of the form 'e1[i1],e2[i2],...'. If no brackets, i = 1."""
        stimulus_elements = [x.strip() for x in stimulus.split(',')]
        elements_and_intensities = dict()
        for element_and_intensity in stimulus_elements:
            element, intensity, err = ParseUtil.parse_element_and_intensity(element_and_intensity, variables,
                                                                            safe_intensity_eval)
            if err:
                return None, err
            elements_and_intensities[element] = intensity
        return elements_and_intensities, None

    @staticmethod
    def parse_element_and_intensity(expr, variables=None, safe_intensity_eval=False):
        """
        Parse an expression of the form 'element[intensity]'. If no brackets, intensity = 1.
        Return element (str), intensity (float), and error (str).

        If safe_intensity_eval is True and intensity cannot be evaluated, return
        the expression for the intensity (str) instead of the evaluated value (float).
        """
        err_output = (None, None, f"Invalid expression {expr}.")
        expr = expr.strip()
        if '[' in expr:
            lb_inds = [m.start() for m in re.finditer('\[', expr)]
            rb_inds = [m.start() for m in re.finditer('\]', expr)]
            if len(lb_inds) != 1 or len(rb_inds) != 1:
                return err_output
            lb_ind = lb_inds[0]
            rb_ind = rb_inds[0]
            if lb_ind == 0:
                return err_output
            if rb_ind != len(expr) - 1:  # ']' must be at the end
                return err_output
            element = expr[0: lb_ind].strip()
            intensity_str = expr[lb_ind + 1: -1]

            intensity, _ = ParseUtil.evaluate(intensity_str, variables)
            if intensity is None:
                if safe_intensity_eval:
                    intensity = intensity_str
                else:
                    return err_output
        else:
            element = expr
            intensity = 1
        return element, intensity, None

    @staticmethod
    def parse_element_behavior(expr, all_stimulus_elements, all_behaviors):
        """
        First, split specified string with respect to arrows (->) and then to commas to tuple while stripping each part.

        Example:
            arrow2tuple("a ->   b,c->x,2->z") returns ('a', ('b', 'c'), ('x', '2'), 'z').
        """
        arrow_inds = [m.start() for m in re.finditer('->', expr)]
        n_arrows = len(arrow_inds)
        if n_arrows == 0:
            return None, "Expression must include a '->'."
        elif n_arrows > 1:
            return None, "Expression must include only one '->'."

        stimulus_element, behavior = expr.split('->')
        if stimulus_element not in all_stimulus_elements:
            return None, f"Expected a stimulus element, got {stimulus_element}."
        if behavior not in all_behaviors:
            return None, f"Expected a behavior name, got {behavior}."
        return (stimulus_element, behavior), None

    @staticmethod
    def parse_element_element(expr, all_stimulus_elements):
        """
        First, split specified string with respect to arrows (->) and then to commas to tuple while stripping each part.

        Example:
            arrow2tuple("a ->   b,c->x,2->z") returns ('a', ('b', 'c'), ('x', '2'), 'z').
        """
        arrow_inds = [m.start() for m in re.finditer('->', expr)]
        n_arrows = len(arrow_inds)
        if n_arrows == 0:
            return None, "Expression must include a '->'."
        elif n_arrows > 1:
            return None, "Expression must include only one '->'."

        stimulus_element1, stimulus_element2 = expr.split('->')
        if stimulus_element1 not in all_stimulus_elements:
            return None, f"Expected a stimulus element, got {stimulus_element1}."
        if stimulus_element2 not in all_stimulus_elements:
            return None, f"Expected a stimulus element, got {stimulus_element2}."
        return (stimulus_element1, stimulus_element2), None

    # @staticmethod
    # def arrow2evalexpr_n(expr):
    #     # arrow2evalexpr_n
    #     """
    #     From an expression of the form "s11,s12,...->r1->s21,s22,...->r2->...", return the
    #     list [('s11','s12',...), 'r1', ('s21','s22',...), 'r2', ...]. If there is only one "s",
    #     it will not be in a tuple (of length 1).

    #     Example: "s->b->s1,s2" returns ['s', 'b', ('s1','s2')].
    #     """
    #     if '->' in expr:
    #         arrowsplit = expr.split('->')
    #         return list(ParseUtil.arrow2evalexpr_n(x.strip()) for x in arrowsplit)
    #     elif ',' in expr:
    #         commasplit = expr.split(',')
    #         return tuple(x.strip() for x in commasplit)
    #     else:
    #         return expr


def parse_equals(str):
    strspl = re.split('=| =|= ', str)
    strspl = list(filter(None, strspl))
    if len(strspl) != 2:
        raise Exception("Error parsing " + str + ".")
    lhs = strspl[0].strip(' ')
    rhs = strspl[1].strip(' ')
    return [lhs, rhs]


def startswith(string, prefixes):
    """Checks if str starts with any of the strings in the prefixes tuple.
    Returns the first string in prefixes that matches. If there is no match,
    the function returns None.
    """
    if isinstance(prefixes, tuple):
        for prefix in prefixes:
            if string.startswith(prefix):
                return prefix
        return None
    elif isinstance(prefixes, str):
        prefix = prefixes
        if string.startswith(prefix):
            return prefix
        return None
    else:
        raise Exception('Second argument must be string or a tuple of strings.')


def strsplit(string, substrings):
    """Splits up the specified string at each occurrence of any of the specified substrings,
    removing the substrings. Returns a list of strings and a list of matching substrings. If no
    match is found, return the empty list.
    """
    assert(type(string) == str)
    if type(substrings) is not list:
        substrings = [substrings]
    for substring in substrings:
        assert(type(substring) == str)
    # if not any(substring in string for substring in substrings):
    #     return [string]
    indices = list()
    for substring in substrings:
        ind = [m.start() for m in re.finditer(substring, string)]
        indices.extend(ind)
    indices.sort()
    parts = [string[i:j] for i, j in zip(indices, indices[1:] + [None])]

    # matches = list()
    # for i in range(len(parts)):d
    #     part = parts[i]
    #     for substring in substrings:
    #         if part.startswith(substring):
    #             # matches.append(substring)
    #             parts[i] = parts[i][len(substring):]
    #             break
    # assert(len(matches) == len(parts))
    return parts  # , matches


def split1(string, sep=' '):
    string_spl = string.split(sep, 1)
    out0 = string_spl[0]
    if len(string_spl) == 1:
        out1 = None
    else:
        out1 = string_spl[1]
    return out0, out1


def split1_strip(string, sep=' '):
    out0, out1 = split1(string, sep)
    if out0 is not None:
        out0 = out0.strip()
    if out1 is not None:
        out1 = out1.strip()
    return out0, out1


def is_posint(string):
    try:
        val = ast.literal_eval(string)
    except ValueError:
        return False, None
    if type(val) != int:
        return False, None
    if val <= 0:
        return False, None
    return True, val


def is_tuple(string):
    try:
        val = ast.literal_eval(string)
    except ValueError:
        return False, None
    if type(val) != tuple:
        return False, None
    return True, val


def is_tuple_of_str(input):
    input_type = type(input)
    if input_type is not tuple:
        return False
    for i in input:
        if type(i) is not str:
            return False
    return True


def is_number(string):
    try:
        val = ast.literal_eval(string)
        return True, val
    except ValueError:
        if string.count('/') != 1:
            return False, None
        else:
            num_str, den_str = string.split('/')
            num_ok, num = is_number(num_str)
            den_ok, den = is_number(den_str)
            if num_ok and den_ok:
                return True, num / den
            else:
                return False, None


def is_prob(string):
    isnum, val = is_number(string)
    if not isnum:
        return False, None
    else:
        if val < 0 or val > 1:
            return False, None
    return True, val


def is_valid_name(name, parameters, kw):
    """Checks if name is a valid script variable name. Returns the error."""
    if not name.isidentifier():
        return "Variable name '{}' is not a valid identifier.".format(name)
    if name in kw.KEYWORDS:
        return "Variable name '{}' is a keyword.".format(name)
    behaviors = parameters.get(kw.BEHAVIORS)
    if behaviors is not None and name in behaviors:
        return "Variable name '{}' equals a behavior name.".format(name)
    stimulus_elements = parameters.get(kw.STIMULUS_ELEMENTS)
    if stimulus_elements is not None and name in stimulus_elements:
        return "Variable name '{}' equals a stimulus element name.".format(name)
    return None


def strip_quotes(string):
    string_out = string
    string_out = string_out.replace('"', '')
    string_out = string_out.replace("'", "")
    return string_out


def make_readable_list_of_strings(input_list):
    """Return the string "'a', 'b' and 'c'" for the input ['a', 'b', 'c']."""
    out = "'" + input_list[0] + "'"
    list_length = len(input_list)
    if list_length > 1:
        for i in range(1, list_length):
            s = input_list[i]
            if i == list_length - 1:
                out += " and " + "'" + s + "'"
            else:
                out += ", " + "'" + s + "'"
    return out


def weighted_choice(prob_cumsum):
    '''
       Returns index into prob_cumsum, chosen at random with probabilities given by prob_cumsum.
       If sum(prob_cumsum)<1, None is returned with probability (1-sum(prob_cumsum)).
    '''
    prob_cumsum1 = prob_cumsum[:]
    prob_cumsum1.append(1)
    rnd = random.random()
    ind = 0
    for i, cumsum_part in enumerate(prob_cumsum1):
        if rnd < cumsum_part:
            ind = i
            break
    if ind == len(prob_cumsum1) - 1:
        return None
    else:
        return i


def parse_sso(string):
    '''
       Parse a space-separated string of python objects and return the objects in a list.
       For example,
       line = "'reward' {'subject': 1}  [1, 2, 'foo']" gives the output
              ['reward', {'subject':1}, [1,2,'foo']]
       Note: Consecutive spaces in strings will be parsed into a single space. For example,
       line = "'re    ward' 123" gives the output
              ['re ward', 123]
    '''
    if len(string.strip()) == 0:
        return None
    stringspl = string.split()
    used_ind = list()
    nchunks = len(stringspl)
    out = list()
    startind = 0
    stopind = 1
    done = False
    while not done:
        string = ' '.join(stringspl[startind:stopind])
        try:
            valid_item = ast.literal_eval(string)
            out.append(valid_item)
            used_ind.extend(range(startind, stopind))
            startind = stopind
            stopind = startind + 1
        except Exception:
            stopind += 1
        done = (stopind == nchunks + 1)
    if len(used_ind) == nchunks:
        return out
    else:
        return None


def eval_average(datas):
    '''data is a list of float-lists (of different lengths).'''
    ndata = len(datas)
    data_lengths = [0] * ndata
    for i, data in enumerate(datas):
        data_lengths[i] = len(data)
    maxlen = max(data_lengths)
    sumpoints = [0] * maxlen
    npoints = [0] * maxlen
    for ind in range(maxlen):
        for i in range(ndata):
            if ind < data_lengths[i]:
                sumpoints[ind] += datas[i][ind]
                npoints[ind] += 1
    for ind in range(maxlen):
        sumpoints[ind] /= npoints[ind]
    return sumpoints


def dict_of_list_ind(d, ind):
    '''d is a dict where all values are lists of equal length. Returns a new dict where each
       value is the ind:th list item for each key.'''
    out = dict()
    for key, val in d.items():
        out[key] = d[key][ind]
    return out


def find_and_cumsum(seq, pattern, use_exact_match):
    '''
    seq is list of strings and tuples.
    pattern is a string, a tuple of strings or a list of strings and tuples of strings.
    If use_exact_match is false, count also part of tuples as match.
    '''
    def _is_match(seq, pattern, use_exact_match):
        for i in range(len(seq)):
            if not _is_match_local(seq[i], pattern[i], use_exact_match):
                return False
        return True

    def _is_match_local(st, pattern, use_exact_match):
        st_type = type(st)
        pattern_type = type(pattern)
        if pattern_type is tuple:
            if st_type is tuple:
                if use_exact_match:
                    return set(st) == set(pattern)
                else:
                    return set(pattern).issubset(set(st))
            else:
                return False
        else:
            if st_type is tuple:
                if use_exact_match:
                    return False
                else:
                    return pattern in st
            else:
                return pattern == st

    assert(type(seq) == list)
    for s in seq:
        s_type = type(s)
        assert((s_type is str) or (s_type is tuple) or (s is None))

    pattern_type = type(pattern)
    assert((pattern_type is list) or (pattern_type is tuple) or (pattern_type is str))
    pattern_len = 1
    if pattern_type is tuple:
        for p in pattern:
            assert(type(p) is str)
        pattern_list = [pattern]
    elif pattern_type is list:
        pattern_len = len(pattern)
        for p in pattern:
            assert((type(p) is str) or (type(p) is tuple))
        pattern_list = pattern
    else:  # pattern_type is str
        pattern_list = [pattern]

    seq_len = len(seq)

    findind = [0] * seq_len
    cumsum_out = [None] * seq_len
    cumsum_curr = 0
    # pattern_is_tuple = (pattern_type is tuple)
    for i in range(seq_len - pattern_len + 1):
        seqpart = seq[i: (i + pattern_len)]
        if _is_match(seqpart, pattern_list, use_exact_match):  # , pattern_is_tuple):
            findind[i] = 1
            cumsum_curr += 1
        cumsum_out[i] = cumsum_curr
    # The last indices for which the pattern is too long will be counted as no match:
    for i in range(seq_len - pattern_len + 1, seq_len):
        findind[i] = 0
        cumsum_out[i] = cumsum_curr

    return findind, cumsum_out


def find_and_cumsum_interval(seq, pattern, use_exact_match,
                             interval_pattern, interval_pattern_exact):
    """
    Return the number of occurances of pattern in seq, between every two consecutive
    occurrences of interval_pattern.

    Example:
        find_and_cumsum_interval(['a','b','a','X','b','a','X','X'], 'a', True, 'X', True)
        returns [2, 1, 0]
    """
    ind_seq, _ = find_and_cumsum(seq, pattern, use_exact_match)
    ind_int, _ = find_and_cumsum(seq, interval_pattern, interval_pattern_exact)
    cnt = 0
    out = list()
    for i in range(len(ind_seq)):
        cnt += ind_seq[i]
        if ind_int[i] == 1:
            out.append(cnt)
            cnt = 0
    #print(f"seq={seq}")
    #print(f"out={out}")
    #print(f"cumsum(out) = {cumsum(out)}")
    #input()
    return out, cumsum(out)


def cumsum(arr):
    out = [None] * len(arr)
    curr = 0
    for i, x in enumerate(arr):
        curr += x
        out[i] = curr
    return out


def arraydivide(num, den):
    assert(type(num) == type(den) == list)
    arraylen = len(num)
    assert(len(den) == arraylen)
    out = [None] * arraylen
    for i in range(arraylen):
        if den[i] != 0:
            out[i] = num[i] / den[i]
        else:
            out[i] = num[i]
    return out


def diff(x, diffind):
    '''Returns [ x[ind1[0]]-x[0], x[ind1[1]]-x[ind1[0]], x[ind1[2]]-x[ind1[1]], ...,
                 x[-1]-x[ind1[-1]] ]
       where ind1 are the indices to the ones (1) in diffind.'''
    assert (len(x) == len(diffind)), "x and diffind must have equal length."
    out = list()
    if len(x) > 0:
        curr = 0
        for i, indval in enumerate(diffind):
            if indval == 1:
                out.append(x[i] - curr)
                curr = x[i]
        out.append(x[-1] - curr)
    return out


def arrayind(x, ind):
    assert (len(x) == len(ind)), "x and ind must have equal length."
    out = list()
    for i, indval in enumerate(ind):
        if indval == 1:
            out.append(x[i])
    return out


def dict_inv(d_in):
    d = dict(d_in)
    key_errmsg = "All keys must be non-empty strings."
    val_errmsg = "Each value must be a non-empty string or a list/set of non-empty strings."
    for key, val in d.items():
        if type(key) is not str:
            raise Exception(key_errmsg)
        elif len(key) == 0:
            raise Exception(key_errmsg)
        if type(val) is str:  # not list:
            val = [val]
            d[key] = val
        elif type(val) is not list and type(val) is not set:
            raise Exception(val_errmsg)
        for v in val:
            if type(v) is not str:
                raise Exception(val_errmsg)
            elif len(v) == 0:
                raise Exception(val_errmsg)

    all_val = set()
    for key, val in d.items():
        for v in val:
            all_val.add(v)
    d_out = dict()
    for v in all_val:
        d_out[v] = list()
        for key, val in d.items():
            if v in val:
                d_out[v].append(key)
    return d_out


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
