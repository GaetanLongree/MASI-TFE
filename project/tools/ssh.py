from paramiko import client


class Ssh:
    client = None

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

    def __transfer_setup__(self):
        if (self.client):
            sftp_client = self.client.open_sftp()
            sftp_client.put('tools/setup.py', 'setup.py')
            sftp_client.close()
        else:
            raise Exception("Cannot run command if no connection has been established")

    def run_command(self, command):
        # TODO include command checking?
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                if stdout.channel.exit_status_ready():
                    result = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        result += stdout.channel.recv(1024)

                    return str(result, 'utf8')
        else:
            raise Exception("Cannot run command if no connection has been established")

