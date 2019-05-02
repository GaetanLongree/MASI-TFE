import json

from . import runtime_info, debug

# TODO manage the API
def notify_client(param):
    debug.log(param)


def update_job_status():
    #debug.log(json.dumps(runtime_info.job_status, indent=4))
    pass


def update_job_id(job_id):
    debug.log("Job has been submitted with job id = {}".format(job_id))
