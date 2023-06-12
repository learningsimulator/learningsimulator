import multiprocessing
import traceback

def worker(q):
    while True:
        try:
            script_obj = q.get()
            simulation_data = script_obj.run()
            q.put((simulation_data, ))
        except Exception as ex:
            q.put((ex, traceback.format_exc()))

worker_queue = multiprocessing.Queue()
progress_queue = multiprocessing.Queue()
process = multiprocessing.Process(target=worker, args=(worker_queue,))
