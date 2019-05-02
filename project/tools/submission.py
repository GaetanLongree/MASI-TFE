import json
import os
import re
import tarfile
import uuid
from project import package_directory, current_directory
from project.tools.connection import Ssh, is_reachable
from project.tools.dao import submissions
from project.tools.dao import inventory
from project.tools.parser import Parser


class Submission:
    def __init__(self):
        self.connection = None
        self.job_uuid = uuid.uuid4()
        self.ONLINE_JOB_FILE = None
        self.TAR_FILE = None
        self.input = None
        self.destination_cluster = None
        self.modules = None
        self.aggregated_data = dict()

    def import_user_input(self, user_input_file):
        user_input = Parser.yaml(user_input_file)
        if self.__validate_input__(user_input):
            self.input = user_input
        else:
            raise Exception("Error in the user input file.")

        # Find the target cluster from User desired input
        self.destination_cluster = inventory.get_cluster(user_input['destination_cluster'])
        if self.destination_cluster is None:
            raise Exception("Cluster {} not present in database.".format(user_input['destination_cluster']))

        # Assert if the job file is local or a repository for transfer
        if "http" in self.input['job']:
            self.ONLINE_JOB_FILE = True
        else:
            self.ONLINE_JOB_FILE = False

    def update_input(self, input_dict):
        if self.__validate_input__(input_dict):
            self.input = input_dict

    def import_modules(self, modules):
        self.modules = modules

    def connect(self):
        # Done so that new targets don't add additional preferred jobs
        self.original_target_preferred_jobs = self.destination_cluster['preferred_jobs']

        # self.connection = Ssh(
        #     self.destination_cluster['hostname'],
        #     self.input['username'],
        #     self.input['password'])
        self.connection = Ssh(
            self.destination_cluster['hostname'],
            self.destination_cluster['port'],
            self.input['username'],
            self.input['private_key'],
            self.input['passphrase'])
        # If not reachable, check the original target cluster preferred jobs
        # and offer to user clusters with similar jobs
        while not self.connection.__connect__():
            print("Unable to connect to cluster {} ({}), the cluster is unreachable".format(
                self.destination_cluster['name'], self.destination_cluster['hostname']))
            print("Searching for available clusters...")

            # search cluster with similar preferred jobs
            alt_clusters = []
            for job in self.original_target_preferred_jobs:
                alt_clusters += inventory.get_cluster_similar_jobs(job)

            # TODO check if alternative are reachable instead of based on current target name
            alt_clusters = [entry for entry in alt_clusters if is_reachable(entry['hostname'])]

            if len(alt_clusters) == 0:
                print("No clusters with similar job preferences were found")
                self.input['destination_cluster'] = input("Please enter the name of a new destination cluster: ")
                self.destination_cluster = inventory.get_cluster(self.input['destination_cluster'])
                if self.destination_cluster is None:
                    raise Exception(
                        "Cluster {} not present in database.".format(self.input['destination_cluster']))
            else:
                print("We found clusters with similar job preferences based on your original target")
                for i in range(0, len(alt_clusters)):
                    print("\t{} - {} - preferred jobs: {}".format(i + 1, alt_clusters[i]['name'],
                                                                  alt_clusters[i]['preferred_jobs']))
                choice = input("Enter the nbr of the new destination cluster [1-{}]: ".format(len(alt_clusters)))
                self.destination_cluster = alt_clusters[int(choice) - 1]
                self.input['destination_cluster'] = self.destination_cluster['name']

            # self.connection = Ssh(
            #     self.destination_cluster['hostname'],
            #     self.input['username'],
            #     self.input['password'])
            self.connection = Ssh(
                self.destination_cluster['hostname'],
                self.destination_cluster['port'],
                self.input['username'],
                self.input['private_key'],
                self.input['passphrase'])

        self.connection.__prep_remote_env__(self.job_uuid)

    def run(self):

        # check if job is a local file or a directory
        if not self.ONLINE_JOB_FILE:
            if os.path.isdir(self.input['job']):
                # TAR the dir
                self.TAR_FILE = True
                with tarfile.open(os.path.join(current_directory, self.input['job']+".tar.gz"), "w:gz") as tar:
                    tar.add(os.path.join(current_directory, self.input['job']),
                            os.path.basename(os.path.join(current_directory, self.input['job'])))
                    tar.close()
                    self.connection.__transfer__(self.input['job']+".tar.gz", current_directory)
            else:
                self.TAR_FILE = False
                self.connection.__transfer__(self.input['job'], current_directory)

        # save data in DB
        submissions.save_user_data(self.job_uuid, self.aggregated_data)
        # delete sensitive data before sending to cluster
        del self.aggregated_data['input']['private_key']
        del self.aggregated_data['input']['passphrase']

        # write USER DATA to file for sending then delete file
        with open(os.path.join(package_directory, 'input.json'), 'w') as file:
            # json.dump(self.user_input, file)
            file.write(json.dumps(self.aggregated_data))
            file.close()

        self.connection.__transfer__('input.json', os.path.join(package_directory,''))
        self.connection.__transfer_wrapper__()
        self.connection.run_command('tar zxf ' + str(self.job_uuid) + '/wrapper.tar.gz -C ' + str(self.job_uuid) + '/')
        # pip install must be run in foreground to install dependencies
        self.connection.run_command_foreground('pip install --user -r ' + str(self.job_uuid) + '/wrapper/requirements.txt')
        self.connection.run_command('cd ' + str(self.job_uuid) + ' \n python -m wrapper -i input.json')

    def __validate_input__(self, user_input):
        # TODO perform some kind of validation
        return True

    def prep_aggregated_data(self):
        self.aggregated_data['job_uuid'] = str(self.job_uuid)
        self.aggregated_data['input'] = self.input
        self.aggregated_data['destination_cluster'] = self.destination_cluster
        self.aggregated_data['modules'] = self.modules
        self.aggregated_data['online_job_file'] = self.ONLINE_JOB_FILE
        self.aggregated_data['tar_file'] = self.TAR_FILE

    def close(self):
        # Cleanup files
        os.remove(os.path.join(package_directory, 'input.json'))
        os.remove(os.path.join(package_directory, 'wrapper.tar.gz'))
        self.connection.__close__()

    @staticmethod
    def retrieve_result(job_uuid):
        # manage results in an array
        submission = submissions.get(job_uuid)
        # connection = Ssh(
        #     submission['user_input']['destination_cluster']['hostname'],
        #     submission['user_input']['input']['username'],
        #     submission['user_input']['input']['password'])
        connection = Ssh(
            submission['user_input']['destination_cluster']['hostname'],
            submission['user_input']['destination_cluster']['port'],
            submission['user_input']['input']['username'],
            submission['user_input']['input']['private_key'],
            submission['user_input']['input']['passphrase'])
        connection.__connect__()

        # TODO use data received from Wrapper with the job directory
        # Workaround until API is up and running
        working_dir = ""
        if submission['user_input']['online_job_file'] or submission['user_input']['tar_file']:
            if re.search(r"\.git$", submission['user_input']['input']['job']):
                regex = r"\/([^\/]+)\/?(?=\.git$)"
                folder_name = (re.search(regex, submission['user_input']['input']['job'])).group(1)
                working_dir = job_uuid + '/' + folder_name + '/'
            else:
                working_dir = job_uuid + '/' + submission['user_input']['input']['job'] + '/'
        else:
            working_dir = job_uuid + '/'

        if len(submission['user_input']['input']['output']) > 0:
            if isinstance(submission['user_input']['input']['output'], str):
                # do single command compilation
                connection.__retrieve__(job_uuid, submission['user_input']['input']['output'],
                                        working_dir + submission['user_input']['input']['output'])
            elif isinstance(submission['user_input']['input']['output'], list):
                for output in submission['user_input']['input']['output']:
                    # do list command compilation
                    connection.__retrieve__(job_uuid, output, working_dir + output)

    def validate_agreggate_data(self):
        # TODO verify that user input contains all the needed information (prompt user to correct and continue?)
        return True
