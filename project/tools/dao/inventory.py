from project.tools.dao import inventory_db


def get_cluster(cluster_name):
    return next(item for item in inventory_db if item["name"] == cluster_name)
