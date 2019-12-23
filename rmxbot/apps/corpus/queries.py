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
      ), {
      availableFeats,
      texts {
        dataId
        title
        texthash
        url
        fileId
        titleId
      },
      corpusid,
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


class CrawlReady(graphene.ObjectType):

    corpusid = graphene.String()
    ready = graphene.Boolean()


class Query(graphene.ObjectType):

    corpus_data = graphene.Field(CorpusDataView,
                                 corpusid=graphene.String(required=True))

    test = graphene.String()

    paginate = graphene.List(CorpusStructure,
                             start=graphene.Int(),
                             limit=graphene.Int())

    corpus_ready = graphene.Field(
        CorpusReady,
        corpusid=graphene.String(),
        feats=graphene.Int())

    crawl_ready = graphene.Field(CrawlReady, corpusid=graphene.String())

    text_upload_ready = graphene.Boolean()

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

        return data.corpus_crawl_ready(corpusid=corpusid)

