# TODO connect to database here
import configparser
from pymongo import MongoClient

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus


def get_mongo():
    config = configparser.ConfigParser()
    config.read("dao/config.ini")

    uri = "mongodb://%s:%s@%s:%s/%s" % (quote_plus(config["mongodb"].get("Username")),
                                        quote_plus(config["mongodb"].get("Password")),
                                        config["mongodb"].get("ServerIp"),
                                        config["mongodb"].get("ServerPort"),
                                        config["mongodb"].get("Database"))
    client = MongoClient(uri)

    db = client[config["mongodb"].get("Database")]
    return db


database = get_mongo()
