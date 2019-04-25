from . import runtime_info, workload_manager, debug
import subprocess


def run():
    # TODO create execution script based on workload manager used and resources requested
    script = workload_manager.parse(runtime_info.user_input['destination_cluster']['workload_manager'],
                                    runtime_info.user_input['resources'])
    debug.log(script)
    if 'file' in runtime_info.job:
        subprocess.call('chmod +x ' + runtime_info.job['file'], shell=True)
        subprocess.call('./' + runtime_info.job['file'], shell=True)
