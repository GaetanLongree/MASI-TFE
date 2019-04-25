import json
import os
import uuid
from project import package_directory
from project.tools.connection import Ssh
from project.tools.dao import submissions
from project.tools.dao import inventory
from project.tools.parser import Parser

class Submission:
    def __init__(self):
        self.connection = None
        self.uuid = uuid.uuid4()

    def __update_user_input__(self, user_input_file):
        user_input = Parser.yaml(user_input_file)
        if self.__validate_input__(user_input):
            self.user_input = user_input
        else:
            raise Exception("Error in the user input file.")

        # Find the target cluster from User desired input
        self.target_cluster = inventory.get_cluster(user_input['destination_cluster'])

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
        self.connection.__prep_remote_env__(self.uuid)

    def __run__(self):
        # TODO Run modules if needed

        # TODO write USER DATA to file for sending then delete file
        self.__prep_data__()
        with open(os.path.join(package_directory,'input.json'), 'w') as file:
            json.dump(self.user_input, file)

        # TODO save data in DB
        submissions.save_user_data(self.uuid, self.user_input)

        self.connection.__transfer__('input.json', package_directory + '\\')
        self.connection.__transfer_wrapper__()
        self.connection.run_command('tar zxf ' + str(self.uuid) + '/wrapper.tar.gz -C ' + str(self.uuid) + '/')
        self.connection.run_command('cd ' + str(self.uuid) + ' \n python -m wrapper -i input.json')

    def __validate_input__(self, user_input):
        # TODO perform some kind of validation
        return True

    def __prep_data__(self):
        self.user_input['job_uuid'] = str(self.uuid)
        self.user_input['destination_cluster'] = self.target_cluster
        self.user_input['online_job_file'] = self.ONLINE_JOB_FILE

    def __close__(self):
        # TODO Cleanup files
        os.remove(os.path.join(package_directory, 'input.json'))
        os.remove(os.path.join(package_directory, 'wrapper.tar.gz'))
        self.connection.__close__()

    @staticmethod
    def retrieve_result(job_uuid):
        submission = submissions.get(job_uuid)
        output_filename = submission['user_input']['output']
        connection = Ssh(
            submission['user_input']['destination_cluster']['hostname'],
            submission['user_input']['username'],
            submission['user_input']['password'])
        connection.__connect__()
        connection.__retrieve__(output_filename, job_uuid)

