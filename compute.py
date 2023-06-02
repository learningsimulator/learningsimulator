import multiprocessing

def compute( q ):
    while True:
        script_obj = q.get()
        simulation_data = script_obj.run()
        q.put( simulation_data )

queue = multiprocessing.Queue()
process = multiprocessing.Process( target=compute, args=(queue,) )
process.start()


