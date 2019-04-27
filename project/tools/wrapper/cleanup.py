import json
import os
import shutil


def delete_exec_files():
    os.remove('input.json')
    os.remove('wrapper.tar.gz')
    shutil.rmtree('wrapper')


def write_file_output(input):
    with open(os.path.join('output.json'), 'w') as file:
        json.dump(input, file)


def run(output):
    delete_exec_files()
    write_file_output(output)
