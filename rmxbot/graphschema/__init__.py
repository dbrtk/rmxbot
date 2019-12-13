

import graphene

from ..apps.corpus.graph import force_directed_graph
from .corpus import Corpus, DataObject, ForceDirectedGraph


class RootQuery(graphene.ObjectType):

    hello = graphene.String(name=graphene.String(default_value="stranger"))

    goodbye = graphene.String()

    corpus_all = graphene.List(Corpus)

    corpus = graphene.Field(Corpus)

    force_directed_graph = graphene.Field(ForceDirectedGraph)

    def resolve_hello(root, info):

        print("resolve hello")
        print(root)
        print(info)
        return "Hello stranger!"

    def resolve_corpus_all(root, info):

        print("resolving corpus all")
        print(root)
        print(info)

        return []

    def resolve_corpus(root, info, corpusid):

        pass

    def revolve_force_directed_graph(root, info, *args, **kwds):

        print("resolving features")
        print(root)
        print(info)
        print(*args)
        print(**kwds)

        # force_directed_graph({
        #     'feats': '',
        #     'docs_pre_feat': '',
        #     'feats_per_doc': '',
        #     'words': '',
        #     'corpusid': ''
        # })

    def resolve_hello(root, info, name):
        return f'Hello {name}!'

    def resolve_goodbye(root, info):
        return 'See ya!'


class MutationQuery(graphene.ObjectType):
    pass


class SubscriptionQuery(graphene.ObjectType):
    pass


class Query(graphene.ObjectType):
    # this defines a Field `hello` in our Schema with a single Argument `name`
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    goodbye = graphene.String()

    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (name) for the Field and returns data for the query Response

    def resolve_hello(root, info, name):
        return f'Hello {name}!'

    def resolve_goodbye(root, info):
        return 'See ya!'


schema = graphene.Schema(query=RootQuery)


