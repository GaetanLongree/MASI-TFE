from . import runtime_info
import subprocess


def run():
    if 'file' in runtime_info.job:
        subprocess.call('chmod +x ' + runtime_info.job['file'], shell=True)
        subprocess.call('./' + runtime_info.job['file'], shell=True)
