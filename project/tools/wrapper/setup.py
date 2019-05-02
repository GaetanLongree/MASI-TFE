import json
import os
import platform
import re
import shlex
import subprocess
import wget

from . import runtime_info, debug, workload_manager, api_communicator


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
    facts['cluster'] = workload_manager.get(runtime_info.destination_cluster['workload_manager']).get_cluster_resources()
    runtime_info.__update_facts__(facts)
    # TODO POST to API


def __execute_requirements__():
    if 'requirements' in runtime_info.user_input:
        for command in runtime_info.user_input['requirements']:
            process = subprocess.Popen(shlex.split(command),
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = process.communicate()
            return_code = process.returncode
            if return_code is not 0:
                debug.log("ERROR: command {} of requirements returned a non-zero return code" + \
                          "\nOutput: {}" + \
                          "\nError: {}".format(command, output, err))


def __prep_job__():
    if runtime_info.ONLINE_JOB_FILE:
        if re.search(r"\.git$", runtime_info.user_input['job']):
            # clone using git
            process = subprocess.Popen(shlex.split('git clone --recursive ' + runtime_info.user_input['job']),
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = process.communicate()
            return_code = process.returncode
            if return_code is not 0:
                debug.log("ERROR: cloning job through GIT returned a non-zero return code" + \
                          "\nOutput: {}" + \
                          "\nError: {}".format(output, err))
                raise Exception("ERROR: cloning job through GIT returned a non-zero return code")

            # get repo name
            regex = r"\/([^\/]+)\/?(?=\.git$)"
            folder_name = (re.search(regex, runtime_info.user_input['job'])).group(1)
            os.chdir(folder_name)
        else:
            wget.download(runtime_info.user_input['job'], 'job')
    elif runtime_info.TAR_FILE:
        # unpack transferred job if necessary
        process = subprocess.Popen(shlex.split('tar zxf ' + runtime_info.user_input['job'] + '.tar.gz'),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        return_code = process.returncode
        if return_code is not 0:
            debug.log("ERROR: tarfile extraction returned a non-zero return code" + \
                      "\nOutput: {}" + \
                      "\nError: {}".format(output, err))
            raise Exception("ERROR: tarfile extraction returned a non-zero return code")

        os.chdir(runtime_info.user_input['job'])

    # compile the job if necessary
    if 'compilation' in runtime_info.user_input:
        def compilation(command):
            process = subprocess.Popen(shlex.split(command),
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = process.communicate()
            return_code = process.returncode
            if return_code is not 0:
                debug.log("ERROR: command {} of compilation returned a non-zero return code" + \
                          "\nOutput: {}" + \
                          "\nError: {}".format(command, output, err))

        if len(runtime_info.user_input['compilation']) > 0:
            if isinstance(runtime_info.user_input['compilation'], str):
                # do single command compilation
                compilation(runtime_info.user_input['compilation'])
            elif isinstance(runtime_info.user_input['compilation'], list):
                for command in runtime_info.user_input['compilation']:
                    # do list command compilation
                    compilation(command)


def run(input_file):
    __import_input__(input_file)
    # debug.log(json.dumps(runtime_info.user_input, indent=4))
    __gather_facts__()
    __prep_job__()
    __execute_requirements__()
    # debug.log(runtime_info.user_input)
    # debug.log(runtime_info.facts)
