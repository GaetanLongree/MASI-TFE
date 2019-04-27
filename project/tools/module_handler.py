import json
import os
import shlex
import shutil
import subprocess
import numpy
from shutil import copyfile

try:
    from project import package_directory
except ImportError:
    from . import runtime_info
    package_directory = runtime_info.working_directory

try:
    from project.constants import WRAPPER_PATH
except ImportError:
    WRAPPER_PATH = os.path.join(package_directory, 'tools', 'wrapper')

try:
    import project.tools.parser as parser
except ImportError:
    from . import parser


class ModuleHandler:
    def __init__(self):
        self.__modules__ = None

    def from_yaml(self, path_to_module_file):
        self.__modules__ = parser.Parser.yaml(path_to_module_file)

    def from_dict(self, modules):
        self.__modules__ = modules

    def __exec_cmd__(self, command, stage, module):
        # change to the module directory (save the current one to return after)
        prev_dir = os.getcwd()
        try:
            os.chdir(os.path.join(package_directory, 'modules'))
        except OSError:
            # if on remote cluster
            os.chdir(os.path.join(package_directory, 'wrapper', 'modules'))

        # run the command
        process = subprocess.Popen(shlex.split(command),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        return_code = process.returncode

        # return to the previous directory
        os.chdir(prev_dir)

        if return_code is not 0:
            raise Exception("Error during module execution in {} stage of the {} module:\n{}".format(
                stage, module['module'], err))
        else:
            return output

    def run(self, stage, user_input):
        for i in range(1, len(self.__modules__[stage]) + 1):
            try:
                module = self.__modules__[stage][i]
            except KeyError:
                # once ported to the cluster, integer are transformed to strings
                module = self.__modules__[stage][str(i)]

            # compile the module if needed
            if 'compilation' in module and module['compilation'] is not None:
                compilation_cmd = module['compilation'] + ' ' + module['module']
                output = self.__exec_cmd__(compilation_cmd, stage, module)

            # run the module based on execution
            execution_cmd = module['execution'] + " '" + json.dumps(user_input) + "'"
            output = self.__exec_cmd__(execution_cmd, stage, module)

            # TODO parse the command output to add to the user_input
            try:
                self.__modules__[stage][i]['module_output'] = json.loads(output)
            except KeyError:
                self.__modules__[stage][str(i)]['module_output'] = json.loads(output)

            user_input = json.loads(output)

        user_input['modules'] = self.__modules__
        return user_input

    def prep_remote(self):
        # TODO to do lel

        # dat list comprehension tho
        remote_stages = ['preprocessing', 'postprocessing']
        remote_modules = [self.__modules__[stage][i + 1]['module']
                          for stage in remote_stages
                          for i in range(0, len(self.__modules__[stage]))]

        remote_modules = numpy.unique(remote_modules)

        # create modules folder in wrapper
        if os.path.isdir(os.path.join(WRAPPER_PATH, 'modules')):
            shutil.rmtree(os.path.join(WRAPPER_PATH, 'modules'))
        os.mkdir(os.path.join(WRAPPER_PATH, 'modules'))
        # copy required modules to new folder
        for module in remote_modules:
            copyfile(os.path.join(package_directory, 'modules', module),
                     os.path.join(WRAPPER_PATH, 'modules', module))
        # copy this file to the wrapper folder
        copyfile(__file__, os.path.join(WRAPPER_PATH, os.path.basename(__file__)))
        # Copy other user files
        copyfile(os.path.join(os.path.dirname(__file__), 'parser.py'),
                 os.path.join(WRAPPER_PATH, 'parser.py'))
