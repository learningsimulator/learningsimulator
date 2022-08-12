import time

from parsing import Script


def fake_sim(s):
    print("Starting task")
    for i in range(s):
        print(i)
        time.sleep(1)
    print("Task completed")

def run_simulation(script):
    script_obj = Script(script)
    print("Simluating...")
    script_obj.parse()
    simulation_data = script_obj.run()
    script_obj.postproc(simulation_data)
    # time.sleep(2)
    # print(simulation_data.run_outputs.keys())

    print("...done")
    print("Script finished successfully.")

    return script_obj.script_parser.postcmds
    # for cmd in script_obj.script_parser.postcmds.cmds:
    #     if cmd.plot_data is not None:
    #         out += f"{cmd.plot_data.ydata_list}"
    #     else:
    #         out += "None"

    

    # return out