""" The module getting the database connection, the database and the collection.
"""

from pymongo import MongoClient

# from ...config import MONGODB_LOCATION MONGODB_NAME, MONGODB_PWD, MONGODB_USR
from ...config import MONGODB_LOCATION, MONGODB_NAME, MONGODB_PORT

# guest connection
CLIENT = MongoClient(MONGODB_LOCATION, MONGODB_PORT)

# CLIENT.rmx.authenticate(MONGODB_USR,
#                         MONGODB_PWD,
#                         mechanism='SCRAM-SHA-1')


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
