class RuntimeInfo:
    def __init__(self):
        self.user_input = None
        self.facts = None
        self.job = dict()

    def __update_input__(self, values):
        self.user_input = values

    def __update_facts__(self, values):
        self.facts = values

    def __update_job__(self, value):
        self.job['file'] = value

    def get(self, key):
        return self.values[key]


runtime_info = RuntimeInfo()

