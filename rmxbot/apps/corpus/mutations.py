

import graphene

from . import data


class CreateCorpus(graphene.Mutation):
    """
    Creating a corpus for a given endpoint.

    ```
    mutation {
      create(
        endpoint:"http://example.com/",
        name:"Name (or title) of the data set",
        crawl:true
      ) {
        success
      }
    }
    ```
    """
    class Arguments:
        name = graphene.String(required=True)
        endpoint = graphene.String(required=True)
        crawl = graphene.Boolean(default_value=True)

    success = graphene.String()

    def mutate(root, info, name, endpoint, crawl):

        data.create_from_crawl(name=name, endpoint=endpoint, crawl=crawl)
        return CreateCorpus(success=True)


class UpdateCorpus(graphene.Mutation):
    """
    Starting a crawl on an existing corpus.

    ```
    mutation {
      crawl(
        endpoint:"https://another-endpoint.com/",
        corpusid:"<CORPUS_ID>",
        crawl:true
      ) {
        success
      }
    }
    ```
    """
    class Arguments:
        corpusid = graphene.String(required=True)
        endpoint = graphene.String(required=True)
        crawl = graphene.Boolean(default_value=True)

    success = graphene.String()

    def mutate(root, info, corpusid, endpoint, crawl=True):

        data.crawl(corpusid=corpusid, endpoint=endpoint, crawl=crawl)
        return CreateCorpus(success=True)


class Mutation(graphene.ObjectType):

    create = CreateCorpus.Field()
    crawl = UpdateCorpus.Field()

