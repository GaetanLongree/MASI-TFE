import os


class RuntimeInfo:
    def __init__(self):
        self.user_input = None
        self.facts = None
        self.job = dict()
        self.working_directory = os.getcwd()

    def __update_input__(self, values):
        self.user_input = values

    def __update_facts__(self, values):
        self.facts = values

    def __update_job__(self, value):
        self.job['file'] = value


runtime_info = RuntimeInfo()


