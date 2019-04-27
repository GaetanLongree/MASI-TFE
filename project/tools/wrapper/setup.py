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
        runtime_info.__update_input__(json.load(file))


def __gather_facts__():
    system_facts = {}
    system_facts['platform'] = platform.platform()
    system_facts['system'] = platform.system()
    system_facts['release'] = platform.release()
    system_facts['version'] = platform.version()
    runtime_info.__update_facts__(system_facts)

def __requirements__():
    # if runtime_info.user_input['destination_cluster']['name'] == 'test':
    #     cmd = 'sudo -S ' + sys.executable + ' -m pip install -r wrapper/requirements.txt'
    #     # https://stackoverflow.com/questions/44684764/how-to-type-sudo-password-when-using-subprocess-call
    #     p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    #     out, err = p.communicate('{}\n'.format(runtime_info.user_input['password']))
    # else:
    debug.log(os.getcwd())
    cmd = 'pip install --user -r wrapper/requirements.txt'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    debug.log(str(out))
    debug.log(str(err))

def __prep_job__():
    # TODO assert if job file is local or a git repository
    import wget
    if runtime_info.user_input['online_job_file']:
        wget.download(runtime_info.user_input['job'], 'job.sh')
        runtime_info.__update_job__('job.sh')
    pass


def run(input_file):
    __import_input__(input_file)
    #__requirements__()
    __gather_facts__()
    __prep_job__()
    debug.log(runtime_info.user_input)
    debug.log(runtime_info.facts)
    debug.log(runtime_info.job)
