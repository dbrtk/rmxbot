"""Defining a model for the Data Object that holds the data coming from a
   scraped web page. """
import datetime
import hashlib
import os
import stat
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
import uuid

import bson
from pymongo import UpdateOne

from ...config import DATA_COLL
from ...contrib.db.models.document import Document
from ...contrib.db.models.fields.urlfield import UrlField
from ...contrib.utils import dictionary
from .errors import DuplicateUrlError

from ...contrib.db.connection import get_collection


_COLLECTION = get_collection(collection=DATA_COLL)

SPECIAL_TAGS = ['img']
MEDIA_TAGS = ['img', 'video', 'canvas', 'audio']
BLOCK_TAGS = MEDIA_TAGS + ['meta', 'button', 'nav']

# miscellaneous tags are basically difficult tags.
MISCELLANEOUS_TAGS = ['div', 'a', 'ul', 'li', 'span']


LISTURLS_PROJECT = {
    'id': '$_id',
    'url': '$url',
    'created': '$created',
    'title': '$title',
    'hostname': '$hostname'
}

LIST_SCREENPLAYS_PROJECT = {
    'id': '$_id',
    'created': '$created',
    'title': '$title',
    'author': '$author',
    'director': '$director',
    'release_date': '$release_date',
    'fileid': '$fileid',
    'filename': '$filename'
}


PROXY_SCRAPER = 1
Code = bson.code.Code


class DataModel(Document):
    """ This model holds the scrapped pages along with the links, images and
    the word count.

    The structure of the data list:

    data: [
        {
            tag: "string describing the tag - i.e. 'img'",
            data: "the actual content of the tag, by default it is a string, in
                   the case of and image an instance of bson.ObjectId that
                   points to the image document",
            attrs: "relevant tag attributes"
        }, [..]
    ],
    word_count: {
        word: count <int>
    }
    """
    __collection__ = _COLLECTION
    structure = {
        'hostname':  str,
        'url': UrlField,
        'created': datetime.datetime,
        'updated': datetime.datetime,

        'data': list,
        'title': str,
        'corpusid': str,

        'hashtxt': str,
        'hashfile': str,

        'links': list,

        # a hash that defines the file unique id.
        'fileid': str,
        'filepath': str,

        # fields typical to poems and screenplays
        'author': str,
        'director': str,
        'resource_url': UrlField,
        'release_date': str,
        'genre': str,
        'description': str,
        'filename': str,

        # the detected languages by nlp:
        'languages': list
    }
    required_fields = ['url', 'created']

    def save(self):

        self['updated'] = datetime.datetime.now()

        return super().save()

    def __init__(self, *args, **kwds):
        """
        """
        self.default_values = {
            'created': datetime.datetime.now()
        }
        super(DataModel, self).__init__(*args, **kwds)

    @classmethod
    def create_empty(cls, corpusid: str = None, title: str = None,
                     fileid: str = None):

        data_obj = cls()
        data_obj['title'] = title
        data_obj['corpusid'] = corpusid
        if not fileid:
            fileid = data_obj.file_identifier()
        data_obj['fileid'] = fileid

        docid = data_obj.save()
        assert isinstance(bson.ObjectId(docid), bson.ObjectId)
        return data_obj, fileid

    @classmethod
    def create(cls, data: list = None, corpus_id: str = None,
               links: list = None, corpus_file_path: str = None,
               endpoint: str = None, title: str = None):
        """Creates a DataModel document."""
        data_obj = cls()
        data_obj['title'] = title
        data_obj['links'] = list(set(links))
        data_obj['url'] = UrlField(endpoint).get_value()

        try:
            file_id = data_obj.data_to_corpus(
                path=corpus_file_path,
                file_id=data_obj.file_identifier(),
                data=data
            )
        except DuplicateUrlError as _:

            return None, None
        else:
            data_obj['fileid'] = file_id

        docid = data_obj.save()
        assert isinstance(bson.ObjectId(docid), bson.ObjectId)
        return data_obj, file_id

    @classmethod
    def inst_by_id(cls, docid):
        """
        """
        doc = _COLLECTION.find_one({"_id": bson.ObjectId(docid)})
        assert isinstance(
            doc, dict), "Got a badly formatted doc: \n <%r>" % doc
        return dictionary.update(cls(), doc) if doc else None

    @classmethod
    def get_directory(cls, start=0, limit=100):
        """ retrieving the list of scrapped web pages """
        return cls.range_query_html({}, LISTURLS_PROJECT, start, limit)

    @classmethod
    def query_data_project(cls, query={}, project={}, direct=-1):
        """
        """
        return list(cls.__collection__.aggregate([
            {'$match': query},
            {'$sort': {'created': direct}},
            {'$project': project}
        ]))

    def file_identifier(self):
        """Generating a unique id for the file name."""

        return uuid.uuid4().hex
        # return str(self.get_id())

    def data_to_corpus(self, path, data, file_id: str = None, id_as_head=True):
        """ Dumping data into a corpus file. """
        # todo(): revie this method - make it more general or delete
        path = os.path.normpath(os.path.join(path, file_id))

        if os.path.isfile(path):
            raise DuplicateUrlError

        self.save()

        hasher = hashlib.md5()
        with open(path, 'a+') as _file:
            if id_as_head:

                _file.write(str(self.get_id()))
                _file.write('\n\n')
            for txt in data:
                hasher.update(bytes(txt, 'utf-8'))
                _file.write(txt)
                # _file.write(txt.encode(encoding='UTF-8'))
                _file.write('\n\n')

        self['hashtxt'] = hasher.hexdigest()

        # permissions 'read, write, execute' to user, group, other (777)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        return file_id

    def txt_file_to_corpus(self, txt: str = None):

        pass

    def purge_data(self):
        self['data'] = []
        return self.save()

    def set_hashtxt(self, value: str = None):
        """
        :param value:
        :return:
        """
        if _COLLECTION.find_one({
            'corpusid': self.get('corpusid'), 'hashtxt': value}):
            raise ValueError(self)
        return _COLLECTION.update_one(
            {'_id': self.get_id()},
            {'$set': {'hashtxt': value}}
        )

    def cleanup_error(self):

        pass

    @classmethod
    def delete_many(cls, dataids):
        """Delete many documents from the database."""
        return _COLLECTION.delete_many({
            "_id": {"$in": [bson.ObjectId(_) for _ in dataids]}
        })


def get_doc_for_bulk(obj):

    struct = DataModel.structure
    out = {}
    for k, v in obj.items():
        if k not in struct:
            continue
        if struct[k] in [datetime.date, datetime.datetime]:
            if not v:
                continue
            v = datetime.datetime.strptime(v, '%Y-%m-%d')
        elif struct[k] is int:
            v = int(v)
        elif struct[k] is float:
            v = float(v)

        if isinstance(v, struct.get(k)):
            out[k] = v
    return out


def update_many(id_key_vals: dict = None):

    query = []
    for docid, key_vals in id_key_vals.items():
        key_vals = get_doc_for_bulk(key_vals)
        query.append(
            UpdateOne({'_id': bson.ObjectId(docid)},
                      {'$set': key_vals})
        )
    res = _COLLECTION.bulk_write(query, ordered=False)
    return res.bulk_api_result
