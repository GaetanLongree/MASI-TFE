import time
from . import runtime_info


def log(string):
    timestamp = time.asctime()
    if runtime_info.user_input:
        log = '[' + timestamp + '] - [' + str(runtime_info.user_input['job_uuid']) + '] - ' + str(string) + '\n'
    else:
        log = '[' + timestamp + '] - ' + str(string) + '\n'
    file = open("/tmp/debug.log", "a+")
    file.write(log)
    file.close()
