import os
import re
import shlex
import subprocess

import numpy

from . import runtime_info, workload_manager, debug, api_communicator


def run():
    # create execution script based on workload manager used and resources requested
    script = workload_manager.parse(runtime_info.destination_cluster['workload_manager'],
                                    runtime_info.destination_cluster,
                                    runtime_info.user_input['resources'],
                                    runtime_info.user_input['execution'])

    with open('submit.sh', 'w') as file:
        file.write(script)
        file.close()

    debug.log(script)

    if os.path.exists('submit.sh'):
        debug.log("Launching the job")
        process = subprocess.Popen(shlex.split("sbatch submit.sh"),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        return_code = process.returncode

        if return_code == 0:
            # TODO manage for multiple JOB IDs being returned
            job_id = re.search(r"(?<=job )\b(\d*)(?= on)", output).group(1)
            api_communicator.update_job_id(job_id)
        else:
            debug.log("ERROR: running slurm job - sbatch returned a non-zero return code" + \
                      "\nOutput: {}" + \
                      "\nError: {}".format(output, err))
            raise Exception("ERROR: running slurm job - sbatch returned a non-zero return code" + \
                      "\nOutput: {}" + \
                      "\nError: {}".format(output, err))

    # if 'execution' in runtime_info.user_input:
    #     debug.log("Launching the job")
    #     for command in runtime_info.user_input['execution']:
    #         process = subprocess.Popen(shlex.split(command),
    #                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #         output, err = process.communicate()
    #         return_code = process.returncode
    #         debug.log("Job finished")
    #         debug.log(output)
    #         if return_code is not 0:
    #             debug.log("ERROR: running execution command {} returned a non-zero return code" + \
    #                       "\nOutput: {}" + \
    #                       "\nError: {}".format(command, output, err))
    #             raise Exception("ERROR: running execution command {} returned a non-zero return code".format(
    #                 runtime_info.user_input['execution']))


def wait():
    # continuously get the job status and check for the job state (or states if in array)
    # NB: WLM = Workload Manager
    wlm_handler = workload_manager.get(runtime_info.destination_cluster['workload_manager'])
    job_status = wlm_handler.get_job_status()
    statuses = wlm_handler.get_job_states(job_status)
    unique_statuses = numpy.unique(statuses)

    while len(unique_statuses) != 1 and unique_statuses not in wlm_handler.TERMINATED_STATUSES:
        runtime_info.__update_job_status__(job_status)

        # TODO do the API
        api_communicator.update_job_status()
        if statuses in wlm_handler.WAITING_STATUSES:
            api_communicator.notify_client("Job is currently in a waiting state (statuses : {})".format(statuses))
        elif statuses in wlm_handler.RUNNING_STATUSES:
            api_communicator.notify_client("Job is currently in a running state (statuses : {})".format(statuses))
        elif statuses in wlm_handler.EVENT_STATUSES:
            api_communicator.notify_client("Job state has changed to {} (statuses : {})".format(unique_statuses, statuses))

    # TODO once completed --> store output to safe storage location + send notificaiton to API
    if unique_statuses in wlm_handler.TERMINATED_SUCCESSFULLY_STATUSES:
        api_communicator.notify_client("Job has successfully terminated its execution")
        return True
    else:
        api_communicator.notify_client("Job has terminated with the following status: {}".format(statuses))
        return False
