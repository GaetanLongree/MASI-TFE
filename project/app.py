from project.tools.parser import Parser
from project.tools.connection import Ssh
from project.tools.submission import Submission
from project.tools.dao.submissions import get


def run_with_module(user_file, module_file):
    None


def run(user_file):
    submission = Submission()
    submission.__update_user_input__(user_file)
    submission.__connect__()
    submission.__run__()
    submission.__close__()
    print('Your submission ID = {}'.format(submission.uuid))
    print(get(submission.uuid))
    exit(0)


# def run():
#     inventory = Parser.yaml("data/inventory.yml")
#
#     server_connection = Ssh(
#         inventory['target']['hostname'],
#         inventory['target']['username'],
#         inventory['target']['password'])
#
#     server_connection.__connect__()
#     server_connection.__transfer_wrapper__()
#     result = server_connection.run_command('ping 192.168.1.254 -c 10 > /tmp/test.txt')
#     #parsed_result = Parser.str_to_dict(result)
#
#     #print("Destination cluster is running on {} with release {}".format(parsed_result['system'], parsed_result['release']))


