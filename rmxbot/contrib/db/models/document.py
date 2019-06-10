""" implementation of a Base Document to be used in order to talk to docs
within data collecitons """

import pymongo
import bson

from ...utils import dictionary
from ...datamodel.rmxdict import RmxDict


class Document(RmxDict):
    """
    """
    __collection__ = None
    __database__ = None

    structure = {}

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)

        if hasattr(self, 'default_values'):
            for k, v in self.default_values.items():
                if not any_value(self.get(k)):
                    self[k] = self.default_values[k]

    def save(self):
        """ saving existing documents or inserting new ones. """
        document = self  # todo(): implement validation
        _docid = document.get("_id")
        if _docid:
            self.__collection__.bulk_write([
                pymongo.UpdateOne({'_id': self.get_id()}, {'$set': self})
            ])
            docid = self.get_id()
        else:
            docid = self.__collection__.insert_one(document).inserted_id
        return docid

    @classmethod
    def get_recent(cls, limit=10):
        """ get the 'n' recent documents """
        return cls.__collection__.find().batch_size(250).sort(
            "created", pymongo.DESCENDING).limit(limit)

    @classmethod
    def inst_by_id(cls, docid):
        """ Instantiating a document by id.
        """
        doc = cls.__collection__.find_one({"_id": bson.ObjectId(docid)})
        if doc and isinstance(doc.get('_id'), bson.ObjectId):
            instance = cls()
            dictionary.update(instance, doc)
            return instance
        return 0

    @classmethod
    def inst_from_doc(cls, doc):
        """ given a class object and a document, returns its instance """
        return dictionary.update(cls(), doc)

    @classmethod
    def inst_from_ids(cls, docids):
        """ Instantiating many documents given a list of ids.
        """
        cursor = cls.__collection__.find({"_id": {
            "$in": [bson.ObjectId(_id) for _id in docids]
        }})
        return [cls.inst_from_doc(item) for item in cursor]

    def doc_exists(self):
        """ returns 1 if the doc is saved in the database else 0 """
        if self.get('_id') and isinstance(self.get('_id'), bson.ObjectId):
            return 1
        return 0

    @classmethod
    def create(cls, doc=None):
        """ given a dictionary with key, value pairs, creating and saving a
        document """
        inst = dictionary.update(cls(), doc)
        # todo(): implement the doc's validation
        docid = inst.save()
        return docid

    @classmethod
    def range_query(cls, query={}, projection={}, start=0, limit=100,
                    direct=pymongo.DESCENDING):
        """ range query  """
        return cls.__collection__.find(
            query, projection).sort('created', direct).skip(
                start).limit(limit)

    @classmethod
    def range_query_html(cls, query={}, project={}, start=0, limit=100):
        """
        """
        data = cls.__collection__.aggregate([
            {'$match': query},
            {'$sort': {'created': -1}},
            {'$skip': start},
            {'$limit': limit},
            {'$project': project}
        ])
        # todo(): fix this!
        return list(data)  # return data.get('result')

    @classmethod
    def simple_validation(cls, doc):
        """ Simple validation going one level into the doc."""
        struct = cls.structure
        for key, val in doc.items():
            if key not in struct:
                raise ValueError(doc)
            if not isinstance(val, struct.get(key)):
                raise ValueError(doc)

        return doc

    def get_id(self): return self.get('_id')

    def rm_doc(self):
        """Remove a doc from the database."""
        return self.__collection__.delete_one({'_id': self.get_id()})


def any_value(value):
    """ Checking if there is any value attached to the variable. """

    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (int, float)):
        return True

    try:
        iter(value)
    except (TypeError):
        pass
    else:
        # is iterable
        return True

    return False
