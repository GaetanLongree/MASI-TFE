import json
import traceback

from project.tools.module_handler import ModuleHandler
from project.tools.submission import Submission


def run_with_module(user_file, module_file):
    submission = Submission()
    handler = ModuleHandler()
    validated = False

    while not validated:
        submission.import_user_input(user_file)
        # Execute module handling - Staging
        handler.from_yaml(module_file)
        try:
            print("Running the STAGING modules, this could take a while...")
            aggregated_input = handler.run('staging', submission.input)
            submission.update_input(aggregated_input['input'])
            submission.import_modules(aggregated_input['modules'])
        except BaseException as err_msg:
            print(err_msg)
            str_in = ""
            while str_in not in ('y', 'yes', 'n', 'no'):
                str_in = input("An error has occurred during the Staging of modules' execution,"
                               "do you wish to continue with the script execution ? [Y|N] ")
                str_in = str_in.lower()
            if str_in in ('n', 'no'):
                exit(1)

        # Prepare for pre- and post- modules execution on cluster
        handler.prep_remote()
        submission.prep_aggregated_data()
        validated = submission.validate_aggregated_data()

    if validated:
        submission.connect()
        submission.run()
        submission.close()
        print('Your submission ID = {}'.format(submission.job_uuid))
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
        exit(0)


def retrieve(job_uuid):
    Submission.retrieve_result(job_uuid)
