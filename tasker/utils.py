from os import walk, sep
import time
from datetime import timedelta
from time import time


class Timer:

    def __init__(self):
        self.start_time = time()

    def stop(self):
        run_time = timedelta(seconds=time() - self.start_time)
        return run_time


def get_files_in(directory: str):
    f = []
    for subdir, _, files in walk(directory):
        for file in files:
            filepath = subdir + sep + file
            f.append(filepath)
    return f
