from project.tools.parser import Parser
from project.tools.ssh import Ssh


def run():
    inventory = Parser.yaml("data/inventory.yml")

    server_connection = Ssh(
        inventory['target']['hostname'],
        inventory['target']['username'],
        inventory['target']['password'])

    server_connection.__connect__()
    server_connection.__transfer_setup__()
    result = server_connection.run_command('python setup.py')
    parsed_result = Parser.str_to_dict(result)

    print("Destination cluster is running on {} with release {}".format(parsed_result['system'], parsed_result['release']))


