import os
import subprocess
import io
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from paramiko import client, RSAKey
import tarfile
from project import package_directory, os_family
from project.constants import WRAPPER_PATH


def is_reachable(hostname):
    # TODO manage if the System is not supported

    ping_cmd = "ping -n 1 " if os_family == 'Windows' else "ping -c 1 "
    # test if cluster is reachable beforehand
    if subprocess.call(ping_cmd + hostname, shell=True, stdout=open(os.devnull, 'w')) is 0:
        return True
    else:
        return False


class Ssh:
    client = None
    channel = None

    # def __init__(self, address, username, password):
    #     self.address = address
    #     self.username = username
    #     self.password = password
    #     self.client = client.SSHClient()

    def __init__(self, address, port, username, pkey_file, passphrase):
        self.address = address
        self.port = port
        self.username = username
        self.pkey_file = RSAKey.from_private_key_file(pkey_file, passphrase)
        self.passphrase = passphrase
        self.client = client.SSHClient()

    def __connect__(self):
        # Allow auto adding is host is not known
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())

        # test if cluster is reachable beforehand
        if is_reachable(self.address):
            # self.client.connect(
            #     hostname=self.address,
            #     username=self.username,
            #     password=self.password,
            #     look_for_keys=False
            # )

            self.client.connect(
                hostname=self.address,
                port=self.port,
                username=self.username,
                pkey=self.pkey_file,
                passphrase=self.passphrase,
                look_for_keys=False
            )
            return True
        else:
            return False

    def __prep_remote_env__(self, job_uuid):
        self.run_command('mkdir ' + str(job_uuid))
        self.remote_path = str(job_uuid) + '/'

    def __close__(self):
        if self.client:
            self.client.close()
        else:
            raise Exception("Cannot run command if no connection has been established")

    def __transfer_wrapper__(self):
        # transfer wrapper to a common directory to all clusters
        # Compress wrapper into a TAR for easier transfer
        with tarfile.open(os.path.join(package_directory, "wrapper.tar.gz"), "w:gz") as tar:
            tar.add(WRAPPER_PATH, arcname=os.path.basename(WRAPPER_PATH))
            tar.close()
        if self.client:
            sftp_client = self.client.open_sftp()
            sftp_client.put(os.path.join(package_directory, "wrapper.tar.gz"), self.remote_path + 'wrapper.tar.gz')
            sftp_client.close()
        else:
            raise Exception("Cannot run command if no connection has been established")

    def __transfer__(self, file_name, path_to_file):
        if self.client:
            sftp_client = self.client.open_sftp()
            out = sftp_client.put(os.path.join(path_to_file, file_name), self.remote_path + file_name)
            sftp_client.close()
            return out
        else:
            raise Exception("Cannot run command if no connection has been established")

    def __retrieve__(self, job_uuid, file_name, path_to_file):
        # local path depends on the local OS in use
        local = os.path.join(os.getcwd(), file_name)
        # remote path is assumed as always being UNIX-based
        remote = path_to_file
        if self.client:
            sftp_client = self.client.open_sftp()
            sftp_client.get(remote, local)
            sftp_client.close()
        else:
            raise Exception("Cannot run command if no connection has been established")

    def run_command(self, command):
        self.channel = self.client.get_transport().open_session()
        if self.channel:
            self.channel.exec_command(command)
        else:
            raise Exception("Cannot run command if no connection has been established")

    def run_command_foreground(self, command):
        if self.client:
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                if stdout.channel.exit_status_ready():
                    result = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        result += stdout.channel.recv(1024)
                    return str(result)
        else:
            raise Exception("Cannot run command if no connection has been established")
