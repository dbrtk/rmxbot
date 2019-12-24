"""GraphQL queries."""

import graphene

from . import data


class TxtDatum(graphene.ObjectType):
    """
    Text objects that are contained by instances of the CorpusModel.
    """
    data_id = graphene.String()
    title = graphene.String()
    texthash = graphene.String()
    url = graphene.String()
    file_id = graphene.String()
    title_id = graphene.String()


class CorpusStructure(graphene.ObjectType):
    """
    The basic structure for the corpus, that maps to the one of the
    model/document as it is saved in the database.
    """
    _id = graphene.String()
    name = graphene.String()
    description = graphene.String()
    created = graphene.DateTime()
    updated = graphene.DateTime()

    urls = graphene.List(TxtDatum)

    active = graphene.Boolean()

    crawl_ready = graphene.Boolean()

    integrity_check_in_progress = graphene.Boolean()
    corpus_ready = graphene.Boolean()

    data_from_files = graphene.Boolean()
    data_from_the_web = graphene.Boolean()


class CorpusDataView(graphene.ObjectType):
    """
    Returns the corpus data view calling corpus.data.corpus_data.
    Querying the corpus data view:
    ```
    query {
      corpusData(
        corpusid:"5e00fe205dbae8b568d496b6"
      ) {
      availableFeats
      texts {
        dataId
        title
        texthash
        url
        fileId
        titleId
      }
      corpusid
      name
    }}
    ```
    """
    corpusid = graphene.String(required=True)
    available_feats = graphene.List(graphene.Int)
    name = graphene.String()
    texts = graphene.List(TxtDatum, description="list holding text objects")


class CorpusReady(graphene.ObjectType):
    """
    Checks if a corpus is available and ready to compute.

    The graphql query:
    ```
    {corpusReady(
      corpusid:"5e00fe205dbae8b568d496b6",
      feats:10
    ) {
      corpusid
      requestedFeatures
      busy
      available
      featuresCount
      featureNumber
    }}
    ```
    """
    corpusid = graphene.String()
    busy = graphene.Boolean()
    available = graphene.Boolean()
    requested_features = graphene.Int()
    features_count = graphene.List(graphene.Int)
    feature_number = graphene.Int()


class DatasetReady(graphene.ObjectType):
    """Checking if the dataset is ready after a crawl or file upload."""
    corpusid = graphene.String()
    ready = graphene.Boolean()


class TextInDataset(graphene.ObjectType):
    """Lists all the texts in the database. Used by the Texts class."""
    id = graphene.String()
    url = graphene.String()
    created = graphene.DateTime()
    title = graphene.String()
    hostname = graphene.String()


class Texts(graphene.ObjectType):
    """
    Returns texts attached to the dataset.

    This is the query:
    ```
    query {
      texts(corpusid:"5e00fe205dbae8b568d496b6") {
        corpusid
        filesUploadEndpoint
        datatype
        name
        data {
          id
          url
          created
          title
          hostname
        }
      }
    }
    ```
    """
    files_upload_endpoint = graphene.String()
    datatype = graphene.String()
    corpusid = graphene.String()
    name = graphene.String()
    data = graphene.List(TextInDataset)


class ContextPhrase(graphene.ObjectType):
    """The structure for sentences with a fileid."""
    # the unique id of the file in the dataset/folder. There is a fileid
    # field on the level of data.models.DataModel
    fileid = graphene.String()
    # a list of sentences
    sentences = graphene.List(graphene.String)


class FeatureContext(graphene.ObjectType):
    """
    Retrieves sentences (from a dataset) that contain one or more feature-word.

    The graphql query:
    ```
    query {
      featureContext(
        corpusid:"5dffc8c93e767601249f2fa7",
        words:["earth","remember","dream","call","picture","plane","book",
               "free","spirit","military","gyroscope","seed","fly","pole",
               "nasa","fishbowl","artificial","horizon","cloud","flat"]
      ){
        corpusid
        data {
          sentences
          fileid
        }
        success
      }
    }
    ```
    """
    corpusid = graphene.String()
    success = graphene.Boolean()
    data = graphene.List(ContextPhrase)


class FileText(graphene.ObjectType):
    """
    For a given corpusid and dataid, returns all sentences that are contained
    in the file.
    Graphql query:
    ```
    query {
      fileText(corpusid:"<CORPUS-ID>", dataid:"<DATA-ID>"){
        dataid
        corpusid
        length
        text
      }
    }
    ```
    """
    corpusid = graphene.String()
    dataid = graphene.String()
    text = graphene.List(graphene.String)
    length = graphene.Int()


class Query(graphene.ObjectType):
    """Query handler."""

    corpus_data = graphene.Field(
        CorpusDataView,
        corpusid=graphene.String(required=True)
    )

    paginate = graphene.List(
        CorpusStructure,
        start=graphene.Int(),
        limit=graphene.Int()
    )

    corpus_ready = graphene.Field(
        CorpusReady,
        corpusid=graphene.String(),
        feats=graphene.Int()
    )

    crawl_ready = graphene.Field(DatasetReady, corpusid=graphene.String())

    text_upload_ready = graphene.Field(
        DatasetReady, corpusid=graphene.String())

    texts = graphene.Field(Texts, corpusid=graphene.String())

    feature_context = graphene.Field(
        FeatureContext,
        corpusid=graphene.String(),
        words=graphene.List(graphene.String)
    )

    file_text = graphene.Field(
        FileText,
        corpusid=graphene.String(),
        dataid=graphene.String()
    )

    def resolve_corpus_data(parent, info, corpusid):
        """
        Retrieve data that summarise a corpus/crawl
        :param info:
        :param corpusid:
        :return:
        """
        return data.corpus_data(corpusid)

    def resolve_paginate(parent, info, start, limit):
        """
        Paginates the datasets, retrieving a limited number of field for each
        corpus.

        This is the query:
        ```
        {paginate(start:0, limit:100){
          Id
          description
          name
          urls{
            dataId
            url
            title
            fileId
            texthash
          }
        }}
        ```
        :param info:
        :param start:
        :param limit:
        :return:
        """
        return data.paginate(start=start, limit=limit)

    def resolve_corpus_ready(parent, info, corpusid, feats):

        return data.corpus_is_ready(corpusid=corpusid, feats=feats)

    def resolve_crawl_ready(parent, info, corpusid):
        """
        Checks if the crawl is ready.
        Query:
        ```
        query {
          crawlReady(corpusid:"5e00fe205dbae8b568d496b6") {
            corpusid
            ready
          }
        }
        ```
        :param info:
        :param corpusid:
        :return:
        """
        return data.corpus_crawl_ready(corpusid=corpusid)

    def resolve_text_upload_ready(parent, info, corpusid):
        """
        Checks if the creation of a data set/corpus from file upload is ready.
        Query:
        ```
        query {
          textUploadReady(corpusid:"5e00fe205dbae8b568d496b6") {
            corpusid
            ready
          }
        }
        ```
        :param info:
        :param corpusid:
        :return:
        """
        return data.file_upload_ready(corpusid)

    def resolve_texts(parent, info, corpusid):
        """Retrieves texts attached to a dataset."""
        return data.texts(corpusid)

    def resolve_feature_context(parent, info, corpusid, words):
        """
        Retrieves a context for a feature (list of words).
        :param info:
        :param corpusid: the corpus id
        :param words: list of words
        :return:
        """
        return data.lemma_context(corpusid=corpusid, words=words)

    def resolve_file_text(parent, info, corpusid, dataid):

        return data.get_text_file(corpusid=corpusid, dataid=dataid)


