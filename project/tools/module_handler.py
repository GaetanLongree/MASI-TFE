import json
import os
import shlex
import subprocess

from project import package_directory
from project.tools.parser import Parser


class ModuleHandler:
    def __init__(self, path_to_module_file):
        self.__modules__ = Parser.yaml(path_to_module_file)

    def __exec_cmd__(self, command, stage, module):
        # change to the module directory (save the current one to return after)
        prev_dir = os.getcwd()
        os.chdir(os.path.join(package_directory, 'modules'))

        # debuging
        print(command)

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
        for i in range(1, len(self.__modules__[stage])+1):
            module = self.__modules__[stage][i]
            # compile the module if needed
            if 'compilation' in module and module['compilation'] is not None:
                compilation_cmd = module['compilation'] + ' ' + module['module']
                output = self.__exec_cmd__(compilation_cmd, stage, module)
                print(output)

            # run the module based on execution
            execution_cmd = module['execution'] + " '" + json.dumps(user_input) + "'"
            output = self.__exec_cmd__(execution_cmd, stage, module)
            print(output)
            # TODO parse the command output to add to the user_input
            user_input = json.loads(output)

        return user_input

    def prep_remote(self):
        # TODO to do lel
        pass

