import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class SlaskTest(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def foo_test_profile(self):
        text = '''
# Simulation of pretraining and experiment 1A, 1B, 2A, 2B, 2C in Gruber et al. 2018:
# "New Caledonian Crows Use Mental Representations to Solve Metatool Problems"


#@variables stop_cond:50

n_subjects              : 10
mechanism               : GA
behaviors               : GoApparatusStick,GoApparatusStone,
              GoTubeStick,GoTubeStone,UseStickApparatus,
              UseStoneApparatus,UseStickTube,UseStoneTube,
              other,FirstStickToStick,FirstStickToTube,
              FirstStickToApparatus,FirstStickToStone,
              FirstStoneToStone,FirstStoneToStick,
              FirstStoneToApparatus,FirstStoneToTube,
              FirstStoneToAppStone
stimulus_elements       : background,stick,stone,reward,noreward,
              apparatusstick,apparatusstone,tubestick,
              tubestone,apparatus,tube,firststick,firststone,newtrial
start_v                 : default:1
alpha_v                 : 0.2
alpha_w                 : 0.2
beta                    : 1
behavior_cost           : default:0.1,other:0
u                       : reward:12, default:0
response_requirements   : GoApparatusStick:stick,
              GoApparatusStone:stone,
              GoTubeStick:stick,
              GoTubeStone:stone,
              UseStickApparatus:apparatusstick,
              UseStoneApparatus:apparatusstone,
              UseStickTube:tubestick,
              UseStoneTube:tubestone,
              FirstStickToStone:firststick,
              FirstStickToStick:firststick,
              FirstStickToTube:firststick,
              FirstStickToApparatus:firststick,
              FirstStoneToStone:firststone,
              FirstStoneToStick:firststone,
              FirstStoneToApparatus:firststone,
              FirstStoneToTube:firststone
bind_trials             : off

# Pretraining takes place with a piece of meat in front of apparatus S(platform) or S(tube). 
# "Crows learned over time to inhibit the impulse to take a tool without seeing the apparatus first"/Gruber in email.

# Training Phase 1: Birds were allowed to inspect apparatus, then choose tool, or the other way around 
@phase Training1 stop: background=100

new_trial       newtrial          | APPARATUS(0.5),TUBE(0.5)        | END 
APPARATUS       apparatus,reward  | CHOICE                          | END 
TUBE            tube,reward       | CHOICE                          | END 
CHOICE          stick,stone       | GoApparatusStick:APPARATUSSTICK | GoApparatusStone:APPARATUSSTONE | GoTubeStick:TUBESTICK | GoTubeStone:TUBESTONE |END 
APPARATUSSTICK  apparatusstick    | UseStickApparatus:NOREWARD      | END 
APPARATUSSTONE  apparatusstone    | UseStoneApparatus:REWARD        | END 
TUBESTICK       tubestick         | UseStickTube:REWARD             | END 
TUBESTONE       tubestone         | UseStoneTube:NOREWARD           | END 
NOREWARD        noreward          | END 
REWARD          reward            | END 
END             background        | new_trial 

# Training Phase 2: Birds were allowed to inspect apparatus, then choose tool, or the other way around 
@phase Training2 stop: background=100

new_trial       newtrial          | APPARATUS(0.5),TUBE(0.5)            | END 
APPARATUS       apparatus,reward  | COMPARTMENT1(0.5),COMPARTMENT2(0.5) | END 
TUBE            tube,reward       | COMPARTMENT3(0.5),COMPARTMENT4(0.5) | END 
COMPARTMENT1    stone             | GoApparatusStone:APPARATUSSTONE     | END 
COMPARTMENT2    stick             | GoApparatusStick:APPARATUSSTICK     | END 
COMPARTMENT3    stone             | GoTubeStone:TUBESTONE               |END 
COMPARTMENT4    stick             | GoTubeStick:TUBESTICK 
APPARATUSSTONE  apparatusstone    | UseStoneApparatus:REWARD        | END 
APPARATUSSTICK  apparatusstick    | UseStickApparatus:NOREWARD      | END 
TUBESTONE       tubestone         | UseStoneTube:NOREWARD           | END 
TUBESTICK       tubestick         | UseStickTube:REWARD             | END 
NOREWARD        noreward          | END 
REWARD          reward            | END 
END             background        | new_trial 

# Experiment 1A - With presentation of apparatus before start.
@phase Experiment1A stop: background=48
new_trial       newtrial          | APPARATUS                       | END 
APPARATUS       apparatus         | FIRSTSTICK                      | END
FIRSTSTICK      firststick        | FirstStickToStone:TUBESTONE     | FirstStickToStick:TUBESTICK | FirstStickToTube:TUBESTONE(0.5),TUBESTICK(0.5) | END      
TUBESTONE       stone,tube        | GoApparatusStone:APPARATUSSTONE | END 
TUBESTICK       stick,tube        | GoApparatusStick:NOREWARD       | END 
APPARATUSSTONE  apparatusstone    | UseStoneApparatus:REWARD        | END 
REWARD          reward            | END
NOREWARD        noreward          | END
END             background        | new_trial

# Experiment 1B - With presentation of apparatus before start.
@phase Experiment1B stop: background=48
new_trial       newtrial          | TUBE                             | END 
TUBE            tube              | FIRSTSTONE                       | END
FIRSTSTONE      firststone        | FirstStoneToStick:APPARATUSSTICK | FirstStoneToStone:APPARATUSSTONE | FirstStoneToApparatus:APPARATUSSTICK(0.5),APPARATUSSTONE(0.5) | END
APPARATUSSTICK  apparatus,stick   | GoTubeStick:TUBESTICK            | END
APPARATUSSTONE  apparatus,stone   | GoTubeStone:NOREWARD             | END
TUBESTICK       tubestick         | UseStickTube:REWARD              | END
REWARD          reward            | END
NOREWARD        noreward          | END
END             background        | new_trial

# Experiment 2A - With presentation of apparatus before start.
@phase Experiment2A stop: background=60
new_trial       newtrial          | TUBE                             | END 
TUBE            tube              | FIRSTSTONE                       | END
FIRSTSTONE      firststone        | FirstStoneToStick:APPARATUSSTICK | FirstStoneToStone:APPARATUSSTONE | FirstStoneToApparatus:APPARATUSSTICK(0.5),APPARATUSSTONE(0.5) | END
APPARATUSSTICK  apparatus,stick   | GoTubeStick:TUBESTICK            | END
APPARATUSSTONE  apparatus,stone   | GoTubeStone:NOREWARD             | END
TUBESTICK       tubestick         | UseStickTube:REWARD              | END
REWARD          reward            | END
NOREWARD        noreward          | END
END             background        | new_trial

# Experiment 2B - With presentation of apparatus before start.
@phase Experiment2B stop: background=600
new_trial       newtrial          | APPARATUS                       | END 
APPARATUS       apparatus         | FIRSTSTICK                      | END
FIRSTSTICK      firststick        | FirstStickToStone:TUBESTONE     | FirstStickToStick:TUBESTICK | FirstStickToTube:TUBESTONE(0.5),TUBESTICK(0.5) | END      
TUBESTONE       stone,tube        | GoApparatusStone:APPARATUSSTONE | END 
TUBESTICK       stick,tube        | GoApparatusStick:NOREWARD       | END 
APPARATUSSTONE  apparatusstone    | UseStoneApparatus:REWARD        | END
REWARD          reward            | END
NOREWARD        noreward          | END
END             background        | new_trial

# Experiment 2C - The "shortcut-trial". With presentation of apparatus before start.
@phase Experiment2C stop: background=60
new_trial       newtrial          | APPARATUS                       | END 
APPARATUS       apparatus         | FIRSTSTONE                      | END
FIRSTSTONE      firststone        | FirstStoneToStick:APPARATUSSTICK(0.5),TUBESTICK(0.5) | FirstStoneToTube:TUBESTICK | FirstStoneToAppStone:APPARATUSSTONE | END
TUBESTICK       stick,tube        | NOREWARD                        | END 
APPARATUSSTICK  apparatus,stick   | NOREWARD                        | END 
APPARATUSSTONE  apparatusstone    | UseStoneApparatus:REWARD        | END 
REWARD          reward            | END
NOREWARD        noreward          | END
END             background        | new_trial

# Experiment 3A - With presentation of apparatus before start.
@phase Experiment3A stop: background=60
new_trial       newtrial          | APPARATUS                        | END 
APPARATUS       apparatus         | FIRSTSTICK                       | END
FIRSTSTICK      firststick        | FirstStickToStone:TUBESTONE(0.5),APPARATUS1STONE(0.5) | FirstStickToTube:TUBESTONE | FirstStickToApparatus:APPARATUS1STONE | END      
TUBESTONE       stone,tube        | GoApparatusStone:APPARATUS2STONE | END 
APPARATUS1STONE apparatus,stone   | NOREWARD                         | END
APPARATUS2STONE apparatusstone    | UseStoneApparatus:REWARD         | END 
REWARD          reward            | END
NOREWARD        noreward          | END
END             background        | new_trial

# Experiment 3B - With presentation of apparatus before start.
@phase Experiment3B stop: background=60
new_trial       newtrial          | TUBE                             | END 
TUBE            tube              | FIRSTSTONE                       | END
FIRSTSTONE      firststone        | FirstStoneToStick:TUBE1STICK(0.5),APPARATUSSTICK(0.5) | FirstStoneToApparatus:APPARATUSSTICK | FirstStoneToTube:TUBE1STICK | END
TUBE1STICK      tube,stick        | NOREWARD                         | END
APPARATUSSTICK  apparatus,stick   | GoTubeStick:TUBE2STICK           | END
TUBE2STICK       tubestick        | UseStickTube:REWARD              | END
REWARD          reward            | END
NOREWARD        noreward          | END
END             background        | new_trial

@run Training1,Experiment1A,Experiment1B,Experiment2A,Experiment2B,Experiment2C,Experiment3A,Experiment3B

# Figure panel with tests
@figure Tests experiment 1-3: Probability
xscale: newtrial

@subplot 331 - {'xlabel':'Trial','ylabel':'Probability','title':'Test Experiment 1A'}
phases:   Experiment1A
subject: all
@pplot firststick->FirstStickToStone {'linewidth':0.3,'color':'darkgrey','label':''}
@pplot firststick->FirstStickToStick {'linewidth':0.3,'color':'steelblue','label':''}
subject: average
@pplot firststick->FirstStickToStone {'linewidth':3,'color':'black','label':'Correct'}
@pplot firststick->FirstStickToStick {'linewidth':3,'color':'steelblue','label':'Incorrect'}
@legend

@subplot 332 - {'xlabel':'Trial','ylabel':'Probability','title':'Test Experiment 1B'}
phases:   Experiment1B
subject: all
@pplot firststone->FirstStoneToStick {'linewidth':0.3,'color':'darkgrey','label':''}
@pplot firststone->FirstStoneToStone {'linewidth':0.3,'color':'steelblue','label':''}
subject: average
@pplot firststone->FirstStoneToStick {'linewidth':3,'color':'black'}
@pplot firststone->FirstStoneToStone {'linewidth':3,'color':'steelblue'}
@legend

@subplot 333 - {'xlabel':'Trial','ylabel':'Probability','title':'Test Experiment 2A'}
phases:   Experiment2A
subject: all
@pplot firststone->FirstStoneToStick {'linewidth':0.3,'color':'darkgrey','label':''}
@pplot firststone->FirstStoneToStone {'linewidth':0.3,'color':'steelblue','label':''}
subject: average
@pplot firststone->FirstStoneToStick {'linewidth':3,'color':'black'}
@pplot firststone->FirstStoneToStone {'linewidth':3,'color':'steelblue'}
@legend

@subplot 334 - {'xlabel':'Trial','ylabel':'Probability','title':'Test Experiment 2B'}
phases:   Experiment2B
subject: all
@pplot firststick->FirstStickToStone {'linewidth':0.3,'color':'darkgrey','label':''}
@pplot firststick->FirstStickToStick {'linewidth':0.3,'color':'steelblue','label':''}
subject: average
@pplot firststick->FirstStickToStone {'linewidth':3,'color':'black'}
@pplot firststick->FirstStickToStick {'linewidth':3,'color':'steelblue'}
@legend

@subplot 335 - {'xlabel':'Trial','ylabel':'Probability','title':'Test Experiment 2C'}
phases:   Experiment2C
subject: all
@pplot firststone->FirstStoneToAppStone {'linewidth':0.3,'color':'lightsalmon','label':''}
@pplot firststone->FirstStoneToStick {'linewidth':0.3,'color':'darkgrey','label':''}
@pplot firststone->FirstStoneToStone {'linewidth':0.3,'color':'steelblue','label':''}
subject: average
@pplot firststone->FirstStoneToAppStone {'linewidth':3,'color':'salmon'}
@pplot firststone->FirstStoneToStick {'linewidth':3,'color':'black'}
@pplot firststone->FirstStoneToStone {'linewidth':3,'color':'steelblue'}
@legend

@subplot 336 - {'xlabel':'Trial','ylabel':'Probability','title':'Test Experiment 3A'}
phases:  Experiment3A
subject: all
@pplot firststick->FirstStickToTube {'linewidth':0.3,'color':'lightsalmon','label':''}
@pplot firststick->FirstStickToApparatus {'linewidth':0.3,'color':'darkgrey','label':''}
@pplot firststick->FirstStickToStone {'linewidth':0.3,'color':'steelblue','label':''}
subject: average
@pplot firststick->FirstStickToTube {'linewidth':3,'color':'salmon'}
@pplot firststick->FirstStickToApparatus {'linewidth':3,'color':'black'}
@pplot firststick->FirstStickToStone {'linewidth':3,'color':'steelblue'}
@legend

@subplot 337 - {'xlabel':'Trial','ylabel':'Probability','title':'Test Experiment 3B'}
phases:  Experiment3B
subject: all
@pplot firststone->FirstStoneToApparatus  {'linewidth':0.3,'color':'lightsalmon','label':''}
@pplot firststone->FirstStoneToTube {'linewidth':0.3,'color':'darkgrey','label':''}
@pplot firststone->FirstStoneToStick  {'linewidth':0.3,'color':'steelblue','label':''}
subject: average
@pplot firststone->FirstStoneToApparatus {'linewidth':3,'color':'salmon'}
@pplot firststone->FirstStoneToTube {'linewidth':3,'color':'black'}
@pplot firststone->FirstStoneToStick {'linewidth':3,'color':'steelblue'}
@legend

# Figure panel with correct choices
@figure Tests experiment 1-3. Correct choices 
xscale: newtrial

@subplot 331 - {'xlabel':'Trial','ylabel':'n choices','title':'Test Experiment 1A'}
phases:  Experiment1A
subject: all
@nplot firststick->FirstStickToStone {'linewidth':0.3,'color':'darkgrey','label':''}
subject: average
@nplot firststick->FirstStickToStone {'linewidth':3,'color':'black'}
@legend

@subplot 332 - {'xlabel':'Trial','ylabel':'n choices','title':'Test Experiment 1B'}
phases:  Experiment1B
subject: all
@nplot firststone->FirstStoneToStick {'linewidth':0.3,'color':'black','label':''}
subject: average
@nplot firststone->FirstStoneToStick {'linewidth':3,'color':'black'}
@legend

@subplot 333 - {'xlabel':'Trial','ylabel':'n choices','title':'Test Experiment 2A'}
phases:  Experiment2A
subject: all
@nplot firststone->FirstStoneToStick {'linewidth':0.3,'color':'black','label':''}
subject: average
@nplot firststone->FirstStoneToStick {'linewidth':3,'color':'black'}
@legend

@subplot 334 - {'xlabel':'Trial','ylabel':'n choices','title':'Test Experiment 2B'}
phases:  Experiment2B
subject: all
@nplot firststick->FirstStickToStone {'linewidth':0.3,'color':'darkgrey','label':''}
subject: average
@nplot firststick->FirstStickToStone {'linewidth':3,'color':'black'}
@legend

@subplot 335 - {'xlabel':'Trial','ylabel':'n choices','title':'Test Experiment 2C'}
phases:  Experiment2C
subject: all
@nplot firststone->FirstStoneToAppStone {'linewidth':0.3,'color':'darkgrey','label':''}
subject: average
@nplot firststone->FirstStoneToAppStone {'linewidth':3,'color':'black'}
@legend

@subplot 336 - {'xlabel':'Trial','ylabel':'n choices','title':'Test Experiment 3A'}
phases:  Experiment3A
subject: all
@nplot firststick->FirstStickToTube {'linewidth':0.3,'color':'darkgrey','label':''}
subject: average
@nplot firststick->FirstStickToTube {'linewidth':3,'color':'black'}
@legend

@subplot 337 - {'xlabel':'Trial','ylabel':'n choices','title':'Test Experiment 3B'}
phases:  Experiment3B
subject: all
@nplot firststone->FirstStoneToApparatus {'linewidth':0.3,'color':'darkgrey','label':''}
subject: average
@nplot firststone->FirstStoneToApparatus {'linewidth':3,'color':'black'}
@legend
        '''
        script, simulation_data = run(text)
