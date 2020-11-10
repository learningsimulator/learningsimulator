script = """@parameters
{
'subjects'          : 1, # number  of individuals
'mechanism'         : 'Enquist',
'behaviors'         : ['R0','R'],
'stimulus_elements' : ['0','reward','US','CS','new'],
'start_v'           : {'default':-1}, 
'alpha_v'           : 0.1,
'alpha_w'           : 0.1,
'beta'              : 1,
'behavior_cost'     : {'R':2,'default':0},
'u'                 : {'reward':10, 'default': 0}
# 'omit_learning'     : ['new']
}

@phase {'label': 'phase 1', 'end': 'reward=200'}
NEW_PHASE  'new'      |  CONTEXT 		
CONTEXT '0'      | 50:US      | CONTEXT
US      'US'     | 'R':REWARD | NEW_PHASE
REWARD  'reward' | NEW_PHASE

# @phase {'label': 'phase 2', 'end': 'reward=20'}
# CONTEXT '0'      | 50:CS      | CONTEXT
# CS      'CS'     | 2:US       | CS
# US      'US'     | 'R':REWARD | CONTEXT
# REWARD  'reward' | CONTEXT

@run

@vplot ('US','R')"""

# y vid x=4000 skall vara mellan 34 och 35
