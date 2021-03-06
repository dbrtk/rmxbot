
import datetime
import json
import os
import re
import stat
from typing import List

import bson
import pymongo

from ...app import celery
from ...config import CORPUS_COLL, CORPUS_ROOT, MATRIX_FOLDER, TEXT_FOLDER
from ...contrib.db.connection import get_collection
from ...contrib.db.models.document import Document
from ...core.matrix_files import get_available_features
from ...tasks.celeryconf import NLP_TASKS

_COLLECTION = get_collection(collection=CORPUS_COLL)


class DataObject(Document):
    """Class mapping the urls in the container to their original Data objects.
    """

    structure = {
        'data_id': str,
        'file_id': str,  # this is a string representation of a uuid

        # todo(): delete
        'file_path': str,

        'texthash': str,
        'file_hash': str,

        'title': str,
        'file_name': str,

        'url': str,
        'text_url': str,

        'checked': bool,
    }


class ExpectedFile(Document):

    structure = {
        'file_name': str,
        'unique_id': str,
        'content_type': str,
        'charset': str,
        'tmp_path': str,
    }


class ContainerStatus(Document):
    """Status object used when computing features."""
    structure = {
        'busy': bool,
        'type': str,
        'feats': int,
        'task_name': str,
        'task_id': str,
        'updated': datetime.datetime
    }

    def __init__(self, *args, **kwds):
        self.default_values = dict(
            updated=datetime.datetime.now(),
            busy=False,
            type='features'
        )
        super().__init__(*args, **kwds)


class ContainerModel(Document):

    __collection__ = _COLLECTION

    structure = {

        'name': str,
        'description': str,
        'created': datetime.datetime,
        'updated': datetime.datetime,

        'urls': list,
        'data_objects': list,

        'active': bool,

        'status': list,

        'crawl_ready': bool,
        'integrity_check_in_progress': bool,
        'corpus_ready': bool,

        'screenplay': bool,

        'data_from_files': bool,
        'data_from_the_web': bool,

        'expected_files': list,

    }
    required_fields = ['created']

    def __init__(self, *args, **kwds):
        """
        """
        self.default_values = {
            'urls': [],
            'data_objects': [],
            'screenplay': False,
            'status': [],
            'active': True,

            'crawl_ready': False,
            'integrity_check_in_progress': False,
            'corpus_ready': True,

            'expected_files': [],
            'created': datetime.datetime.now(),

            # container type
            'data_from_files': False,
            'data_from_the_web': False,

        }
        super().__init__(*args, **kwds)

    @classmethod
    def inst_new_doc(cls, name=None, save=1, **kwds):

        _doc = cls(name=name)

        if 'screenplay' in kwds and kwds.get('screenplay'):
            _doc['screenplay'] = True

        if save:
            docid = _doc.save()
            _doc.create_folder()
            return docid
        else:
            return _doc

    @classmethod
    def range_query(cls, projection=None, start=0, limit=100,
                    direction=pymongo.ASCENDING, query={}):
        """Overriding document's range_query method in order to get a sliced
           list of urls.
        """
        if not projection:
            projection = {
                'urls': {'$slice': 10},
                'name': 1,
                'description': 1,
                'created': 1
            }
        return super().range_query(
            projection=projection,
            start=start,
            query=query,
            limit=limit,
            direct=direction)

    def get_dataids(self):
        return [bson.ObjectId(_.get('data_id')) for _ in self.get('urls')]

    def get_folder_path(self):
        """ Returns the path to the container directory. """
        return os.path.abspath(os.path.normpath(
            os.path.join(
                CORPUS_ROOT, str(self.get('_id'))
            )
        ))

    def get_vectors_path(self):
        """ Returns the path of the file that contains the vectors. """
        return os.path.join(self.matrix_path, 'vectors.npy')

    @property
    def matrix_path(self):
        return os.path.join(self.get_folder_path(), MATRIX_FOLDER)

    @property
    def matrix_exists(self):
        """Returns True is the matix directory with its files exists."""
        return os.path.exists(self.matrix_path) and os.listdir(
            self.matrix_path)

    @property
    def wf_path(self): return os.path.join(self.matrix_path, 'wf')

    def get_lemma_path(self):
        """Returns the path to the json file that contains the mapping between
           lemma and words, as these appear in texts.
        """
        path = os.path.join(self.matrix_path, 'lemma.json')
        if not os.path.isfile(path):
            raise RuntimeError(path)
        return path

    def get_lemma_words(self, lemma: (str, list) = None):
        """For a list of lemma, returns all the words that can be found in
           texts.
        """
        lemma_list = lemma.split(',') if isinstance(lemma, str) else lemma
        if not all(isinstance(_, str) for _ in lemma):
            raise ValueError(lemma)
        pattern = r"""(\{.*(%s).*\})""" % '|'.join(lemma_list)
        with open(self.get_lemma_path(), 'r') as _file:
            content = _file.read()
            dicts = [_[0] for _ in re.findall(pattern, content)]
            return map(json.loads, dicts), lemma_list

    def texts_path(self):
        """ Returns the path that will contain the files that make the
            container.
        """
        return os.path.join(self.get_folder_path(), TEXT_FOLDER)

    def create_folder(self):
        """ Creating the directory for the texts and matrices.

            permissions 'read, write, execute' to user, group and
            other (777).

        """
        # (_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        path = self.get_folder_path()
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=False)
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for _path in [os.path.join(path, MATRIX_FOLDER),
                      os.path.join(path, TEXT_FOLDER)]:
            if not os.path.isdir(_path):
                os.makedirs(_path, exist_ok=False)
                os.chmod(_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        return path

    def get_features(self,
                     feats: int = 10,
                     words: int = 6,
                     docs_per_feat: int = 0,
                     feats_per_doc: int = 3,
                     **_):
        """ Getting the features from nlp. This will call a view method that
            will retrieve or generate the requested data.
        """

        features, docs = celery.send_task(
            NLP_TASKS['features_and_docs'], kwargs={
                'path': self.get_folder_path(),
                'feats': feats,
                'corpusid': str(self.get_id()),
                'words': words,
                'docs_per_feat': docs_per_feat,
                'feats_per_doc': feats_per_doc
            }
        ).get()

        features = sorted(
            features,
            key=lambda _: _.get('features')[0].get('weight'),
            reverse=True
        )
        return self.features_to_json(features), self.docs_to_json(docs)

    def get_status_feats(self, feats: int = None):

        try:
            return next(_ for _ in self.get('status', None)
                        if _.get('feats') == feats)
        except StopIteration:
            return None

    def set_status_feats(self, feats: int = None, busy: bool = True, **kwds):

        if self.get_status_feats(feats=feats):

            return True
        return _COLLECTION.update({'_id': self.get('_id')}, {
            '$push': {'status': ContainerStatus(
                busy=busy,
                feats=feats,
                **kwds
            )}
        })

    def del_status_feats(self, feats: int = None):
        # todo(): view this method and delete
        return _COLLECTION.update({'_id': self.get('_id')}, {
            '$pull': {'status': {'feats': feats}}
        })

    def update_on_nlp_callback(self, feats: int = None):

        return _COLLECTION.update_one({'_id': self.get('_id')}, {
            '$set': {'crawl_ready': True},
            '$pull': {'status': {'feats': feats}}
        })

    def features_availability(self, feature_number: int = 10):
        """ Checking feature's availability. """
        status = self.get_status_feats(feats=feature_number)

        out = {
            'requested_features': feature_number,
            'corpusid': self.get_id(),
            'busy': False
        }
        if status:
            if status.get('busy') is True and status.get(
                    'feats') == feature_number:
                delta = datetime.datetime.now() - status.get('updated')
                delta = divmod(delta.total_seconds(), 60)
                # after 15 minutes, the status lock should be deleted (in case
                # of bugs, crashes).
                if delta[0] >= 15:
                    self.del_status_feats(feats=feature_number)
                else:
                    out['busy'] = True
        if out['busy'] is False:
            try:
                _count = get_available_features(
                    containerid=str(self.get_id()),
                    folder_path=self.get_folder_path())
                next(_ for _ in _count if int(
                    _.get('featcount')) == feature_number)
                _count = list(int(_.get('featcount')) for _ in _count)
            except StopIteration:
                out['available'] = False
            else:
                out['features_count'] = _count
                out['feature_number'] = feature_number
                out['available'] = feature_number in _count
        return out

    def get_features_count(self, verbose: bool = False):
        """ Returning the features count. """

        avl = get_available_features(containerid=str(self.get_id()),
                                     folder_path=self.get_folder_path())
        if verbose:
            return avl
        else:
            return sorted([int(_.get('featcount')) for _ in avl])

    def get_url_doc(self, docid):
        """ Get the url doc for id. """
        try:
            return next(
                _ for _ in self.get('urls')
                if _.get('data_id') == docid or _.get('file_id') == docid
            )
        except StopIteration:
            raise RuntimeError(docid)

    def features_to_json(self, features):
        """ Mapping a list of given docs to feature's doc. """
        for _ftr in features:
            for _doc in _ftr.get('docs'):
                _ = self.get_url_doc(_doc.get('dataid'))
                _doc['title'] = _.get('title')
                _doc['url'] = _.get('url')
        return features

    def docs_to_json(self, docs):
        """
        """
        for doc in docs:
            url_obj = self.get_url_doc(doc.get('dataid'))
            doc['url'] = url_obj.get('url')
            doc['title'] = url_obj.get('title')
            doc['fileid'] = url_obj.get('file_id')
        return docs

    @classmethod
    def file_extract_callback(cls,
                              containerid: str = None,
                              unique_file_id: str = None):
        """
        :param containerid:
        :param unique_file_id:
        :return:
        """
        _COLLECTION.update_one({'_id': bson.ObjectId(containerid)}, {
            '$pull': {'expected_files': {'unique_id': unique_file_id}}
        })
        doc = cls.inst_by_id(containerid)
        return doc

    @classmethod
    def update_expected_files(
            cls, containerid: str = None, file_objects: list = None):
        """ Updaing the expected_files field with file objects that are
        created.
        :param containerid:
        :param file_objects:
        :return:
        """
        # for item in file_objects:
        #     ExpectedFile.simple_validation(item)
        return _COLLECTION.update_one(
            {'_id': bson.ObjectId(containerid)},
            {
                '$addToSet': {'expected_files': {'$each': file_objects}},
                '$set': {
                    'crawl_ready': False,
                    'data_from_files': True,
                    'data_from_the_web': False,
                }
            })

    def set_container_type(self,
                           data_from_files: bool = False,
                           data_from_the_web: bool = False):
        """
        :param data_from_files: bool
        :param data_from_the_web: bool
        :return:
        """
        if data_from_files:
            query = {
                'data_from_files': True,
                'data_from_the_web': False
            }
        elif data_from_the_web:
            query = {
                'data_from_files': False,
                'data_from_the_web': True
            }
        else:
            query = {
                'data_from_files': data_from_files,
                'data_from_the_web': data_from_the_web
            }
        return _COLLECTION.update_one({'_id': self.get_id()}, {'$set': query})

    def dataid_fileid(self, data_ids: List[str] = None) -> List[tuple]:
        """Returns a mapping between data ids and file ids."""
        return [(_.get('data_id'), _.get('file_id'),)
                for _ in self.get('urls') if _.get('data_id') in data_ids]

    def del_data_objects(self, data_ids: List[str] = None):
        """Deleting data objects from the urls list.
        :param data_ids:
        :return:
        """
        return _COLLECTION.update_one(
            {'_id': self.get_id()},
            {'$pull': {
                'urls': {
                    'data_id': {
                        "$in": data_ids
                    }
                }
            }}
        )


def insert_urlobj(containerid: (str, bson.ObjectId) = None,
                  url_obj: dict = None):
    """ Validating the url object and inserting it in the container list of urls.
    """
    DataObject.simple_validation(url_obj)

    containerid = bson.ObjectId(containerid)
    _COLLECTION.update_one(
        {'_id': containerid},
        {'$push': {'urls': url_obj}}
    )
    return containerid


def set_crawl_ready(containerid, value):
    """ Set the value of crawl_ready on the container. """
    _id = bson.ObjectId(containerid)
    if not isinstance(value, bool):
        raise RuntimeError(value)
    return _COLLECTION.update({'_id': _id}, {'$set': {'crawl_ready': value}})


def set_integrity_check_in_progress(containerid, value):
    """ Set the value of crawl_ready on the container. """
    _id = bson.ObjectId(containerid)
    if not isinstance(value, bool):
        raise RuntimeError(value)
    return _COLLECTION.update({'_id': _id}, {
        '$set': {'integrity_check_in_progress': value}})


def integrity_check_ready(containerid):
    """Called when a crawl and the integrity check succeed."""
    return _COLLECTION.update({'_id': bson.ObjectId(containerid)}, {
        '$set': {
            'integrity_check_in_progress': False,
            'crawl_ready': True,
            'corpus_ready': True
        }})


def container_status(containerid):
    """Retrieves status related data for a container id."""
    return _COLLECTION.find_one({'_id': bson.ObjectId(containerid)}, {
        'crawl_ready': 1,
        'integrity_check_in_progress': 1,
        'corpus_ready': 1,
        'data_from_files': 1,
        'data_from_the_web': 1,
    })


def request_availability(containerid, reqobj: dict, container=None):
    """ Checks for the availability of a feature.
    The reqobj should look like this:
    {
        public: 'bool - if true, send this message to the group',
        features: 'the number of features',
        words: 'the number of feature words',
        documents: 'the number of documents per feature'
    }
    """
    structure = dict(
        features=int
    )
    for k, v in reqobj.items():
        if not isinstance(v, structure.get(k)):
            raise ValueError(reqobj)

    container = container or ContainerModel.inst_by_id(containerid)

    availability = container.features_availability(
        feature_number=reqobj['features'])

    return availability
