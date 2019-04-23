import os
import shutil


def delete_exec_files():
    os.remove('input.json')
    os.remove('wrapper.tar.gz')
    shutil.rmtree('wrapper')


def run():
    delete_exec_files()
