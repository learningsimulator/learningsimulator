import queue
import threading

# Queue for progress messages from simulation workers to the GUI thread.
# Messages are tuples like ("report1", "Running run1"), ("increment1",), etc.
progress_queue = queue.Queue()

# Event to signal simulation workers to stop (e.g. when the user clicks Stop).
stop = threading.Event()
