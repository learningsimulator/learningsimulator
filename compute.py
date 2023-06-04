import multiprocessing

def worker(q):
    while True:
        script_obj = q.get()
        simulation_data = script_obj.run()
        q.put(simulation_data)


worker_queue = multiprocessing.Queue()
progress_queue = multiprocessing.Queue()
process = multiprocessing.Process(target=worker, args=(worker_queue,))
process.start()
