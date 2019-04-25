from project.tools.dao import inventory_table
from tinydb import where


def get_cluster(cluster_name):
    result = inventory_table.get(where('name') == cluster_name)
    return result
