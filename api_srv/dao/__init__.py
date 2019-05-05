# TODO connect to database here
import configparser
import os

from pymongo import MongoClient


def get_mongo():
    config = configparser.ConfigParser()
    # Done for the docker version launched differently
    if os.path.exists("dao/config.ini"):
        config_path = "dao/config.ini"
    elif os.path.exists("api_srv/dao/config.ini"):
        config_path = "api_srv/dao/config.ini"

    config.read(config_path)

    uri = "mongodb://%s:%s/%s" % (config["mongodb"].get("ServerIp"),
                                  config["mongodb"].get("ServerPort"),
                                  config["mongodb"].get("Database"))
    client = MongoClient(uri)

    db = client[config["mongodb"].get("Database")]
    return db


database = get_mongo()
