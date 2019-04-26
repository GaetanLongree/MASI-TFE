from project.tools.dao import inventory_table
from tinydb import where, Query


def get_cluster(cluster_name):
    return inventory_table.get(where('name') == cluster_name)


def get_cluster_similar_jobs(preferred_job):
    return inventory_table.search(Query().preferred_jobs.any(preferred_job))
