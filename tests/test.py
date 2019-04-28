import json
import os
import subprocess
import tarfile
import re

from project.tools.module_handler import ModuleHandler
from project.tools.parser import Parser

# file = "/home/tux/testing/project/data/modules.yml"
# user_input_file = "/home/tux/testing/project/data/user_input.yml"
# user_input = Parser.yaml(user_input_file)
# print(user_input)
#
# handler = ModuleHandler(file)
# handler.run('staging', user_input)

if __name__ == '__main__':
    file = "E:\\git\\MASI-TFE\\project\\data\\modules.yml"
    #user_input_file = "E:\\git\\MASI-TFE\\project\\data\\user_input.yml"
    #user_input = Parser.yaml(user_input_file)
    #print(user_input)

    handler = ModuleHandler(file)
    #handler.run('staging', user_input)
    handler.prep_remote()

