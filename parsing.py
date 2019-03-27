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
from exceptions import ParseException
from util import ParseUtil


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
                raise Exception("Comment block start '###' on line " +
                                "{}".format(lineno_multicomment_delimiter) +
                                " has no matching end.")
        lines[lineno0] = line

    # Remove all blank lines at the end of the script
    while lines and lines[-1] == '':
        lines.pop()

    return lines


class Script():
    def __init__(self, script):
        self.script = script
        self.script_parser = ScriptParser(self.script)

    def parse(self):
        self.script_parser.parse()

    def run(self):
        return self.script_parser.runs.run()

    def postproc(self, simulation_data, block=True):
        # self.postcmds.set_output(self.script_output)
        self.script_parser.postcmds.run(simulation_data)
        plt.show(block)


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

    def __init__(self, line):
        self.line = line
        self.linesplit_colon = line.split(':', 1)  # Has length 1 or 2
        self.linesplit_space = line.split(' ', 1)  # Has length 1 or 2
        self.param = None  # The parameter when line is "param: value"
        self.line_type = None

    def parse(self):
        possible_param = self.linesplit_colon[0].strip().lower()
        if is_parameter_name(possible_param):
            self.param = possible_param
            self.line_type = LineParser.PARAMETER
        first_word = self.linesplit_space[0].lower()
        if first_word == kw.VARIABLES:
            self.line_type = LineParser.VARIABLES
        elif first_word == kw.RUN:
            self.line_type = LineParser.RUN
        elif first_word == kw.PHASE:
            self.line_type = LineParser.PHASE
        elif first_word in (kw.VPLOT, kw.WPLOT, kw.PPLOT, kw.NPLOT):
            self.line_type = LineParser.PLOT
        elif first_word == kw.FIGURE:
            self.line_type = LineParser.FIGURE
        elif first_word == kw.SUBPLOT:
            self.line_type = LineParser.SUBPLOT
        elif first_word in (kw.VEXPORT, kw.WEXPORT, kw.PEXPORT, kw.NEXPORT):
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
                # line = line.strip(',')

            line_parser = LineParser(line)
            line_parser.parse()
            linesplit_colon = line_parser.linesplit_colon
            linesplit_space = line_parser.linesplit_space

            if in_prop or in_variables or in_phase:
                parse_this_line_done = True
                err = None
                if in_prop:
                    in_prop = line_endswith_comma
                    err = self.parameters.str_append(prop, line, self.variables,
                                                     self.phases.labels_set(), self.all_run_labels,
                                                     line_endswith_comma)
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
                if len(linesplit_colon) == 1:
                    raise ParseException(lineno, f"Parameter '{prop}' is not specified.")
                possible_val = linesplit_colon[1].strip()
                if len(possible_val) == 0:
                    raise ParseException(lineno, f"Parameter '{prop}' is not specified.")
                if line_endswith_comma:
                    if not self.parameters.may_end_with_comma(prop):
                        raise ParseException(lineno, "Value for {} may not end by comma.".format(prop))
                    in_prop = self.parameters.is_csv(prop)
                err = self.parameters.str_set(prop, possible_val, self.variables,
                                              self.phases.labels_set(), self.all_run_labels,
                                              line_endswith_comma)
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
                run = Run(world, mechanism_obj, n_subjects, bind_trials)
                self.runs.add(run, run_label, lineno)
                continue

            elif line_parser.line_type == LineParser.PHASE:
                gen_err = "@PHASE line must have the form '@PHASE label stop:condition'."
                if len(linesplit_space) == 1:
                    raise ParseException(lineno, gen_err)
                curr_phase_label, stop_condition = ParseUtil.split1(linesplit_space[1])
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
                export_parameters = copy.deepcopy(self.parameters)  # Params may change betweeen plot
                self._evalparse(lineno, export_parameters)
                export_parameters.val[kw.FILENAME] = filename  # If filename only given on export line
                export_cmd = ExportCmd(cmd, expr, export_parameters)
                self.postcmds.add(export_cmd)

            else:
                raise ParseException(lineno, f"Invalid expression '{line}'.")

    def _evalparse(self, lineno, parameters):
        """Handles parameters that depend on currently defined runs."""
        run_label = parameters.get(kw.EVAL_RUNLABEL)
        if len(run_label) == 0:
            run_label = list(self.runs.runs.keys())[-1]
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
        """
        cmd = linesplit_space[0]
        filename_param = self.parameters.get(kw.FILENAME)
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
        if cmd == kw.VPLOT:
            expr, err = ParseUtil.parse_element_behavior(expr0, all_stimulus_elements, all_behaviors)
        elif cmd == kw.PPLOT:
            expr, err = ParseUtil.parse_stimulus_behavior(expr0, all_stimulus_elements, all_behaviors)
        elif cmd == kw.NPLOT:
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
        args = linesplit_space[1]
        expr0, mpl_prop_str = ParseUtil.split1_strip(args)
        expr = expr0
        if mpl_prop_str is None:
            mpl_prop = dict()
        else:
            is_dict, mpl_prop = ParseUtil.is_dict(mpl_prop_str)
            if not is_dict:
                raise Exception(lineno, f"Expected a dict, got {mpl_prop_str}.")
        all_stimulus_elements = self.parameters.get(kw.STIMULUS_ELEMENTS)
        all_behaviors = self.parameters.get(kw.BEHAVIORS)
        err = None
        if cmd == kw.VPLOT:
            expr, err = ParseUtil.parse_element_behavior(expr0, all_stimulus_elements, all_behaviors)
        elif cmd == kw.PPLOT:
            expr, err = ParseUtil.parse_stimulus_behavior(expr0, all_stimulus_elements, all_behaviors)
        elif cmd == kw.NPLOT:
            expr, err = ParseUtil.parse_chain(expr0, all_stimulus_elements, all_behaviors)
        if err:
            raise ParseException(lineno, err)
            # expr = ParseUtil._arrow2tuple_np(expr0, self.parameters.get(kw.STIMULUS_ELEMENTS))

            # # util.find_and_cumsum takes list
            # expr = list(expr)

            # # Single-element stimuli are written to history as strings, so ('s',) in expr won't
            # # match 's' in history, so change ('s',) to 's' in expr
            # for i, _ in enumerate(expr):
            #     if type(expr[i]) is tuple and len(expr[i]) == 1:
            #         expr[i] = expr[i][0]

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
            args = linesplit_space[1]
            subplotspec, title_mplprop = ParseUtil.split1_strip(args)
            if title_mplprop is None:  # @subplot subplotspec
                title = title_param
                mpl_prop = dict()
            else:
                title, mpl_prop_str = ParseUtil.split1_strip(title_mplprop)
                if mpl_prop_str is None:
                    is_dict, mpl_prop = ParseUtil.is_dict(title)
                    if not is_dict:
                        mpl_prop = dict()
                else:
                    is_dict, mpl_prop = ParseUtil.is_dict(mpl_prop_str)
                    if not is_dict:
                        raise Exception(lineno, f"Expected a dict, got {mpl_prop_str}.")
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
            args = linesplit_space[1].split()
            nargs = len(args)
            found_dict = False
            for i in range(nargs - 1, 0, -1):
                candidate = ''.join(args[i: nargs])
                found_dict, d = ParseUtil.is_dict(candidate)
                if found_dict:
                    mpl_prop = d
                    title = ' '.join(args[0: i])
                    break
            if not found_dict:
                mpl_prop = dict()
                title = ' '.join(linesplit_space[1:])
        return title, mpl_prop

    def _parse_run(self, after_run, lineno):
        """
        Parses a @RUN line ("@RUN  phase1,phase2,... [runlabel:lbl]") and returns the run label and
        a list of phase labels.
        """
        match_objs_iterator = re.finditer(' runlabel[\s]*:', after_run)
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
        self.cmds = list()  # List of PlotCmd or ExportCmd objects

    def add(self, cmd):
        self.cmds.append(cmd)

    def run(self, simulation_data):
        for cmd in self.cmds:
            type_cmd = type(cmd)
            if type_cmd is not FigureCmd and \
               type_cmd is not SubplotCmd and \
               type_cmd is not PlotCmd and \
               type_cmd is not ExportCmd and \
               type_cmd is not LegendCmd:
                raise Exception(f"Internal error. Invalid type {type_cmd}.")
            cmd.run(simulation_data)


class PlotCmd():
    def __init__(self, cmd, expr, expr0, parameters, mpl_prop):
        self.cmd = cmd
        self.expr = expr
        self.expr0 = expr0
        self.parameters = parameters
        self.mpl_prop = mpl_prop
        # parse_eval_prop(cmd, expr, parameters)

    def run(self, simulation_data):
        if 'linewidth' not in self.mpl_prop:
            self.mpl_prop['linewidth'] = 1
        if self.cmd == kw.VPLOT:
            ydata = simulation_data.vwpn_eval('v', self.expr, self.parameters)
            legend_label = f"v({self.expr0})"
        elif self.cmd == kw.WPLOT:
            ydata = simulation_data.vwpn_eval('w', self.expr, self.parameters)
            # label_expr = beautify_expr_for_label(self.expr)
            legend_label = f"w({self.expr0})"
        elif self.cmd == kw.PPLOT:
            ydata = simulation_data.vwpn_eval('p', self.expr, self.parameters)
            legend_label = f"p({self.expr0})"
        elif self.cmd == kw.NPLOT:
            ydata = simulation_data.vwpn_eval('n', self.expr, self.parameters)
            legend_label = f"n({self.expr0})"

        if self.parameters.get(kw.SUBJECT) == kw.EVAL_ALL:
            subject_legend_labels = list()
            for i, subject_ydata in enumerate(ydata):
                subject_legend_label = "{0}, subject {1}".format(legend_label, i)
                subject_legend_labels.append(subject_legend_label)
            for i, subject_ydata in enumerate(ydata):
                subject_legend_label = subject_legend_labels[i]
                plt.plot(subject_ydata, label=subject_legend_label, **self.mpl_prop)
        else:
            plt.plot(ydata, label=legend_label, **self.mpl_prop)
        plt.grid(True)


class ExportCmd():
    def __init__(self, cmd, expr, expr0, parameters):
        self.cmd = cmd
        self.expr = expr
        self.expr0 = expr0
        self.parameters = parameters
        # parse_eval_prop(cmd, expr, eval_prop, VALID_PROPS[cmd])

    def run(self, simulation_data):
        filename = self.parameters.get(kw.EVAL_FILENAME)
        if len(filename) == 0:
            raise Exception(f"Parameter {kw.EVAL_FILENAME} to {self.cmd} is mandatory.")
        if not filename.endswith(".csv"):
            filename = filename + ".csv"
        file = open(filename, 'w', newline='')

        if self.cmd == kw.HEXPORT:
            self._h_export(file, simulation_data)
        else:
            self._vwpn_export(file, simulation_data)

    def _h_export(self, file, simulation_data):
        evalprops = simulation_data._evalparse(self.parameters)
        with file as csvfile:
            w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, escapechar=None)

            # if self.eval_prop[EVAL_SUBJECT] == EVAL_ALL:
            run_label = evalprops[kw.EVAL_RUNLABEL]
            n_subjects = len(simulation_data.run_outputs[run_label].output_subjects)
            subject_legend_labels = list()
            for i in range(n_subjects):
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
                    if histind < len(history):
                        stimulus = history[histind]
                        response = history[histind + 1]
                        datarow.append(stimulus)
                        datarow.append(response)
                    else:
                        datarow.append(' ')
                w.writerow(datarow)
            # else:
            #     # Write headers
            #     w.writerow(['step', 'stimulus', 'response'])

            #     # Write data
            #     for row in range(len(ydata)):
            #         datarow = [row, ydata[row]]
            #         w.writerow(datarow)

    def _vwpn_export(self, file, simulation_data):
        label_expr = self.expr0  # beautify_expr_for_label(self.expr)
        if self.cmd == kw.VEXPORT:
            ydata = simulation_data.vwpn_eval('v', self.expr, self.parameters)
            legend_label = "v{}".format(label_expr)
        elif self.cmd == kw.WEXPORT:
            ydata = simulation_data.vwpn_eval('w', self.expr, self.parameters)
            legend_label = "w{}".format(label_expr)
        elif self.cmd == kw.PEXPORT:
            ydata = simulation_data.vwpn_eval('p', self.expr, self.parameters)
            legend_label = "p{}".format(label_expr)
        elif self.cmd == kw.NEXPORT:
            ydata = simulation_data.vwpn_eval('n', self.expr, self.parameters)
            legend_label = "n{}".format(label_expr)

        n_ydata = len(ydata)

        with file as csvfile:
            w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, escapechar=None)

            if self.parameters(kw.EVAL_SUBJECT) == kw.EVAL_ALL:
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


class FigureCmd():
    def __init__(self, title, mpl_prop):
        self.title = title
        self.mpl_prop = mpl_prop

    def run(self, simulation_data):
        f = plt.figure(**self.mpl_prop)
        if self.title is not None:
            f.suptitle(self.title)  # Figure title


class SubplotCmd():
    def __init__(self, spec, title, mpl_prop):
        self.spec = spec  # Subplot specification, e.g. 211 or (2,1,1)
        self.mpl_prop = mpl_prop
        if kw.TITLE not in mpl_prop:
            self.mpl_prop[kw.TITLE] = title

    def run(self, simulation_data):
        plt.subplot(self.spec, **self.mpl_prop)


class LegendCmd():
    def __init__(self, mpl_prop):
        # self.labels = labels
        self.mpl_prop = mpl_prop

    def run(self, simulation_data):
        # if self.labels is not None:
        #     plt.legend(self.labels, **self.mpl_prop)
        # else:
        plt.legend(**self.mpl_prop)


# class ScriptBlock():
#     def __init__(self, keyword, pvdict, content):
#         self.keyword = keyword
#         self.pvdict = pvdict
#         self.content = content


# ---------------------- Static methods ----------------------
# def beautify_expr_for_label(expr0):
#     expr = expr0[:]
#     expr_type = type(expr)
#     is_list = (expr_type is list)
#     is_tuple = (expr_type is tuple)
#     if is_list or is_tuple:
#         expr = [e for e in expr if e is not None]
#     else:
#         return "('" + expr + "')"
#     for i, e in enumerate(expr):
#         if type(e) is tuple and len(e) == 1:
#             expr[i] = e[0]
#     if len(expr) == 1:
#         return beautify_expr_for_label(expr[0])
#     else:
#         if is_tuple:
#             return tuple(expr)
#         else:
#             return expr


# def parse_postcmd(cmd, cmdarg, simulation_parameters):
#     if cmdarg is not None:
#         args = LsUtil.parse_sso(cmdarg)
#         if args is None:  # Parse failed
#             raise LsParseException("Invalid argument list to {}".format(cmd))
#         nargs = len(args)
#     else:
#         args = list()  # Empty list
#         nargs = 0

#     if cmd == FIGURE:
#         if nargs > 2:
#             raise LsParseException("The number of arguments to {} must be <= 2.".format(cmd))
#         title = None
#         mpl_prop = dict()
#         if nargs == 2:
#             title = args[0]
#             mpl_prop = args[1]
#         elif nargs == 1:
#             either = args[0]
#             if type(either) is str:
#                 title = either
#             elif type(either) is dict:
#                 mpl_prop = either
#             else:
#                 raise LsParseException("Arguments to {} must be string and/or dict.".format(cmd))

#         if title is not None:
#             if type(title) != str:
#                 raise LsParseException("Title argument to {} must be a string.".format(cmd))
#         if type(mpl_prop) != dict:
#             raise LsParseException("Figure properties argument to {} must be a dict.".format(cmd))
#         return FigureCmd(title, mpl_prop)

#     elif cmd == SUBPLOT:
#         if nargs > 2 or nargs == 0:
#             raise LsParseException("The number of arguments to {} must be 1 or 2.".format(cmd))
#         spec = args[0]
#         errmsg = "First argument (subplot specification) to {} must be a tuple or three-positive-digits integer.".format(cmd)
#         parse_subplotspec(spec, errmsg)
#         mpl_prop = dict()
#         if nargs == 2:
#             mpl_prop = args[1]
#             if type(mpl_prop) is not dict:
#                 raise LsParseException("Second argument to {} must be a dictionary.".format(cmd))
#         return SubplotCmd(spec, mpl_prop)

#     elif cmd == LEGEND:
#         if nargs > 2:
#             raise LsParseException("The number of arguments to {} must be <=2.".format(cmd))
#         labels = None
#         mpl_prop = dict()
#         if nargs == 2:
#             labels = args[0]
#             mpl_prop = args[1]
#         elif nargs == 1:
#             either = args[0]
#             if (type(either) is tuple) or (type(either) is str):
#                 labels = either
#             elif type(either) is dict:
#                 mpl_prop = either
#             else:
#                 raise LsParseException("Arguments to {} must be tuple, string or dict.".format(cmd))
#         if labels is not None:
#             if type(labels) is str:
#                 labels = (labels,)
#             if type(labels) is not tuple:
#                 raise LsParseException(
#                     "Legend labels must be a tuple ('label1','label2',...) or a string.".format(cmd))
#         if type(mpl_prop) is not dict:
#             raise LsParseException("Second argument to {} must be a dictionary.".format(cmd))
#         return LegendCmd(labels, mpl_prop)

#     elif cmd == PPLOT or cmd == PEXPORT:
#         if nargs == 0:
#             raise LsParseException("No arguments given to {}".format(cmd))
#         expr = args[0]
#         if type(expr) is not tuple:
#             raise LsParseException("First argument to {} must be a tuple.".format(cmd))
#         if type(expr[0]) is not tuple:
#             listexpr = list(expr)
#             listexpr[0] = (listexpr[0],)
#             expr = tuple(listexpr)
#         beta = simulation_parameters.get(BETA)
#         eval_prop = {BETA: beta}
#         if nargs >= 2:
#             eval_prop.update(args[1])
#         if cmd == PPLOT:
#             plot_prop = dict()
#             if nargs >= 3:
#                 plot_prop = args[2]
#             return PlotCmd(cmd, expr, eval_prop, plot_prop)
#         else:
#             if nargs >= 3:
#                 raise LsParseException("The number of arguments to {} must be 1 or 2.".format(cmd))
#             return ExportCmd(cmd, expr, eval_prop)

#     elif cmd == NPLOT or cmd == NEXPORT:
#         if cmd == NPLOT:
#             if (nargs == 0) or (nargs > 4):
#                 raise LsParseException("The number of arguments to {} must be 1, 2, 3 or 4.".
#                                        format(cmd))
#         elif cmd == NEXPORT:
#             if (nargs == 0) or (nargs > 3):
#                 raise LsParseException("The number of arguments to {} must be 1, 2 or 3.".
#                                        format(cmd))
#         seq = args[0]
#         seqref = None
#         eval_prop = dict()
#         if nargs >= 2:
#             if (type(args[1]) is str) or (type(args[1]) is tuple) or (type(args[1]) is list):
#                 seqref = args[1]
#             elif type(args[1]) is dict:
#                 eval_prop = args[1]
#             else:
#                 raise LsParseException("Invalid second argument to {}.".format(cmd))
#         if cmd == NPLOT:
#             plot_prop = dict()
#             if nargs >= 3:
#                 if seqref is None:
#                     plot_prop = args[2]
#                 else:
#                     eval_prop = args[2]
#             if nargs == 4:
#                 plot_prop = args[3]
#             return PlotCmd(cmd, (seq, seqref), eval_prop, plot_prop)
#         else:
#             if nargs >= 3:
#                 if seqref is None:
#                     raise LsParseException("Invalid arguments to {}.".format(cmd))
#                 else:
#                     eval_prop = args[2]
#             return ExportCmd(cmd, (seq, seqref), eval_prop)

#     elif cmd == VPLOT or cmd == WPLOT:
#         if nargs == 0:
#             raise LsParseException("No arguments given to {}".format(cmd))
#         expr = args[0]
#         if cmd == VPLOT:
#             if type(expr) is not tuple:
#                 raise LsParseException("First argument to {} must be a tuple.".format(cmd))
#             for e in expr:
#                 if type(e) is not str:
#                     raise LsParseException("First argument to {} must be a tuple of strings.".format(cmd))
#         else:  # WPLOT
#             if type(expr) is not str:
#                 raise LsParseException("First argument to {} must be a string.".format(cmd))
#         eval_prop = dict()
#         if nargs >= 2:
#             eval_prop = args[1]
#             if type(eval_prop) is not dict:
#                 raise LsParseException("Properties to {} must be a dict.".format(cmd))
#         plot_prop = dict()
#         if nargs >= 3:
#             plot_prop = args[2]
#             if type(plot_prop) is not dict:
#                 raise LsParseException("Plot properties to {} must be a dict.".format(cmd))
#         return PlotCmd(cmd, expr, eval_prop, plot_prop)

#     elif cmd == VEXPORT or cmd == WEXPORT:
#         if nargs == 0:
#             raise LsParseException("No arguments given to {}".format(cmd))
#         expr = args[0]
#         if cmd == VEXPORT:
#             if type(expr) is not tuple:
#                 raise LsParseException("First argument to {} must be a tuple.".format(cmd))
#             for e in expr:
#                 if type(e) is not str:
#                     raise LsParseException("First argument to {} must be a tuple of strings.".format(cmd))
#         else:  # WEXPORT
#             if type(expr) is not str:
#                 raise LsParseException("First argument to {} must be a string.".format(cmd))
#         eval_prop = dict()
#         if nargs >= 2:
#             eval_prop = args[1]
#         if nargs >= 3:
#             raise LsParseException("The number of arguments to {} must be 1 or 2.".
#                                    format(cmd))
#         return ExportCmd(cmd, expr, eval_prop)

#     else:  # cmd == HEXPORT
#         if nargs == 0:
#             raise LsParseException("No arguments given to {}".format(cmd))
#         if nargs > 1:
#             raise LsParseException("The number of arguments to {} must be 1.".format(cmd))
#         eval_prop = args[0]
#         if type(eval_prop) is not dict:
#             raise LsParseException("Export properties to {} must be a dict.".format(cmd))
#         return ExportCmd(cmd, expr=None, eval_prop=eval_prop)


# def parse_eval_prop(cmd, expr, eval_prop, valid_prop):
#     pass
#     # if type(expr) is not str:
#     #     raise LsParseException("First input to {} must be a string, got {}".format(cmd, expr))
#     #    for p in eval_prop:
#     #        if p not in valid_prop:
#     #            raise LsParseException("Invalid property '{}' to {}".format(p, cmd))


# def parse_subplotspec(spec, errmsg):
#     if type(spec) is tuple:
#         if len(spec) != 3:
#             raise LsParseException(errmsg)
#         for i in spec:
#             if type(spec[i]) != int:
#                 raise LsParseException(errmsg)
#             if spec[i] <= 0:
#                 raise LsParseException(errmsg)
#     elif type(spec) is int:
#         if spec <= 0:
#             raise LsParseException(errmsg)
#         strspec = str(spec)
#         if len(strspec) != 3:
#             raise LsParseException(errmsg)
#         if '0' in strspec:
#             raise LsParseException(errmsg)
#     else:
#         raise LsParseException(errmsg)
# ----------------------------------------------------------------------------------

# class Figure():
#     parameters = {'title'}

#     def __init__(self):
#         pass


# class Subplot():
#     parameters = {'subplottitle'}

#     def __init__(self):
#         pass


# class Plot():
#     parameters = {''}

#     def __init__(self):
#         pass


# class Export():
#     def __init__(self):
#         pass
