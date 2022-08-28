import time

import util
from parsing import Script


def fake_sim(s):
    print("Starting task")
    for i in range(s):
        print(i)
        time.sleep(1)
    print("Task completed")

def run_simulation(script):
    try:
        script_obj = Script(script)
        script_obj.parse()
        simulation_data = script_obj.run()
        script_obj.postproc(simulation_data)
        return False, script_obj.script_parser.postcmds
    except Exception as ex:
        err_msg, stack_trace = util.get_errormsg(ex)
        return True, (err_msg, stack_trace)
