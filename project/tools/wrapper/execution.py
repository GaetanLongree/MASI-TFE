import os
import re
import shlex
import subprocess
import time

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

    if os.path.exists('submit.sh'):
        debug.log("Launching the job")
        process = subprocess.Popen(shlex.split("sbatch submit.sh"),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        return_code = process.returncode

        if return_code == 0:
            # TODO manage for multiple JOB IDs being returned
            job_id = re.search(r"(?<=job )\b(\d*)", output).group(1)
            api_communicator.update_job_id(job_id)
        else:
            debug.log("ERROR: running slurm job - sbatch returned a non-zero return code" + \
                      "\nOutput: {}" + \
                      "\nError: {}".format(output, err))
            raise Exception("ERROR: running slurm job - sbatch returned a non-zero return code" + \
                            "\nOutput: {}" + \
                            "\nError: {}".format(output, err))


def wait():
    # continuously get the job status and check for the job state (or states if in array)
    # NB: WLM = Workload Manager
    wlm_handler = workload_manager.get(runtime_info.destination_cluster['workload_manager'])
    job_status = wlm_handler.get_job_status()
    statuses = wlm_handler.get_job_states(job_status)
    unique_statuses = numpy.unique(statuses)

    while (len(unique_statuses) == 1
           and not any(status in wlm_handler.TERMINATED_STATUSES for status in unique_statuses)):
        runtime_info.__update_job_status__(job_status)

        # TODO do the API
        api_communicator.update_job_status()
        if any(status in wlm_handler.WAITING_STATUSES for status in unique_statuses):
            api_communicator.notify_client("Job is currently in a waiting state (statuses : {})".format(statuses))
        elif any(status in wlm_handler.RUNNING_STATUSES for status in unique_statuses):
            api_communicator.notify_client("Job is currently in a running state (statuses : {})".format(statuses))
        else:
            api_communicator.notify_client(
                "Job state has changed to {} (statuses : {})".format(unique_statuses, statuses))

        time.sleep(15)

        job_status = wlm_handler.get_job_status()
        statuses = wlm_handler.get_job_states(job_status)
        unique_statuses = numpy.unique(statuses)

    # TODO once completed --> store output to safe storage location + send notification to API
    runtime_info.__update_job_status__(job_status)

    if any(status in wlm_handler.TERMINATED_SUCCESSFULLY_STATUSES for status in unique_statuses):
        api_communicator.notify_client("Job has successfully terminated its execution")
        return True
    else:
        api_communicator.notify_client("Job has terminated with the following status: {}".format(statuses))
        return False
