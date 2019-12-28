

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
        containerid
      }
    }
    ```
    """
    class Arguments:
        name = graphene.String(required=True)
        endpoint = graphene.String(required=True)
        crawl = graphene.Boolean(default_value=True)

    success = graphene.String()
    containerid = graphene.String()

    def mutate(root, info, name, endpoint, crawl):

        resp = data.create_from_crawl(name=name, endpoint=endpoint, crawl=crawl)
        return CreateCorpus(**resp)


class UpdateCorpus(graphene.Mutation):
    """
    Starting a crawl on an existing corpus.

    ```
    mutation {
      crawl(
        endpoint:"https://another-endpoint.com/",
        containerid:"<CORPUS_ID>",
        crawl:true
      ) {
        success
        containerid
      }
    }
    ```
    """
    class Arguments:
        containerid = graphene.String(required=True)
        endpoint = graphene.String(required=True)
        crawl = graphene.Boolean(default_value=True)

    success = graphene.String()
    containerid = graphene.String()

    def mutate(root, info, containerid, endpoint, crawl=True):

        resp = data.crawl(containerid=containerid, endpoint=endpoint, crawl=crawl)
        return CreateCorpus(**resp)


class DeleteTexts(graphene.Mutation):
    """
    Deleting texts attached to the data-set/container.
    Example of a graphql query:
    ```
    mutation {
      deleteTexts(
        containerid:"<CORPUS_ID>",
        dataids: [<DATA-ID>, <DATA-ID>, <DATA-ID>]
      ) {
        success
        containerid
      }
    }

    ```
    """

    class Arguments:
        containerid = graphene.String(required=True)
        dataids = graphene.List(graphene.String, required=True)

    success = graphene.Boolean()
    containerid = graphene.String()

    def mutate(root, info, containerid, dataids):

        data.delete_texts(containerid=containerid, dataids=dataids)
        return DeleteTexts(success=True)


class Mutation(graphene.AbstractType):

    create = CreateCorpus.Field()
    crawl = UpdateCorpus.Field()
    delete_texts = DeleteTexts.Field()
