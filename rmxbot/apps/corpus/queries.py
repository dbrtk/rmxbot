"""GraphQL queries."""

import graphene

from . import data


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
    """
    the future structure for the corpus, that maps to the one of the
    model/document.
    """
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
    texts = graphene.List(CorpusTexts, description="list holding text objects")


class Query(graphene.ObjectType):

    corpus_data = graphene.Field(CorpusDataView,
                                 corpusid=graphene.String(required=True))

    test = graphene.String()

    def resolve_corpus_data(parent, info, corpusid):
        """retrieve data to display a corpus"""
        return data.corpus_data(corpusid)

