import json
import os
import shutil
from . import runtime_info


def delete_exec_files():
    os.remove(os.path.join(runtime_info.job_directory, 'input.json'))
    os.remove(os.path.join(runtime_info.job_directory, 'wrapper.tar.gz'))
    shutil.rmtree(os.path.join(runtime_info.job_directory, 'wrapper'))


def write_file_output(input):
    with open(os.path.join('output.json'), 'w') as file:
        json.dump(input, file)


def run(output):
    delete_exec_files()
    write_file_output(output)
