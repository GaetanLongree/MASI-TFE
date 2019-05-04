import bson
from . import database


def get_table(param):
    return database[param]


def to_dict(cursor):
    result = {}
    for entry in cursor:
        del entry['_id']
        backup = str(entry['job_uuid'])
        result[backup] = entry
    return result


def get_clusters():
    table = get_table('clusters')
    result = {}
    for entry in table.find():
        backup = str(entry['_id'])
        del entry['_id']
        result[backup] = entry
    return result


def get_entry(job_id):
    table = get_table('jobs')
    if job_id is None:
        raise Exception("No ID given")
    else:
        result = table.find({"job_uuid": (job_id)})
    return to_dict(result)


def insert_new_job(new_job):
    table = get_table('jobs')

    result = table.find({"job_uuid": new_job["job_uuid"]})
    if result.count() >= 1:
        raise ValueError("An entry with value 'job_uuid: {}' is already present. Duplicate "
                         "entries are not allowed".format(new_job["job_uuid"]))
    else:
        post_id = table.insert_one(new_job)
        if post_id is not None:
            return str(new_job['job_uuid'])
        else:
            return ""


def update_job(job_id, job_update):
    table = get_table('jobs')

    # Check if the id exists
    result = table.find({"job_uuid": job_id})
    if result.count() < 1:
        raise bson.errors.InvalidId("No entry found with user_id {}".format(job_id))

    result = table.update_one({"job_uuid": job_id}, {"$set": job_update})
    return result.matched_count


def get_job_state(job_id):
    table = get_table('jobs')

    # Check if the id exists
    result = table.find({"job_uuid": job_id})
    if result.count() < 1:
        raise bson.errors.InvalidId("No entry found with user_id {}".format(job_id))

    result = to_dict(result)
    
    if 'job_status' in result[job_id]:
        return result[job_id]['job_status']['State']
    else:
        return ['NOT_SUBMITTED']
