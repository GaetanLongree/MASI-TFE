from . import database


def get_table(param):
    return database[param]


def to_dict(cursor):
    result = {}
    for entry in cursor:
        backup = str(entry['_id'])
        del entry['_id']
        result[backup] = entry
    return result


def get_clusters():
    table = get_table('clusters')
    return to_dict(table.find())

def insert_new_entry(new_entry):
    return None
