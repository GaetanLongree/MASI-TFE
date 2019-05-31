import os
import re
import shlex
import subprocess
import time

import numpy

from . import runtime_info, workload_manager, debug, api_communicator


def run():
    # create execution script based on workload manager used and resources requested
    script_filename = workload_manager.get(runtime_info.destination_cluster['workload_manager']) \
        .create_script(runtime_info.destination_cluster,
                       runtime_info.user_input['resources'],
                       runtime_info.user_input['execution'])

    debug.log("Launching the job")
    return_code, job_id = workload_manager.get(runtime_info.destination_cluster['workload_manager']).submit_job()

    if return_code == 0:
        job_id = job_id
        runtime_info.__update_working_dir__(os.getcwd())


def __status_comparator__(statuses, values):
    for status in statuses:
        for value in values:
            yield (status == value) or (value in status)


def wait():
    # continuously get the job status and check for the job state (or states if in array)
    # NB: WLM = Workload Manager
    wlm_handler = workload_manager.get(runtime_info.destination_cluster['workload_manager'])
    job_status = wlm_handler.get_job_status()
    while job_status is None:
        time.sleep(5)
        job_status = wlm_handler.get_job_status()
    statuses = wlm_handler.get_job_states(job_status)
    unique_statuses = numpy.unique(statuses)
    prev_statuses = []

    while (len(unique_statuses) == 1
           and not any(__status_comparator__(unique_statuses, wlm_handler.TERMINATED_STATUSES))):
        runtime_info.__update_job_status__(job_status)

        debug.log("Job is currently in the state: {}".format(unique_statuses))

        unique_statuses.sort()
        prev_statuses.sort()

        if unique_statuses != prev_statuses:
            api_communicator.update_job_status()
            if any(status in wlm_handler.WAITING_STATUSES for status in unique_statuses):
                api_communicator.notify_client_state_change(unique_statuses)
            elif any(status in wlm_handler.RUNNING_STATUSES for status in unique_statuses):
                api_communicator.notify_client_state_change(unique_statuses)
            else:
                api_communicator.notify_client_state_change(unique_statuses)

        time.sleep(5)

        prev_statuses = unique_statuses[:]
        job_status = wlm_handler.get_job_status()
        statuses = wlm_handler.get_job_states(job_status)
        unique_statuses = numpy.unique(statuses)

    # TODO once completed --> store output to safe storage location + send notification to API
    runtime_info.__update_job_status__(job_status)
    api_communicator.update_job_status()

    if any(status in wlm_handler.TERMINATED_SUCCESSFULLY_STATUSES for status in unique_statuses):
        api_communicator.notify_client_state_change(unique_statuses)
        return True
    else:
        api_communicator.notify_client_state_change(unique_statuses)
        return False
