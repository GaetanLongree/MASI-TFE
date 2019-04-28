import json

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
    handler = ModuleHandler()
    handler.from_yaml(module_file)
    aggregated_input = handler.run('staging', submission.input)
    submission.update_input(aggregated_input['input'])
    submission.import_modules(aggregated_input['modules'])

    # Prepare for pre- and post- modules execution on cluster
    handler.prep_remote()

    submission.__connect__()
    submission.__run__()
    submission.__close__()
    print('Your submission ID = {}'.format(submission.job_uuid))
    print(json.dumps(get(submission.job_uuid)))
    exit(0)


def run(user_file):
    submission = Submission()
    submission.__import_user_input__(user_file)
    submission.__connect__()
    submission.__run__()
    submission.__close__()
    print('Your submission ID = {}'.format(submission.job_uuid))
    print(json.dumps(get(submission.job_uuid)))
    exit(0)


def retrieve(job_uuid):
    Submission.retrieve_result(job_uuid)



