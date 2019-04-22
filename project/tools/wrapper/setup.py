import json
import platform
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
    pass


def __job__():
    # TODO assert if job file is local or a git repository
    pass


def run(input_file):
    __import_input__(input_file)
    __gather_facts__()
    debug.log(runtime_info.user_input)
    debug.log(runtime_info.facts)
    __requirements__()
