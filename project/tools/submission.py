import json
from project import package_directory
from project.tools.connection import Ssh
from project.tools.dao.inventory import get_cluster
from project.tools.parser import Parser

class Submission:
    def __init__(self):
        self.connection = None

    def __update_user_input__(self, user_input_file):
        user_input = Parser.yaml(user_input_file)
        if self.__validate_input__(user_input):
            self.user_input = user_input
        else:
            raise Exception("Error in the user input file.")

        # Find the target cluster from User desired input
        self.target_cluster = get_cluster(user_input['destination_cluster'])

        # Assert if the job file is local or a repository for transfer
        if "http" in self.user_input['job']:
            self.ONLINE_JOB_FILE = True
        else:
            self.ONLINE_JOB_FILE = False

    def __connect__(self):
        self.connection = Ssh(
            self.target_cluster['hostname'],
            self.user_input['username'],
            self.user_input['password'])
        self.connection.__connect__()

    def __run__(self):
        # TODO write USER DATA to file for sending then delete file
        self.__prep_data__()
        with open('input.json', 'w') as file:
            json.dump(self.user_input, file)
        self.connection.__transfer__('input.json', package_directory + '\\')
        self.connection.__transfer_wrapper__()
        self.connection.run_command('tar zxf wrapper.tar.gz')
        self.connection.run_command('python -m wrapper -i input.json')

    def __validate_input__(self, user_input):
        # TODO perform some kind of validation
        return True

    def __prep_data__(self):
        self.user_input['destination_cluster'] = self.target_cluster
        self.user_input['online_job_file'] = self.ONLINE_JOB_FILE
        pass

    def __close__(self):
        self.connection.__close__()
