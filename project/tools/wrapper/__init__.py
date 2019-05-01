import os


class RuntimeInfo:
    def __init__(self):
        self.job_uuid = None
        self.ONLINE_JOB_FILE = None
        self.TAR_FILE = None
        self.user_input = None
        self.destination_cluster = None
        self.modules = None
        self.facts = None
        self.job_directory = os.path.join(os.getcwd(),'')
        self.working_directory = os.path.join(os.getcwd(), '')
        self.job_status = None

    def update(self, input_values):
        self.job_uuid = input_values['job_uuid']
        self.ONLINE_JOB_FILE = input_values['online_job_file']
        self.TAR_FILE = input_values['tar_file']
        self.user_input = input_values['input']
        self.destination_cluster = input_values['destination_cluster']
        self.modules = input_values['modules']

    def __update_input__(self, values):
        self.user_input = values

    def __update_modules__(self, values):
        self.modules = values

    def __update_facts__(self, values):
        self.facts = values

    def __update_job_status__(self, values):
        self.job_status = values

    def __update_working_dir__(self, path):
        self.working_directory = path

    def get_all(self):
        aggregated = dict()
        aggregated['job_uuid'] = self.job_uuid
        aggregated['online_job_file'] = self.ONLINE_JOB_FILE
        aggregated['tar_file'] = self.TAR_FILE
        aggregated['user_input'] = self.user_input
        aggregated['destination_cluster'] = self.destination_cluster
        aggregated['modules'] = self.modules
        aggregated['facts'] = self.facts
        aggregated['job_directory'] = self.job_directory
        aggregated['working_directory'] = self.working_directory
        aggregated['job_status'] = self.job_status
        return aggregated


runtime_info = RuntimeInfo()


