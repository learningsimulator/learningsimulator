@parameters
{
'subjects'          : 1,  # number of individuals
'mechanism'         : 'Enquist',
'behaviors'         : ['R0','R'],
'stimulus_elements' : ['0','reward','US','CS','new'],
'start_v'           : {'default':-1}, 
'alpha_v'           : 0.1,
'alpha_w'           : 0.1,
'beta'              : 1,
'behavior_cost'     : {'R':2,'default':0},
'u'                 : {'reward':10, 'default': 0},
'omit_learning'     : ['new']
}

@phase {'label': 'phase 1', 'end': 'reward=20'}
NEW_TRIAL 'new'  |  CONTEXT 		
CONTEXT '0'      | 10:US      | CONTEXT
US      'US'     | 'R':REWARD | NEW_TRIAL
REWARD  ('0','reward') | NEW_TRIAL

@run
@hplot 'reward' {'cumulative':'on', 'exact':'on'} # noll

@hplot 'reward' {'cumulative':'on', 'exact':'off'} # ej noll
