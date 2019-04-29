from . import runtime_info, workload_manager, debug
import subprocess


def run():
    # TODO create execution script based on workload manager used and resources requested
    script = workload_manager.parse(runtime_info.destination_cluster['workload_manager'],
                                    runtime_info.user_input['resources'])
    debug.log(script)
    if 'file' in runtime_info.job:
        subprocess.call('chmod +x ' + runtime_info.job['file'], shell=True)
        subprocess.call('./' + runtime_info.job['file'], shell=True)
def wait():
    # TODO continusouly get the job status and check for the job state (or states if in array)
    job_status = workload_manager.Slurm.get_job_status()
    # TODO update runtime info

    # TODO post job state update to API

    # TODO as soon as a single running is done, start waiting for completion + send notification to API

    # TODO once completed --> store output to safe storage location + send notificaiton to API
    return None
