import os
from ast import literal_eval

from yaml import load as yaml_load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class Parser(object):
    @staticmethod
    def yaml(path):
        if os.path.exists(path):
            with open(path, 'r') as yaml_file:
                return yaml_load(yaml_file, Loader=Loader) or {}

    @staticmethod
    def str_to_dict(string):
        return literal_eval(string)
