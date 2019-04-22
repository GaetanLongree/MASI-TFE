import os

from paramiko import client
import tarfile

from project import package_directory
from project.constants import WRAPPER_PATH


class Ssh:
    client = None
    channel = None

    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.client = client.SSHClient()

    def __connect__(self):
        # Allow auto adding is host is not known
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(
            hostname=self.address,
            username=self.username,
            password=self.password,
            look_for_keys=False
        )

    def __close__(self):
        if self.client:
            self.client.close()
        else:
            raise Exception("Cannot run command if no connection has been established")

    def __transfer_wrapper__(self):
        # Compress wrapper into a TAR for easier transfer
        with tarfile.open("wrapper.tar.gz", "w:gz") as tar:
            tar.add(WRAPPER_PATH, arcname=os.path.basename(WRAPPER_PATH))
        if self.client:
            sftp_client = self.client.open_sftp()
            sftp_client.put('wrapper.tar.gz', 'wrapper.tar.gz')
            sftp_client.close()
        else:
            raise Exception("Cannot run command if no connection has been established")

    def __transfer__(self, file_name, path_to_file):
        if self.client:
            sftp_client = self.client.open_sftp()
            sftp_client.put(path_to_file+file_name, file_name)
            sftp_client.close()
        else:
            raise Exception("Cannot run command if no connection has been established")

    def run_command(self, command):
        # TODO include command checking?
        self.channel = self.client.get_transport().open_session()
        if self.channel:
            self.channel.exec_command(command)
        else:
            raise Exception("Cannot run command if no connection has been established")

    def run_command_foreground(self, command):
        # TODO include command checking?
        if self.client:
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                if stdout.channel.exit_status_ready():
                    result = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        result += stdout.channel.recv(1024)
                    return str(result, 'utf8')
        else:
            raise Exception("Cannot run command if no connection has been established")

