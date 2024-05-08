import sys
import os
import threading
import time
from queue import Queue, Empty as QueueEmpty

# Function to get the target directory or file from the command line arguments
def get_target(args):
    for arg in args:
        if arg.startswith(("--target_dir=", "-td=", "--target=", "-t=")):
            return arg.split("=", 1)[1]

# Function to get the source directory or file from the command line arguments
def get_source(args):
    for arg in args:
        if arg.startswith(("--source_dir=", "-sd=", "--source=", "-s=")):
            source = arg.split("=", 1)[1]
            if os.path.isdir(source):
                return get_sources_from_source_dir(source)

# Function to get all files from a source directory
def get_sources_from_source_dir(source):
    files = [os.path.join(source, f) for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
    return sorted(files)  # Sort files alphabetically

# Function to process a file
def process_file(file):
    print(f"\nProcessing file: {file}\n")
    # Replace the "target_dir" argument value in the command line arguments by "target" and current file
    for i, arg in enumerate(sys.argv):
        if arg.startswith(("--target_dir=", "-td=", "--target=", "-t=")):
            sys.argv[i:i+1] = ["--target=" + file]
            break
    # Execute
    os.system("python run.py " + " ".join('"{0}"'.format(arg) for arg in sys.argv[1:]) + " --headless")

# Function for worker threads
def worker():
    while not exit_flag[0]:
        try:
            file = queue.get(timeout=1)
            if file is None:
                break
            process_file(file)
            queue.task_done()
        except QueueEmpty:
            pass

# Get the source and target from the command line arguments
source = get_source(sys.argv[1:])
target = get_target(sys.argv[1:])

# Create a queue of files
queue = Queue()

# If the target is a directory, add all files in the directory to the queue
if os.path.isdir(target):
    files = [os.path.join(target, f) for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))]
    for file in sorted(files):  # Sort files alphabetically
        queue.put(file)
else:
    # If the target is a single file, add it to the queue
    queue.put(target)

# Create worker threads
threads = []
exit_flag = [False]
for _ in range(10):  # Maximum of threads
    time.sleep(5)  # Delay creation of each worker 
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

try:
    # Wait for all tasks to be completed
    queue.join()
except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Stopping threads...")

# Stop worker threads
exit_flag[0] = True
for _ in range(10):  # Maximum of threads
    queue.put(None)

for t in threads:
    t.join()
