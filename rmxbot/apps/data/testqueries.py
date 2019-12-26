#!/usr/bin/env python

from pymongo import MongoClient
import re

CLIENT = MongoClient()


def get_connection(db='rmx', collection=None):
    """ returns a database connection and the collection """
    assert isinstance(collection, str), "No collection name provided."
    database = CLIENT[db]
    collection = database[collection]
    return database, collection


def get_collection(collection=None):
    """ returns an instance of the mongodb collection """
    conn = get_connection(collection=collection)
    return conn[1]


_COLLECTION = get_collection('data')


def query(search_txt=None, imgs=0):
    """ Given a search_txt (word or sentetnce), queries the database and returns
    stuff. """
    assert isinstance(search_txt, str), 'a string is required as query'
    if not search_txt:
        return []
    ptrn = re.compile(r'.*%s.*' % re.escape(search_txt),
                      re.IGNORECASE | re.DOTALL)
    return _COLLECTION.aggregate([
        {'$match': {'$text': {'$search': search_txt}}},
        {'$project': {'_id': 1, 'url': 1, 'data': 1}},
        {'$unwind': '$data'},
        {'$match': {'$or': [
            {'data.data': {'$regex': ptrn}},
            {'data.tag': 'img'}
        ]} if imgs else {'data.data': {'$regex': ptrn}}},
        {'$project': {'data': '$data.data',
                      '_id': '$_id',
                      'url': '$url',
                      'tag': '$data.tag'}
        }
    ])


def with_map_reduce(search_txt=None, imgs=0):
    """ Given a search_txt (word or sentetnce), queries the database and returns
    stuff. """
    assert isinstance(search_txt, str), 'a string is required as query'
    if not search_txt:
        return []
    ptrn = re.compile(r'.*%s.*' % re.escape(search_txt),
                      re.IGNORECASE | re.DOTALL)
    
    
    return 



def query_with3imgs(search_query):
    """ Querying for paragraphs (text tags) with max 3 images below and
    above. """

    def _process_docs(docs):
        for item in docs:
            yield item 

    docs = list(_process_docs(query(search_query)))
    return docs


def test_query(query, imgs=0):
    """ building an aggregation for retrieving tags and surrounding images
    """    
    ptrn = re.compile(r'.*%s.*' % re.escape(query), re.IGNORECASE | re.DOTALL)
    data = _COLLECTION.aggregate([
        {'$match': {'$text': {'$search': query}}},
        {'$project': {'_id': 1, 'url': 1, 'data': 1}},
        {'$unwind': '$data'},
        {'$match': {'$or': [
            {'data.data': {'$regex': ptrn}},
            {'data.tag': 'img'}
        ]} if imgs else {'data.data': {'$regex': ptrn}}},
        {'$project': {'data': '$data.data',
                      '_id': '$_id',
                      'url': '$url',
                      'tag': '$data.tag'}
        }
    ])
    return data


if __name__ == '__main__':    
    # test_query('drug', imgs=1)
    query('drug', imgs=1)
