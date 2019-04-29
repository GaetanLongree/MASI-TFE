import os
import shlex
import subprocess
from . import runtime_info, workload_manager, debug


def run():
    # TODO create execution script based on workload manager used and resources requested
    script = workload_manager.parse(runtime_info.destination_cluster['workload_manager'],
                                    runtime_info.user_input['resources'])
    debug.log(script)
    if 'execution' in runtime_info.user_input:
        process = subprocess.Popen(shlex.split(runtime_info.user_input['execution']),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        return_code = process.returncode
        if return_code is not 0:
            debug.log("ERROR: running execution command {} returned a non-zero return code" + \
                      "\nOutput: {}" + \
                      "\nError: {}".format(runtime_info.user_input['execution'], output, err))
            raise Exception("ERROR: running execution command {} returned a non-zero return code".format(
                                runtime_info.user_input['execution']))


def wait():
    # TODO continusouly get the job status and check for the job state (or states if in array)
    job_status = workload_manager.Slurm.get_job_status()
    # TODO update runtime info

    # TODO post job state update to API

    # TODO as soon as a single running is done, start waiting for completion + send notification to API

    # TODO once completed --> store output to safe storage location + send notificaiton to API
    return None
