from project.tools.dao import submissions_table
from tinydb import where


def save_user_data(uuid, user_input):
    submissions_table.insert({'user_uuid': str(uuid), 'user_input': user_input})


def get(uuid):
    return submissions_table.get(where('user_uuid') == str(uuid))
