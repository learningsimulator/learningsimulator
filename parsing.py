import platform
import re
import copy
import matplotlib.pyplot as plt
import csv
import math

import posteval
import keywords as kw
from parameters import Parameters
from parameters import is_parameter_name
from simulation import Runs, Run
from variables import Variables
from phases import Phases
from exceptions import ParseException, InterruptedSimulation, EvalException
from util import ParseUtil  # , eval_average

POST_MATH = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
             'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh, 'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
             'ceil': math.ceil, 'floor': math.floor,
             'exp': math.exp, 'log': math.log, 'log10': math.log10, 'sqrt': math.sqrt}


def clean_script(text):
    lines = text.split('\n')

    in_comment_block = False
    lineno_multicomment_delimiter = 0
    for lineno0, orig_line in enumerate(lines):
        lineno = lineno0 + 1
        line = orig_line

        # Replace each tab with a space
        line = line.replace('\t', ' ')

        # Strip leading and trailing blanks
        line = line.strip()

        # Remove line comment and strip leading and trailing blanks after comment removal
        line_is_multicomment_delimiter = (line == '###')
        if not line_is_multicomment_delimiter:
            line = line.split('#')[0].strip()

        # Handle comment block
        if line_is_multicomment_delimiter:
            line = ''
            in_comment_block = not in_comment_block  # Toggle status
            lineno_multicomment_delimiter = lineno   # Line number used in error message
        if in_comment_block:
            line = ''
            if lineno == len(lines):
                msg = f"Comment block start '###' on line {lineno_multicomment_delimiter} has no matching end."
                raise ParseException(lineno, msg)
        lines[lineno0] = line

    # Remove all blank lines at the end of the script
    while lines and lines[-1] == '':
        lines.pop()

    return lines


class Script():
    def __init__(self, script):
        self.script = script
        self.script_parser = ScriptParser(self.script)

    def parse(self, is_gui=False):
        self.script_parser.parse()

    def check_deprecated_syntax(self):
        return self.script_parser.check_deprecated_syntax()

    def run(self):
        return self.script_parser.runs.run()

    def postproc(self, simulation_data, progress=None):
        if (progress is not None) and (progress.dlg is not None):
            progress.dlg.set_visibility2(False)
            progress.dlg.set_title("Plot/Export Progress")

        self.script_parser.postcmds.run(simulation_data, progress)

    def plot(self, block=True, progress=None):
        self.script_parser.postcmds.plot()
        if progress is not None:
            progress.close_dlg()
        isMac = platform.system().lower() == "darwin"
        if isMac:
            block = False
        plt.show(block=block)
        if isMac:
            plt.draw()  # Issue with subplots on Mac (10.15 (Catalina))


class LineParser():
    VARIABLES = 0
    VARIABLES_CONT = 1
    PARAMETER = 2
    PARAMETER_CONT = 3
    PHASE = 4
    PHASE_CONT = 5
    RUN = 6
    FIGURE = 7
    SUBPLOT = 8
    XPLOT = 9  # vplot, wplot, pplot, nplot, vssplot
    XEXPORT = 10
    LEGEND = 11
    PREV_DEFINED_VARIABLE = 12
    PLOT = 13
    EXPORT = 14

    def __init__(self, line, global_variables):
        self.line = line
        self.global_variables = global_variables
        self.linesplit_colon = line.split(':', 1)  # Has length 1 or 2
        self.linesplit_equal = line.split('=', 1)  # Has length 1 or 2
        self.linesplit_space = line.split(' ', 1)  # Has length 1 or 2
        self.param = None  # The parameter when line is "param: value"
        self.line_type = None

    def parse(self):
        possible_param_colon = self.linesplit_colon[0].strip().lower()
        possible_param_equal = self.linesplit_equal[0].strip().lower()
        is_parameter_name_colon = is_parameter_name(possible_param_colon)
        is_parameter_name_equal = is_parameter_name(possible_param_equal)
        if is_parameter_name_colon or is_parameter_name_equal:
            if is_parameter_name_colon:
                self.param = possible_param_colon
            else:
                self.param = possible_param_equal
            self.line_type = LineParser.PARAMETER

        if self.global_variables.contains(possible_param_equal):
            self.line_type = LineParser.PREV_DEFINED_VARIABLE

        first_word = self.linesplit_space[0].lower()
        if first_word == kw.VARIABLES:
            self.line_type = LineParser.VARIABLES
        elif first_word == kw.RUN:
            self.line_type = LineParser.RUN
        elif first_word == kw.PHASE:
            self.line_type = LineParser.PHASE
        elif first_word in (kw.VPLOT, kw.VSSPLOT, kw.WPLOT, kw.PPLOT, kw.NPLOT):
            self.line_type = LineParser.XPLOT
        elif first_word == kw.PLOT:
            self.line_type = LineParser.PLOT
        elif first_word == kw.FIGURE or first_word.startswith(kw.FIGURE + '('):  # @figure or @figure(subplotspec)
            self.line_type = LineParser.FIGURE
        elif first_word in (kw.SUBPLOT, kw.PANEL):
            self.line_type = LineParser.SUBPLOT
        elif first_word in (kw.VEXPORT, kw.WEXPORT, kw.PEXPORT, kw.NEXPORT, kw.HEXPORT,
                            kw.VSSEXPORT):
            self.line_type = LineParser.XEXPORT
        elif first_word == kw.EXPORT:
            self.line_type = LineParser.EXPORT
        elif first_word == kw.LEGEND:
            self.line_type = LineParser.LEGEND


class FigureSubplotGrid():
    def __init__(self, subplotgrid):
        self.subplotgrid = subplotgrid
        self.curr_ind = 1

    def next_subplotspec(self):
        ind = self.curr_ind
        self.curr_ind += 1
        return self.subplotgrid + [ind]


class ScriptParser():
    def __init__(self, script):
        self.lines = clean_script(script)

        self.variables = Variables()

        self.parameters = Parameters()

        self.phases = Phases()

        self.runs = Runs()

        self.all_run_labels = list()

        self.postcmds = PostCmds()

        # Used to label unlabelled @run-statements with "run1", "run2", ...
        self.unnamed_run_cnt = 1

        # Used to label unlabelled @phase-statements with "phase1", "phase2", ...
        self.unnamed_phase_cnt = 1

    def parse(self):
        if len(self.lines) == 0:
            raise ParseException(1, "Script is empty.")
        prop = None
        curr_phase_label = None
        in_prop = False
        in_variables = False
        in_phase = False
        in_run = False
        run_lines = None
        curr_figure_subplotgrid = None

        for lineno0, line_orig in enumerate(self.lines):
            line = line_orig
            lineno = lineno0 + 1

            # Handle empty line
            if len(line) == 0:
                continue

            line_endswith_comma = line.endswith(',')
            if line_endswith_comma:
                line = line[:-1]

            line_parser = LineParser(line, self.variables)
            line_parser.parse()
            linesplit_colon = line_parser.linesplit_colon
            linesplit_equal = line_parser.linesplit_equal
            linesplit_space = line_parser.linesplit_space

            if in_prop or in_variables or in_phase or in_run:  # Possible multiline elements
                parse_this_line_done = True
                err = None
                if in_prop:
                    in_prop = line_endswith_comma
                    err = self.parameters.str_append(prop, line, self.variables, self.phases,
                                                     self.all_run_labels, line_endswith_comma)
                elif in_variables:
                    in_variables = line_endswith_comma
                    err = self.variables.add_cs_varvals(line, self.parameters)
                elif in_phase:
                    in_phase = line_parser.line_type is None
                    if in_phase:
                        self.phases.append_line(curr_phase_label, line, lineno)
                    else:
                        parse_this_line_done = False
                        # Phase with label curr_phase_label is complete, parse it
                        self.phases.parse_phase(curr_phase_label, self.parameters, self.variables)
                elif in_run:
                    in_run = line_parser.line_type is None  # Because the line is just a phase name
                    # in_run = (
                    #     line_parser.line_type is None or           # The line is just a phase name
                    #     line_parser.param == kw.STIMULUS_ELEMENTS  # The line is stimulus_elements=...
                    # )
                    if in_run:
                        run_lines.append((line, lineno))
                        parse_this_line_done = True
                    else:
                        run, run_label = self._parse_run_lines(run_lines)
                        self.runs.add(run, run_label)
                        parse_this_line_done = False
                if err:
                    raise ParseException(lineno, err)
                if parse_this_line_done:
                    continue

            if line_parser.line_type == LineParser.PARAMETER:
                # Handle line that sets a parameter (e.g. "prop   :    val")
                prop = line_parser.param
                if len(linesplit_colon) == 1 and len(linesplit_equal) == 1:
                    raise ParseException(lineno, f"Parameter '{prop}' is not specified.")
                first_colon_index = line_orig.find(':')
                first_equal_index = line_orig.find('=')
                if first_equal_index > 0 and first_colon_index > 0:
                    if first_colon_index < first_equal_index:          # u : a=1, b=2
                        possible_val = linesplit_colon[1].strip()
                    else:                                              # u = a:1, b:2
                        possible_val = linesplit_equal[1].strip()
                elif first_equal_index > 0 and first_colon_index < 0:  # u = 2
                    possible_val = linesplit_equal[1].strip()
                elif first_colon_index > 0 and first_equal_index < 0:  # u : 2
                    possible_val = linesplit_colon[1].strip()
                if len(possible_val) == 0:
                    raise ParseException(lineno, f"Parameter '{prop}' is not specified.")
                if line_endswith_comma:
                    if not self.parameters.may_end_with_comma(prop):
                        raise ParseException(lineno, "Value for {} may not end by comma.".format(prop))
                    in_prop = self.parameters.is_csv(prop)
                err = self.parameters.str_set(prop, possible_val, self.variables, self.phases,
                                              self.all_run_labels, line_endswith_comma)
                if err:
                    raise ParseException(lineno, err)
                continue

            elif line_parser.line_type == LineParser.VARIABLES:
                if len(linesplit_space) == 1:
                    raise ParseException(lineno, "@VARIABLES not specified.")
                in_variables = line_endswith_comma
                cs_varvals = linesplit_space[1].strip()
                err = self.variables.add_cs_varvals(cs_varvals, self.parameters)
                if err:
                    raise ParseException(lineno, err)
                else:
                    continue

            elif line_parser.line_type == LineParser.PREV_DEFINED_VARIABLE:
                err = self.variables.add_cs_varvals(line.strip(), self.parameters)
                if err:
                    raise ParseException(lineno, err)
                else:
                    continue

            elif line_parser.line_type == LineParser.RUN:
                in_run = True
                run_lines = [(line, lineno)]
                continue

            elif line_parser.line_type == LineParser.PHASE:
                gen_err = "@PHASE line must have the form '@PHASE label stop:condition'."
                if len(linesplit_space) == 1:
                    raise ParseException(lineno, gen_err)
                lbl_and_stopcond = linesplit_space[1].strip()
                curr_phase_label, stop_condition = ParseUtil.split1(lbl_and_stopcond)

                inherited_from = None
                if '(' in curr_phase_label and curr_phase_label.endswith(')'):
                    lind = curr_phase_label.index('(')
                    inherited_from = curr_phase_label[(lind + 1):-1]
                    curr_phase_label = curr_phase_label[0:lind]
                    if not self.phases.contains(inherited_from):
                        raise ParseException(lineno, f"Invalid phase label '{inherited_from}'.")

                if self.phases.contains(curr_phase_label):
                    raise ParseException(lineno, f"Redefinition of phase '{curr_phase_label}'.")
                if not curr_phase_label.isidentifier():
                    raise ParseException(lineno, f"Phase label '{curr_phase_label}' is not a valid identifier.")
                if stop_condition is not None:
                    err, condition = self.parse_stop_colon_cond(stop_condition)
                    if err:
                        raise ParseException(lineno, err)
                else:
                    condition = None

                in_phase = True
                if inherited_from:
                    self.phases.inherit_from(inherited_from, curr_phase_label, condition, lineno)
                else:
                    self.phases.add_phase(curr_phase_label, condition, lineno)
                continue

            elif line_parser.line_type == LineParser.FIGURE:
                figure_title, subplotgrid, mpl_prop = self._parse_figure(lineno, linesplit_space)
                curr_figure_subplotgrid = FigureSubplotGrid(subplotgrid)
                figure_cmd = FigureCmd(figure_title, mpl_prop)
                self.postcmds.add(figure_cmd)

            elif line_parser.line_type == LineParser.SUBPLOT:
                subplotspec_list, subplot_title, mpl_prop = self._parse_subplot(lineno, linesplit_space, curr_figure_subplotgrid)
                subplot_cmd = SubplotCmd(subplotspec_list, subplot_title, mpl_prop)
                self.postcmds.add(subplot_cmd)

            elif line_parser.line_type in (LineParser.XPLOT, LineParser.PLOT):
                isx = (line_parser.line_type == LineParser.XPLOT)
                if isx:
                    exprs, mpl_prop, exprs_str = self._parse_xplot(lineno, linesplit_space)
                else:
                    exprs, mpl_prop, exprs_str = self._parse_plot(lineno, linesplit_space)
                cmd = linesplit_space[0].lower()
                plot_parameters = copy.deepcopy(self.parameters)  # Params may change betweeen plot
                self._evalparse(lineno, plot_parameters)

                runlabel = self.parameters.get(kw.RUNLABEL)
                if runlabel:
                    run_parameters = self.runs.get(runlabel).mechanism_obj.parameters
                else:
                    run_parameters = self.runs.get_last_run_obj().mechanism_obj.parameters

                for expr, expr_str in zip(exprs, exprs_str):
                    mpl_prop_copy = dict(mpl_prop)  # Since PlotCmd edits mpl_prop
                    plot_cmd = PlotCmd(cmd, expr, expr_str, plot_parameters, run_parameters, self.variables,
                                       mpl_prop_copy, lineno)
                    if not isx:
                        plot_cmd.is_postexpr = True
                    self.postcmds.add(plot_cmd)

            elif line_parser.line_type == LineParser.LEGEND:
                mpl_prop = self._parse_legend(lineno, linesplit_space)
                legend_cmd = LegendCmd(mpl_prop)
                self.postcmds.add(legend_cmd)

            elif line_parser.line_type in (LineParser.XEXPORT, LineParser.EXPORT):
                isx = (line_parser.line_type == LineParser.XEXPORT)
                if isx:
                    exprs, filename, exprs_str = self._parse_xexport(lineno, linesplit_space)
                else:
                    exprs, filename, exprs_str = self._parse_export(lineno, linesplit_space)
                cmd = linesplit_space[0].lower()
                export_parameters = copy.deepcopy(self.parameters)  # Params may change betweeen exports
                self._evalparse(lineno, export_parameters)

                runlabel = self.parameters.get(kw.RUNLABEL)
                if runlabel:
                    run_parameters = self.runs.get(runlabel).mechanism_obj.parameters
                else:
                    run_parameters = self.runs.get_last_run_obj().mechanism_obj.parameters

                export_parameters.val[kw.FILENAME] = filename  # If filename only given on export line
                export_cmd = ExportCmd(lineno, cmd, exprs, exprs_str,
                                       export_parameters, run_parameters, self.variables)
                if not isx:
                    export_cmd.is_postexpr = True
                self.postcmds.add(export_cmd)

            else:
                raise ParseException(lineno, f"Invalid expression '{line}'.")

        # If @run is the last statement in the script, finish the parsing of this
        if in_run:
            run, run_label = self._parse_run_lines(run_lines)
            self.runs.add(run, run_label)

    def parse_stop_colon_cond(self, stop_colon_cond):
        stop, condition = ParseUtil.split1_strip(stop_colon_cond, ':')
        if stop != "stop" or condition is None or len(condition) == 0:
            return "Phase stop condition must have the form 'stop:condition'.", None
        else:
            return None, condition

    def check_deprecated_syntax(self):
        return self.phases.check_deprecated_syntax()

    def _evalparse(self, lineno, parameters):
        """Handles parameters that depend on currently defined runs."""
        if len(self.all_run_labels) == 0:
            raise ParseException(lineno, "There is no @RUN.")
        run_label = parameters.get(kw.EVAL_RUNLABEL)
        if len(run_label) == 0:
            run_label = self.all_run_labels[-1]
            parameters.val[kw.EVAL_RUNLABEL] = run_label
        else:
            if run_label not in self.all_run_labels:
                raise ParseException(lineno, f"Unknown run label '{run_label}'.")

    def _parse_legend(self, lineno, linesplit_space):
        if len(linesplit_space) == 1:  # @legend
            mpl_prop = dict()
        elif len(linesplit_space) == 2:  # @legend {mpl_prop}
            arg = linesplit_space[1]
            is_dict, mpl_prop = ParseUtil.is_dict(arg)
            if not is_dict:
                raise ParseException(lineno, f"Invalid @legend argument {arg}.")
        return mpl_prop

    def _parse_xexport(self, lineno, linesplit_space):
        """
        @vexport expr
        @vexport expr filename

        @hexport
        @hexport filename
        """
        cmd = linesplit_space[0]
        filename_param = self.parameters.get(kw.FILENAME)

        if cmd == kw.HEXPORT:
            if len(linesplit_space) == 1:  # @hexport
                if len(filename_param) == 0:
                    raise ParseException(lineno, f"Invalid {cmd} command.")
                else:
                    filename = filename_param
            else:  # @hexport filename
                filename = linesplit_space[-1]
            return None, filename, None

        if len(linesplit_space) == 1:  # @export
            raise ParseException(lineno, f"Invalid {cmd} command.")
        args = linesplit_space[1]

        all_stimulus_elements = self.parameters.get(kw.STIMULUS_ELEMENTS)
        all_behaviors = self.parameters.get(kw.BEHAVIORS)
        if cmd == kw.VEXPORT:
            exprs, exprs0, filename, err = ParseUtil.parse_element_behavior_semicolon(args, all_stimulus_elements, all_behaviors,
                                                                                      allow_wildcard=True, allow_filename=True)

        elif cmd == kw.VSSEXPORT:
            exprs, exprs0, filename, err = ParseUtil.parse_element_element_semicolon(args, all_stimulus_elements,
                                                                                     allow_wildcard=True,
                                                                                     allow_filename=True)
        elif cmd == kw.PEXPORT:
            exprs, exprs0, filename, err = ParseUtil.parse_stimulus_behavior_semicolon(args, all_stimulus_elements,
                                                                                       all_behaviors, self.variables, allow_wildcard=True,
                                                                                       allow_filename=True)
        elif cmd == kw.WEXPORT:
            exprs, exprs0, filename, err = ParseUtil.parse_element_semicolon(args, all_stimulus_elements,
                                                                             allow_wildcard=True, allow_filename=True)
        elif cmd == kw.NEXPORT:
            expr, expr0, filename, err = ParseUtil.parse_chain(args, all_stimulus_elements, all_behaviors, allow_filename=True)
            exprs = [expr]
            exprs0 = [expr0]
        else:
            err = f"Internal error."
        if err:
            raise ParseException(lineno, err)

        if filename is None:
            if len(filename_param) == 0:
                raise ParseException(lineno, f"No filename given to {cmd}.")
            else:
                filename = filename_param

        return exprs, filename, exprs0

    def _parse_export(self, lineno, linesplit_space):
        """
        @export expr
        @export expr filename
        """
        cmd = linesplit_space[0]
        filename = self.parameters.get(kw.FILENAME)
        if len(filename) == 0:
            raise ParseException(lineno, f"Filename needs to be specified before {cmd}.")

        if len(linesplit_space) == 1:  # @export
            raise ParseException(lineno, f"Invalid {cmd} command.")

        expr0 = linesplit_space[1]  # E.g. n(plant -> approach) * 2
        expr = expr0

        all_se = self.parameters.get(kw.STIMULUS_ELEMENTS)
        all_b = self.parameters.get(kw.BEHAVIORS)

        exprs_list = [e.strip() for e in expr.split(';')]
        exprs_str = list(exprs_list)
        post_expr_objs = []
        for e in exprs_list:
            post_expr_obj, err = posteval.parse_postexpr(e, self.variables, POST_MATH)
            if err:
                raise ParseException(lineno, err)

            # Don't allow mixing n with v, p, w, vss when xscale=all
            if self.parameters.get(kw.XSCALE) == kw.EVAL_ALL:
                fns = [post_var.fn for post_var in post_expr_obj.post_vars.values()]
                if 'n' in fns:
                    if set(fns) == {'n'}:  # Only 'n' - ok
                        pass
                    else:
                        raise ParseException(lineno, "Cannot mix n with v,p,w,vss when xscale is 'all'.")

            for post_var in post_expr_obj.post_vars.values():
                fn = post_var.fn
                arg = post_var.arg

                if fn == 'v':
                    parsed_arg, _, _, err = ParseUtil.parse_element_behavior(arg, all_se, all_b, allow_wildcard=False,
                                                                             allow_filename=False)
                elif fn == 'vss':
                    parsed_arg, _, _, err = ParseUtil.parse_element_element(arg, all_se, allow_wildcard=False,
                                                                            allow_filename=False)
                elif fn == 'w':
                    parsed_arg, _, _, err = ParseUtil.parse_element(arg, all_se, allow_wildcard=False,
                                                                    allow_filename=False)
                elif fn == 'p':
                    parsed_arg, _, _, err = ParseUtil.parse_stimulus_behavior(arg, all_se, all_b, self.variables,
                                                                              allow_wildcard=False, allow_filename=False)
                elif fn == 'n':
                    parsed_arg, _, _, err = ParseUtil.parse_chain(arg, all_se, all_b, allow_filename=False)
                else:
                    err = "Internal error."
                if err:
                    raise ParseException(lineno, err)

                if fn != 'n':
                    parsed_arg = parsed_arg[0]

                post_var.parsed_arg = parsed_arg
                post_expr_objs.append(post_expr_obj)

        return post_expr_objs, filename, exprs_str

    def _parse_xplot(self, lineno, linesplit_space):
        """
        @vplot expr {mpl_prop}
        @wplot expr {mpl_prop}
        @pplot expr {mpl_prop}
        @nplot expr {mpl_prop}
        @vssplot expr {mpl_prop}
        """
        cmd = linesplit_space[0]
        if len(linesplit_space) == 1:  # @plot
            raise ParseException(lineno, f"Invalid {cmd} command.")

        expr_str, mpl_prop = ParseUtil.get_ending_dict(linesplit_space[1])
        if mpl_prop is None:
            mpl_prop = dict()

        all_stimulus_elements = self.parameters.get(kw.STIMULUS_ELEMENTS)
        all_behaviors = self.parameters.get(kw.BEHAVIORS)
        err = None
        if cmd == kw.VPLOT:
            exprs, exprs_str, _, err = ParseUtil.parse_element_behavior_semicolon(expr_str, all_stimulus_elements,
                                                                                  all_behaviors)
        elif cmd == kw.VSSPLOT:
            exprs, exprs_str, _, err = ParseUtil.parse_element_element_semicolon(expr_str, all_stimulus_elements,
                                                                                 allow_filename=False)
        elif cmd == kw.PPLOT:
            exprs, exprs_str, _, err = ParseUtil.parse_stimulus_behavior_semicolon(expr_str, all_stimulus_elements,
                                                                                   all_behaviors, self.variables)
        elif cmd == kw.WPLOT:
            exprs, exprs_str, _, err = ParseUtil.parse_element_semicolon(expr_str, all_stimulus_elements)
        elif cmd == kw.NPLOT:
            exprs, exprs_str, _, err = ParseUtil.parse_chain_semicolon(expr_str, all_stimulus_elements,
                                                                       all_behaviors)
        else:
            err = "Internal error."
        if err:
            raise ParseException(lineno, err)
        return exprs, mpl_prop, exprs_str

    def _parse_plot(self, lineno, linesplit_space):
        """
        @plot expr {mpl_prop}
        """
        cmd = linesplit_space[0]
        if len(linesplit_space) == 1:  # @plot
            raise ParseException(lineno, f"Invalid {cmd} command.")

        expr0, mpl_prop = ParseUtil.get_ending_dict(linesplit_space[1])
        if mpl_prop is None:
            mpl_prop = dict()

        expr = expr0
        all_se = self.parameters.get(kw.STIMULUS_ELEMENTS)
        all_b = self.parameters.get(kw.BEHAVIORS)

        exprs_list = [e.strip() for e in expr.split(';')]
        exprs_str = list(exprs_list)
        post_expr_objs = []
        for e in exprs_list:
            post_expr_obj, err = posteval.parse_postexpr(e, self.variables, POST_MATH)
            if err:
                raise ParseException(lineno, err)

            # Don't allow mixing n with v, p, w, vss when xscale=all
            if self.parameters.get(kw.XSCALE) == kw.EVAL_ALL:
                fns = [post_var.fn for post_var in post_expr_obj.post_vars.values()]
                if 'n' in fns:
                    if set(fns) == {'n'}:  # Only 'n' - ok
                        pass
                    else:
                        raise ParseException(lineno, "Cannot mix n with v,p,w,vss when xscale is 'all'.")

            for post_var in post_expr_obj.post_vars.values():
                fn = post_var.fn
                arg = post_var.arg

                if fn == 'v':
                    parsed_arg, _, _, err = ParseUtil.parse_element_behavior(arg, all_se, all_b, allow_wildcard=False)
                elif fn == 'vss':
                    parsed_arg, _, _, err = ParseUtil.parse_element_element(arg, all_se, allow_wildcard=False)
                elif fn == 'w':
                    parsed_arg, _, _, err = ParseUtil.parse_element(arg, all_se, allow_wildcard=False)
                elif fn == 'p':
                    parsed_arg, _, _, err = ParseUtil.parse_stimulus_behavior(arg, all_se, all_b, self.variables,
                                                                        allow_wildcard=False)
                elif fn == 'n':
                    parsed_arg, _, _, err = ParseUtil.parse_chain(arg, all_se, all_b, allow_filename=False)
                else:
                    err = "Internal error."
                if err:
                    raise ParseException(lineno, err)

                if fn != 'n':
                    parsed_arg = parsed_arg[0]

                post_var.parsed_arg = parsed_arg
                post_expr_objs.append(post_expr_obj)

        return post_expr_objs, mpl_prop, exprs_str

    def _parse_subplot(self, lineno, linesplit_space, figure_subplotgrid):
        """
        If subplotgrid not given from @figure:
        @subplot/@panel
        @subplot/@panel subplotspec
        @subplot/@panel subplotspec title
        @subplot/@panel subplotspec {mpl_prop}
        @subplot/@panel subplotspec title {mpl_prop}

        If subplotgrid IS given from @figure:
        @subplot/@panel
        @subplot/@panel
        @subplot/@panel title
        @subplot/@panel {mpl_prop}
        @subplot/@panel title {mpl_prop}
        """
        def _parse_subplotspec_and_title(args):
            subplotspec, title = ParseUtil.parse_initial_tuple(args)
            if subplotspec is not None:
                subplotspec_list = ParseUtil.parse_subplotspec(subplotspec)
                return subplotspec_list, subplotspec, title
            else:
                subplotspec_str, title = ParseUtil.split1_strip(args)
                subplotspec_list = ParseUtil.parse_subplotspec(subplotspec_str)
                return subplotspec_list, subplotspec_str, title

        assert(linesplit_space[0] in (kw.SUBPLOT, kw.PANEL))
        if len(linesplit_space) > 1:
            linesplit_space[1] = linesplit_space[1].strip()

        title_param = self.parameters.get(kw.SUBPLOTTITLE)
        mpl_prop = None

        if figure_subplotgrid is not None and figure_subplotgrid.subplotgrid is not None:  # subplot grid is given in @figure
            subplotspec_list = figure_subplotgrid.next_subplotspec()
            if len(linesplit_space) == 1:  # @subplot
                title_line = ""
            else:
                title_line, mpl_prop = ParseUtil.get_ending_dict(linesplit_space[1])
        else:
            if len(linesplit_space) == 1:  # @subplot/@panel (without arguments)
                subplotspec_list = [1, 1, 1]
                title_line = ""
            elif len(linesplit_space) == 2:  # @subplot/@panel subplotspec ...
                args, mpl_prop = ParseUtil.get_ending_dict(linesplit_space[1])
                subplotspec_list, subplotspec_str, title_line = _parse_subplotspec_and_title(args)
                if subplotspec_list is None:
                    raise ParseException(lineno, f"Invalid @subplot argument {subplotspec_str}.")

        if title_line:
            title = title_line
        else:
            title = title_param
        if mpl_prop is None:
            mpl_prop = dict()
        return subplotspec_list, title, mpl_prop

    def _parse_figure(self, lineno, linesplit_space):
        """
        @figure
        @figure title
        @figure {mpl_prop}
        @figure title {mpl_prop}

        @figure(mn) or @figure(m,n)
        @figure(mn) title
        @figure(mn) {mpl_prop}
        @figure(mn) title {mpl_prop}

        linesplit_space is either @figure or @figure(mn) or @figure(m,n)
        """
        def parse_fun_arg(fun_arg):
            """
            Parse a string of the form "fun(arg)".
            Return error if fun is not "@figure".
            """
            ERR = "Invalid @figure command."

            n_lpar = fun_arg.count('(')
            n_rpar = fun_arg.count(')')
            if (n_lpar == 0 and n_rpar == 0):
                return None, None
            elif (n_lpar != 1 or n_rpar != 1):
                return None, ERR
            elif (fun_arg[-1] != ')'):  # Does not end with a ')'
                return None, ERR
            elif fun_arg.split('(')[0] != kw.FIGURE:  # Substring before '(' is not @figure
                return None, ERR
            ind_lpar = fun_arg.index('(')
            ind_rpar = fun_arg.index(')')
            arg = fun_arg[(ind_lpar + 1): ind_rpar]
            if ',' in arg:
                arg = tuple(arg.split(','))  # E.g. ('1','2')
            arg_intlist = ParseUtil.parse_subplotspec(arg, expected_len=2)
            if arg_intlist is None:
                return None, ERR
            return arg_intlist, None

        title = self.parameters.get(kw.TITLE)
        subplotgrid, err = parse_fun_arg(linesplit_space[0])
        if err:
            raise ParseException(lineno, err)
        if len(linesplit_space) == 1:  # @figure
            mpl_prop = dict()
        elif len(linesplit_space) == 2:  # @figure args
            title, mpl_prop = ParseUtil.get_ending_dict(linesplit_space[1])
            if mpl_prop is None:
                mpl_prop = dict()
        return title, subplotgrid, mpl_prop

    def _parse_run_lines(self, run_lines):
        # First line is of the form
        #    @run
        #    @run [myrunlabel]
        #    @run [myrunlabel]  phase1,phase2,...,phasen [,]  [runlabel:myrunlabel]  # Both runlabels not allowed

        # Each other line is of the form
        #     phase1,phase2,...,phasen  [,]    [runlabel:myrunlabel]

        run_phase_labels = []

        # Parse first line
        line, lineno = run_lines[0]
        linesplit_space = line.split(' ', 1)  # Has length 1 or 2
        assert(linesplit_space[0] == kw.RUN)
        got_run_label = False
        first_line_after_run_and_lbl = ''
        if len(linesplit_space) == 2:
            after_run = linesplit_space[1].strip()
            first_word = ParseUtil.space_split(after_run.replace(',', ' '))[0]  # To regard "phase( stop : COND )" as one word
            err, phase_label, condition = self._parse_phase_with_cond(first_word)
            if err:
                raise ParseException(lineno, err)
            got_run_label = not self.phases.contains(phase_label)

            if got_run_label:  # Then we interpret the first word (after @run) as run label
                run_label = first_word
                first_line_after_run_and_lbl = line.split(run_label, 1)[1]
            else:
                first_line_after_run_and_lbl = after_run

        # Remove @run (and possibly runlbl) from first line so that the first line can be parsed like all others
        run_lines[0] = (first_line_after_run_and_lbl, lineno)

        # Parse all lines
        for line, lineno in run_lines:
            match_objs_iterator = re.finditer(r' runlabel[\s]*:', line)
            match_objs = tuple(match_objs_iterator)
            n_runlabel = len(match_objs)

            if n_runlabel == 0:
                phases_str = line.strip()
            elif n_runlabel == 1:
                match_obj = match_objs[0]
                start_index = match_obj.start() + 1  # Index of "r" in "runlabel"
                end_index = match_obj.end()  # Index of character after ":"
                run_label2 = line[end_index:].strip()
                if got_run_label:
                    raise ParseException(lineno, f"Duplicate run labels {run_label} and {run_label2} on a {kw.RUN} line.")
                elif run_label2 in self.all_run_labels:
                    raise ParseException(lineno, f"Duplication of run label '{run_label2}'.")
                run_label = run_label2
                got_run_label = True
                phases_str = line[0: start_index].strip()
            else:
                raise ParseException(lineno, f"Maximum one instance of 'runlabel:' on a {kw.RUN} line.")
            if len(phases_str) > 0:
                run_phase_labels_line = ParseUtil.space_split(phases_str.replace(',', ' '))
                run_phase_labels_line = [(lbl.strip(), lineno) for lbl in run_phase_labels_line]
                run_phase_labels.extend(run_phase_labels_line)

        if len(run_phase_labels) == 0:
            raise ParseException(run_lines[0][1], "No phase label given in @run.")

        if not got_run_label:
            run_label = f'run{self.unnamed_run_cnt}'
            self.unnamed_run_cnt += 1

        self.all_run_labels.append(run_label)

        phase_labels_with_cond = []
        for phase_label_with_cond, lineno in run_phase_labels:
            err, phase_label, condition = self._parse_phase_with_cond(phase_label_with_cond)
            if err:
                raise ParseException(lineno, err)
            if not self.phases.contains(phase_label):
                raise ParseException(lineno, f"Phase {phase_label} undefined.")
            phase_labels_with_cond.append((phase_label, condition, lineno))

        # Now that we have a run-label and phases to run, create Run object
        world = self.phases.make_world(phase_labels_with_cond, lineno)

        run_parameters = copy.deepcopy(self.parameters)  # Params may change betweeen runs
        mechanism_obj, err = run_parameters.make_mechanism_obj()
        if err:
            raise ParseException(lineno, err)
        n_subjects = run_parameters.get(kw.N_SUBJECTS)
        bind_trials = run_parameters.get(kw.BIND_TRIALS)
        err, err_lineno = mechanism_obj.check_compatibility_with_world(world)
        if err:
            raise ParseException(err_lineno, err)
        run = Run(run_label, world, mechanism_obj, n_subjects, bind_trials)

        return run, run_label


    def _parse_phase_with_cond(self, phase_with_cond):
        n_left_par = phase_with_cond.count('(')
        n_right_par = phase_with_cond.count(')')
        if n_left_par == 0 and n_right_par == 0:
            return None, phase_with_cond, None
        elif n_left_par == 1 and n_right_par == 1:
            index_left_par = phase_with_cond.index('(')
            index_right_par = phase_with_cond.index(')')
            if index_left_par > index_right_par:
                return f"Invalid parenthesis in phase label with stop condition: {phase_with_cond}.", None, None
            else:
                if index_right_par == index_left_par + 1:
                    return "Empty condition in phase label with stop condition.", None, None
                elif index_right_par != len(phase_with_cond) - 1:
                    return f"Malformed phase label with stop condition: {phase_with_cond}.", None, None
                elif index_left_par == 0:
                    return f"Empty phase label in phase with stop condition: {phase_with_cond}.", None, None
                else:
                    phase_label = phase_with_cond[0: index_left_par]
                    stop_cond = phase_with_cond[index_left_par + 1: index_right_par]
                    err, cond = self.parse_stop_colon_cond(stop_cond)
                    if err:
                        return err, None, None
                    else:
                        return None, phase_label.strip(), cond
        else:
            return f"Invalid parenthesis in phase label with stop condition: {phase_with_cond}.", None, None


# -----------------------------------------------------------
class PostCmds():
    def __init__(self):
        self.cmds = list()  # List of PostCmd objects

    def add(self, cmd):
        self.cmds.append(cmd)

    def run(self, simulation_data, progress=None):
        if progress:
            progress.reset1()
            progress.reset2()
            progress.report2("")
        n_commands = len(self.cmds)
        for i, cmd in enumerate(self.cmds):
            assert(isinstance(cmd, PostCmd))
            if progress and progress.stop_clicked:
                raise InterruptedSimulation()
            cmd.run(simulation_data)
            if progress:
                progress.report1(f"Running {cmd.progress_label()}")
                progress.progress1.set((i + 1) / n_commands * 100)

    def plot(self):
        for cmd in self.cmds:
            cmd.plot()

        # # XXX Add average plots in all subplots
        # fig_average = plt.figure()
        # ax_average = fig_average.add_subplot(1, 1, 1)
        # for i in plt.get_fignums():
        #     fig = plt.figure(i)
        #     if fig == fig_average:
        #         continue
        #     axes = fig.get_axes()
        #     for axis in axes:
        #         lines = axis.get_lines()
        #         all_y = list()
        #         for line in lines:
        #             all_y.append(line.get_ydata())
        #             # line.set_visible(False)
        #         if len(lines) > 0:
        #             average = eval_average(all_y)
        #             ax_average.plot(lines[0].get_xdata(), average, label=axis.get_title())
        #         ax_average.legend()
        #     ax_average.grid()


class PostCmd():
    def __init__(self):
        self.plot_data = None

    def run(self, simulation_data, progress=None):
        pass  # All matplotlib commands should be done in plot()

    def plot(self):  # Matplotlib commands may be placed here
        pass

    def progress_label(self):
        return ""


class PlotCmd(PostCmd):
    def __init__(self, cmd, expr, expr0, parameters, run_parameters, variables, mpl_prop, lineno):
        super().__init__()
        self.cmd = cmd
        self.expr = expr
        self.is_postexpr = False
        self.expr0 = expr0
        self.parameters = parameters
        self.variables = variables
        self.run_parameters = run_parameters
        self.mpl_prop = mpl_prop
        self.lineno = lineno

    def run(self, simulation_data):
        self.parameters.scalar_expand()  # If beta is not specified, scalar_expand has not been run
        start_at_1 = False
        if 'linewidth' not in self.mpl_prop:
            self.mpl_prop['linewidth'] = 1

        if self.is_postexpr:  # @plot v(s->b) + 2*w(s) / sin(n(s->b->s))
            post_expr = self.expr
            ydata, err = post_expr.eval(simulation_data, self.parameters, self.run_parameters, self.variables,
                                        POST_MATH)
            if err is not None:
                raise EvalException(f"Expression evaluation failed.", self.lineno)
            default_label = self.expr0

            # # Evaluate each variable v(s->b), w(s), n(s->b->s)
            # var_ydata = dict()  # Dict with evaluated ydata for each PostVar, keyed by alias variable
            # n_values = None

            # for alias, var in post_expr.post_vars.items():
            #     var_ydata[alias] = simulation_data.vwpn_eval(var.fn, var.parsed_arg, self.parameters, self.run_parameters)
            #     if n_values is None:
            #         n_values = len(var_ydata[alias])
            #     else:  # Number of evaluated values should be the same for all variables
            #         assert(n_values == len(var_ydata[alias])), f"{n_values} != {len(var_ydata[alias])}"

            # # Evaluate the expression using the evaluated variable values
            # ydata = [None] * n_values
            # for i in range(n_values):
            #     alias_values = {key: val[i] for key, val in var_ydata.items()}
            #     alias_values.update(POST_MATH)
            #     alias_values.update(self.variables.values)
            #     try:
            #         ydata[i] = eval(post_expr.expr, {'__builtins__': {'round': round}}, alias_values)
            #     except Exception as e:
            #         raise EvalException(f"Expression evaluation failed.", self.lineno)

        else:  # vplot s->b OR wplot(s) OR ...
            if self.cmd == kw.VPLOT:
                ydata = simulation_data.vwpn_eval('v', self.expr, self.parameters, self.run_parameters)
                default_label = f"v({self.expr0})"
            elif self.cmd == kw.VSSPLOT:
                ydata = simulation_data.vwpn_eval('vss', self.expr, self.parameters, self.run_parameters)
                default_label = f"vss({self.expr0})"
            elif self.cmd == kw.WPLOT:
                ydata = simulation_data.vwpn_eval('w', self.expr, self.parameters, self.run_parameters)
                default_label = f"w({self.expr0})"
            elif self.cmd == kw.PPLOT:
                ydata = simulation_data.vwpn_eval('p', self.expr, self.parameters, self.run_parameters)
                default_label = f"p({self.expr0})"
            elif self.cmd == kw.NPLOT:
                ydata = simulation_data.vwpn_eval('n', self.expr, self.parameters, self.run_parameters)
                default_label = f"n({self.expr0})"
                start_at_1 = ((self.parameters.get(kw.CUMULATIVE) == kw.EVAL_OFF) and
                            (self.parameters.get(kw.XSCALE) != kw.EVAL_ALL))

        if 'label' in self.mpl_prop:
            legend_label = self.mpl_prop['label']
            self.mpl_prop.pop('label')
        else:
            legend_label = default_label

        if self.parameters.get(kw.SUBJECT) == kw.EVAL_ALL:
            self.ydata_list = ydata
            self.plot_args_list = list()
            for i, _ in enumerate(ydata):
                if len(legend_label) > 0:
                    subject_legend_label = f"{legend_label} subject {i + 1}"
                else:
                    subject_legend_label = f"subject {i + 1}"
                plot_args = dict({'label': subject_legend_label}, **self.mpl_prop)
                # plt.plot(subject_ydata, **plot_args)
                self.plot_args_list.append(plot_args)
        else:
            self.ydata_list = [ydata]
            plot_args = dict({'label': legend_label}, **self.mpl_prop)
            self.plot_args_list = [plot_args]

        self.plot_data = PlotData(self.ydata_list, self.plot_args_list, start_at_1)

    def plot(self):
        self.plot_data.plot()

    def progress_label(self):
        return f"{self.cmd} {self.expr0}"


class PlotData():
    """
    Encapsulates the data required to produce a PlotCmd plot.
    """

    def __init__(self, ydata_list, plot_args_list, start_at_1):
        self.ydata_list = ydata_list
        self.plot_args_list = plot_args_list
        self.start_at_1 = start_at_1

    def plot(self):
        for ydata, plot_args in zip(self.ydata_list, self.plot_args_list):
            if self.start_at_1:
                xdata = list(range(len(ydata)))
                plt.plot(xdata[1:], ydata[1:], **plot_args)
            else:
                plt.plot(ydata, **plot_args)
        plt.grid(True)

        # cfm = plt.get_current_fig_manager()
        # cfm.window.attributes('-topmost', True)
        # plt.get_current_fig_manager().show()  # To get figures in front of gui (Windows problem) when ProgressDlg has been up
        # plt.get_current_fig_manager().set_window_title("FOO")
        plt.gcf().show()


class ExportCmd(PostCmd):
    def __init__(self, lineno, cmd, exprs, exprs0, parameters, run_parameters, variables):
        super().__init__()
        self.lineno = lineno
        self.cmd = cmd
        self.exprs = exprs
        self.is_postexpr = False
        self.exprs0 = exprs0
        self.parameters = parameters
        self.run_parameters = run_parameters
        self.variables = variables

        # parse_eval_prop(cmd, expr, eval_prop, VALID_PROPS[cmd])

    def run(self, simulation_data, progress=None):
        self.parameters.scalar_expand()  # If beta is not specified, scalar_expand has not been run
        filename = self.parameters.get(kw.EVAL_FILENAME)
        if len(filename) == 0:
            raise ParseException(self.lineno, f"Parameter {kw.EVAL_FILENAME} to {self.cmd} is mandatory.")
        # if not filename.endswith(".csv"):
        #     filename = filename + ".csv"
        file = open(filename, 'w', newline='')

        try:
            if self.cmd == kw.HEXPORT:
                self._h_export(file, simulation_data)
            else:
                self._vwpn_export(file, simulation_data)
        except EvalException as ex:
            file.close()
            raise ex

    def _h_export(self, file, simulation_data):
        # evalprops = simulation_data._evalparse(self.parameters)
        with file as csvfile:
            w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_MINIMAL, escapechar=None)

            run_label = self.parameters.get(kw.EVAL_RUNLABEL)
            n_subjects = len(simulation_data.run_outputs[run_label].output_subjects)
            all_stimulus_elements = self.parameters.get(kw.STIMULUS_ELEMENTS)

            # Figure out variable names
            variable_history = simulation_data.run_outputs[run_label].output_subjects[0].variables
            all_variables = dict()
            for v in variable_history:
                for k in v.values.keys():
                    all_variables[k] = 1
            all_variables = list(all_variables.keys())
            
            # Write headers
            w.writerow(['run','phase','subject','step','line','stimuli','behavior'] + all_stimulus_elements + all_variables)
            
            for s in range(n_subjects):
                rows = list()
                subject_output = simulation_data.run_outputs[run_label].output_subjects[s]
                history = subject_output.history
                phase_line_labels = subject_output.phase_line_labels
                phase_line_labels_steps = subject_output.phase_line_labels_steps
                variables = subject_output.variables
                first_step_phase = subject_output.first_step_phase
                for i in range(len(phase_line_labels_steps)):
                    step = phase_line_labels_steps[i]
                    p = 0
                    while first_step_phase[1][p+1] <= step:
                        p += 1
                    phase = first_step_phase[0][p]
                    compound = [""]
                    response = ""
                    intensities = [""] * len(all_stimulus_elements)
                    if i==len(phase_line_labels_steps)-1 or step != phase_line_labels_steps[i+1]:
                        stimulus = history[2*(step-1)]
                        response = history[2*(step-1)+1]
                        # Next loop figures out element intensities and
                        # the compound representation of stimulus
                        intensities = []
                        compound = []
                        for e in all_stimulus_elements:
                            if e in stimulus:
                                intensity = stimulus[e]
                                intensities.append(f"{intensity:.2g}")
                                if intensity==1:
                                    compound.append(f"{e}")
                                else:
                                    compound.append(f"{e}[{intensity:.2g}]")
                            else:
                                intensities.append("0")
                    # Saving variables must take care of keeping the
                    # same order and adding NA for variables that may
                    # not have a value at this step
                    step_variables = list()
                    for v in all_variables:
                        if v in variables[i].values:
                            step_variables.append(f"{variables[i].values[v]:.2g}")
                        else:
                            step_variables.append("")
                    # Note: subject numbers are 1-based in CSV and figure output
                    rows.append([run_label, phase, s+1, step, phase_line_labels[i], ','.join(compound), response] + intensities +
                               step_variables)
                w.writerows( rows )

    def _vwpn_export(self, file, simulation_data):
        run_label = self.parameters.get(kw.EVAL_RUNLABEL)
        with file as csvfile:
            w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, escapechar=None)
            w.writerow(['run','expr','subject','step','value'])

            ydatas = []
            legend_labels = []
            for expr, expr0 in zip(self.exprs, self.exprs0):
                label_expr = expr0  # beautify_expr_for_label(self.expr)
                if self.is_postexpr:  # @export v(s->b) + 2*w(s) / sin(n(s->b->s))
                    post_expr = expr
                    ydata, err = post_expr.eval(simulation_data, self.parameters, self.run_parameters, self.variables,
                                                POST_MATH)
                    if err is not None:
                        raise EvalException(f"Expression evaluation failed.", self.lineno)
                    legend_label = label_expr
                else:
                    if self.cmd == kw.VEXPORT:
                        ydata = simulation_data.vwpn_eval('v', expr, self.parameters, self.run_parameters)
                        legend_label = f"v({label_expr})"
                    if self.cmd == kw.VSSEXPORT:
                        ydata = simulation_data.vwpn_eval('vss', expr, self.parameters, self.run_parameters)
                        legend_label = f"vss({label_expr})"
                    elif self.cmd == kw.WEXPORT:
                        ydata = simulation_data.vwpn_eval('w', expr, self.parameters, self.run_parameters)
                        legend_label = f"w({label_expr})"
                    elif self.cmd == kw.PEXPORT:
                        ydata = simulation_data.vwpn_eval('p', expr, self.parameters, self.run_parameters)
                        legend_label = f"p({label_expr})"
                    elif self.cmd == kw.NEXPORT:
                        ydata = simulation_data.vwpn_eval('n', expr, self.parameters, self.run_parameters)
                        legend_label = f"n({label_expr})"
                ydatas.append(ydata)
                legend_labels.append(legend_label)

            for i in range(len(ydatas)):
                ydata = ydatas[i]
                legend_label = legend_labels[i]
                eval_subject = self.parameters.get(kw.EVAL_SUBJECT)
                if eval_subject == "all":
                    for subject_ind in range(len(ydata)):
                        subject_data = ydata[subject_ind]
                        subject_label = subject_ind + 1 # 1-based in CSV and figure output
                        for step in range(len(subject_data)):
                            w.writerow( [run_label, legend_label, subject_label, step, subject_data[step]] )
                else:
                    if eval_subject == kw.EVAL_AVERAGE:
                        subject_label = "average"
                    elif type(eval_subject) is int:
                        subject_label = eval_subject + 1 # 1-base in CSV and figure output
                    else:
                        # 'Internal error' because parameters have been checked already when parsing
                        raise EvalException(f"Internal error on eval_subject={eval_subject}.", self.lineno)
                    for step in range(len(ydata)):
                        w.writerow( [run_label, legend_label, subject_label, step, ydata[step]] )

    def progress_label(self):
        # return f"{self.cmd} {self.exprs0}"
        return f"{self.cmd}"


class FigureCmd(PostCmd):
    def __init__(self, title, mpl_prop):
        super().__init__()
        self.title = title
        self.mpl_prop = mpl_prop

    def plot(self):
        f = plt.figure(**self.mpl_prop)
        if self.title is not None:
            f.suptitle(self.title)  # Figure title

    def progress_label(self):
        return kw.FIGURE


class SubplotCmd(PostCmd):
    def __init__(self, spec_list, title, mpl_prop):
        super().__init__()
        self.spec_list = spec_list  # Subplot specification, e.g. [2,1,1]
        self.mpl_prop = mpl_prop
        if kw.TITLE not in mpl_prop:
            self.mpl_prop[kw.TITLE] = title

    def plot(self):
        plt.subplot(*self.spec_list, **self.mpl_prop)

    def progress_label(self):
        return kw.SUBPLOT


class LegendCmd(PostCmd):
    def __init__(self, mpl_prop):
        super().__init__()
        # self.labels = labels
        self.mpl_prop = mpl_prop

    def plot(self):
        # if self.labels is not None:
        #     plt.legend(self.labels, **self.mpl_prop)
        # else:
        plt.legend(**self.mpl_prop)

    def progress_label(self):
        return kw.LEGEND
