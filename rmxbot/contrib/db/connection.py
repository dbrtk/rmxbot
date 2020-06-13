""" The module getting the database connection, the database and the collection.
"""
from pymongo import MongoClient

from ...config import (MONGODB_LOCATION, MONGODB_NAME, MONGODB_PASS,
                       MONGODB_USER)

CLIENT = None


def get_client():

    global CLIENT
    if not isinstance(CLIENT, MongoClient):
        CLIENT = MongoClient(MONGODB_LOCATION,
                             username=MONGODB_USER,
                             password=MONGODB_PASS,
                             authSource=MONGODB_NAME)
    return CLIENT


def get_connection(db=MONGODB_NAME, collection=None):
    """ returns a database connection and the collection """
    assert isinstance(collection, str), "No collection name provided."
    cli = get_client()
    database = cli[db]
    collection = database[collection]
    return database, collection


def get_collection(collection=None):
    """ returns an instance of the mongodb collection """
    conn = get_connection(collection=collection)
    return conn[1]
