import getpass
import json
import os
import re
import tarfile
import time
import uuid

import numpy

from project import package_directory, current_directory
from project.tools.connection import Ssh, is_reachable
from project.tools.wrapper import workload_manager
from project.tools import api_handler
from project.tools.parser import Parser


class Submission:
    REQUIRED = ('username', 'private_key', 'user_mail', 'destination_cluster', 'job', 'execution', 'output')
    OPTIONAL = ('passphrase', 'requirements', 'resources', 'kwargs')
    AGGREGATED_REQUIRED = ('username', 'private_key', 'user_mail', 'destination_cluster', 'job', 'execution', 'output',
                           'resources')
    AGGREGATED_OPTIONAL = ('passphrase', 'resources', 'kwargs')

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
        self.destination_cluster = api_handler.get_cluster(user_input['destination_cluster'])
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
        original_target_preferred_jobs = self.destination_cluster['preferred_jobs']

        if 'passphrase' not in self.input:
            passphrase = getpass.getpass(prompt="Please enter the passphrase to your private key file: ")
        else:
            passphrase = self.input['passphrase']

        self.connection = Ssh(
            self.destination_cluster['hostname'],
            self.destination_cluster['port'],
            self.input['username'],
            self.input['private_key'],
            passphrase)

        # TODO use data from API to know if cluster is up or not

        # If not reachable, check the original target cluster preferred jobs
        # and offer to user clusters with similar jobs
        while not self.connection.__connect__():
            print("Unable to connect to cluster {} ({}), the cluster is unreachable".format(
                self.destination_cluster['name'], self.destination_cluster['hostname']))
            choice = input("Do you still wish to connect? (not recommended) [Y|N]")
            if choice in ('y', 'Y'):
                self.connection.__connect_unreachable__()
                break
            else:
                print("Searching for available clusters...")

                # search cluster with similar preferred jobs
                alt_clusters = api_handler.get_cluster_similar_jobs(original_target_preferred_jobs)

                # check if alternative are reachable instead of based on current target name
                alt_clusters = [entry for entry in alt_clusters if is_reachable(entry['hostname'])]

                if len(alt_clusters) == 0:
                    print("No clusters with similar job preferences were found")
                    self.input['destination_cluster'] = input("Please enter the name of a new destination cluster: ")
                    self.destination_cluster = api_handler.get_cluster(self.input['destination_cluster'])
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

                self.connection = Ssh(
                    self.destination_cluster['hostname'],
                    self.destination_cluster['port'],
                    self.input['username'],
                    self.input['private_key'],
                    passphrase)

        # Get the remote home path
        cluster_home_var = "$CECIHOME"  # TODO get this from the DB
        # this is necessary because the CECIHOME variable is not sources on non-interactive shells
        # TODO fix the fact that ECHO is not executed on Hercules and the binary is not located at the same place on all clusters
        command = "sleep 1 && source /etc/profile.d/ceci.sh && echo " + cluster_home_var
        remote_home_path = None
        while remote_home_path is None:
            remote_home_path = self.connection.run_command_foreground(command)
        remote_home_path = remote_home_path.decode("utf-8").split("\r\n")[-2]

        self.connection.__prep_remote_env__(self.job_uuid, remote_home_path)

    def run(self):
        # check if job is a local file or a directory
        if not self.ONLINE_JOB_FILE:
            if os.path.isdir(self.input['job']):
                # TAR the dir
                self.TAR_FILE = True
                with tarfile.open(os.path.join(current_directory, self.input['job'] + ".tar.gz"), "w:gz") as tar:
                    tar.add(os.path.join(current_directory, self.input['job']),
                            os.path.basename(os.path.join(current_directory, self.input['job'])))
                    tar.close()
                    self.connection.__transfer__(self.input['job'] + ".tar.gz", current_directory)
            else:
                self.TAR_FILE = False
                self.connection.__transfer__(self.input['job'], current_directory)

        # delete sensitive data before sending to cluster
        del self.aggregated_data['user_input']['private_key']
        if 'passphrase' in self.input:
            del self.aggregated_data['user_input']['passphrase']

        # save data in DB
        api_handler.submit_job(self.job_uuid, self.aggregated_data)

        # write USER DATA to file for sending then delete file
        with open(os.path.join(package_directory, 'input.json'), 'w') as file:
            # json.dump(self.user_input, file)
            file.write(json.dumps(self.aggregated_data))
            file.close()

        # Check if the Python version 2.7 is available on destination cluster
        python_version = None
        while python_version is None:
            python_version = self.connection.run_command_foreground("python --version 2>&1")
        regex_version = r"^Python\ 2\.7.*?$"
        matches = re.findall(regex_version, python_version.decode("utf-8"), re.MULTILINE)

        if len(matches) > 0:
            while not os.path.exists(os.path.join(package_directory, 'input.json')):
                time.sleep(1)
            self.connection.__transfer__('input.json', os.path.join(package_directory, ''))
            self.connection.__transfer_wrapper__()
            self.connection.run_command(
                'tar zxf ' + self.connection.remote_path + 'wrapper.tar.gz -C ' + self.connection.remote_path)

            # pip install must be run in foreground to install dependencies
            self.connection.run_command_foreground(
                'python -m pip install --user -r ' + self.connection.remote_path + 'wrapper/requirements.txt ' +
                ' || pip install --user -r ' + self.connection.remote_path + 'wrapper/requirements.txt')
            self.connection.run_command('cd ' + self.connection.remote_path + ' \n ' +
                                        'python -m wrapper -i input.json')

        else:
            # if python 2.7 is not preinstalled, check if it can be loaded
            matches = []
            for entry in ("Python/2.7", "python/2.7"):
                python_versions = None
                while python_versions is None:
                    python_versions = self.connection.run_command_foreground("module avail " + entry +
                                                                             " -t 2>&1 \n sleep 1")

                regex = r"^python\/2\.7.*?$"
                temp_matches = re.findall(regex, python_versions.decode("utf-8"), re.MULTILINE | re.IGNORECASE)
                matches += temp_matches

            if len(matches) > 0:
                self.connection.__transfer__('input.json', os.path.join(package_directory, ''))
                self.connection.__transfer_wrapper__()
                self.connection.run_command(
                    'tar zxf ' + self.connection.remote_path + 'wrapper.tar.gz -C ' + self.connection.remote_path)

                # pip install must be run in foreground to install dependencies
                self.connection.run_command_foreground(
                    'module load ' + matches[0] + ' \n ' +
                    'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \n ' +
                    'python get-pip.py \n ' +
                    'python -m pip install --user -r ' + self.connection.remote_path + 'wrapper/requirements.txt ' +
                    ' || pip install --user -r ' + self.connection.remote_path + 'wrapper/requirements.txt')
                self.connection.run_command('cd ' + self.connection.remote_path + ' \n ' +
                                            'module load ' + matches[0] + ' \n ' +
                                            'python -m wrapper -i input.json')
            else:
                raise Exception("The destination cluster ({}) does not support Python version 2.7, please select "
                                "another destination cluster".format(
                                            self.aggregated_data['destination_cluster']['name']))

    def __validate_input__(self, user_input, required=REQUIRED, optional=OPTIONAL, stage="user input file import"):
        if not all(elem in user_input for elem in required):
            print("ERROR during {}: elements are missing from user input - minimum required: {}"
                  .format(stage, required))
            return False

        if not all(elem in user_input for elem in optional):
            print("Some optional elements appear to be missing during the {} (optional entries: {} )"
                  .format(stage, optional))
            print("If you are using modules to determine these input, "
                  "be sure to pass and verify the modules as argument as well.")
            str_in = ""
            while str_in not in ('y', 'yes', 'n', 'no'):
                str_in = input("Are you sure you wish to continue without these entries? [Y|N] ")
                str_in = str_in.lower()

            if str_in in ('y', 'yes'):
                return True
            else:
                return False

        return True

    def prep_aggregated_data(self):
        self.aggregated_data['job_uuid'] = str(self.job_uuid)
        self.aggregated_data['user_input'] = self.input
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
        job_state = api_handler.get_job_state(job_uuid)
        job_state = numpy.unique(job_state)
        submission = api_handler.get_job(job_uuid)

        wlm_handler = workload_manager.get(submission['destination_cluster']['workload_manager'])

        if all(state in wlm_handler.TERMINATED_SUCCESSFULLY_STATUSES for state in job_state):
            if 'private_key' in submission['user_input'] and os.path.exists(submission['user_input']['private_key']):
                pkey_path = submission['user_input']['private_key']
            else:
                valid = False
                path = ""
                while not valid:
                    string = input("Original private key file not found at the original given location ({})\n"
                                   "Please enter the path to the private key file to connect to the cluster: "
                                   .format(path))
                    valid = os.path.exists(string)
                    path = string

                pkey_path = os.path.abspath(path)

            passphrase = getpass.getpass(prompt="Please enter the passphrase to your private key file: ")

            connection = Ssh(
                submission['destination_cluster']['hostname'],
                submission['destination_cluster']['port'],
                submission['user_input']['username'],
                pkey_path,
                passphrase)
            if not connection.__connect__():
                connection.__connect_unreachable__()

            # use data received from Wrapper with the job directory
            working_dir = submission['working_directory']

            if 'output' in submission['user_input'] and len(submission['user_input']['output']) > 0:
                if isinstance(submission['user_input']['output'], str):
                    # retrieve a single file
                    connection.__retrieve__(job_uuid, submission['user_input']['output'],
                                            working_dir + submission['user_input']['output'])
                elif isinstance(submission['user_input']['output'], list):
                    for output in submission['user_input']['output']:
                        # do list command compilation
                        connection.__retrieve__(job_uuid, output, working_dir + '/' + output)
        else:
            print("The job you're trying to retrieve has not completed yet\n"
                  "Current state of job: {}".format(job_state))

    def validate_aggregated_data(self):
        # verify that user input contains all the needed information (prompt user to correct and continue?)
        if self.__validate_input__(self.aggregated_data['user_input'],
                                   required=self.AGGREGATED_REQUIRED,
                                   optional=self.AGGREGATED_OPTIONAL,
                                   stage="aggregated data verification"):
            return True
        else:
            str_in = ""
            while str_in not in ('y', 'yes'):
                str_in = input("Please verify your user input and/or your modules file, then enter Y to retry: ")
                str_in = str_in.lower()

            return False
