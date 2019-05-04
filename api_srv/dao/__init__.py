# TODO connect to database here
import configparser
from pymongo import MongoClient


def get_mongo():
    config = configparser.ConfigParser()
    config.read("dao/config.ini")

    uri = "mongodb://%s:%s/%s" % (config["mongodb"].get("ServerIp"),
                                  config["mongodb"].get("ServerPort"),
                                  config["mongodb"].get("Database"))
    client = MongoClient(uri)

    db = client[config["mongodb"].get("Database")]
    return db


database = get_mongo()
