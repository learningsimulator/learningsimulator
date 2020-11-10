import LsScript

script='''@parameters
{
'subjects'          : 1,
'mechanism'         : 'Enquist',
'behaviors'         : ['R0','R1','R2'],
'stimulus_elements' : ['S1','S2','reward','reward2','new trial'],
'start_v'           : {'default':-1},
'alpha_v'           : 0.1,
'alpha_w'           : 0.1,
'beta'              : 1,
'behavior_cost'     : {'R1':1, 'R2':1, 'default':0},
'u'                 : {'reward':10, 'default': 0},
'omit_learning'     : ['new trial']
}



## ------------- SEQUENCE LEARNING -------------
@phase {'label':'chaining', 'end': 'reward=25'}
NEW_TRIAL	'new trial'	    | STIMULUS_1	
STIMULUS_1	'S1'	          | R1: STIMULUS_2     | NEW_TRIAL 
STIMULUS_2	'S2'	          | R2: REWARD         | NEW_TRIAL
REWARD     reward 	   | NEW_TRIAL	

@phase {'label':'test_A', 'end': 'S1=100'}
NEW_TRIAL	 'new trial'	   | STIMULUS_1	
STIMULUS_1	'S1'           | REWARD
REWARD     'reward2' 	    | NEW_TRIAL	

@phase {'label':'test_B', 'end': 'S1=100'}
NEW_TRIAL	'new trial'	  | STIMULUS_1	
STIMULUS_1	'S1'	          | R1: STIMULUS_2     | NEW_TRIAL
STIMULUS_2	'S2'	          | NEW_TRIAL	

@run {'phases':('chaining','test_B')}

@figure
@wplot 'S1'
@wplot 'S2'
@legend

@figure
@pplot ('S1', 'R1')
@pplot ('S1', 'R0')
@legend


@figure
@vplot ('S1', 'R1')
@vplot ('S1', 'R0')
@legend
'''

script_obj = LsScript.LsScript(script)
simulation_data = script_obj.run()

