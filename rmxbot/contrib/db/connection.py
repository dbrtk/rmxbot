""" The module getting the database connection, the database and the collection.
"""
from pymongo import MongoClient

from ...config import (MONGODB_LOCATION, MONGODB_NAME, MONGODB_PASS,
                       MONGODB_PORT, MONGODB_USER)

CLIENT = MongoClient(MONGODB_LOCATION,
                     username=MONGODB_USER,
                     password=MONGODB_PASS,
                     authSource=MONGODB_NAME)


def get_connection(db=MONGODB_NAME, collection=None):
    """ returns a database connection and the collection """
    assert isinstance(collection, str), "No collection name provided."
    database = CLIENT[db]
    collection = database[collection]
    return database, collection


def get_collection(collection=None):
    """ returns an instance of the mongodb collection """
    conn = get_connection(collection=collection)
    return conn[1]
