import re
import copy
import matplotlib.pyplot as plt
import csv

import keywords as kw
from parameters import Parameters
from parameters import is_parameter_name
from simulation import Runs, Run
from variables import Variables
from phases import Phases
from exceptions import ParseException, InterruptedSimulation, EvalException
from util import ParseUtil  # , eval_average


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

    def run(self, progress=None):
        return self.script_parser.runs.run(progress)

    def postproc(self, simulation_data, progress=None):
        if progress is not None:
            progress.dlg.set_visibility2(False)
            progress.dlg.set_title("Plot/Export Progress")

        self.script_parser.postcmds.run(simulation_data, progress)

    def plot(self, block=True, progress=None):
        self.script_parser.postcmds.plot()
        if progress is not None:
            progress.close_dlg()
        plt.show(block=block)


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
    PLOT = 9
    EXPORT = 10
    LEGEND = 11
    PREV_DEFINED_VARIABLE = 12

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
        elif first_word in (kw.VPLOT, kw.VSSPLOT, kw.WPLOT, kw.XPLOT, kw.YPLOT, kw.ZPLOT, kw.PPLOT, kw.NPLOT):
            self.line_type = LineParser.PLOT
        elif first_word == kw.FIGURE:
            self.line_type = LineParser.FIGURE
        elif first_word == kw.SUBPLOT:
            self.line_type = LineParser.SUBPLOT
        elif first_word in (kw.VEXPORT, kw.WEXPORT, kw.PEXPORT, kw.NEXPORT, kw.HEXPORT,
                            kw.VSSEXPORT):
            self.line_type = LineParser.EXPORT
        elif first_word == kw.LEGEND:
            self.line_type = LineParser.LEGEND


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

            if in_prop or in_variables or in_phase:
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
                if len(linesplit_space) == 1:
                    raise ParseException(lineno, "@RUN line must have the form '@RUN phases [runlabel:label].")
                after_run = linesplit_space[1].strip()
                run_label, run_phase_labels = self._parse_run(after_run, lineno)
                world = self.phases.make_world(run_phase_labels)
                run_parameters = copy.deepcopy(self.parameters)  # Params may change betweeen runs
                mechanism_obj, err = run_parameters.make_mechanism_obj()
                if err:
                    raise ParseException(lineno, err)
                n_subjects = run_parameters.get(kw.N_SUBJECTS)
                bind_trials = run_parameters.get(kw.BIND_TRIALS)
                is_ok, err, err_lineno = mechanism_obj.check_compatibility_with_world(world)
                if err:
                    raise ParseException(err_lineno, err)
                run = Run(run_label, world, mechanism_obj, n_subjects, bind_trials)
                self.runs.add(run, run_label, lineno)
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
                if stop_condition is None:
                    raise ParseException(lineno, gen_err)
                stop, condition = ParseUtil.split1_strip(stop_condition, ':')
                if stop != "stop" or condition is None or len(condition) == 0:
                    raise ParseException(lineno, "Phase stop condition must have the form 'stop:condition'.")
                in_phase = True
                if inherited_from:
                    self.phases.inherit_from(inherited_from, curr_phase_label, condition, lineno)
                else:
                    self.phases.add_phase(curr_phase_label, condition, lineno)
                continue

            elif line_parser.line_type == LineParser.FIGURE:
                figure_title, mpl_prop = self._parse_figure(lineno, linesplit_space)
                figure_cmd = FigureCmd(figure_title, mpl_prop)
                self.postcmds.add(figure_cmd)

            elif line_parser.line_type == LineParser.SUBPLOT:
                subplotspec, subplot_title, mpl_prop = self._parse_subplot(lineno, linesplit_space)
                subplot_cmd = SubplotCmd(subplotspec, subplot_title, mpl_prop)
                self.postcmds.add(subplot_cmd)

            elif line_parser.line_type == LineParser.PLOT:
                expr, mpl_prop, expr0 = self._parse_plot(lineno, linesplit_space)
                cmd = linesplit_space[0].lower()
                plot_parameters = copy.deepcopy(self.parameters)  # Params may change betweeen plot
                self._evalparse(lineno, plot_parameters)
                plot_cmd = PlotCmd(cmd, expr, expr0, plot_parameters, mpl_prop)
                self.postcmds.add(plot_cmd)

            elif line_parser.line_type == LineParser.LEGEND:
                mpl_prop = self._parse_legend(lineno, linesplit_space)
                legend_cmd = LegendCmd(mpl_prop)
                self.postcmds.add(legend_cmd)

            elif line_parser.line_type == LineParser.EXPORT:
                expr, filename, expr0 = self._parse_export(lineno, linesplit_space)
                cmd = linesplit_space[0].lower()
                export_parameters = copy.deepcopy(self.parameters)  # Params may change betweeen exports
                self._evalparse(lineno, export_parameters)
                export_parameters.val[kw.FILENAME] = filename  # If filename only given on export line
                export_cmd = ExportCmd(lineno, cmd, expr, expr0, export_parameters)
                self.postcmds.add(export_cmd)

            else:
                raise ParseException(lineno, f"Invalid expression '{line}'.")

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

    def _parse_export(self, lineno, linesplit_space):
        """
        @export expr
        @export expr filename

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
                filename = linesplit_space[1]
            return None, filename, None

        if len(linesplit_space) == 1:  # @export
            raise ParseException(lineno, f"Invalid {cmd} command.")
        args = linesplit_space[1]
        expr0, filename = ParseUtil.split1_strip(args)
        expr = expr0
        if filename is None:
            if len(filename_param) == 0:
                raise ParseException(lineno, f"No filename given to {cmd}.")
            else:
                filename = filename_param
        all_stimulus_elements = self.parameters.get(kw.STIMULUS_ELEMENTS)
        all_behaviors = self.parameters.get(kw.BEHAVIORS)
        err = None
        if cmd == kw.VEXPORT:
            expr, err = ParseUtil.parse_element_behavior(expr0, all_stimulus_elements, all_behaviors)
        elif cmd == kw.VSSEXPORT:
            expr, err = ParseUtil.parse_element_element(expr0, all_stimulus_elements)
        elif cmd == kw.PEXPORT:
            stimulus, behavior, err = ParseUtil.parse_stimulus_behavior(expr0, all_stimulus_elements,
                                                                        all_behaviors, self.variables)
            expr = (stimulus, behavior)
        elif cmd == kw.NEXPORT:
            expr, err = ParseUtil.parse_chain(expr0, all_stimulus_elements, all_behaviors)
        if err:
            raise ParseException(lineno, err)
        return expr, filename, expr0

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
        all_stimulus_elements = self.parameters.get(kw.STIMULUS_ELEMENTS)
        all_behaviors = self.parameters.get(kw.BEHAVIORS)
        err = None
        if cmd in (kw.VPLOT, kw.YPLOT):
            expr, err = ParseUtil.parse_element_behavior(expr0, all_stimulus_elements, all_behaviors)
        elif cmd == kw.VSSPLOT:
            expr, err = ParseUtil.parse_element_element(expr0, all_stimulus_elements)
        elif cmd == kw.PPLOT:
            stimulus, behavior, err = ParseUtil.parse_stimulus_behavior(expr0, all_stimulus_elements,
                                                                        all_behaviors, self.variables)
            expr = (stimulus, behavior)
        elif cmd == kw.ZPLOT:
            expr, err = ParseUtil.parse_element_behavior_element(expr0, all_stimulus_elements, all_behaviors)
        elif cmd == kw.NPLOT:
            expr, err = ParseUtil.parse_chain(expr0, all_stimulus_elements, all_behaviors)
        if err:
            raise ParseException(lineno, err)
        return expr, mpl_prop, expr0

    def _parse_subplot(self, lineno, linesplit_space):
        """
        @subplot
        @subplot subplotspec
        @subplot subplotspec title
        @subplot subplotspec {mpl_prop}
        @subplot subplotspec title {mpl_prop}
        """
        title_param = self.parameters.get(kw.SUBPLOTTITLE)

        if len(linesplit_space) == 1:  # @subplot
            subplotspec = '111'
            title = title_param
            mpl_prop = dict()
        elif len(linesplit_space) == 2:  # @subplot ...
            args, mpl_prop = ParseUtil.get_ending_dict(linesplit_space[1])
            if mpl_prop is None:
                mpl_prop = dict()
            subplotspec, title_line = ParseUtil.split1_strip(args)
            if title_line is None:  # @subplot subplotspec
                title = title_param
            else:
                title = title_line
        return subplotspec, title, mpl_prop

    def _parse_figure(self, lineno, linesplit_space):
        """
        @figure
        @figure title
        @figure {mpl_prop}
        @figure title {mpl_prop}
        """
        title = self.parameters.get(kw.TITLE)
        if len(linesplit_space) == 1:  # @figure
            mpl_prop = dict()
        elif len(linesplit_space) == 2:  # @figure args
            title, mpl_prop = ParseUtil.get_ending_dict(linesplit_space[1])
            if mpl_prop is None:
                mpl_prop = dict()
        return title, mpl_prop

    def _parse_run(self, after_run, lineno):
        """
        Parses a @RUN line ("@RUN  phase1,phase2,... [runlabel:lbl]") and returns the run label and
        a list of phase labels.
        """
        match_objs_iterator = re.finditer(r' runlabel[\s]*:', after_run)
        match_objs = tuple(match_objs_iterator)
        n_matches = len(match_objs)
        if n_matches == 0:
            label = f'run{self.unnamed_run_cnt}'
            self.unnamed_run_cnt += 1
            phases_str = after_run
        elif n_matches == 1:
            match_obj = match_objs[0]
            start_index = match_obj.start() + 1  # Index of "l" in "label"
            end_index = match_obj.end()  # Index of character after ":"
            label = after_run[end_index:].strip()
            phases_str = after_run[0: start_index].strip()
        else:
            raise ParseException(lineno, f"Maximum one instance of 'runlabel:' on a {kw.RUN} line.")

        if label in self.all_run_labels:
            raise ParseException(lineno, f"Duplication of run label '{label}'.")
        else:
            self.all_run_labels.append(label)

        phase_labels = phases_str.strip(',').split(',')
        phase_labels = [phase_label.strip() for phase_label in phase_labels]
        for phase_label in phase_labels:
            if not self.phases.contains(phase_label):
                raise ParseException(lineno, f"Phase {phase_label} undefined.")

        return label, phase_labels


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
    def __init__(self, cmd, expr, expr0, parameters, mpl_prop):
        super().__init__()
        self.cmd = cmd
        self.expr = expr
        self.expr0 = expr0
        self.parameters = parameters
        self.mpl_prop = mpl_prop

    def run(self, simulation_data):
        self.parameters.scalar_expand()  # If beta is not specified, scalar_expand has not been run
        start_at_1 = False
        if 'linewidth' not in self.mpl_prop:
            self.mpl_prop['linewidth'] = 1
        if self.cmd == kw.VPLOT:
            ydata = simulation_data.var_eval('v', self.expr, self.parameters)
            default_label = f"v({self.expr0})"
        elif self.cmd == kw.VSSPLOT:
            ydata = simulation_data.var_eval('vss', self.expr, self.parameters)
            default_label = f"vss({self.expr0})"
        elif self.cmd == kw.WPLOT:
            ydata = simulation_data.var_eval('w', self.expr, self.parameters)
            default_label = f"w({self.expr0})"
        elif self.cmd == kw.XPLOT:
            ydata = simulation_data.var_eval('x', self.expr, self.parameters)
            default_label = f"x({self.expr0})"
        if self.cmd == kw.YPLOT:
            ydata = simulation_data.var_eval('y', self.expr, self.parameters)
            default_label = f"y({self.expr0})"
        if self.cmd == kw.ZPLOT:
            ydata = simulation_data.var_eval('z', self.expr, self.parameters)
            default_label = f"z({self.expr0})"
        elif self.cmd == kw.PPLOT:
            ydata = simulation_data.var_eval('p', self.expr, self.parameters)
            default_label = f"p({self.expr0})"
        elif self.cmd == kw.NPLOT:
            ydata = simulation_data.var_eval('n', self.expr, self.parameters)
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
                    subject_legend_label = f"{legend_label}, subject {i + 1}"
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
    def __init__(self, lineno, cmd, expr, expr0, parameters):
        super().__init__()
        self.lineno = lineno
        self.cmd = cmd
        self.expr = expr
        self.expr0 = expr0
        self.parameters = parameters
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
                self._var_export(file, simulation_data)
        except EvalException as ex:
            file.close()
            raise ex

    def _h_export(self, file, simulation_data):
        # evalprops = simulation_data._evalparse(self.parameters)
        with file as csvfile:
            w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, escapechar=None)

            # if self.eval_prop[EVAL_SUBJECT] == EVAL_ALL:
            run_label = self.parameters.get(kw.EVAL_RUNLABEL)
            n_subjects = len(simulation_data.run_outputs[run_label].output_subjects)
            subject_legend_labels = list()
            for i in range(n_subjects):
                # subject_legend_labels.append("phase line subject {}".format(i))
                subject_legend_labels.append("stimulus subject {}".format(i))
                subject_legend_labels.append("response subject {}".format(i))

            # Write headers
            w.writerow(['step'] + subject_legend_labels)

            # Write data
            maxlen = 0

            for i in range(n_subjects):
                len_history_i = len(simulation_data.run_outputs[run_label].output_subjects[i].history)
                if len_history_i > maxlen:
                    maxlen = len_history_i
            for histind in range(0, maxlen, 2):
                datarow = [histind // 2]
                for i in range(n_subjects):
                    history = simulation_data.run_outputs[run_label].output_subjects[i].history
                    # phase_line_labels = simulation_data.run_outputs[run_label].output_subjects[i].phase_line_labels
                    # phase_line_labels_steps = simulation_data.run_outputs[run_label].output_subjects[i].phase_line_labels_steps
                    # print(history)
                    # print(phase_line_labels)
                    # print(phase_line_labels_steps)
                    if histind < len(history):
                        stimulus = history[histind]
                        response = history[histind + 1]
                        # phase_line = phase_line_labels[]
                        datarow.append(stimulus)
                        datarow.append(response)
                    else:
                        datarow.append(' ')
                        datarow.append(' ')
                w.writerow(datarow)
            # else:
            #     # Write headers
            #     w.writerow(['step', 'stimulus', 'response'])

            #     # Write data
            #     for row in range(len(ydata)):
            #         datarow = [row, ydata[row]]
            #         w.writerow(datarow)

    def _var_export(self, file, simulation_data):
        label_expr = self.expr0  # beautify_expr_for_label(self.expr)
        if self.cmd == kw.VEXPORT:
            ydata = simulation_data.var_eval('v', self.expr, self.parameters)
            legend_label = f"v({label_expr})"
        if self.cmd == kw.VSSEXPORT:
            ydata = simulation_data.var_eval('vss', self.expr, self.parameters)
            legend_label = f"vss({label_expr})"
        elif self.cmd == kw.WEXPORT:
            ydata = simulation_data.var_eval('w', self.expr, self.parameters)
            legend_label = f"w({label_expr})"
        elif self.cmd == kw.PEXPORT:
            ydata = simulation_data.var_eval('p', self.expr, self.parameters)
            legend_label = f"p({label_expr})"
        elif self.cmd == kw.NEXPORT:
            ydata = simulation_data.var_eval('n', self.expr, self.parameters)
            legend_label = f"n({label_expr})"

        n_ydata = len(ydata)

        with file as csvfile:
            w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, escapechar=None)

            if self.parameters.get(kw.EVAL_SUBJECT) == kw.EVAL_ALL:
                subject_legend_labels = list()
                for i, subject_ydata in enumerate(ydata):
                    subject_legend_label = "{0} subject {1}".format(legend_label, i)
                    subject_legend_labels.append(subject_legend_label)

                # Write headers
                w.writerow(['x'] + subject_legend_labels)

                # Write data
                maxlen = 0
                for i in range(n_ydata):
                    len_ydata_i = len(ydata[i])
                    if len_ydata_i > maxlen:
                        maxlen = len_ydata_i
                for row in range(maxlen):
                    datarow = [row]
                    for i in range(n_ydata):
                        if row < len(ydata[i]):
                            datarow.append(ydata[i][row])
                        else:
                            datarow.append(' ')
                    w.writerow(datarow)
            else:
                # Write headers
                w.writerow(['x', legend_label])

                # Write data
                for row in range(len(ydata)):
                    datarow = [row, ydata[row]]
                    w.writerow(datarow)

    def progress_label(self):
        return f"{self.cmd} {self.expr0}"


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
    def __init__(self, spec, title, mpl_prop):
        super().__init__()
        self.spec = spec  # Subplot specification, e.g. 211 or (2,1,1)
        self.mpl_prop = mpl_prop
        if kw.TITLE not in mpl_prop:
            self.mpl_prop[kw.TITLE] = title

    def plot(self):
        plt.subplot(self.spec, **self.mpl_prop)

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
