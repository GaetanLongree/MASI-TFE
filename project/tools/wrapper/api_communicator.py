import json
import requests
from requests.auth import HTTPBasicAuth

from . import runtime_info, debug

URI = "https://www.longree.be/tfe/api"
HEADER = {"Content-Type": "application/json"}
AUTH = HTTPBasicAuth('username', 'password')

session = requests.Session()
session.headers.update(HEADER)


def notify_client_state_change(state):
    if len(state) == 1:
        payload = {"state": state[0]}
    elif len(state) > 1:
        payload = {"state": state}

    response = session.put(URI + "/jobs/" + str(runtime_info.job_uuid) + "/state",
                           data=json.dumps(payload),
                           auth=AUTH)

    if response.status_code != 200:
        err = "Error while submitting job to the API.\nServer response ({}): {}" \
            .format(response.status_code, response.text)
        debug.log(err)
        # raise Exception(err)


def notify_client(message):
    payload = {"message": message}

    response = session.put(URI + "/jobs/" + str(runtime_info.job_uuid) + "/notify",
                           data=json.dumps(payload),
                           auth=AUTH)

    if response.status_code != 200:
        err = "Error while submitting job to the API.\nServer response ({}): {}" \
            .format(response.status_code, response.text)
        debug.log(err)
        # raise Exception(err)


def update_job_status():
    response = session.put(URI + "/jobs/" + str(runtime_info.job_uuid),
                           data=json.dumps(runtime_info.get_all()),
                           auth=AUTH)
    if response.status_code != 200:
        err = "Error while submitting job to the API.\nServer response ({}): {}"\
            .format(response.status_code, response.text)
        debug.log(err)
        # raise Exception(err)


def update_cluster_status():
    response = session.put(URI + "/clusters",
                           data=json.dumps(runtime_info.cluster_status),
                           auth=AUTH)
    if response.status_code != 200:
        err = "Error while updating cluster status to the API.\nServer response ({}): {}"\
            .format(response.status_code, response.text)
        debug.log(err)
        #raise Exception(err)
