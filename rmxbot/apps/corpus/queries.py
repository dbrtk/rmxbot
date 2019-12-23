"""GraphQL queries."""

import graphene

from . import data


class UpdateCrawl(graphene.ObjectType):

    corpusid = graphene.String(required=True)
    endpoint = graphene.String(required=True)
    crawl = graphene.Boolean(default_value=True)


class LaunchCrawl(graphene.ObjectType):

    name = graphene.String(required=True)
    endpoint = graphene.String(required=True)
    crawl = graphene.Boolean(default_value=True)


class CorpusTexts(graphene.ObjectType):
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

    name = graphene.String()
    description = graphene.String()
    created = graphene.DateTime()
    updated = graphene.DateTime()

    # 'urls': list,
    # 'data_objects': list,

    active = graphene.Boolean()

    # 'status': list,
    #
    crawl_ready = graphene.Boolean()

    integrity_check_in_progress = graphene.Boolean()
    corpus_ready = graphene.Boolean()

    # screenplay = graphene.Boolean()

    data_from_files = graphene.Boolean()
    data_from_the_web = graphene.Boolean()

    # 'expected_files': list,


class CorpusDataView(graphene.ObjectType):

    corpusid = graphene.String(required=True)
    available_feats = graphene.List(graphene.Int)
    corpus_name = graphene.String()
    texts = graphene.List(CorpusTexts, description="list holding text objects")


class Corpus(graphene.ObjectType):

    create_from_crawl = graphene.Field(LaunchCrawl)

    crawl = graphene.Field(UpdateCrawl)

    corpus_data = graphene.Field(CorpusDataView, corpusid=graphene.String(required=True))

    test = graphene.String()

    def resolve_create_from_crawl(parent, info, name, endpoint, crawl):

        return 'create from crawl called'

    def resolve_crawl(parent, info, corpusid, endpoint, crawl):

        return 'crawl called'

    def resolve_corpus_data(parent, info, corpusid):
        """
        Returns the corpus data view calling corpus.data.corpus_data.
        Querying the corpus data view:
        ```
        {corpusData(corpusid:"<THE_CORPUS_ID>"), {
          corpusid,
          availableFeats,
          corpusName,
          texts {
            dataId
            title
            texthash
            url
            fileId
            title
          }
        }}
        ```
        """
        return data.corpus_data(corpusid)

    def resolve_test(parent, info): return 'good pferdle...'


schema = graphene.Schema(query=Corpus)

