example_scripts = [
{
    "name": "Basic Pavlovian learning",
    "code": '''# Learning mechanism: Rescola Wagner 
# This script contains the classical experiment of Pavlov's dog 
#
# The bell is the conditioned stimulus (CS)
# The food is the unconditioned stimulus (US)
# Salivation is the conditioned response (CR) 

n_subjects        : 1
mechanism         : rw
behaviors         : ignore,cr
stimulus_elements : bell,food 
start_vss         : default:0 
alpha_vss         : 0.1
beta              : 1
lambda            : food:10, default: 0

@phase Experiment stop: bell=100
CS      bell   | US
US      food   | CS

@run Experiment

Title: Strength of S-S association
@figure
@subplot 111 {'xlabel':'Trial number', 'ylabel':'S-S association'}
xscale: bell
subject: average
@vssplot bell->food {'linewidth':2, 'color':'black'}
    '''
},

{
    "name": "Instrumental learning",
    "code": '''# Basic instrumental conditioning:
# This script contains a case of instrumental learning. An animal learns to press
# a lever in order to receive a food reward.
#
# Mechanism: Stimulus-response learning
# This is an example of a rat in a Skinner box. The rat receives a reward when
# it presses the lever.

n_subjects        : 50
mechanism         : SR
behaviors         : press,other
stimulus_elements : lever,reward
start_v           : lever->other:0, default:-1
alpha_v           : 0.1
beta              : 1
u                 : reward:2, default:0 

@phase instrumental_conditioning stop: lever=60   
LEVER    lever       | press: REWARD  | LEVER
REWARD   reward      | LEVER

@run instrumental_conditioning
 
xscale: lever

@figure Instrumental conditioning (blue line shows average)
@subplot 121 {'xlabel':'Trial number','ylabel':'Probability of response', 'ylim':[0,1], 'title':'Probability of pressing lever'}
subject: average
@pplot lever->press {'linewidth':4}
subject: all
@pplot lever->press {'linewidth':0.5}

 
@subplot 122 - {'xlabel':'Trial number','ylabel':'SR association or value (v)', 'title':'SR association lever-press'  }
subject: average
@vplot lever->press {'linewidth':4}
subject: all
@vplot lever->press {'linewidth':0.5}
    '''
},

{
    "name": "Chaining",
    "code": '''# Basic chaining with the GA mechanism 
#
# Here we deal with a situation where an animal encounters a plant that contains
# berries The berries contain suger, which is a primary reinforcer with a
# value (u). Initially, the animal does not know that there are edible berries
# in a particular plant. They are, initially, not interested in approaching
# either the plant or the berry. This script shows how the animals acquire a
# chain of behaviours: approaching the plant and eating the berry. Over time
# the w-value for the berry increases and acts as a conditional reinforcer
# rewarding approaches to the plant.

n_subjects        			: 100
mechanism         			: GA
behaviors         			: approach,eat,other
stimulus_elements 			: plant,berry,sugar,no_reward
response_requirements			: approach:plant, eat:berry
start_v           			: plant->other:0, berry->other:0, default:-1
alpha_v           			: 0.1
alpha_w           			: 0.1
beta              			: 1
behavior_cost     			: approach:1, default: 0
u                 			: sugar:10, default:0 

@phase acquisition stop: plant=150
START                     | @omit_learn, PLANT
PLANT          plant      | approach: BERRY    |  START
BERRY          berry      | eat: REWARD        |  NO_REWARD
REWARD         sugar      | START
NO_REWARD      no_reward  | START

@run acquisition 

xscale: plant
subject: average
@figure Chaining:  plant -> approach -> berry -> eat -> sugar
@subplot 131 - {'xlabel':'Trial','ylabel':'Probability of response', 'title':'Probability of response' }
@pplot berry->eat {'linewidth':3,'color':'red'}
@pplot plant->approach {'linewidth':3,'color':'green'}
@legend

@subplot 132 w-value (berry) {'xlabel':'Trial','ylabel':'w-value',}
@wplot berry {'linewidth':3,'color':'steelblue'}
@legend

@subplot 133 {'xlabel':'Trial','ylabel':'v-value','title':'v - values'  }
@vplot berry->eat {'linewidth':3,'color':'red'}
@vplot plant->approach {'linewidth':3,'color':'green'}
@legend
    '''
}
]
