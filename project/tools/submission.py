import json
import os
import uuid
from project import package_directory
from project.tools.connection import Ssh, is_reachable
from project.tools.dao import submissions
from project.tools.dao import inventory
from project.tools.parser import Parser


class Submission:
    def __init__(self):
        self.connection = None
        self.uuid = uuid.uuid4()
        self.user_input = None
        self.modules = None

    def __import_user_input__(self, user_input_file):
        user_input = Parser.yaml(user_input_file)
        if self.__validate_input__(user_input):
            self.user_input = user_input
        else:
            raise Exception("Error in the user input file.")

        # Find the target cluster from User desired input
        self.target_cluster = inventory.get_cluster(user_input['destination_cluster'])
        if self.target_cluster is None:
            raise Exception("Cluster {} not present in database.".format(user_input['destination_cluster']))

        # Assert if the job file is local or a repository for transfer
        if "http" in self.user_input['job']:
            self.ONLINE_JOB_FILE = True
        else:
            self.ONLINE_JOB_FILE = False

    def update_input(self, input_dict):
        if self.__validate_input__(input_dict):
            self.user_input = input_dict

    def import_modules(self, modules):
        self.modules = modules

    def __connect__(self):
        # Done so that new targets don't add additional preferred jobs
        self.original_target_preferred_jobs = self.target_cluster['preferred_jobs']

        self.connection = Ssh(
            self.target_cluster['hostname'],
            self.user_input['username'],
            self.user_input['password'])
        # TODO If not reachable, check the original target cluster preferred jobs and offer to user clusters with similar jobs
        while not self.connection.__connect__():
            print("Unable to connect to cluster {} ({}), the cluster is unreachable".format(
                self.target_cluster['name'], self.target_cluster['hostname']))
            print("Searching for available clusters...")

            # TODO search cluster with similar preferred jobs

            alt_clusters = []
            for job in self.original_target_preferred_jobs:
                alt_clusters += inventory.get_cluster_similar_jobs(job)

            # TODO check if alternative are reachable instead of based on current target name
            alt_clusters = [entry for entry in alt_clusters if is_reachable(entry['hostname'])]

            if len(alt_clusters) == 0:
                print("No clusters with similar job preferences were found")
                self.user_input['destination_cluster'] = input("Please enter the name of a new destination cluster: ")
                self.target_cluster = inventory.get_cluster(self.user_input['destination_cluster'])
                if self.target_cluster is None:
                    raise Exception(
                        "Cluster {} not present in database.".format(self.user_input['destination_cluster']))
            else:
                print("We found clusters with similar job preferences based on your original target")
                for i in range(0, len(alt_clusters)):
                    print("\t{} - {} - preferred jobs: {}".format(i + 1, alt_clusters[i]['name'],
                                                                  alt_clusters[i]['preferred_jobs']))
                choice = input("Enter the nbr of the new destination cluster [1-{}]: ".format(len(alt_clusters)))
                self.target_cluster = alt_clusters[int(choice) - 1]
                self.user_input['destination_cluster'] = self.target_cluster['name']

            self.connection = Ssh(
                self.target_cluster['hostname'],
                self.user_input['username'],
                self.user_input['password'])

        self.connection.__prep_remote_env__(self.uuid)

    def __run__(self):
        # TODO write USER DATA to file for sending then delete file
        self.__prep_data__()
        with open(os.path.join(package_directory, 'input.json'), 'w') as file:
            #json.dump(self.user_input, file)
            print(self.user_input)
            file.write(json.dumps(self.user_input))

        # TODO save data in DB
        submissions.save_user_data(self.uuid, self.user_input) # TODO fix modules not being saved in the DB

        self.connection.__transfer__('input.json', os.path.join(package_directory,''))
        self.connection.__transfer_wrapper__()
        self.connection.run_command('tar zxf ' + str(self.uuid) + '/wrapper.tar.gz -C ' + str(self.uuid) + '/')
        # pip install must be run in foreground to install dependencies
        self.connection.run_command_foreground('pip install --user -r ' + str(self.uuid) + '/wrapper/requirements.txt')
        self.connection.run_command('cd ' + str(self.uuid) + ' \n python -m wrapper -i input.json')

    def __validate_input__(self, user_input):
        # TODO perform some kind of validation
        return True

    def __prep_data__(self):
        self.user_input['job_uuid'] = str(self.uuid)
        self.user_input['destination_cluster'] = self.target_cluster
        #self.user_input['modules'] = self.modules
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
