import requests
import json


URI = "http://127.0.0.1:7676"


def get_clusters():
    # get all clusters
    response = requests.get(URI + "/clusters")
    clusters = {}
    if response.status_code == 200:
        for key, value in json.loads(response.text)['result'].items():
            clusters[value['name']] = value
            clusters[value['name']]['port'] = int(clusters[value['name']]['port'])
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
    pass


def get_job(job_uuid):
    return None


