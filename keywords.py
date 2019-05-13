# Parameters
BEHAVIORS = 'behaviors'
STIMULUS_ELEMENTS = 'stimulus_elements'
MECHANISM_NAME = 'mechanism'
START_V = 'start_v'
START_VSS = 'start_vss'
START_W = 'start_w'
ALPHA_V = 'alpha_v'
ALPHA_VSS = 'alpha_vss'
ALPHA_W = 'alpha_w'
BETA = 'beta'
BEHAVIOR_COST = 'behavior_cost'
U = 'u'
LAMBDA = 'lambda'
RESPONSE_REQUIREMENTS = 'response_requirements'
BIND_TRIALS = 'bind_trials'
N_SUBJECTS = 'n_subjects'
TITLE = 'title'
SUBPLOTTITLE = 'subplottitle'
RUNLABEL = 'runlabel'
SUBJECT = 'subject'
XSCALE = 'xscale'
XSCALE_MATCH = 'xscale_match'
PHASES = 'phases'
CUMULATIVE = 'cumulative'
MATCH = 'match'
FILENAME = 'filename'

# Commands
RUN = '@run'
VARIABLES = '@variables'
PHASE = '@phase'
FIGURE = '@figure'
SUBPLOT = '@subplot'
LEGEND = '@legend'
VPLOT = '@vplot'
VSSPLOT = '@vssplot'
WPLOT = '@wplot'
PPLOT = '@pplot'
NPLOT = '@nplot'
VEXPORT = '@vexport'
WEXPORT = '@wexport'
PEXPORT = '@pexport'
NEXPORT = '@nexport'
HEXPORT = '@hexport'

# Other
DEFAULT = 'default'
RAND = 'rand'
COUNT = 'count'
COUNT_LINE = 'count_line'

KEYWORDS = (BEHAVIORS,
            STIMULUS_ELEMENTS,
            MECHANISM_NAME,
            START_V,
            START_VSS,
            START_W,
            ALPHA_V,
            ALPHA_VSS,
            ALPHA_W,
            BETA,
            BEHAVIOR_COST,
            U,
            LAMBDA,
            RESPONSE_REQUIREMENTS,
            BIND_TRIALS,
            N_SUBJECTS,
            TITLE,
            SUBPLOTTITLE,
            RUNLABEL,
            SUBJECT,
            XSCALE,
            XSCALE_MATCH,
            PHASES,
            CUMULATIVE,
            MATCH,
            FILENAME,
            VARIABLES,
            PHASE,
            RUN,
            FIGURE,
            SUBPLOT,
            LEGEND,
            VPLOT,
            VSSPLOT,
            WPLOT,
            PPLOT,
            NPLOT,
            VEXPORT,
            WEXPORT,
            PEXPORT,
            NEXPORT,
            DEFAULT,
            RAND,
            COUNT,
            COUNT_LINE)

PHASEDIV = '|'

# Properties for evaluation
EVAL_SUBJECT = "subject"
EVAL_RUNLABEL = "runlabel"
# EVAL_EXACTSTEPS = "exact_steps"
EVAL_EXACT = "exact"
# EVAL_EXACTN = "exact_n"
EVAL_CUMULATIVE = "cumulative"
EVAL_PHASES = "phases"
EVAL_FILENAME = "filename"

# Property values for evaluation
EVAL_AVERAGE = "average"
EVAL_ON = "on"
EVAL_OFF = "off"
EVAL_ALL = "all"
