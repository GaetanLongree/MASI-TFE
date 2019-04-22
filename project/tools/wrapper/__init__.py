class RuntimeInfo:
    def __init__(self):
        self.user_input = None
        self.facts = None

    def __update_input__(self, values):
        self.user_input = values

    def __update_facts__(self, values):
        self.facts = values

    def get(self, key):
        return self.values[key]


runtime_info = RuntimeInfo()
