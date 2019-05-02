import json

from project.tools.module_handler import ModuleHandler
from project.tools.parser import Parser
from project.tools.connection import Ssh
from project.tools.submission import Submission
from project.tools.dao.submissions import get


def run_with_module(user_file, module_file):
    submission = Submission()
    handler = ModuleHandler()
    validated = False

    while not validated:
        submission.import_user_input(user_file)
        # Execute module handling - Staging
        handler.from_yaml(module_file)
        aggregated_input = handler.run('staging', submission.input)
        submission.update_input(aggregated_input['input'])
        submission.import_modules(aggregated_input['modules'])
        # Prepare for pre- and post- modules execution on cluster
        handler.prep_remote()
        submission.prep_aggregated_data()
        validated = submission.validate_aggregated_data()

    if validated:
        submission.connect()
        submission.run()
        submission.close()
        print('Your submission ID = {}'.format(submission.job_uuid))
        print(json.dumps(get(submission.job_uuid)))
        exit(0)


def run(user_file):
    submission = Submission()
    handler = ModuleHandler()
    validated = False

    while not validated:
        submission.import_user_input(user_file)
        # Prepare for pre- and post- modules execution on cluster
        handler.prep_remote(modules=False)
        submission.prep_aggregated_data()
        validated = submission.validate_aggregated_data()

    if validated:
        submission.connect()
        submission.run()
        submission.close()
        print('Your submission ID = {}'.format(submission.job_uuid))
        print(json.dumps(get(submission.job_uuid)))
        exit(0)


def retrieve(job_uuid):
    Submission.retrieve_result(job_uuid)



