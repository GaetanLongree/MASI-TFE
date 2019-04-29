import json
import os
import platform
import sys
import subprocess

from . import runtime_info, debug

if __name__ == '__main__':
    system_facts = {}

    system_facts['platform'] = platform.platform()
    system_facts['system'] = platform.system()
    system_facts['release'] = platform.release()
    system_facts['version'] = platform.version()

    print(system_facts)


def __import_input__(input_file):
    with open(input_file, 'r') as file:
        runtime_info.update(json.load(file))


def __gather_facts__():
    facts = dict()
    os = dict()
    os['platform'] = platform.platform()
    os['system'] = platform.system()
    os['release'] = platform.release()
    os['version'] = platform.version()

    facts['os'] = os
    # TODO uncomment once testing to prod
    #if runtime_info.destination_cluster['workload_manager'] == 'slurm':
    #    facts['cluster'] = workload_manager.Slurm.get_cluster_resources()

    runtime_info.__update_facts__(facts)

def __prep_job__():
    # TODO assert if job file is local or a git repository
    import wget
    if runtime_info.ONLINE_JOB_FILE:
        wget.download(runtime_info.user_input['job'], 'job.sh')
        runtime_info.__update_job__('job.sh')
    pass


def run(input_file):
    __import_input__(input_file)
    #__requirements__()
    __gather_facts__()
    __prep_job__()
    # debug.log(runtime_info.user_input)
    # debug.log(runtime_info.facts)
    # debug.log(runtime_info.job)
