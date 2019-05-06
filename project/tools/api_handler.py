import requests
import json
from requests.auth import HTTPBasicAuth

URI = "https://www.longree.be/tfe/api"
HEADER = {"Content-Type": "application/json"}
AUTH = HTTPBasicAuth('username', 'password')


def get_clusters(status=False):
    # get all clusters
    response = requests.get(URI + "/clusters", auth=AUTH)
    clusters = {}
    if response.status_code == 200:
        for key, value in json.loads(response.text)['result'].items():
            clusters[value['name']] = value
            clusters[value['name']]['port'] = int(clusters[value['name']]['port'])
            if not status and 'status' in clusters[value['name']]:
                del clusters[value['name']]['status']
    return clusters


def get_cluster(name):
    clusters = get_clusters()
    if name in clusters:
        return clusters[name]
    else:
        return None


def get_cluster_similar_jobs(jobs):
    # return all clusters with the preferred job given
    clusters = get_clusters()
    return [value for key, value in clusters.items() if any(job in value['preferred_jobs'] for job in jobs)]


def submit_job(job_uuid, job):
    response = requests.post(URI + "/jobs/" + str(job_uuid),
                             data=json.dumps(job),
                             headers=HEADER,
                             auth=AUTH)
    if response.status_code != 200:
        raise Exception("Error while submitting job to the API.\nServer response ({}): {}"
                        .format(response.status_code, response.text))


def get_job(job_uuid):
    response = requests.get(URI + "/jobs/" + str(job_uuid), auth=AUTH)
    if response.status_code == 200:
        return json.loads(response.text)['result'][str(job_uuid)]
    else:
        raise Exception("Unable to retrieve job from server.\nError {} : {}"
                        .format(response.status_code, response.text))


def get_job_state(job_uuid):
    response = requests.get(URI + "/jobs/" + str(job_uuid) + "/state", auth=AUTH)
    if response.status_code == 200:
        return json.loads(response.text)['result']
    else:
        raise Exception("Unable to retrieve job state from server.\nError {} : {}"
                        .format(response.status_code, response.text))
