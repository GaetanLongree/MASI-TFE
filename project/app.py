from project.tools.module_handler import ModuleHandler
from project.tools.parser import Parser
from project.tools.connection import Ssh
from project.tools.submission import Submission
from project.tools.dao.submissions import get


def run_with_module(user_file, module_file):
    submission = Submission()
    submission.__import_user_input__(user_file)

    # Execute module handling
    # Staging
    handler = ModuleHandler(module_file)
    aggregated_input = handler.run('staging', submission.user_input)
    print(aggregated_input)
    submission.update_input(aggregated_input)
    # Perpare for pre- and post- modules execution on cluster
    handler.prep_remote()

    submission.__connect__()
    submission.__run__()
    submission.__close__()
    print('Your submission ID = {}'.format(submission.uuid))
    print(get(submission.uuid))
    exit(0)


def run(user_file):
    submission = Submission()
    submission.__import_user_input__(user_file)
    submission.__connect__()
    submission.__run__()
    submission.__close__()
    print('Your submission ID = {}'.format(submission.uuid))
    print(get(submission.uuid))
    exit(0)


def retrieve(job_uuid):
    Submission.retrieve_result(job_uuid)



