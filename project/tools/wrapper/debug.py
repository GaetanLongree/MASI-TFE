import os
import time
from . import runtime_info


def log(string):
    timestamp = time.asctime()
    if runtime_info.user_input:
        log = '[' + timestamp + '] - [' + str(runtime_info.job_uuid) + '] - ' + str(string) + '\n'
    else:
        log = '[' + timestamp + '] - ' + str(string) + '\n'
    # tmp = open("/tmp/debug.log", "a+")
    # tmp.write(log)
    # tmp.close()
    file = open(os.path.join(runtime_info.working_directory, "debug.log"), "a+")
    file.write(log)
    file.close()
